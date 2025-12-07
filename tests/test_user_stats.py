import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import os
from sqlalchemy import create_engine

# Usa una BD de prueba distinta a la de producción
SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgre@localhost:5432/studyblossom-test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def auth_token(client, clean_db):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teststats@gmail.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]


class TestUserStats:

    def test_get_user_stats_initial(self, client, auth_token):
        """Prueba obtener estadísticas iniciales"""
        response = client.get(
            "/api/v1/stats/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Puede retornar 404 si no existen stats o 200 con valores por defecto
        assert response.status_code in [200, 404]

    def test_get_dashboard_stats(self, client, auth_token):
        """Prueba obtener estadísticas del dashboard"""
        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_xp" in data
        assert "current_level" in data
        assert "current_streak" in data
        assert "total_sessions" in data

    def test_stats_after_study_session(self, client, auth_token):
        """Prueba estadísticas después de sesión de estudio"""
        # Crear sesión de estudio
        client.post(
            "/api/v1/study-sessions/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "goal_name": "Test Goal",
                "topic": "Test Topic",
                "mode": "text",
                "study_time": 30
            }
        )

        # Verificar stats actualizadas
        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] >= 1
        assert data["total_xp"] >= 5  # XP mínimo por sesión text

    def test_stats_xp_accumulation(self, client, auth_token):
        """Prueba acumulación de XP"""
        # Crear múltiples sesiones
        for mode in ["text", "visual", "audio"]:
            client.post(
                "/api/v1/study-sessions/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "goal_name": "Test",
                    "topic": "Test",
                    "mode": mode,
                    "study_time": 30
                }
            )

        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        # text=5, visual=10, audio=5 = 20 total
        assert data["total_xp"] >= 20

    def test_stats_level_progression(self, client, auth_token):
        """Prueba progresión de nivel"""
        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert data["current_level"] >= 1
        assert "level_name" in data
        assert "plant_stage" in data

    def test_stats_streak_tracking(self, client, auth_token):
        """Prueba seguimiento de racha"""
        # Crear sesión hoy
        client.post(
            "/api/v1/study-sessions/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "goal_name": "Streak Test",
                "topic": "Test",
                "mode": "text",
                "study_time": 15
            }
        )

        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert data["current_streak"] >= 1

    def test_stats_study_time_tracking(self, client, auth_token):
        """Prueba seguimiento de tiempo de estudio"""
        # Crear sesiones con diferentes tiempos
        client.post(
            "/api/v1/study-sessions/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "goal_name": "Time Test 1",
                "topic": "Test",
                "mode": "text",
                "study_time": 30
            }
        )
        client.post(
            "/api/v1/study-sessions/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "goal_name": "Time Test 2",
                "topic": "Test",
                "mode": "text",
                "study_time": 45
            }
        )

        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert data["total_study_time"] >= 75  # 30 + 45

    def test_stats_no_auth(self, client, clean_db):
        """Prueba acceder a estadísticas sin autenticación"""
        response = client.get("/api/v1/stats/")
        assert response.status_code == 403

    def test_stats_progress_percentage(self, client, auth_token):
        """Prueba porcentaje de progreso al siguiente nivel"""
        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "progress_percentage" in data
        assert 0 <= data["progress_percentage"] <= 100

    def test_stats_xp_for_next_level(self, client, auth_token):
        """Prueba XP necesario para siguiente nivel"""
        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "xp_for_next_level" in data
        assert data["xp_for_next_level"] >= 0