import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from unittest.mock import patch
import base64
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
            "email": "testvoice@gmail.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]


class TestVoiceTutor:

    @patch('app.services.voice_tutor_service.voice_tutor_service.ask_tutor')
    def test_ask_voice_tutor_success(self, mock_ask, client, auth_token):
        """Prueba hacer pregunta al tutor de voz"""
        fake_audio = base64.b64encode(b"fake_audio").decode()
        mock_ask.return_value = {
            "text_response": "Python es un lenguaje de programación muy popular.",
            "audio_response": f"data:audio/wav;base64,{fake_audio}",
            "follow_up_suggestions": [
                "¿Cuáles son las ventajas de Python?",
                "¿Qué puedo hacer con Python?",
                "¿Es Python difícil de aprender?"
            ]
        }

        response = client.post(
            "/api/v1/voice-tutor/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Python",
                "user_question": "¿Qué es Python?",
                "conversation_history": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "text_response" in data
        assert "audio_response" in data
        assert "follow_up_suggestions" in data
        assert len(data["follow_up_suggestions"]) == 3

    @patch('app.services.voice_tutor_service.voice_tutor_service.ask_tutor')
    def test_ask_voice_tutor_with_history(self, mock_ask, client, auth_token):
        """Prueba tutor con historial de conversación"""
        fake_audio = base64.b64encode(b"fake_audio").decode()
        mock_ask.return_value = {
            "text_response": "Las variables en Python son espacios de memoria.",
            "audio_response": f"data:audio/wav;base64,{fake_audio}",
            "follow_up_suggestions": ["¿Qué tipos de variables hay?"]
        }

        response = client.post(
            "/api/v1/voice-tutor/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Python",
                "user_question": "¿Qué son las variables?",
                "conversation_history": [
                    {"role": "user", "content": "¿Qué es Python?"},
                    {"role": "assistant", "content": "Python es un lenguaje de programación."}
                ]
            }
        )
        assert response.status_code == 200

    def test_create_voice_conversation(self, client, auth_token):
        """Prueba crear conversación de voz"""
        response = client.post(
            "/api/v1/voice-tutor/conversations",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Python Básico"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "Python Básico"
        assert "id" in data

    def test_add_message_to_conversation(self, client, auth_token):
        """Prueba añadir mensaje a conversación"""
        # Crear conversación
        conv_response = client.post(
            "/api/v1/voice-tutor/conversations",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Test"}
        )
        conversation_id = conv_response.json()["id"]

        # Añadir mensaje
        response = client.post(
            f"/api/v1/voice-tutor/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "conversation_id": conversation_id,
                "role": "user",
                "content": "¿Qué es Python?"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "¿Qué es Python?"

    def test_add_message_conversation_not_found(self, client, auth_token):
        """Prueba añadir mensaje a conversación inexistente"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/v1/voice-tutor/conversations/{fake_uuid}/messages",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "conversation_id": fake_uuid,
                "role": "user",
                "content": "Test"
            }
        )
        assert response.status_code == 404

    def test_get_user_conversations(self, client, auth_token):
        """Prueba obtener conversaciones del usuario"""
        # Crear algunas conversaciones
        for i in range(3):
            client.post(
                "/api/v1/voice-tutor/conversations",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"topic": f"Topic {i}"}
            )

        response = client.get(
            "/api/v1/voice-tutor/conversations",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_conversation_messages(self, client, auth_token):
        """Prueba obtener mensajes de conversación"""
        # Crear conversación
        conv_response = client.post(
            "/api/v1/voice-tutor/conversations",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "Test"}
        )
        conversation_id = conv_response.json()["id"]

        # Añadir mensajes
        for i in range(3):
            client.post(
                f"/api/v1/voice-tutor/conversations/{conversation_id}/messages",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "conversation_id": conversation_id,
                    "role": "user",
                    "content": f"Message {i}"
                }
            )

        # Obtener mensajes
        response = client.get(
            f"/api/v1/voice-tutor/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_messages_conversation_not_found(self, client, auth_token):
        """Prueba obtener mensajes de conversación inexistente"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/v1/voice-tutor/conversations/{fake_uuid}/messages",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404

    def test_voice_tutor_empty_question(self, client, auth_token):
        """Prueba tutor con pregunta vacía"""
        response = client.post(
            "/api/v1/voice-tutor/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Test",
                "user_question": "",
                "conversation_history": []
            }
        )
        assert response.status_code == 422

    def test_conversations_pagination(self, client, auth_token):
        """Prueba paginación de conversaciones"""
        # Crear 15 conversaciones
        for i in range(15):
            client.post(
                "/api/v1/voice-tutor/conversations",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"topic": f"Topic {i}"}
            )

        response = client.get(
            "/api/v1/voice-tutor/conversations?skip=0&limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_voice_tutor_no_auth(self, client, clean_db):
        """Prueba acceder a tutor sin autenticación"""
        response = client.post(
            "/api/v1/voice-tutor/ask",
            json={
                "topic": "Test",
                "user_question": "Test",
                "conversation_history": []
            }
        )
        assert response.status_code == 403