from fastapi.testclient import TestClient
from sqlmodel import Session
from app.course.types import CourseBase

from app.db.models.course.course import Course
from app.db.models.user.user import Teacher


class TestCourseRoutes:
    def test_list_courses(self, client: TestClient, course: Course):
        response = client.get("/course")
        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        course_response = response_json[0]
        assert course.name == course_response["name"]

    def test_get_course_by_id(self, client: TestClient, course: Course):
        response = client.get(f"/course/{course.id}")
        assert response.status_code == 200
        course_response = response.json()
        assert course.name == course_response["name"]

    def test_delete_course(
        self, session: Session, client: TestClient, course: Course
    ):
        response = client.delete(f"/course/{course.id}")
        assert response.status_code == 200
        course_in_db = session.get(Course, course.id)
        assert not course_in_db

    def test_update_course(
        self, session: Session, client: TestClient, course: Course
    ):
        # first get the course
        response = client.get(f"/course/{course.id}")
        assert response.status_code == 200
        course_response = response.json()
        new_name = "new_name"
        new_description = "new_description"
        new_price = 999
        new_teacher_id = 1
        course_response["name"] = new_name
        course_response["description"] = new_description
        course_response["price"] = new_price
        course_response["teacher_ids"] = [new_teacher_id]
        res = client.put(f"/course/{course.id}", json=course_response)
        assert res.status_code == 200
        course_in_db = session.get(Course, course.id)
        assert course_in_db
        assert course_in_db.name == new_name
        assert course_in_db.price == new_price
        assert course_in_db.description == new_description
        assert course_in_db.course_teachers[0].id == 1

    def test_create_course(
        self, session: Session, client: TestClient, teacher: Teacher
    ):
        course_payload = CourseBase(
            name="name",
            description="description",
            difficulty=1,
            max_students=3,
            price=100,
            teacher_ids=[teacher.id or 1],
        )
        res = client.post("/course", json=course_payload.__dict__)
        assert res.status_code == 200
        course_response = res.json()
        assert course_response.get("id")
        course_in_db = session.get(Course, course_response.get("id"))
        assert course_in_db
        assert course_in_db.name == course_payload.name
        assert course_in_db.price == course_payload.price
        assert course_in_db.description == course_payload.description
        assert len(course_in_db.course_teachers) == len(
            course_payload.teacher_ids
        )
        for course_teacher in course_in_db.course_teachers:
            assert course_teacher.id == teacher.id
