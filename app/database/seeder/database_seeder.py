
import sys
import os



# Add the project root to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import app.database.base # Important: Ensure all models are loaded in registry

from app.database.seeder.admin_seeder import AdminSeeder
from app.database.seeder.categories_seeder import CategoriesSeeder
from app.database.seeder.supplier_type_seeder import SupplierTypeSeeder
from app.database.seeder.supplier_seeder import SupplierSeeder
from app.database.seeder.product_type_seeder import ProductTypeSeeder
from app.database.seeder.product_seeder import ProductSeeder
from app.database.seeder.product_image_seeder import ProductImageSeeder
from app.database.seeder.initial_data_import_seeder import InitialDataImportSeeder
from app.database.seeder.product_view_seeder import ProductViewSeeder
from app.database.seeder.country_seeder import CountrySeeder
from app.database.seeder.move_local_image_to_s3 import MoveLocalImagesToS3
from app.database.session import get_db

class DatabaseSeeder:
    def run(self):
        print("Starting Database Seeder...")
        # Manually get the session generator and the session object
        db_gen = get_db()
        db = next(db_gen)
        try:
            # Call individual seeders here, passing the db session
            AdminSeeder().run(db=db)
            # CategoriesSeeder().run(db=db)
            # SupplierTypeSeeder().run(db=db)
            # SupplierSeeder().run(db=db)
            # ProductTypeSeeder().run(db=db)
            # ProductSeeder().run(db=db)
            # ProductImageSeeder().run(db=db)
            # InitialDataImportSeeder().run(db=db)
            # ProductViewSeeder().run(db=db)
            # CountrySeeder().run(db=db)
            # MoveLocalImagesToS3().run(db=db)
            print("✅ Database Seeding Completed Successfully!")
        finally:
            try:
                next(db_gen) 
            except StopIteration:
                pass
            db_gen.close()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()
