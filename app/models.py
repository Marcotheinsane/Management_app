from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Persona(Base):
    __tablename__ = "personas"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(20), unique=True, nullable=False)
    apellidos = Column(String(255), nullable=False)
    nombres = Column(String(255), nullable=False)


class Asunto(Base):
    __tablename__ = "asuntos"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)  # taller, entrega, otra
    descripcion = Column(String(500), nullable=True)
    coordinadora = Column(String(255), nullable=False)
    lugar = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AsuntoInstancia(Base):
    __tablename__ = "asunto_instancias"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    asunto_id = Column(Integer, ForeignKey("asuntos.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    lugar = Column(String(255), nullable=True)
    coordinadora = Column(String(255), nullable=True)
    observaciones = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Asistencia(Base):
    __tablename__ = "asistencia"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    asunto_instancia_id = Column(Integer, ForeignKey("asunto_instancias.id"), nullable=False)
    asistio = Column(Boolean, default=False, nullable=False)
    fecha_marcado = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

