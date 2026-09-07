import unittest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.services.payment_service import _payment_price, process_sslcommerz_notification


class _Query:
    def __init__(self, order):
        self.order = order

    def options(self, *_args):
        return self

    def filter(self, *_args):
        return self

    def first(self):
        return self.order


class _Database:
    def __init__(self, order):
        self.order = order
        self.commits = 0

    def query(self, *_args):
        return _Query(self.order)

    def commit(self):
        self.commits += 1

    def refresh(self, _order):
        pass


def _order():
    return SimpleNamespace(
        order_number="GSE-TEST",
        status="pending",
        currency="BDT",
        total=Decimal("1220.00"),
        paid_at=None,
        sslcommerz_transaction_id="GSESSL-TEST",
        sslcommerz_validation_id=None,
        sslcommerz_bank_transaction_id=None,
        sslcommerz_card_type=None,
        items=[],
    )


class SSLCommerzPaymentTests(unittest.TestCase):
    def test_usd_prices_are_converted_to_bdt(self):
        with patch("app.services.payment_service.settings.USD_TO_BDT_RATE", "122.00"):
            self.assertEqual(_payment_price(Decimal("10"), "USD", "BDT"), Decimal("1220.00"))

    @patch("app.services.payment_service._require_sslcommerz_config", return_value=("store", "password", "https://sandbox"))
    @patch("app.services.payment_service._sslcommerz_request")
    def test_valid_notification_marks_order_paid(self, request_mock, _config_mock):
        order = _order()
        request_mock.return_value = {
            "status": "VALID", "tran_id": order.sslcommerz_transaction_id,
            "amount": "1220.00", "currency": "BDT", "risk_level": "0",
            "bank_tran_id": "BANK-1", "card_type": "VISA",
        }
        db = _Database(order)
        result = process_sslcommerz_notification(
            {"tran_id": order.sslcommerz_transaction_id, "status": "VALID", "val_id": "VAL-1"}, db
        )
        self.assertEqual(result.status, "paid")
        self.assertIsNotNone(result.paid_at)
        self.assertEqual(result.sslcommerz_bank_transaction_id, "BANK-1")
        self.assertEqual(db.commits, 1)

    @patch("app.services.payment_service._require_sslcommerz_config", return_value=("store", "password", "https://sandbox"))
    @patch("app.services.payment_service._sslcommerz_request")
    def test_amount_mismatch_is_rejected(self, request_mock, _config_mock):
        order = _order()
        request_mock.return_value = {
            "status": "VALID", "tran_id": order.sslcommerz_transaction_id,
            "amount": "1.00", "currency": "BDT", "risk_level": "0",
        }
        with self.assertRaises(HTTPException) as raised:
            process_sslcommerz_notification(
                {"tran_id": order.sslcommerz_transaction_id, "status": "VALID", "val_id": "VAL-1"},
                _Database(order),
            )
        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(order.status, "pending")

    @patch("app.services.payment_service._require_sslcommerz_config", return_value=("store", "password", "https://sandbox"))
    @patch("app.services.payment_service._sslcommerz_request")
    def test_risky_notification_is_held_for_review(self, request_mock, _config_mock):
        order = _order()
        request_mock.return_value = {
            "status": "VALIDATED", "tran_id": order.sslcommerz_transaction_id,
            "amount": "1220.00", "currency": "BDT", "risk_level": "1",
        }
        process_sslcommerz_notification(
            {"tran_id": order.sslcommerz_transaction_id, "status": "VALID", "val_id": "VAL-2"},
            _Database(order),
        )
        self.assertEqual(order.status, "payment_review")
        self.assertIsNone(order.paid_at)

    def test_cancel_notification_marks_pending_order_cancelled(self):
        order = _order()
        process_sslcommerz_notification(
            {"tran_id": order.sslcommerz_transaction_id, "status": "CANCELLED"},
            _Database(order),
        )
        self.assertEqual(order.status, "cancelled")


if __name__ == "__main__":
    unittest.main()
