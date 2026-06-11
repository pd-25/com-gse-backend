import random
from faker import Faker
from sqlalchemy.orm import Session

from app.models.product_image import ProductImage
from app.models.product import Product

fake = Faker()


class ProductImageSeeder:

    def seed(self, db: Session, images_per_product: int = 3):
        try:
            # Fetch existing product IDs
            product_ids = [p.id for p in db.query(Product.id).all()]

            if not product_ids:
                print("⚠️  No products found. Run ProductSeeder first.")
                return []

            product_images = []

            for product_id in product_ids:
                num_images = random.randint(1, images_per_product)

                for i in range(num_images):
                    product_image = ProductImage(
                        product_id=product_id,
                        image=fake.image_url(width=800, height=600),
                        is_preview=(i == 0),  # First image is the preview
                    )
                    product_images.append(product_image)

            db.add_all(product_images)
            db.commit()

            print(f"✅ Seeded {len(product_images)} product images for {len(product_ids)} products")
            return product_images

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding product images: {e}")
            raise e

    def run(self, db: Session):
        return self.seed(db=db)
