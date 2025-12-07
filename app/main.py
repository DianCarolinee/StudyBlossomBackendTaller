from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import get_settings
from app.database import engine, Base
from app.routes import api_router
import time

settings = get_settings()

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    description="API para StudyBlossom - Plataforma de aprendizaje con IA"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Error de validación",
            "details": errors,
            "status_code": 422
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "details": str(exc) if settings.DEBUG else None,
            "status_code": 500
        }
    )


# Health check
@app.get("/health")
async def health_check():
    """
    Endpoint de salud de la API
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Endpoint raíz
    """
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Incluir routers
app.include_router(api_router, prefix="/api/v1")


# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Ejecuta al iniciar la aplicación
    """
    print(f"🚀 {settings.APP_NAME} v{settings.VERSION} iniciado")
    print(f"📚 Documentación disponible en: http://{settings.HOST}:{settings.PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Ejecuta al cerrar la aplicación
    """
    print(f"👋 {settings.APP_NAME} detenido")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )