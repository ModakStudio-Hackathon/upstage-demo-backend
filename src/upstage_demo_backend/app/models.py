from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    payment_date = Column(DateTime, nullable=False)
    merchant_file = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    account_category = Column(String(100), nullable=False)
    review_status = Column(Boolean, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
