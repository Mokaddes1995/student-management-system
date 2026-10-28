from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Student
from app.schemas.student import (
    StudentCreate,
    StudentListResponse,
    StudentRead,
    StudentUpdate,
)

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


@router.post(
    "/",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
) -> Student:
    student = Student(**student_data.model_dump())

    db.add(student)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student code or email already exists.",
        ) from err

    return student


@router.get(
    "/",
    response_model=StudentListResponse,
)
def list_students(
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> StudentListResponse:
    statement = select(Student)

    if search is not None:
        search_term = f"%{search.strip()}%"

        statement = statement.where(
            or_(
                Student.student_code.ilike(search_term),
                Student.full_name.ilike(search_term),
                Student.email.ilike(search_term),
                Student.department.ilike(search_term),
            )
        )

    total_statement = select(func.count()).select_from(statement.subquery())
    total = db.scalar(total_statement) or 0

    statement = statement.order_by(Student.id).offset(skip).limit(limit)

    students = list(db.scalars(statement).all())

    return StudentListResponse(
        items=students,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{student_id}",
    response_model=StudentRead,
    status_code=status.HTTP_200_OK,
)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
) -> Student:
    student = db.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )

    update_data = student_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one field must be provided.",
        )

    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Fields cannot be null.",
        )

    for field, value in update_data.items():
        setattr(student, field, value)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student code or email already exists.",
        ) from err

    return student


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
) -> None:
    student = db.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )

    db.delete(student)
    db.commit()
