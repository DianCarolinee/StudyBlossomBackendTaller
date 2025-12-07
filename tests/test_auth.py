import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.security import get_password_hash
import uuid
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


class TestAuth:

    def test_register_success(self, client, clean_db):
        """Prueba registro exitoso de usuario"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@gmail.com",
                "password": "Test123!@#",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@gmail.com"

    def test_register_duplicate_email(self, client, clean_db):
        """Prueba registro con email duplicado"""
        # Primer registro
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@gmail.com",
                "password": "Test123!@#",
                "full_name": "Test User"
            }
        )

        # Segundo registro con mismo email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@gmail.com",
                "password": "Test123!@#",
                "full_name": "Test User 2"
            }
        )
        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"]

    def test_register_invalid_email(self, client, clean_db):
        """Prueba registro con email inválido"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@invalid.com",
                "password": "Test123!@#",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422

    def test_register_weak_password(self, client, clean_db):
        """Prueba registro con contraseña débil"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@gmail.com",
                "password": "weak",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422

    def test_login_success(self, client, clean_db):
        """Prueba login exitoso"""
        # Registrar usuario
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@gmail.com",
                "password": "Test123!@#",
                "full_name": "Test User"
            }
        )

        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@gmail.com",
                "password": "Test123!@#"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "login@gmail.com"

    def test_login_wrong_password(self, client, clean_db):
        """Prueba login con contraseña incorrecta"""
        # Registrar usuario
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@gmail.com",
                "password": "Test123!@#",
                "full_name": "Test User"
            }
        )

        # Login con contraseña incorrecta
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@gmail.com",
                "password": "WrongPassword123!@#"
            }
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, clean_db):
        """Prueba login con usuario inexistente"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@gmail.com",
                "password": "Test123!@#"
            }
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, clean_db):
        """Prueba obtener usuario actual"""
        # Registrar y obtener token
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "current@gmail.com",
                "password": "Test123!@#",
                "full_name": "Current User"
            }
        )
        token = register_response.json()["access_token"]

        # Obtener usuario actual
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "current@gmail.com"

    def test_get_current_user_no_token(self, client, clean_db):
        """Prueba obtener usuario sin token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client, clean_db):
        """Prueba obtener usuario con token inválido"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_verify_token_valid(self, client, clean_db):
        """Prueba verificar token válido"""
        # Registrar y obtener token
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "verify@gmail.com",
                "password": "Test123!@#",
                "full_name": "Verify User"
            }
        )
        token = register_response.json()["access_token"]

        # Verificar token
        response = client.get(
            "/api/v1/auth/verify-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["valid"] == True

    def test_verify_token_invalid(self, client, clean_db):
        """Prueba verificar token inválido"""
        response = client.get(
            "/api/v1/auth/verify-token",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401