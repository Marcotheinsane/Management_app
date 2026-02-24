import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models import Persona, Asunto, AsuntoInstancia, Asistencia, Base
from app.schemas import (
    PersonaCreate, PersonaUpdate, PersonaResponse,
    AsuntoCreate, AsuntoUpdate, AsuntoResponse, AsuntoDetailResponse,
    AsuntoInstanciaCreate, AsuntoInstanciaUpdate, AsuntoInstanciaResponse, AsuntoInstanciaDetailResponse,
    AsistenciaCreate, AsistenciaUpdate, AsistenciaResponse, AsistenciaDetailResponse
)
from app.database import get_db, engine
from app.settings import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Evento de startup para crear las tablas
@app.on_event("startup")
async def startup_event():
    """Crea las tablas en la base de datos al iniciar"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tablas de base de datos creadas/verificadas")
        print(f"✓ CORS permitido para: {settings.FRONTEND_URL}")
        logger.info("✓ Startup completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error durante startup: {type(e).__name__}: {str(e)}", exc_info=True)
        print(f"❌ Error durante startup: {type(e).__name__}: {str(e)}")
        # No lanzar la excepción para permitir que la app inicie ugualmente y ver los logs
        import traceback
        print(traceback.format_exc())

# Parsear FRONTEND_URL (puede ser una o múltiples separadas por coma)
allowed_origins = [url.strip() for url in settings.FRONTEND_URL.split(",")]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Endpoints cru

# GET: Obtener todas las personas
@app.get("/personas/", response_model=list[PersonaResponse])
async def get_personas(db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todas las personas"""
    try:
        result = await db.execute(select(Persona))
        personas = result.scalars().all()
        print(f"✓ Personas obtenidas: {len(personas)}")
        return personas
    except Exception as e:
        print(f"❌ Error en get_personas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener personas: {str(e)}")

# GET: Obtener una persona por ID
@app.get("/personas/{persona_id}", response_model=PersonaResponse)
async def get_persona(persona_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene una persona por su ID"""
    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    return persona

# POST: Crea una nueva persona
@app.post("/personas/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(persona: PersonaCreate, db: AsyncSession = Depends(get_db)):
    # Verificar que el RUT sea único
    result = await db.execute(select(Persona).where(Persona.rut == persona.rut))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="El RUT ya existe")
    
    db_persona = Persona(
        rut=persona.rut,
        apellidos=persona.apellidos,
        nombres=persona.nombres
    )
    db.add(db_persona)
    await db.commit()
    await db.refresh(db_persona)
    
    return db_persona

@app.put("/personas/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    persona_update: PersonaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza una persona existente"""
    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    db_persona = result.scalar_one_or_none()
    
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    # Actualizar solo los campos proporcionados
    if persona_update.rut is not None:
        db_persona.rut = persona_update.rut
    if persona_update.apellidos is not None:
        db_persona.apellidos = persona_update.apellidos
    if persona_update.nombres is not None:
        db_persona.nombres = persona_update.nombres
    
    await db.commit()
    await db.refresh(db_persona)
    
    return db_persona

# DELETE: Eliminar una persona
@app.delete("/personas/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(persona_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina una persona"""
    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    db_persona = result.scalar_one_or_none()
    
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    await db.delete(db_persona)
    await db.commit()
    
    return None

@app.get("/health")
async def health_check():
    """Verifica que la API esté disponible"""
    return {"status": "online", "message": "API funcionando correctamente"}


# ========== ENDPOINTS ASUNTOS ==========

@app.get("/asuntos/", response_model=list[AsuntoDetailResponse])
async def get_asuntos(db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todos los asuntos"""
    result = await db.execute(select(Asunto))
    asuntos = result.scalars().all()
    
    # Contar instancias para cada asunto
    for asunto in asuntos:
        count_result = await db.execute(
            select(func.count(AsuntoInstancia.id)).where(AsuntoInstancia.asunto_id == asunto.id)
        )
        asunto.instancias = count_result.scalar() or 0
    
    return asuntos

@app.get("/asuntos/{asunto_id}", response_model=AsuntoDetailResponse)
async def get_asunto(asunto_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un asunto específico"""
    result = await db.execute(select(Asunto).where(Asunto.id == asunto_id))
    asunto = result.scalar_one_or_none()
    
    if not asunto:
        raise HTTPException(status_code=404, detail="Asunto no encontrado")
    
    # Contar instancias
    count_result = await db.execute(
        select(func.count(AsuntoInstancia.id)).where(AsuntoInstancia.asunto_id == asunto.id)
    )
    asunto.instancias = count_result.scalar() or 0
    
    return asunto

@app.post("/asuntos/", response_model=AsuntoResponse, status_code=status.HTTP_201_CREATED)
async def create_asunto(asunto: AsuntoCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo asunto"""
    # Verificar que el nombre sea único
    result = await db.execute(select(Asunto).where(Asunto.nombre == asunto.nombre))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="El nombre del asunto ya existe")
    
    db_asunto = Asunto(**asunto.dict())
    db.add(db_asunto)
    await db.commit()
    await db.refresh(db_asunto)
    
    return db_asunto

@app.put("/asuntos/{asunto_id}", response_model=AsuntoResponse)
async def update_asunto(asunto_id: int, asunto_update: AsuntoUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza un asunto existente"""
    result = await db.execute(select(Asunto).where(Asunto.id == asunto_id))
    db_asunto = result.scalar_one_or_none()
    
    if not db_asunto:
        raise HTTPException(status_code=404, detail="Asunto no encontrado")
    
    update_data = asunto_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_asunto, key, value)
    
    await db.commit()
    await db.refresh(db_asunto)
    
    return db_asunto

@app.delete("/asuntos/{asunto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asunto(asunto_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un asunto"""
    result = await db.execute(select(Asunto).where(Asunto.id == asunto_id))
    db_asunto = result.scalar_one_or_none()
    
    if not db_asunto:
        raise HTTPException(status_code=404, detail="Asunto no encontrado")
    
    await db.delete(db_asunto)
    await db.commit()


# ========== ENDPOINTS INSTANCIAS ==========

@app.get("/asuntos/{asunto_id}/instancias/", response_model=list[AsuntoInstanciaDetailResponse])
async def get_instancias_por_asunto(asunto_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene todas las instancias de un asunto"""
    result = await db.execute(select(AsuntoInstancia).where(AsuntoInstancia.asunto_id == asunto_id))
    instancias = result.scalars().all()
    
    if not instancias:
        # Verificar que el asunto exista
        asunto_result = await db.execute(select(Asunto).where(Asunto.id == asunto_id))
        if not asunto_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Asunto no encontrado")
    
    # Contar registrados y presentes
    for instancia in instancias:
        registrados = await db.execute(
            select(func.count(Asistencia.id)).where(Asistencia.asunto_instancia_id == instancia.id)
        )
        presentes = await db.execute(
            select(func.count(Asistencia.id)).where(
                (Asistencia.asunto_instancia_id == instancia.id) & (Asistencia.asistio == True)
            )
        )
        instancia.registrados = registrados.scalar() or 0
        instancia.presentes = presentes.scalar() or 0
    
    return instancias

@app.get("/instancias/{instancia_id}", response_model=AsuntoInstanciaDetailResponse)
async def get_instancia(instancia_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene una instancia específica"""
    result = await db.execute(select(AsuntoInstancia).where(AsuntoInstancia.id == instancia_id))
    instancia = result.scalar_one_or_none()
    
    if not instancia:
        raise HTTPException(status_code=404, detail="Instancia no encontrada")
    
    # Contar registrados y presentes
    registrados = await db.execute(
        select(func.count(Asistencia.id)).where(Asistencia.asunto_instancia_id == instancia.id)
    )
    presentes = await db.execute(
        select(func.count(Asistencia.id)).where(
            (Asistencia.asunto_instancia_id == instancia.id) & (Asistencia.asistio == True)
        )
    )
    instancia.registrados = registrados.scalar() or 0
    instancia.presentes = presentes.scalar() or 0
    
    return instancia

@app.post("/instancias/", response_model=AsuntoInstanciaResponse, status_code=status.HTTP_201_CREATED)
async def create_instancia(instancia: AsuntoInstanciaCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva instancia de asunto"""
    # Verificar que el asunto exista
    asunto_result = await db.execute(select(Asunto).where(Asunto.id == instancia.asunto_id))
    if not asunto_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Asunto no encontrado")
    
    db_instancia = AsuntoInstancia(**instancia.dict())
    db.add(db_instancia)
    await db.commit()
    await db.refresh(db_instancia)
    
    return db_instancia

@app.put("/instancias/{instancia_id}", response_model=AsuntoInstanciaResponse)
async def update_instancia(instancia_id: int, instancia_update: AsuntoInstanciaUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza una instancia de asunto"""
    result = await db.execute(select(AsuntoInstancia).where(AsuntoInstancia.id == instancia_id))
    db_instancia = result.scalar_one_or_none()
    
    if not db_instancia:
        raise HTTPException(status_code=404, detail="Instancia no encontrada")
    
    update_data = instancia_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_instancia, key, value)
    
    await db.commit()
    await db.refresh(db_instancia)
    
    return db_instancia

@app.delete("/instancias/{instancia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instancia(instancia_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina una instancia de asunto"""
    result = await db.execute(select(AsuntoInstancia).where(AsuntoInstancia.id == instancia_id))
    db_instancia = result.scalar_one_or_none()
    
    if not db_instancia:
        raise HTTPException(status_code=404, detail="Instancia no encontrada")
    
    await db.delete(db_instancia)
    await db.commit()


# ========== ENDPOINTS ASISTENCIA ==========

@app.get("/instancias/{instancia_id}/asistencia/", response_model=list[AsistenciaDetailResponse])
async def get_asistencia_por_instancia(instancia_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene todos los registros de asistencia de una instancia"""
    # Verificar que la instancia exista
    instancia_result = await db.execute(select(AsuntoInstancia).where(AsuntoInstancia.id == instancia_id))
    if not instancia_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Instancia no encontrada")
    
    result = await db.execute(
        select(Asistencia, Persona).join(Persona).where(Asistencia.asunto_instancia_id == instancia_id)
    )
    registros = result.all()
    
    responses = []
    for asistencia, persona in registros:
        responses.append({
            "id": asistencia.id,
            "persona_id": persona.id,
            "nombre": f"{persona.nombres} {persona.apellidos}",
            "rut": persona.rut,
            "asistio": asistencia.asistio
        })
    
    return responses

@app.get("/personas/{persona_id}/asistencia/", response_model=list[dict])
async def get_asistencia_por_persona(persona_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene el historial de asistencia de una persona"""
    # Verificar que la persona exista
    persona_result = await db.execute(select(Persona).where(Persona.id == persona_id))
    persona = persona_result.scalar_one_or_none()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    result = await db.execute(
        select(Asistencia, AsuntoInstancia, Asunto).join(
            AsuntoInstancia
        ).join(
            Asunto
        ).where(Asistencia.persona_id == persona_id).order_by(AsuntoInstancia.fecha.desc())
    )
    registros = result.all()
    
    responses = []
    for asistencia, instancia, asunto in registros:
        responses.append({
            "id": asistencia.id,
            "asunto": asunto.nombre,
            "fecha": instancia.fecha,
            "asistio": asistencia.asistio,
            "lugar": instancia.lugar or asunto.lugar,
            "coordinadora": instancia.coordinadora or asunto.coordinadora
        })
    
    return responses

@app.post("/asistencia/", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
async def create_asistencia(asistencia: AsistenciaCreate, db: AsyncSession = Depends(get_db)):
    """Registra una persona en una instancia de asunto"""
    # Verificar que la persona exista
    persona_result = await db.execute(select(Persona).where(Persona.id == asistencia.persona_id))
    if not persona_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    # Verificar que la instancia exista
    instancia_result = await db.execute(select(AsuntoInstancia).where(AsuntoInstancia.id == asistencia.asunto_instancia_id))
    if not instancia_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Instancia no encontrada")
    
    # Verificar que no esté duplicada
    existing = await db.execute(
        select(Asistencia).where(
            (Asistencia.persona_id == asistencia.persona_id) & 
            (Asistencia.asunto_instancia_id == asistencia.asunto_instancia_id)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Esta persona ya está registrada en esta instancia")
    
    db_asistencia = Asistencia(**asistencia.dict())
    db.add(db_asistencia)
    await db.commit()
    await db.refresh(db_asistencia)
    
    return db_asistencia

@app.put("/asistencia/{asistencia_id}", response_model=AsistenciaResponse)
async def update_asistencia(asistencia_id: int, asistencia_update: AsistenciaUpdate, db: AsyncSession = Depends(get_db)):
    """Marca asistencia de una persona (presente/ausente)"""
    result = await db.execute(select(Asistencia).where(Asistencia.id == asistencia_id))
    db_asistencia = result.scalar_one_or_none()
    
    if not db_asistencia:
        raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
    
    from datetime import datetime
    db_asistencia.asistio = asistencia_update.asistio
    db_asistencia.fecha_marcado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_asistencia)
    
    return db_asistencia

@app.delete("/asistencia/{asistencia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asistencia(asistencia_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un registro de asistencia"""
    result = await db.execute(select(Asistencia).where(Asistencia.id == asistencia_id))
    db_asistencia = result.scalar_one_or_none()
    
    if not db_asistencia:
        raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
    
    await db.delete(db_asistencia)
    await db.commit()

@app.post("/instancias/{instancia_id}/registrar", status_code=status.HTTP_201_CREATED)
async def registrar_persona_instancia(instancia_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    """Registra una persona en una instancia como inasistente por defecto"""
    persona_id = data.get("persona_id")
    asistio = data.get("asistio", False)
    
    if not persona_id:
        raise HTTPException(status_code=400, detail="persona_id es requerido")
    
    # Verificar que la instancia exista
    instancia_result = await db.execute(select(AsuntoInstancia).where(AsuntoInstancia.id == instancia_id))
    if not instancia_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Instancia no encontrada")
    
    # Verificar que la persona exista
    persona_result = await db.execute(select(Persona).where(Persona.id == persona_id))
    if not persona_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    # Verificar que no esté duplicada
    existing = await db.execute(
        select(Asistencia).where(
            (Asistencia.persona_id == persona_id) & 
            (Asistencia.asunto_instancia_id == instancia_id)
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Persona ya está registrada"}
    
    # Crear registro
    db_asistencia = Asistencia(
        persona_id=persona_id,
        asunto_instancia_id=instancia_id,
        asistio=asistio
    )
    db.add(db_asistencia)
    await db.commit()
    await db.refresh(db_asistencia)
    
    return {"id": db_asistencia.id, "persona_id": persona_id, "asistio": asistio}