import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from unittest.mock import patch, AsyncMock
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
            "email": "testaudio@gmail.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    return response.json()["access_token"]


class TestAudio:

    @patch('app.services.audio_service.audio_service.generate_audio')
    def test_generate_audio_success(self, mock_generate, client, auth_token):
        """Prueba generar audio desde texto"""
        # Mock audio data URI
        fake_audio = base64.b64encode(b"fake_audio_data").decode()
        mock_generate.return_value = f"data:audio/wav;base64,{fake_audio}"

        response = client.post(
            "/api/v1/audio/generate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"text": "Hola, este es un texto de prueba"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "media" in data
        assert data["media"].startswith("data:audio/wav;base64,")

    def test_generate_audio_empty_text(self, client, auth_token):
        """Prueba generar audio con texto vacío"""
        response = client.post(
            "/api/v1/audio/generate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"text": ""}
        )
        assert response.status_code == 422

    def test_save_audio_generation(self, client, auth_token):
        """Prueba guardar generación de audio"""
        response = client.post(
            "/api/v1/audio/save",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "text_content": "Texto de prueba",
                "audio_data": "base64_encoded_data",
                "duration_seconds": 10
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["text_content"] == "Texto de prueba"

    def test_get_audio_history(self, client, auth_token):
        """Prueba obtener historial de audio"""
        # Crear algunas generaciones
        for i in range(3):
            client.post(
                "/api/v1/audio/save",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "text_content": f"Text {i}",
                    "audio_data": f"data{i}",
                    "duration_seconds": 10
                }
            )

        response = client.get(
            "/api/v1/audio/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_audio_no_auth(self, client, clean_db):
        """Prueba acceder a audio sin autenticación"""
        response = client.post(
            "/api/v1/audio/generate",
            json={"text": "Test"}
        )
        assert response.status_code == 403


class TestVideo:

    @patch('app.services.video_service.video_service.generate_educational_video')
    def test_generate_video_success(self, mock_generate, client, auth_token):
        """Prueba generar video educativo"""
        mock_generate.return_value = {
            "video_url": "https://example.com/video.mp4",
            "video_id": "video123",
            "script": "Script del video",
            "title": "Título del Video",
            "key_points": ["Punto 1", "Punto 2", "Punto 3"],
            "estimated_duration": "3-5 minutos",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "status": "done"
        }

        response = client.post(
            "/api/v1/video/generate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Python para principiantes",
                "duration": "medium"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "video_url" in data
        assert "script" in data
        assert data["status"] == "done"

    def test_generate_video_invalid_duration(self, client, auth_token):
        """Prueba generar video con duración inválida"""
        response = client.post(
            "/api/v1/video/generate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Test",
                "duration": "invalid"
            }
        )
        assert response.status_code == 422

    def test_save_video(self, client, auth_token):
        """Prueba guardar video"""
        response = client.post(
            "/api/v1/video/save",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Test Topic",
                "duration": "short",
                "script": "Video script",
                "title": "Video Title",
                "key_points": ["Point 1", "Point 2"],
                "video_url": "https://example.com/video.mp4",
                "video_id": "video123",
                "estimated_duration": "1-2 minutos",
                "status": "done"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "Test Topic"

    def test_get_user_videos(self, client, auth_token):
        """Prueba obtener videos del usuario"""
        # Crear algunos videos
        for i in range(3):
            client.post(
                "/api/v1/video/save",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "topic": f"Topic {i}",
                    "duration": "short",
                    "script": f"Script {i}",
                    "title": f"Title {i}",
                    "key_points": ["Point 1"],
                    "video_url": f"https://example.com/video{i}.mp4",
                    "video_id": f"video{i}",
                    "estimated_duration": "1-2 minutos",
                    "status": "done"
                }
            )

        response = client.get(
            "/api/v1/video/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_video_by_id(self, client, auth_token):
        """Prueba obtener video por ID"""
        # Crear video
        create_response = client.post(
            "/api/v1/video/save",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "topic": "Specific Video",
                "duration": "medium",
                "script": "Script",
                "title": "Title",
                "key_points": ["Point 1"],
                "video_url": "https://example.com/video.mp4",
                "video_id": "video123",
                "estimated_duration": "3-5 minutos",
                "status": "done"
            }
        )
        video_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(
            f"/api/v1/video/{video_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["topic"] == "Specific Video"

    def test_get_video_not_found(self, client, auth_token):
        """Prueba obtener video inexistente"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/v1/video/{fake_uuid}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404

    @patch('app.services.video_service.video_service.test_connection')
    def test_did_connection(self, mock_test, client, auth_token):
        """Prueba conexión con D-ID"""
        mock_test.return_value = {
            "success": True,
            "message": "Conexión exitosa",
            "credits": 100
        }

        response = client.get(
            "/api/v1/video/test-connection",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_video_pagination(self, client, auth_token):
        """Prueba paginación de videos"""
        # Crear 15 videos
        for i in range(15):
            client.post(
                "/api/v1/video/save",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "topic": f"Topic {i}",
                    "duration": "short",
                    "script": f"Script {i}",
                    "title": f"Title {i}",
                    "key_points": ["Point"],
                    "video_url": f"https://example.com/video{i}.mp4",
                    "video_id": f"video{i}",
                    "estimated_duration": "1-2 minutos",
                    "status": "done"
                }
            )

        response = client.get(
            "/api/v1/video/?skip=0&limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_video_no_auth(self, client, clean_db):
        """Prueba acceder a videos sin autenticación"""
        response = client.get("/api/v1/video/")
        assert response.status_code == 403