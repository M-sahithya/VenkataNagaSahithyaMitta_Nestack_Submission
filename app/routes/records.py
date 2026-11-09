from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Record, User
from app.schemas import RecordCreateRequest
from app.security.permissions import get_current_user


router = APIRouter(tags=["Records"])


@router.post("/records", status_code=status.HTTP_201_CREATED)
def create_record(
    data: RecordCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_record = Record(
        title=data.title,
        body=data.body,
        owner_id=current_user.id
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "message": "Record created successfully",
        "record": {
            "id": new_record.id,
            "title": new_record.title,
            "body": new_record.body,
            "created_at": new_record.created_at
        }
    }


@router.get("/records/{record_id}")
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if record_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid record ID"
        )

    query = db.query(Record).filter(
        Record.id == record_id
    )

    # Normal users can access only their own records.
    # Admins can access records belonging to any user.
    if current_user.role != "admin":
        query = query.filter(
            Record.owner_id == current_user.id
        )

    record = query.first()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return {
        "id": record.id,
        "title": record.title,
        "body": record.body,
        "created_at": record.created_at
    }