from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def make_hash_password(plain_password: str) -> str:
        return pwd_context.hash(plain_password)
    
    
    
# import bcrypt


# class Hasher:
#     @staticmethod
#     def verify_password(plain_password: str, hashed_password: str) -> bool:
#         return bcrypt.checkpw(
#             plain_password.encode('utf-8'),
#             hashed_password.encode('utf-8')
#         )

#     @staticmethod
#     def make_hash_password(plain_password: str) -> str:
#         salt = bcrypt.gensalt()
#         hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
#         return hashed.decode('utf-8')