from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.controllers.auth_controller import AuthController
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario
    """
    return AuthController.register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Inicia sesión y obtiene token de acceso
    """
    return AuthController.login_user(db, credentials)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la información del usuario actual
    """
    return UserResponse.model_validate(current_user)


@router.get("/verify-token", response_model=dict)
def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verifica si el token es válido
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email
    }