from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime 

class CategorySchema(BaseModel):
    id: int
    title : str

    class Config:
        orm_mode = True

class SupportRequestCreate(BaseModel):
    name: str
    email : EmailStr = Field(..., example="ivan@example.com")
    category_id: int
    description : Optional[str]  = Field(None, example= "I don't have access to my account.")


class SupportRequestResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    category: CategorySchema
    description: Optional[str]
    status: str = Field(default="open", example="open")
    created_at: datetime

    class Config:
        orm_mode = True