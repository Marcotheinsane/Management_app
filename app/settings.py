from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración de la base de datos antes harcodeada
    #DATABASE_URL: str = "postgresql+asyncpg://postgres:2077@localhost:5433/bd_muni"
    # Configuración de FastAPI
    #APP_NAME: str = "FastAPI CRUD"
    #APP_VERSION: str = "1.0.0"
    #DEBUG: bool = True
    #now this a correct way to set a variable
    DATABASE_URL: str
    APP_NAME: str = "FastAPI CRUD"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    FRONTEND_URL: str 
    
    class Config:
        env_file = ".env"

settings = Settings()
