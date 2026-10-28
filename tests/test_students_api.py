def valid_student():
    return {
        "student_code": "STU-101",
        "full_name": "Rahim Ahmed",
        "email": "rahim101@example.com",
        "department": "Computer Science",
        "enrollment_year": 2026,
    }


def test_create_student(client):
    response = client.post(
        "/students/",
        json=valid_student(),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["student_code"] == "STU-101"
    assert data["full_name"] == "Rahim Ahmed"
    assert data["email"] == "rahim101@example.com"
    assert data["created_at"] is not None


def test_list_students(client):
    client.post("/students/", json=valid_student())

    response = client.get("/students/")

    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["student_code"] == "STU-101"
    assert data["total"] == 1
    assert data["skip"] == 0
    assert data["limit"] == 10


def test_duplicate_student_code_returns_409(client):
    client.post("/students/", json=valid_student())

    duplicate = valid_student()
    duplicate["email"] = "another@example.com"

    response = client.post("/students/", json=duplicate)

    assert response.status_code == 409


def test_invalid_email_returns_422(client):
    student = valid_student()
    student["email"] = "not-an-email"

    response = client.post("/students/", json=student)

    assert response.status_code == 422


def test_missing_required_field_returns_422(client):
    student = valid_student()
    del student["full_name"]

    response = client.post("/students/", json=student)

    assert response.status_code == 422


def test_list_students_empty_database(client):
    response = client.get("/students/")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_patch_student_updates_one_field(client):
    created = client.post(
        "/students/",
        json=valid_student(),
    )
    student_id = created.json()["id"]

    response = client.patch(
        f"/students/{student_id}",
        json={"department": "Software Engineering"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["department"] == "Software Engineering"
    assert data["full_name"] == "Rahim Ahmed"
    assert data["email"] == "rahim101@example.com"


def test_patch_student_not_found(client):
    response = client.patch(
        "/students/9999",
        json={"department": "Mathematics"},
    )

    assert response.status_code == 404


def test_patch_student_empty_body(client):
    created = client.post(
        "/students/",
        json=valid_student(),
    )
    student_id = created.json()["id"]

    response = client.patch(
        f"/students/{student_id}",
        json={},
    )

    assert response.status_code == 422


def test_patch_student_duplicate_email(client):
    first = valid_student()

    second = valid_student()
    second["student_code"] = "STU-102"
    second["email"] = "another@example.com"

    client.post("/students/", json=first)
    second_response = client.post("/students/", json=second)
    student_id = second_response.json()["id"]

    response = client.patch(
        f"/students/{student_id}",
        json={"email": first["email"]},
    )

    assert response.status_code == 409


def test_delete_student(client):
    created = client.post(
        "/students/",
        json=valid_student(),
    )

    assert created.status_code == 201
    student_id = created.json()["id"]

    response = client.delete(
        f"/students/{student_id}",
    )

    assert response.status_code == 204
    assert response.content == b""

    list_response = client.get("/students/")

    assert list_response.status_code == 200

    data = list_response.json()

    assert all(student["id"] != student_id for student in data["items"])
    assert data["total"] == 0


def test_delete_student_not_found(client):
    response = client.delete("/students/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found."


def test_list_students_search_by_name(client):
    student = valid_student()
    student["student_code"] = "STU-201"
    student["full_name"] = "Rahim Ahmed"
    student["email"] = "rahim201@example.com"

    created = client.post("/students/", json=student)
    assert created.status_code == 201

    response = client.get("/students/?search=Rahim")

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["full_name"] == "Rahim Ahmed"


def test_list_students_pagination(client):
    for index in range(3):
        student = valid_student()
        student["student_code"] = f"STU-PAGE-{index}"
        student["email"] = f"page{index}@example.com"

        response = client.post("/students/", json=student)
        assert response.status_code == 201

    response = client.get("/students/?skip=1&limit=1")

    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 3
    assert data["skip"] == 1
    assert data["limit"] == 1


def test_list_students_invalid_pagination(client):
    response = client.get("/students/?skip=-1")

    assert response.status_code == 422

    response = client.get("/students/?limit=101")

    assert response.status_code == 422


def test_list_students_search_no_match(client):
    student = valid_student()
    student["student_code"] = "STU-NOMATCH"
    student["email"] = "nomatch@example.com"

    created = client.post("/students/", json=student)
    assert created.status_code == 201

    response = client.get("/students/?search=NonexistentStudent")

    assert response.status_code == 200

    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
