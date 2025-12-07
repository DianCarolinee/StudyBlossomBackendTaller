# StudyBlossom API

API Backend para StudyBlossom - Plataforma de aprendizaje con IA

## 🚀 Características

- ✅ Autenticación con JWT
- ✅ Gestión de metas y sesiones de estudio
- ✅ Generación de flashcards con IA (Gemini)
- ✅ Mapas conceptuales (Mermaid)
- ✅ Técnica Feynman
- ✅ Generación de quizzes
- ✅ Text-to-Speech (TTS)
- ✅ Tutor de voz conversacional
- ✅ Generación de videos educativos (D-ID)
- ✅ Contenido motivacional AIDA
- ✅ Recomendaciones Pomodoro
- ✅ Sistema de XP y niveles
- ✅ Estadísticas y dashboard

## 📋 Requisitos

- Python 3.10+
- PostgreSQL 14+
- API Keys:
  - Google Gemini API
  - D-ID API

## 🛠️ Instalación

1. Clonar el repositorio:
```bash
git clone <repo-url>
cd backend
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. Crear base de datos:
```bash
createdb studyblossom
```

6. Ejecutar el script SQL:
```bash
psql -d studyblossom -f database_schema.sql
```

7. Ejecutar migraciones (opcional si usas Alembic):
```bash
alembic upgrade head
```

## 🏃 Ejecución

### Desarrollo
```bash
python run.py
```

### Producción
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Documentación

La documentación interactiva estará disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing
### Pruebas específicas
```bash
# Un archivo específico
pytest tests/test_auth.py -v

# Una clase específica
pytest tests/test_auth.py::TestAuth -v

# Un test específico
pytest tests/test_auth.py::TestAuth::test_register_success -v
```

### Con cobertura
```bash
pytest tests/ --cov=app --cov-report=html
```

El reporte HTML se genera en `htmlcov/index.html`

## 📊 Cobertura Esperada

Las pruebas cubren:

- ✅ **Autenticación (test_auth.py)**
  - Registro de usuarios
  - Login y validación de tokens
  - Verificación de permisos

- ✅ **Metas de Estudio (test_study_goals.py)**
  - CRUD completo
  - Validación de campos
  - Filtros y paginación

- ✅ **Flashcards (test_flashcards.py)**
  - Generación con IA
  - Creación manual
  - Sistema de revisión
  - Filtrado por tema

- ✅ **Quizzes (test_quiz.py)**
  - Generación desde flashcards
  - Sesiones de quiz
  - Sistema de respuestas
  - Cálculo de puntajes

- ✅ **Estadísticas (test_user_stats.py)**
  - Seguimiento de XP
  - Sistema de niveles
  - Rachas de estudio
  - Tiempo de estudio

- ✅ **Servicios IA (test_ai_services.py)**
  - Contenido AIDA
  - Recomendaciones Pomodoro

- ✅ **Mapas Conceptuales (test_concept_map.py)**
  - Generación con Mermaid
  - Sanitización de caracteres
  - Almacenamiento

- ✅ **Técnica Feynman (test_feynman.py)**
  - Explicaciones simples
  - Análisis de comprensión
  - Feedback personalizado

- ✅ **Audio/Video (test_audio_video.py)**
  - Generación de audio TTS
  - Videos educativos con D-ID
  - Almacenamiento y recuperación

- ✅ **Tutor de Voz (test_voice_tutor.py)**
  - Conversaciones interactivas
  - Historial de mensajes
  - Sugerencias de seguimiento
```
```
## 📁 Estructura del Proyecto
```
backend/
├── app/
│   ├── models/          # Modelos de base de datos
│   ├── schemas/         # Esquemas Pydantic
│   ├── controllers/     # Lógica de negocio
│   ├── services/        # Servicios de IA
│   ├── routes/          # Endpoints API
│   ├── utils/           # Utilidades
│   ├── config.py        # Configuración
│   ├── database.py      # Configuración DB
│   └── main.py          # Aplicación principal
├── alembic/             # Migraciones
├── tests/               # Tests
├── .env                 # Variables de entorno
├── requirements.txt     # Dependencias
└── run.py              # Script de inicio
```

## 🔐 Autenticación

La API utiliza JWT para autenticación. Incluir el token en el header:
```
Authorization: Bearer <token>
```

## 📊 Endpoints Principales

### Autenticación
- `POST /api/v1/auth/register` - Registro
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Usuario actual

### Metas de Estudio
- `POST /api/v1/study-goals/` - Crear meta
- `GET /api/v1/study-goals/` - Listar metas
- `GET /api/v1/study-goals/{id}` - Obtener meta
- `PUT /api/v1/study-goals/{id}` - Actualizar meta
- `DELETE /api/v1/study-goals/{id}` - Eliminar meta

### IA Services
- `POST /api/v1/flashcards/generate` - Generar flashcards
- `POST /api/v1/quiz/generate` - Generar quiz
- `POST /api/v1/concept-map/generate` - Generar mapa
- `POST /api/v1/feynman/explanation` - Explicación Feynman
- `POST /api/v1/audio/generate` - Generar audio
- `POST /api/v1/voice-tutor/ask` - Preguntar al tutor
- `POST /api/v1/video/generate` - Generar video
- `POST /api/v1/ai/aida-engagement` - Contenido AIDA
- `POST /api/v1/ai/pomodoro-recommendations` - Recomendaciones

### Estadísticas
- `GET /api/v1/stats/` - Estadísticas del usuario
- `GET /api/v1/stats/dashboard` - Dashboard completo

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Autores

- DIANA CHANTA

## 🙏 Agradecimientos

- Google Gemini AI
- D-ID
- FastAPI
- PostgreSQL