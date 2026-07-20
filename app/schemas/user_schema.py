from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator   
class ShowUser(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    
    class Config(): #this defines that this response is a orm object not dictionary
        orm_mode: True
#User register validation

NameFieldRule = Annotated[
    str,
    Field(
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9]+$"
    )
]



class UserRegister(BaseModel):
    first_name: NameFieldRule
    last_name: NameFieldRule
    email: Optional[EmailStr] = None
    phone: Annotated[int, Field(min_length=10, max_length=12)]
    country_id: int
    password: Annotated[str, Field(min_length=8)]
    avatar: Optional[str] = None
    


##testing
# try:
#     user = UserRegister(email="jo@sdd.sd")
#     print(user)
# except ValidationError as e:
#     print(e)


class CountryResponse(BaseModel):
    id: int
    name: str
    country_code: str
    dial_code: str
    country_flag: str
class UserResponse(BaseModel):
    id: int
    slug: str
    first_name: str
    last_name: str
    email: str
    phone: str
    country_id: str
    country: CountryResponse
    avatar: str
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str
    deleted_at: str