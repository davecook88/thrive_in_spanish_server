from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db.models.course.course import Course


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
