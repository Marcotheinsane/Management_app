from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event, String
import ssl
from app.settings import settings

# Procesar la URL de conexión para compatibilidad con asyncpg
# Neon proporciona URLs con sslmode=require que asyncpg no reconoce
database_url = settings.DATABASE_URL

# Convertir sslmode=require a ssl=true para asyncpg
if 'sslmode=require' in database_url:
    database_url = database_url.replace('sslmode=require', '')
# Remover sslmode=disable
if 'sslmode=disable' in database_url:
    database_url = database_url.replace('?sslmode=disable', '')

print(f"📊 Conectando a BD: {database_url.split('@')[1] if '@' in database_url else '***'}")

# Crear el engine asincrónico
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "ssl": False,  # Desactivar SSL para localhost
    }
)

# Crear sesión asincrónica
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
