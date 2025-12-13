import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, default=1)
    unit_price: Decimal = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: str
    quantity: int
    unit_price: Decimal
    added_at: datetime


class CartCreate(BaseModel):
    user_id: uuid.UUID | None = None


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    status: str
    created_at: datetime
    updated_at: datetime
    items: list[CartItemResponse] = []
    total_price: Decimal = Decimal("0.00")


class CartMergeRequest(BaseModel):
    source_cart_id: uuid.UUID
