from pydantic import BaseModel, Field
from datetime import datetime, date

class PersonaBase(BaseModel):
    rut: str = Field(..., min_length=1, max_length=20)
    apellidos: str = Field(..., min_length=1, max_length=255)
    nombres: str = Field(..., min_length=1, max_length=255)

class PersonaCreate(PersonaBase):
    pass

class PersonaUpdate(BaseModel):
    rut: str | None = Field(None, max_length=20)
    apellidos: str | None = Field(None, max_length=255)
    nombres: str | None = Field(None, max_length=255)

class PersonaResponse(PersonaBase):
    id: int
    
    class Config:
        from_attributes = True


# ========== ASUNTOS ==========
class AsuntoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    tipo: str = Field(..., pattern="^(taller|entrega|otra)$")
    descripcion: str | None = Field(None, max_length=500)
    coordinadora: str = Field(..., min_length=1, max_length=255)
    lugar: str = Field(..., min_length=1, max_length=255)

class AsuntoCreate(AsuntoBase):
    pass

class AsuntoUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=255)
    tipo: str | None = Field(None, pattern="^(taller|entrega|otra)$")
    descripcion: str | None = Field(None, max_length=500)
    coordinadora: str | None = Field(None, max_length=255)
    lugar: str | None = Field(None, max_length=255)

class AsuntoResponse(AsuntoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AsuntoDetailResponse(AsuntoResponse):
    instancias: int = 0


# ========== ASUNTO INSTANCIAS ==========
class AsuntoInstanciaBase(BaseModel):
    asunto_id: int
    fecha: date
    lugar: str | None = Field(None, max_length=255)
    coordinadora: str | None = Field(None, max_length=255)
    observaciones: str | None = Field(None, max_length=500)

class AsuntoInstanciaCreate(AsuntoInstanciaBase):
    pass

class AsuntoInstanciaUpdate(BaseModel):
    fecha: date | None = None
    lugar: str | None = Field(None, max_length=255)
    coordinadora: str | None = Field(None, max_length=255)
    observaciones: str | None = Field(None, max_length=500)

class AsuntoInstanciaResponse(AsuntoInstanciaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AsuntoInstanciaDetailResponse(AsuntoInstanciaResponse):
    registrados: int = 0
    presentes: int = 0


# ========== ASISTENCIA ==========
class AsistenciaBase(BaseModel):
    persona_id: int
    asunto_instancia_id: int
    asistio: bool = False

class AsistenciaCreate(AsistenciaBase):
    pass

class AsistenciaUpdate(BaseModel):
    asistio: bool
    fecha_marcado: datetime | None = None

class AsistenciaResponse(AsistenciaBase):
    id: int
    fecha_marcado: datetime | None = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AsistenciaDetailResponse(BaseModel):
    id: int
    persona_id: int
    nombre: str
    rut: str
    asistio: bool
    
    class Config:
        from_attributes = True

