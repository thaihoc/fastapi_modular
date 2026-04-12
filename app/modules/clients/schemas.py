from pydantic import BaseModel, EmailStr

class ClientCreate(BaseModel):
    name: str
    email: EmailStr

class ClientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True