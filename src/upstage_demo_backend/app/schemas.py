from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReceiptBase(BaseModel):
    payment_date: datetime
    merchant_file: str = Field(..., min_length=1, max_length=255)
    amount: int
    account_category: str = Field(..., min_length=1, max_length=100)
    review_status: bool
    reason: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(ReceiptBase):
    payment_date: Optional[datetime] = None
    merchant_file: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[int] = None
    account_category: Optional[str] = Field(None, min_length=1, max_length=100)
    review_status: Optional[bool] = None
    reason: Optional[str] = None


class ReceiptResponse(ReceiptBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
