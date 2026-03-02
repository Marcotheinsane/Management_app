from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.settings import settings

# Configurar contexto de hash de contraseñas - usar argon2 en lugar de bcrypt
# para evitar problemas de compatibilidad en Python 3.14
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Configuración JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando argon2
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña sin hashear coincide con la hasheada
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    
    # Usar una clave secreta - en producción debe estar en variables de entorno
    secret_key = getattr(settings, 'SECRET_KEY', 'change-me-in-production-12345')
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica un token JWT y retorna los datos si es válido
    """
    try:
        secret_key = getattr(settings, 'SECRET_KEY', 'change-me-in-production-12345')
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
