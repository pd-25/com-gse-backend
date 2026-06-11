import random
from faker import Faker
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_view import ProductView

fake = Faker()


class ProductViewSeeder:

    def seed(self, db: Session, count: int = 100):
        try:
            # Fetch existing product IDs
            product_ids = [p.id for p in db.query(Product.id).all()]

            if not product_ids:
                print("⚠️  No products found. Run ProductSeeder first.")
                return []

            product_views = []

            for _ in range(count):
                product_view = ProductView(
                    product_id=random.choice(product_ids),
                    client_ip_address=fake.ipv4(),
                )
                product_views.append(product_view)

            db.add_all(product_views)
            db.commit()

            print(f"✅ Seeded {len(product_views)} product views")
            return product_views

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding product views: {e}")
            raise e

    def run(self, db: Session):
        return self.seed(db=db)
