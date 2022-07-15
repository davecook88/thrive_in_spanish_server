from typing import Any, AsyncGenerator, Optional
from dotenv import load_dotenv
from fastapi import FastAPI
import pytest
import pytest_asyncio
from sqlalchemy.future.engine import Engine
from sqlmodel import SQLModel, Session, create_engine
from app.auth.get_current_user import get_current_user
from app.db.models.user.user import Teacher, User, UserFull
from app.main import app
from app.core.config import Settings
from fastapi.testclient import TestClient
from app.db.get_session import get_session
from app.organization.model import OrganizationModel


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    load_dotenv()


@pytest.fixture
def app_settings() -> Settings:
    from app.core.config import settings

    return settings


@pytest_asyncio.fixture
async def engine(app_settings: Settings) -> AsyncGenerator[Engine, Any]:
    engine = create_engine(app_settings.TEST_DATABASE_URL)
    yield engine


@pytest_asyncio.fixture
async def session(engine: Engine) -> AsyncGenerator[Session, Any]:
    meta = SQLModel.metadata
    meta.drop_all(engine)
    meta.create_all(engine)
    with Session(engine) as session:  # type: ignore
        session: Session = session
        yield session

    meta.drop_all(engine)


@pytest.fixture
def fast_api_app() -> FastAPI:
    return app


@pytest.fixture(scope="session")
def google_id() -> str:
    return "abc"


@pytest_asyncio.fixture
def organization(session: Session) -> OrganizationModel:
    return OrganizationModel.get_default_organization(session)


@pytest_asyncio.fixture
async def user(
    session: Session, google_id: str, organization: OrganizationModel
) -> User:
    if not organization.id:
        raise Exception()
    u = User.create_user(
        name="test user",
        email="email@domain.com",
        google_id=google_id,
        organization_id=organization.id,
    )
    await u.save(session)
    user: Optional[User] = session.get(User, u.id)
    if not user:
        raise Exception("User fixture didn't save correctly")
    return user


@pytest_asyncio.fixture
async def teacher(session: Session, user: UserFull):
    t = Teacher(user_id=user.id)
    session.add(t)
    session.commit()
    return t


@pytest.fixture
def client(
    fast_api_app: FastAPI, session: Session, user: UserFull
) -> TestClient:
    async def override_get_session() -> AsyncGenerator[TestClient, None]:
        yield session  # type: ignore
        return

    fast_api_app.dependency_overrides[get_session] = override_get_session
    fast_api_app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(fast_api_app)
