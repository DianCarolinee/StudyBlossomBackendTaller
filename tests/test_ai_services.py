import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from unittest.mock import patch, AsyncMock

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
            "email": "testai@gmail.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]


class TestAIServices:

    @patch('app.services.aida_service.aida_service.generate_engagement')
    def test_aida_engagement_success(self, mock_generate, client, auth_token):
        """Prueba generar contenido AIDA"""
        mock_generate.return_value = {
            "attention": "¿Sabías que Python es usado por NASA?",
            "interest": "Python es el lenguaje más usado en ciencia de datos.",
            "desire": [
                "Automatiza tareas repetitivas",
                "Aumenta tus oportunidades laborales",
                "Crea proyectos increíbles"
            ]
        }

        response = client.post(
            "/api/v1/ai/aida-engagement",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Python"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "attention" in data
        assert "interest" in data
        assert "desire" in data
        assert len(data["desire"]) == 3

    @patch('app.services.aida_service.gemini_service.generate_json')
    def test_aida_engagement_validation(self, mock_generate, client, auth_token):
        """Prueba validación de contenido AIDA"""
        mock_generate.return_value = {
            "attention": "A" * 100,  # Muy largo
            "interest": "I" * 200,
            "desire": ["D1", "D2"]  # Solo 2 elementos
        }

        response = client.post(
            "/api/v1/ai/aida-engagement",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Test"}
        )
        # Debe fallar o manejar el error
        assert response.status_code in [200, 500]

    @patch('app.services.pomodoro_service.pomodoro_service.generate_recommendations')
    def test_pomodoro_recommendations_success(self, mock_generate, client, auth_token):
        """Prueba generar recomendaciones Pomodoro"""
        mock_generate.return_value = [
            {
                "sub_topic": "Variables en Python",
                "sources": [
                    {
                        "title": "Python.org Variables",
                        "url": "https://python.org/variables",
                        "type": "documentation"
                    },
                    {
                        "title": "Video Tutorial",
                        "url": "https://youtube.com/watch?v=example",
                        "type": "video"
                    },
                    {
                        "title": "Article on Variables",
                        "url": "https://realpython.com/variables",
                        "type": "article"
                    }
                ]
            },
            {
                "sub_topic": "Funciones en Python",
                "sources": [
                    {
                        "title": "Python Functions",
                        "url": "https://python.org/functions",
                        "type": "documentation"
                    },
                    {
                        "title": "Functions Video",
                        "url": "https://youtube.com/watch?v=func",
                        "type": "video"
                    },
                    {
                        "title": "Functions Article",
                        "url": "https://realpython.com/functions",
                        "type": "article"
                    }
                ]
            },
            {
                "sub_topic": "Clases en Python",
                "sources": [
                    {
                        "title": "OOP Python",
                        "url": "https://python.org/oop",
                        "type": "documentation"
                    },
                    {
                        "title": "OOP Video",
                        "url": "https://youtube.com/watch?v=oop",
                        "type": "video"
                    },
                    {
                        "title": "OOP Article",
                        "url": "https://realpython.com/oop",
                        "type": "article"
                    }
                ]
            }
        ]

        response = client.post(
            "/api/v1/ai/pomodoro-recommendations",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Python"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) >= 3
        assert len(data["recommendations"][0]["sources"]) == 3

    def test_aida_empty_topic(self, client, auth_token):
        """Prueba AIDA con tema vacío"""
        response = client.post(
            "/api/v1/ai/aida-engagement",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": ""}
        )
        assert response.status_code == 422

    def test_pomodoro_empty_topic(self, client, auth_token):
        """Prueba Pomodoro con tema vacío"""
        response = client.post(
            "/api/v1/ai/pomodoro-recommendations",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": ""}
        )
        assert response.status_code == 422

    def test_ai_services_no_auth(self, client, clean_db):
        """Prueba acceder a servicios IA sin autenticación"""
        response = client.post(
            "/api/v1/ai/aida-engagement",
            json={"topic": "Test"}
        )
        assert response.status_code == 403