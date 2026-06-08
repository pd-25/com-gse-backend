from pydantic import BaseModel, EmailStr   
class ShowUser(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    
    class Config(): #this defines that this response is a orm object not dictionary
        orm_mode: True