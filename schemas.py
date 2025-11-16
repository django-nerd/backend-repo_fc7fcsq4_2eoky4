from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Contact(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=2000)

class Project(BaseModel):
    title: str
    description: Optional[str] = None
    tags: list[str] = []
    repo: Optional[str] = None
    demo: Optional[str] = None
