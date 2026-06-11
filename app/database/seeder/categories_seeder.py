import random
from faker import Faker
from sqlalchemy.orm import Session
from slugify import slugify

from app.models.category import Categories

fake = Faker()

class CategoriesSeeder:

    def seed(self, db: Session, parent_count: int = 10, children_per_parent: int = 5):
        try:
            categories = []
            
            # ---------- Parent Categories ----------
            parents = []
            for _ in range(parent_count):
                name = fake.unique.word().capitalize()
                parent = Categories(
                    name=name,
                    slug=slugify(name),
                    image=fake.image_url(),
                    is_active=True
                )
                parents.append(parent)

            db.add_all(parents)
            db.commit()
            
            # Refresh to get IDs
            for p in parents:
                db.refresh(p)

            # ---------- Child Categories ----------
            for parent in parents:
                for _ in range(children_per_parent):
                    name = fake.unique.word().capitalize()
                    child = Categories(
                        name=name,
                        slug=slugify(f"{name}-{parent.id}"),
                        parent_id=parent.id,
                        image=fake.image_url(),
                        is_active=True
                    )
                    categories.append(child)

            db.add_all(categories)
            db.commit()

            print(f"✅ Seeded {len(parents)} parent categories")
            print(f"✅ Seeded {len(categories)} child categories")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding categories: {e}")
            raise e
            
    def run(self, db: Session):
        self.seed(db=db)
