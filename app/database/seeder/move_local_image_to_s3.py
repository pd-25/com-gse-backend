import os
import mimetypes
from urllib.parse import urlparse
from sqlalchemy.orm import Session

# from app.models.product_image import ProductImage
from app.models.category import Categories

from app.utils.s3_utils import upload_file_to_s3

class DummyUploadFile:
    def __init__(self, filename, file, content_type):
        self.filename = filename
        self.file = file
        self.content_type = content_type

class MoveLocalImagesToS3:

    def seed(self, db: Session):
        try:
            """
            images are stored in product_image table like this- 'https://api.globalsourceexpoltd.com/jute_images/grocery_and_retail_bags.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/promotional_and_branded_bags.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/grocery_and_retail_bags.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/ribbons_and_cords.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/ropes_and_strings_.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/webbing_and_straps.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/wrapping_cloth.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/area_rugs_and_carpets.jpg',
            'https://api.globalsourceexpoltd.com/jute_images/floor_mats_(door,_kitchen,_bathroom).jpg',
            'https://api.globalsourceexpoltd.com/jute_images/braided_and_flat-weave_rugs.webp'
            ....
            
            Task: I need to move all the local static file images to s3
            1. get all the images from db
            2. process one by one or in batch
            3. check if image link contain "https://api.globalsourceexpoltd.com" and image exist in app/static path like static/{folder}/image.jpg
            4. then move the image to s3 using upload_file_to_s3 in this path - S3_PRODUCT_FOLDER = "products"
            5. then update the new s3 image link to the db(product_image table)
            
            """
            # images = db.query(ProductImage).all()
            images = db.query(Categories).all()
            print(f"Found {len(images)} images in DB. Filtering valid ones...")
            
            tasks = []
            for product_image in images:
                if product_image.image and "https://api.globalsourceexpoltd.com" in product_image.image:
                    # Extract the path from the URL
                    parsed_url = urlparse(product_image.image)
                    path = parsed_url.path.lstrip("/") 
                    
                    local_path = os.path.join("app", "static", path)
                    
                    if os.path.exists(local_path):
                        tasks.append((product_image, local_path))
                    else:
                        print(f"Local file not found for URL {product_image.image}: {local_path}")

            print(f"Total valid images to upload: {len(tasks)}")

            def process_upload(img_obj, loc_path):
                filename = os.path.basename(loc_path)
                content_type, _ = mimetypes.guess_type(loc_path)
                if not content_type:
                    content_type = "application/octet-stream"
                
                f = open(loc_path, "rb")
                dummy_file = DummyUploadFile(filename, f, content_type)
                
                # Upload to S3
                # s3_url = upload_file_to_s3(dummy_file, s3_folder="products")
                s3_url = upload_file_to_s3(dummy_file, s3_folder="categories")
                return img_obj.id, s3_url

            from concurrent.futures import ThreadPoolExecutor, as_completed
            successful_uploads = {}
            
            # Using 10 workers to parallelize network I/O, respecting boto3's default connection pool size
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(process_upload, t[0], t[1]): t for t in tasks}
                
                for future in as_completed(futures):
                    try:
                        img_id, s3_url = future.result()
                        successful_uploads[img_id] = s3_url
                        print(f"Uploaded image ID {img_id} -> {s3_url}")
                    except Exception as exc:
                        print(f"Upload generated an exception: {exc}")

            print("Updating database with new S3 URLs...")
            # Update database sequentially to avoid SQLAlchemy thread-safety issues
            for product_image in images:
                if product_image.id in successful_uploads:
                    product_image.image = successful_uploads[product_image.id]
            
            db.commit()
            print("Finished moving local images to S3.")

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding product images: {e}")
            raise e

    def run(self, db: Session):
        return self.seed(db=db)
