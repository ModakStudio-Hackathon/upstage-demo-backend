from pathlib import Path
from typing import Any

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from openai import APIError
from sqlalchemy.orm import Session

from agent.config import check_envs
from agent.exec_agent import USTAgent
from agent.upload import upload
from . import crud, models, schemas
from .database import engine, get_db
from .config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="장부 관리 시스템 API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


@app.post(
    "/receipts/analyze",
    response_model=Any,
    tags=["receipts"],
    summary="영수증 사진 분석",
    description="사진 파일을 받아 Upstage 에이전트 분석 결과(JSON)를 반환합니다.",
)
def analyze_receipt(file: UploadFile = File(...)) -> Any:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="이미지 파일만 업로드할 수 있습니다.",
        )

    max_file_size = 10 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="빈 파일은 분석할 수 없습니다.",
        )
    if file_size > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="이미지 파일은 10MB 이하로 업로드해 주세요.",
        )

    # 업로드 이름은 경로가 아닌 파일명으로만 Upstage에 전달한다.
    filename = (
        Path((file.filename or "receipt-image").replace("\\", "/")).name
        or "receipt-image"
    )
    try:
        check_envs()
        file_id = upload(
            file.file,
            filename=filename,
            content_type=file.content_type,
        )
        return USTAgent().run(file_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except (RuntimeError, APIError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="영수증 분석 서비스에서 오류가 발생했습니다.",
        ) from exc


@app.post(
    "/receipts",
    response_model=schemas.ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["receipts"],
    summary="영수증 장부 항목 생성",
)
def create_receipt(
    receipt: schemas.ReceiptCreate,
    db: Session = Depends(get_db),
):
    return crud.create_receipt(db, receipt)


@app.get(
    "/receipts",
    response_model=list[schemas.ReceiptResponse],
    tags=["receipts"],
    summary="영수증 장부 항목 목록 조회",
)
def read_receipts(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=500, description="최대 조회 항목 수"),
    db: Session = Depends(get_db),
):
    return crud.get_receipts(db, skip=skip, limit=limit)


@app.get(
    "/receipts/{receipt_id}",
    response_model=schemas.ReceiptResponse,
    tags=["receipts"],
    summary="영수증 장부 항목 상세 조회",
)
def read_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = crud.get_receipt(db, receipt_id)
    if receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="영수증 항목을 찾을 수 없습니다.",
        )
    return receipt


@app.patch(
    "/receipts/{receipt_id}",
    response_model=schemas.ReceiptResponse,
    tags=["receipts"],
    summary="영수증 장부 항목 부분 수정",
)
def update_receipt(
    receipt_id: int,
    receipt_update: schemas.ReceiptUpdate,
    db: Session = Depends(get_db),
):
    receipt = crud.update_receipt(db, receipt_id, receipt_update)
    if receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="영수증 항목을 찾을 수 없습니다.",
        )
    return receipt


@app.delete(
    "/receipts/{receipt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["receipts"],
    summary="영수증 장부 항목 삭제",
)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)) -> Response:
    deleted = crud.delete_receipt(db, receipt_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="영수증 항목을 찾을 수 없습니다.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
