from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

def utcnow():
    return datetime.now(timezone.utc)

class Honeytoken(Base):
    __tablename__ = "honeytokens"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    kind = Column(String, nullable=False, default="API credential")
    environment = Column(String, nullable=False, default="Local demo")
    status = Column(String, nullable=False, default="active")
    severity = Column(String, nullable=False, default="high")
    fingerprint = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    rotation_of = Column(String, nullable=True)
    trigger_count = Column(Integer, default=0, nullable=False)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String, primary_key=True)
    token_id = Column(String, ForeignKey("honeytokens.id"), nullable=False)
    title = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open")
    latency_ms = Column(Float, nullable=False)
    rationale = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class SecurityEvent(Base):
    __tablename__ = "security_events"
    id = Column(String, primary_key=True)
    token_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    source = Column(String, nullable=False, default="controlled-demo")
    severity = Column(String, nullable=False)
    incident_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    latency_ms = Column(Float, nullable=True)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True)
    action = Column(String, nullable=False)
    target_id = Column(String, nullable=True)
    details = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
