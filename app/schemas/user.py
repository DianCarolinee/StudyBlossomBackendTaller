from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import uuid
import re


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=15)
    full_name: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        # Validar formato del email
        local_part = v.split('@')[0]
        domain = v.split('@')[1].lower()

        # Mínimo 5 caracteres antes del @
        if len(local_part) < 5:
            raise ValueError('El email debe tener al menos 5 caracteres antes del @')

        # Debe contener al menos una letra
        if not re.search(r'[a-zA-Z]', local_part):
            raise ValueError('El email debe contener al menos una letra')

        # No puede ser solo números
        if re.match(r'^\d+$', local_part):
            raise ValueError('El email no puede ser solo números')

        # Validar caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9._-]+$', local_part):
            raise ValueError('El email contiene caracteres no válidos')

        # Dominios válidos
        valid_domains = [
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'icloud.com', 'live.com', 'msn.com', 'aol.com',
            'protonmail.com', 'zoho.com'
        ]

        # Permitir dominios educativos
        is_educational = re.search(r'\.edu(\.[a-z]{2})?$', domain, re.IGNORECASE)

        if domain not in valid_domains and not is_educational:
            raise ValueError('Por favor, usa un email de un proveedor reconocido o una cuenta educativa (.edu)')

        return v

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: uuid.UUID
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None