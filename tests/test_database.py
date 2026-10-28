import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.student import Student


@pytest.fixture
def db_session():

    test_engin = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    Base.metadata.create_all(bind=test_engin)

    with Session(test_engin) as session:
        yield session

    Base.metadata.drop_all(bind=test_engin)
    test_engin.dispose()


def test_create_and_retrive_student(db_session):

    student = Student(
        student_code="STU-001",
        full_name="Rahim Ahmed",
        email="rahim@example.com",
        department="Computer Science",
        enrollment_year=2026,
    )

    db_session.add(student)
    db_session.commit()

    saved_student = db_session.scalar(select(Student).where(Student.student_code == "STU-001"))

    assert saved_student is not None
    assert saved_student.id is not None
    assert saved_student.full_name == "Rahim Ahmed"
    assert saved_student.email == "rahim@example.com"
    assert saved_student.enrollment_year == 2026
    assert saved_student.created_at is not None


def test_code_must_be_unique(db_session):

    first_student = Student(
        student_code="STU-002",
        full_name="Karim Hassan",
        email="karim@example.com",
        department="Mathematics",
        enrollment_year=2026,
    )

    second_student = Student(
        student_code="STU-002",
        full_name="Nadia Akter",
        email="nadia@example.com",
        department="Physics",
        enrollment_year=2026,
    )

    db_session.add(first_student)
    db_session.commit()

    db_session.add(second_student)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
