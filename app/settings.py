from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str
    
    # Configuración de FastAPI
    APP_NAME: str = "FastAPI CRUD"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    FRONTEND_URL: str
    
    # Configuración de autenticación
    SECRET_KEY: str = "change-me-in-production-12345"  # Cambiar en .env
    
    class Config:
        env_file = ".env"

settings = Settings()
