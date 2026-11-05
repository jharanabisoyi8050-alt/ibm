from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, Enum as SAEnum, JSON, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from app.db.database import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    OFFICER = "OFFICER"
    PUBLIC = "PUBLIC"


class AccidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccidentSource(str, enum.Enum):
    USER = "USER"
    AI_PREDICTED = "AI_PREDICTED"
    CONFIRMED = "CONFIRMED"


class AmbulanceStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    AT_SCENE = "AT_SCENE"
    RETURNING = "RETURNING"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(SAEnum(UserRole), default=UserRole.PUBLIC, nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AccidentReport(Base):
    __tablename__ = "accident_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    severity = Column(SAEnum(AccidentSeverity), nullable=False, default=AccidentSeverity.MEDIUM)
    description = Column(Text)
    is_confirmed = Column(Boolean, default=False)
    source = Column(SAEnum(AccidentSource), nullable=False, default=AccidentSource.USER)
    risk_score = Column(Float)  # 0-100, AI-generated
    weather_condition = Column(String(100))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TrafficRecord(Base):
    __tablename__ = "traffic_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    density_score = Column(Float)  # 0-100
    avg_speed_kmh = Column(Float)
    congestion_level = Column(String(20))  # LOW/MODERATE/HIGH/SEVERE
    vehicle_count = Column(Integer)
    is_simulated = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class RoadCondition(Base):
    __tablename__ = "road_conditions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    pothole_count = Column(Integer, default=0)
    visibility_score = Column(Float)  # 0-100
    surface_quality = Column(Float)   # 0-10
    weather_condition = Column(String(100))
    risk_score = Column(Float)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class AccidentHotspot(Base):
    __tablename__ = "accident_hotspots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_m = Column(Float, default=500.0)
    risk_level = Column(SAEnum(AccidentSeverity), nullable=False)
    incident_count = Column(Integer, default=0)
    cluster_id = Column(Integer)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class EmergencyResponse(Base):
    __tablename__ = "emergency_responses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accident_report_id = Column(UUID(as_uuid=True), ForeignKey("accident_reports.id"))
    recommended_action = Column(Text)
    ai_recommendation = Column(JSONB)  # Full AI recommendation JSON
    human_approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_timestamp = Column(DateTime(timezone=True))
    response_time_s = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Ambulance(Base):
    __tablename__ = "ambulances"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_code = Column(String(20), unique=True, nullable=False)
    status = Column(SAEnum(AmbulanceStatus), default=AmbulanceStatus.AVAILABLE)
    current_lat = Column(Float)
    current_lng = Column(Float)
    hospital_base = Column(String(255))
    crew_count = Column(Integer, default=2)
    is_simulated = Column(Boolean, default=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class AgentMemory(Base):
    __tablename__ = "agent_memory"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TokenUsageLog(Base):
    __tablename__ = "token_usage_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
