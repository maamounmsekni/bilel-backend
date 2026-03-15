from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CommandeCreate(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=1, max_length=50)
    address: str = Field(..., min_length=1, max_length=255)
    commande: str = Field(..., min_length=1)
    date: Optional[datetime] = None

class CommandeUpdate(BaseModel):
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, min_length=1, max_length=255)
    commande: Optional[str] = Field(None, min_length=1)
    date: Optional[datetime] = None

class CommandeOut(BaseModel):
    id: int
    client_name: str
    phone: str
    address: str
    commande: str
    date: datetime

    class Config:
        from_attributes = True
