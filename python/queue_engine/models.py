import pathlib
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class QueueTask(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    module = Column(String)
    phase = Column(String)
    status = Column(String, index=True) # PROPOSED -> APPROVED -> EXECUTING -> VERIFYING -> COMPLETED -> FAILED
    risk_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    payload_json = Column(JSON)
    rollback_json = Column(JSON)

class TelemetryEvent(Base):
    __tablename__ = 'telemetry_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String)
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class RollbackRegistry(Base):
    __tablename__ = 'rollback_registry'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rollback_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    operation_id = Column(String)
    module = Column(String)
    rollback_type = Column(String)
    rollback_payload = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

