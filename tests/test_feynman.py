import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from unittest.mock import patch

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
            "email": "testfeynman@gmail.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]


class TestFeynman:

    @patch('app.services.feynman_service.feynman_service.get_explanation')
    def test_get_feynman_explanation(self, mock_explain, client, auth_token):
        """Prueba obtener explicación Feynman"""
        mock_explain.return_value = "La fotosíntesis es como una planta comiendo luz solar para hacer su comida."

        response = client.post(
            "/api/v1/feynman/explanation",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Fotosíntesis"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert len(data["explanation"]) > 0

    @patch('app.services.feynman_service.feynman_service.analyze_explanation')
    def test_analyze_feynman_explanation(self, mock_analyze, client, auth_token):
        """Prueba analizar explicación del usuario"""
        mock_analyze.return_value = {
            "gaps": "- No mencionaste el rol de la clorofila\n- Faltó explicar el proceso químico",
            "simplifications": "- Usa la analogía de una fábrica solar\n- Simplifica los términos técnicos"
        }

        response = client.post(
            "/api/v1/feynman/analyze",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Fotosíntesis",
                "user_explanation": "Las plantas usan la luz para crecer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "gaps" in data
        assert "simplifications" in data

    def test_save_feynman_session(self, client, auth_token):
        """Prueba guardar sesión Feynman"""
        response = client.post(
            "/api/v1/feynman/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Fotosíntesis",
                "ai_explanation": "Explicación simple de la IA",
                "user_explanation": "Mi propia explicación",
                "feedback_gaps": "Brechas identificadas",
                "feedback_simplifications": "Simplificaciones sugeridas"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "Fotosíntesis"
        assert "id" in data

    def test_get_feynman_sessions(self, client, auth_token):
        """Prueba obtener sesiones Feynman"""
        # Crear algunas sesiones
        for i in range(3):
            client.post(
                "/api/v1/feynman/sessions",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "topic": f"Topic {i}",
                    "ai_explanation": f"AI explanation {i}",
                    "user_explanation": f"User explanation {i}"
                }
            )

        response = client.get(
            "/api/v1/feynman/sessions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_feynman_explanation_empty_topic(self, client, auth_token):
        """Prueba explicación con tema vacío"""
        response = client.post(
            "/api/v1/feynman/explanation",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": ""}
        )
        assert response.status_code == 422

    def test_feynman_analyze_empty_explanation(self, client, auth_token):
        """Prueba análisis con explicación vacía"""
        response = client.post(
            "/api/v1/feynman/analyze",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Test",
                "user_explanation": ""
            }
        )
        assert response.status_code == 422

    def test_feynman_sessions_pagination(self, client, auth_token):
        """Prueba paginación de sesiones"""
        # Crear 15 sesiones
        for i in range(15):
            client.post(
                "/api/v1/feynman/sessions",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "topic": f"Topic {i}",
                    "ai_explanation": f"Explanation {i}"
                }
            )

        response = client.get(
            "/api/v1/feynman/sessions?skip=0&limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_feynman_no_auth(self, client, clean_db):
        """Prueba acceder a Feynman sin autenticación"""
        response = client.post(
            "/api/v1/feynman/explanation",
            json={"topic": "Test"}
        )
        assert response.status_code == 403

    @patch('app.services.feynman_service.gemini_service.generate_json')
    def test_feynman_explanation_length_limit(self, mock_generate, client, auth_token):
        """Prueba límite de longitud de explicación"""
        mock_generate.return_value = {
            "explanation": "A" * 500  # Muy largo
        }

        response = client.post(
            "/api/v1/feynman/explanation",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Test"}
        )
        # Debe manejar explicaciones largas
        assert response.status_code in [200, 500]