from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentCreate(BaseModel):
    student_code: str = Field(
        min_length=1,
        max_length=20,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    department: str = Field(min_length=2, max_length=100)
    enrollment_year: int = Field(ge=1900, le=2100)


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_code: str
    full_name: str
    email: EmailStr
    department: str
    enrollment_year: int
    created_at: datetime


class StudentUpdate(BaseModel):
    student_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )
    email: EmailStr | None = None
    department: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    enrollment_year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )


class StudentListResponse(BaseModel):
    items: list[StudentRead]
    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
