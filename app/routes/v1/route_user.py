from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_schema import ShowUser
# from db.session import get_db
# from db.repository.user import create_new_user
from typing import List, Optional

user_router = APIRouter()


@user_router.get("/")
def get_users():
    return {"message": "This is the user route"}
# @router.get("/", response_model=List[ShowUser])
# def get_blog(id: Optional[int] = None, db: Session = Depends(get_db)):
#     if id:
#         blog = retrive_blog(id=id, db=db)
#         if not blog:
#             raise HTTPException(detail=f"Blog with ID {id} does not exist", status_code=status.HTTP_404_NOT_FOUND)
#         return blog
#     else:
#         print('this')
#         blogs = retrieve_all_blogs(db=db)
#         return blogs