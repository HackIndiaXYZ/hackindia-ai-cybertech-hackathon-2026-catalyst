import hashlib, secrets, uuid, time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .models import Honeytoken, Incident, SecurityEvent, AuditEvent

def now():
    return datetime.now(timezone.utc)

def uid(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def audit(db, action, target_id=None, details=""):
    db.add(AuditEvent(id=uid("aud"), action=action, target_id=target_id, details=details))
    db.commit()

def create_token(db: Session, name, kind="API credential", environment="Local demo",
                 severity="high", rotation_of=None):
    raw = secrets.token_urlsafe(32)
    token = Honeytoken(
        id=uid("canary"), name=name, kind=kind, environment=environment,
        severity=severity, status="active",
        fingerprint=hashlib.sha256(raw.encode()).hexdigest(),
        rotation_of=rotation_of, created_at=now(), trigger_count=0
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    audit(db, "HONEYTOKEN_CREATED", token.id, f"type={kind}; environment={environment}")
    # Raw synthetic token is only returned once at creation; never persisted.
    return token, "cw_demo_" + raw

def trigger_token(db: Session, token_id: str):
    start = time.perf_counter()
    token = db.get(Honeytoken, token_id)
    if not token:
        return None, "not_found"
    if token.status != "active":
        return None, "not_active"
    # Simulated access event. The measured latency is backend processing time.
    token.trigger_count = (token.trigger_count or 0) + 1
    token.status = "triggered"
    token.triggered_at = now()
    incident_id = uid("inc")
    event_id = uid("evt")
    latency_ms = (time.perf_counter() - start) * 1000
    incident = Incident(
        id=incident_id, token_id=token.id, title=f"Canary triggered: {token.name}",
        severity=token.severity, status="open", latency_ms=latency_ms,
        rationale=f"An active deception artifact was intentionally triggered in the controlled demo. Artifact type: {token.kind}."
    )
    event = SecurityEvent(
        id=event_id, token_id=token.id, event_type="CANARY_TRIGGERED",
        source="controlled-demo", severity=token.severity,
        incident_id=incident_id, latency_ms=latency_ms, created_at=now()
    )
    db.add_all([incident, event])
    db.commit()
    audit(db, "CANARY_TRIGGERED", token.id, f"incident={incident_id}; latency_ms={latency_ms:.3f}")
    return {"token": token, "incident": incident, "event": event, "latency_ms": latency_ms}, None

def serialize(obj):
    result = {}
    for c in obj.__table__.columns:
        v = getattr(obj, c.name)
        if isinstance(v, datetime):
            v = v.isoformat()
        result[c.name] = v
    return result
