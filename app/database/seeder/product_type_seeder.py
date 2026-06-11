from faker import Faker
from sqlalchemy.orm import Session

from app.models.product_type import ProductType

fake = Faker()

# Realistic product type names
PRODUCT_TYPE_NAMES = [
    "Electronics",
    "Clothing & Apparel",
    "Food & Beverages",
    "Furniture",
    "Building Materials",
    "Chemicals",
    "Machinery",
    "Automotive Parts",
    "Textiles",
    "Packaging Materials",
    "Medical Supplies",
    "Agricultural Products",
]


class ProductTypeSeeder:

    def seed(self, db: Session, count: int = 12):
        try:
            product_types = []

            names_to_use = PRODUCT_TYPE_NAMES[:count]

            for name in names_to_use:
                product_type = ProductType(name=name)
                product_types.append(product_type)

            db.add_all(product_types)
            db.commit()

            for pt in product_types:
                db.refresh(pt)

            print(f"✅ Seeded {len(product_types)} product types")
            return product_types

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding product types: {e}")
            raise e

    def run(self, db: Session):
        return self.seed(db=db)
