from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Product(BaseModel):
    id: str = Field(alias="_id")
    name: str
    normalized_name: str
    brand: Optional[str] = None
    category: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    margin_score: float = Field(default=0.0, ge=0.0, le=1.0)
    popularity: float = Field(default=0.0, ge=0.0, le=1.0)
    is_sponsored: bool = False
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ProductCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    category: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    margin_score: float = Field(default=0.0, ge=0.0, le=1.0)
    popularity: float = Field(default=0.0, ge=0.0, le=1.0)
    is_sponsored: bool = False
    tags: List[str] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    margin_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    popularity: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_sponsored: Optional[bool] = None
    tags: Optional[List[str]] = None

