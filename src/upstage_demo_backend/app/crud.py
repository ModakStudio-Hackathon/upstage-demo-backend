from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas


def get_receipt(db: Session, receipt_id: int) -> Optional[models.Receipt]:
    return db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()


def get_receipts(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Receipt]:
    return (
        db.query(models.Receipt)
        .order_by(models.Receipt.payment_date.desc(), models.Receipt.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_receipt(db: Session, receipt: schemas.ReceiptCreate) -> models.Receipt:
    db_receipt = models.Receipt(**receipt.model_dump())
    db.add(db_receipt)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_receipt)
    return db_receipt


def update_receipt(
    db: Session,
    receipt_id: int,
    receipt_update: schemas.ReceiptUpdate,
) -> Optional[models.Receipt]:
    db_receipt = get_receipt(db, receipt_id)
    if db_receipt is None:
        return None

    # Update에 실제로 전달된 필드만 반영해 기존 값이 None으로 덮이지 않게 한다.
    for field, value in receipt_update.model_dump(exclude_unset=True).items():
        setattr(db_receipt, field, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_receipt)
    return db_receipt


def delete_receipt(db: Session, receipt_id: int) -> bool:
    db_receipt = get_receipt(db, receipt_id)
    if db_receipt is None:
        return False

    db.delete(db_receipt)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
