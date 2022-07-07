from datetime import datetime
import json
from typing import List

from uuid import uuid4
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session
from app.bookings.types import (
    PostAvailabilityPayload,
    PostAvailabilityPayloadEvent,
    PostAvailabilityPayloadTimeframe,
)
from app.auth.get_current_user import get_current_user
from app.db.models.user.user import User, Teacher, TeacherAvailability


@pytest.fixture
def app_user_override(fast_api_app: FastAPI, user: User):
    """
    Makes sure that the user fixture is returned from the
    get_current_user method
    """
    overrides = fast_api_app.dependency_overrides
    fast_api_app.dependency_overrides[get_current_user] = lambda: user
    yield fast_api_app
    fast_api_app.dependency_overrides = overrides


class TestAvailabilitiesRouter:
    def test_can_access_teacher_from_availability(
        self, schedule: List[TeacherAvailability]
    ):
        assert schedule[0].teacher_id
        assert schedule[0].teacher

    def test_get_availabilities_endpoint(
        self,
        app_user_override: FastAPI,
        session: Session,
        client: TestClient,
        user: User,
        teacher: Teacher,
        schedule: List[TeacherAvailability],
    ):
        """
        GIVEN: A call to GET availability
        THEN: Returns a list of relevant availabilities
        """
        response = client.get(
            "/bookings/teacher-availability",
            params={
                "limit": 100,
                "from_date": datetime(2022, 6, 20).isoformat(),
                "until_date": datetime(2022, 7, 20).isoformat(),
            },
            headers={"authorization": ""},
        )

        assert response.status_code == 200
        availabilities = response.json()
        assert isinstance(availabilities, list)
        assert len(availabilities) == 3

    def test_get_availabilities_endpoint_2(
        self,
        app_user_override: FastAPI,
        session: Session,
        client: TestClient,
        user: User,
        teacher: Teacher,
        schedule: List[TeacherAvailability],
    ):
        """
        GIVEN: A call to GET availability
        THEN: Returns a list of relevant availabilities
        """
        response = client.get(
            "/bookings/teacher-availability",
            params={
                "limit": 100,
                "from_date": datetime(2022, 6, 23).isoformat(),
                "until_date": datetime(2022, 6, 24).isoformat(),
            },
            headers={"authorization": ""},
        )

        assert response.status_code == 200
        availabilities = response.json()
        assert isinstance(availabilities, list)
        assert len(availabilities) == 3

    def test_create_availabilities(
        self,
        app_user_override: FastAPI,
        session: Session,
        client: TestClient,
        user: User,
        teacher: Teacher,
        schedule: List[TeacherAvailability],
    ):
        """
        GIVEN: A call to the POST availability endpoint
        THEN: Existing availability records for the given time
            frame are deleted
        AND: The new events are created
        """
        payload = PostAvailabilityPayload(
            events=[
                PostAvailabilityPayloadEvent(
                    id=uuid4(),
                    start=datetime(2022, 6, 23, 14),
                    end=datetime(2022, 6, 23, 15),
                )
            ],
            timeframe=PostAvailabilityPayloadTimeframe(
                start=datetime(2022, 6, 23, 0), end=datetime(2022, 6, 24, 0)
            ),
        )

        response = client.post(
            "/bookings/teacher-availability",
            data=json.dumps(payload.dict(), default=str),
        )
        assert response.status_code == 200

        all_availability = session.query(TeacherAvailability).all()
        assert len(all_availability) == 2

    def test_delete_availability(
        self,
        app_user_override: FastAPI,
        session: Session,
        client: TestClient,
        user: User,
        teacher: Teacher,
        schedule: List[TeacherAvailability],
    ):
        availability_id = schedule[0].id
        model_in_db = session.get(TeacherAvailability, availability_id)
        assert model_in_db
        if not availability_id:
            raise Exception()
        response = client.delete(
            f"/bookings/teacher-availability/{availability_id}"
        )
        assert response.status_code == 202
        model_in_db = session.get(TeacherAvailability, availability_id)
        assert not model_in_db

    def test_update_availability(
        self,
        app_user_override: FastAPI,
        session: Session,
        client: TestClient,
        user: User,
        teacher: Teacher,
        schedule: List[TeacherAvailability],
    ):
        availability_id = schedule[0].id
        if not availability_id:
            raise Exception()
        new_start = datetime(2022, 8, 1, 9)
        new_end = datetime(2022, 8, 1, 19)
        update = PostAvailabilityPayloadEvent(
            id=availability_id, start=new_start, end=new_end
        )

        response = client.put(
            f"/bookings/teacher-availability/{availability_id}",
            data=json.dumps(update.dict(), default=str),
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["end"] == new_end.isoformat()
        assert response_json["start"] == new_start.isoformat()
