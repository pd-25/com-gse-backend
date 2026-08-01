import os

from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.models.admin import Admin


password_hash = PasswordHash.recommended()


class AdminSeeder:
    def seed(self, db: Session):
        email = os.getenv("ADMIN_EMAIL", "").strip().lower()
        password = os.getenv("ADMIN_PASSWORD")
        name = os.getenv("ADMIN_NAME", "Admin GSE").strip()
        if not email or not password:
            print("ADMIN_EMAIL and ADMIN_PASSWORD are not set; administrator seed skipped")
            return
        if len(password) < 8:
            raise RuntimeError("ADMIN_PASSWORD must contain at least 8 characters")
        if db.query(Admin.id).filter(Admin.email == email).first():
            print(f"Administrator {email} already exists; credentials were not changed")
            return

        db.add(
            Admin(
                name=name,
                email=email,
                password=password_hash.hash(password),
                is_subadmin=False,
            )
        )
        db.commit()
        print(f"Administrator {email} created successfully")

    def run(self, db: Session):
        self.seed(db=db)
