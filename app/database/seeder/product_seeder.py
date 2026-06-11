import random
from decimal import Decimal
from faker import Faker
from slugify import slugify
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import Supplier
from app.models.product_type import ProductType
from app.models.country import Country
from app.models.category import Categories

fake = Faker()

CURRENCIES = ["USD", "EUR", "GBP", "INR", "AED", "CNY"]
MEASUREMENTS = ["per kg", "per unit", "per liter", "per meter", "per ton", "per box", "per dozen"]


class ProductSeeder:

    def seed(self, db: Session, count: int = 900):
        try:
            # Fetch existing foreign key IDs
            supplier_ids = [s.id for s in db.query(Supplier.id).all()]
            product_type_ids = [pt.id for pt in db.query(ProductType.id).all()]
            country_ids = [c.id for c in db.query(Country.id).all()]
            category_ids = [cat.id for cat in db.query(Categories.id).all()]
            # category_ids = [6,36, 37, 38, 39, 40]

            if not supplier_ids:
                print("⚠️  No suppliers found. Run SupplierSeeder first.")
                return []

            products = []

            for _ in range(count):
                title = fake.catch_phrase()
                slug = slugify(f"{title}-{fake.unique.random_int(min=1000, max=99999)}")

                product = Product(
                    slug=slug,
                    title=title,
                    description=fake.paragraph(nb_sentences=5),
                    short_desc=fake.sentence(nb_words=10),
                    currency=random.choice(CURRENCIES),
                    price=Decimal(str(round(random.uniform(5.0, 5000.0), 2))),
                    price_per_measurement=random.choice(MEASUREMENTS),
                    min_order=random.choice([1, 5, 10, 25, 50, 100, 500]),
                    country_id=random.choice(country_ids) if country_ids else None,
                    supplier_id=random.choice(supplier_ids),
                    product_type_id=random.choice(product_type_ids) if product_type_ids else None,
                    category_id=random.choice(category_ids) if category_ids else None,
                )
                products.append(product)

            db.add_all(products)
            db.commit()

            for p in products:
                db.refresh(p)

            print(f"✅ Seeded {len(products)} products")
            return products

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding products: {e}")
            raise e

    def run(self, db: Session):
        return self.seed(db=db)
