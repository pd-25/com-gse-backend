from sqlalchemy.orm import Session

from app.core.hashing import Hasher
from app.models.admin import Admin


class AdminSeeder:
    def seed(self, db: Session):
        # data = {
        #     'name': 'Admin GSE',
        #     'email': 'admin@mail.com',
        #     'password': Hasher.make_hash_password('12345'),
        #     'is_subadmin': 0
        # }
        # hasp = Hasher.make_hash_password('12345')
        # print("seing-------------")
        # print("hasp------------- ", hasp)
        # return
        # admin_data = Admin(
        #     name = 'Admin GSE',
        #     email = 'admin@mail.com',
        #     password = hasp,
        #     is_subadmin = 0
        # )
        admins_data = [
            {
                'name':'Admin GSE',
                'email':'admin1@mail.com',
                'password':'12345',
                'is_subadmin':0
            }
        ]
        for admin_info in admins_data:
            # Check if admin already exists (optional but recommended)
            existing_admin = db.query(Admin).filter(Admin.email == admin_info['email']).first()
            if existing_admin:
                print(f"Admin with email {admin_info['email']} already exists, skipping...")
                hashed_password = Hasher.make_hash_password(admin_info['password'])
                
                existing_admin.name=admin_info['name'],
                existing_admin.password=hashed_password,
                print(f"Admin Updated email {admin_info['email']} already exists, skipping...")
                
                continue
                
            hashed_password = Hasher.make_hash_password(admin_info['password'])
            
            admin = Admin(
                name=admin_info['name'],
                email=admin_info['email'],
                password=hashed_password,
                is_subadmin=admin_info['is_subadmin']
            )
            
            db.add(admin)
            print(f"Added admin: {admin_info['name']} ({admin_info['email']})")
        # db.add(admin_data)
        db.commit()
        print("Db comitted.........")
        
    def run(self, db: Session):
        self.seed(db=db)