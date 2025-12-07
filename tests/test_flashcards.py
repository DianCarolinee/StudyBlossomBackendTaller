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
            "email": "testflash@gmail.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]


class TestFlashcards:

    @patch('app.services.flashcard_service.flashcard_service.generate_flashcards')
    def test_generate_flashcards_success(self, mock_generate, client, auth_token):
        """Prueba generar flashcards con IA"""
        mock_generate.return_value = [
            {"question": "¿Qué es Python?", "answer": "Un lenguaje de programación"},
            {"question": "¿Qué es una variable?", "answer": "Un espacio en memoria"},
            {"question": "¿Qué es una función?", "answer": "Un bloque de código reutilizable"},
            {"question": "¿Qué es un bucle?", "answer": "Una estructura de control"},
            {"question": "¿Qué es una lista?", "answer": "Una colección ordenada"}
        ]

        response = client.post(
            "/api/v1/flashcards/generate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Python básico"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["flashcards"]) == 5
        assert "question" in data["flashcards"][0]
        assert "answer" in data["flashcards"][0]

    def test_create_flashcard_manual(self, client, auth_token):
        """Prueba crear flashcard manualmente"""
        response = client.post(
            "/api/v1/flashcards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "question": "¿Qué es FastAPI?",
                "answer": "Un framework web moderno para Python",
                "topic": "FastAPI"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["question"] == "¿Qué es FastAPI?"
        assert data["times_reviewed"] == 0

    def test_get_user_flashcards(self, client, auth_token):
        """Prueba obtener flashcards del usuario"""
        # Crear algunas flashcards
        for i in range(3):
            client.post(
                "/api/v1/flashcards/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "question": f"Pregunta {i}",
                    "answer": f"Respuesta {i}",
                    "topic": "Test"
                }
            )

        response = client.get(
            "/api/v1/flashcards/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_flashcards_by_topic(self, client, auth_token):
        """Prueba filtrar flashcards por tema"""
        # Crear flashcards de diferentes temas
        client.post(
            "/api/v1/flashcards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "question": "Python question",
                "answer": "Python answer",
                "topic": "Python"
            }
        )
        client.post(
            "/api/v1/flashcards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "question": "JavaScript question",
                "answer": "JavaScript answer",
                "topic": "JavaScript"
            }
        )

        response = client.get(
            "/api/v1/flashcards/?topic=Python",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Python" in data[0]["topic"]

    def test_review_flashcard(self, client, auth_token):
        """Prueba revisar una flashcard"""
        # Crear flashcard
        create_response = client.post(
            "/api/v1/flashcards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "question": "Test question",
                "answer": "Test answer",
                "topic": "Test"
            }
        )
        flashcard_id = create_response.json()["id"]

        # Revisar flashcard
        response = client.post(
            "/api/v1/flashcards/review",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "flashcard_id": flashcard_id,
                "learned": True
            }
        )
        assert response.status_code == 200

    def test_review_flashcard_not_found(self, client, auth_token):
        """Prueba revisar flashcard inexistente"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            "/api/v1/flashcards/review",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "flashcard_id": fake_uuid,
                "learned": True
            }
        )
        assert response.status_code == 404

    def test_delete_flashcard(self, client, auth_token):
        """Prueba eliminar flashcard"""
        # Crear flashcard
        create_response = client.post(
            "/api/v1/flashcards/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "question": "To delete",
                "answer": "Delete this",
                "topic": "Test"
            }
        )
        flashcard_id = create_response.json()["id"]

        # Eliminar flashcard
        response = client.delete(
            f"/api/v1/flashcards/{flashcard_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

    def test_delete_flashcard_not_found(self, client, auth_token):
        """Prueba eliminar flashcard inexistente"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/api/v1/flashcards/{fake_uuid}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404

    def test_flashcards_pagination(self, client, auth_token):
        """Prueba paginación de flashcards"""
        # Crear 15 flashcards
        for i in range(15):
            client.post(
                "/api/v1/flashcards/",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "question": f"Q{i}",
                    "answer": f"A{i}",
                    "topic": "Test"
                }
            )

        # Primera página
        response = client.get(
            "/api/v1/flashcards/?skip=0&limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 10

        # Segunda página
        response = client.get(
            "/api/v1/flashcards/?skip=10&limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_flashcards_no_auth(self, client, clean_db):
        """Prueba acceder a flashcards sin autenticación"""
        response = client.get("/api/v1/flashcards/")
        assert response.status_code == 403