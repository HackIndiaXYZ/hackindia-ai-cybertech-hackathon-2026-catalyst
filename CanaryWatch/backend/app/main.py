import asyncio, os
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .db import Base, engine, get_db, SessionLocal
from .models import Honeytoken, Incident, SecurityEvent, AuditEvent
from .schemas import HoneytokenCreate
from .services import create_token, trigger_token, serialize, uid, audit

Base.metadata.create_all(bind=engine)
app = FastAPI(title="CanaryWatch API", version="0.1.0",
              description="Local deception-security demo. External provider integrations are not enabled.")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])
clients = set()

async def broadcast(payload):
    dead = []
    for ws in list(clients):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "CanaryWatch API", "mode": "local-demo"}

@app.get("/api/v1/dashboard/summary")
def summary(db: Session = Depends(get_db)):
    tokens = db.scalars(select(Honeytoken)).all()
    incidents = db.scalars(select(Incident)).all()
    events = db.scalars(select(SecurityEvent)).all()
    latencies = [e.latency_ms for e in events if e.latency_ms is not None]
    return {
        "active_honeytokens": sum(t.status == "active" for t in tokens),
        "triggered_decoys": sum(t.status == "triggered" for t in tokens),
        "open_incidents": sum(i.status == "open" for i in incidents),
        "total_events": len(events),
        "median_latency_ms": sorted(latencies)[len(latencies)//2] if latencies else None,
        "mode": "controlled local demo"
    }

@app.get("/api/v1/honeytokens")
def list_tokens(db: Session = Depends(get_db)):
    return [serialize(x) for x in db.scalars(select(Honeytoken).order_by(Honeytoken.created_at.desc())).all()]

@app.post("/api/v1/honeytokens")
def new_token(payload: HoneytokenCreate, db: Session = Depends(get_db)):
    token, demo_secret = create_token(db, payload.name, payload.kind, payload.environment, payload.severity)
    result = serialize(token)
    result["demo_secret_once"] = demo_secret
    return result

@app.post("/api/v1/demo/trigger/{token_id}")
async def demo_trigger(token_id: str, db: Session = Depends(get_db)):
    result, error = trigger_token(db, token_id)
    if error == "not_found":
        raise HTTPException(404, "Honeytoken not found")
    if error == "not_active":
        raise HTTPException(409, "Honeytoken is not active; rotate it to create a replacement")
    payload = {"type": "incident.created", "incident": serialize(result["incident"]),
               "event": serialize(result["event"]), "token_id": token_id}
    await broadcast(payload)
    return {"message": "Controlled demo trigger processed", **payload, "measured_latency_ms": result["latency_ms"]}

@app.post("/api/v1/honeytokens/{token_id}/rotate")
def rotate(token_id: str, db: Session = Depends(get_db)):
    token = db.get(Honeytoken, token_id)
    if not token:
        raise HTTPException(404, "Honeytoken not found")
    token.status = "revoked"
    db.commit()
    replacement, secret = create_token(db, f"{token.name} (replacement)", token.kind,
                                       token.environment, token.severity, rotation_of=token.id)
    audit(db, "HONEYTOKEN_ROTATED", token.id, f"replacement={replacement.id}")
    result = serialize(replacement)
    result["demo_secret_once"] = secret
    result["replaces"] = token.id
    return result

@app.post("/api/v1/honeytokens/{token_id}/revoke")
def revoke(token_id: str, db: Session = Depends(get_db)):
    token = db.get(Honeytoken, token_id)
    if not token:
        raise HTTPException(404, "Honeytoken not found")
    token.status = "revoked"
    db.commit()
    audit(db, "HONEYTOKEN_REVOKED", token.id, "Local demo revocation")
    return serialize(token)

@app.get("/api/v1/incidents")
def incidents(db: Session = Depends(get_db)):
    return [serialize(x) for x in db.scalars(select(Incident).order_by(Incident.created_at.desc())).all()]

@app.get("/api/v1/incidents/{incident_id}")
def incident_detail(incident_id: str, db: Session = Depends(get_db)):
    x = db.get(Incident, incident_id)
    if not x:
        raise HTTPException(404, "Incident not found")
    return serialize(x)

@app.post("/api/v1/incidents/{incident_id}/acknowledge")
def acknowledge(incident_id: str, db: Session = Depends(get_db)):
    x = db.get(Incident, incident_id)
    if not x:
        raise HTTPException(404, "Incident not found")
    x.status = "acknowledged"; db.commit(); audit(db, "INCIDENT_ACKNOWLEDGED", x.id)
    return serialize(x)

@app.post("/api/v1/incidents/{incident_id}/resolve")
def resolve(incident_id: str, db: Session = Depends(get_db)):
    x = db.get(Incident, incident_id)
    if not x:
        raise HTTPException(404, "Incident not found")
    x.status = "resolved"; db.commit(); audit(db, "INCIDENT_RESOLVED", x.id)
    return serialize(x)

@app.get("/api/v1/events")
def events(db: Session = Depends(get_db)):
    return [serialize(x) for x in db.scalars(select(SecurityEvent).order_by(SecurityEvent.created_at.desc())).all()]

@app.get("/api/v1/analytics/latency")
def latency(db: Session = Depends(get_db)):
    values = [x.latency_ms for x in db.scalars(select(SecurityEvent)).all() if x.latency_ms is not None]
    ordered = sorted(values)
    def percentile(p):
        return ordered[min(int((len(ordered)-1)*p), len(ordered)-1)] if ordered else None
    return {"sample_count": len(ordered), "min_ms": min(ordered) if ordered else None,
            "median_ms": percentile(.5), "p95_ms": percentile(.95),
            "max_ms": max(ordered) if ordered else None,
            "note": "Backend processing measurement for local demo events; not network-wide detection latency."}

@app.get("/api/v1/integrations")
def integrations():
    return [
        {"name": "Repository canary files", "status": "simulated", "enabled": True},
        {"name": "Cloud storage", "status": "integration interface only", "enabled": False},
        {"name": "Endpoint files", "status": "simulated", "enabled": True},
        {"name": "Database records", "status": "simulated", "enabled": True}
    ]

@app.get("/api/v1/audit")
def audit_events(db: Session = Depends(get_db)):
    return [serialize(x) for x in db.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc())).all()]

@app.post("/api/v1/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    # Explicitly limited to local-demo database tables.
    db.query(SecurityEvent).delete()
    db.query(Incident).delete()
    db.query(Honeytoken).delete()
    db.commit()
    audit(db, "DEMO_RESET", None, "Synthetic demo records cleared")
    return {"status": "reset", "message": "Synthetic demo records cleared"}

@app.post("/api/v1/demo/start")
def start_demo(db: Session = Depends(get_db)):
    count = db.query(Honeytoken).count()
    if count:
        return {"status": "already_initialized", "created": 0}
    seeds = [
        ("Payroll API canary", "API credential", "Demo finance", "critical"),
        ("Repository config decoy", "Config file", "Demo repository", "high"),
        ("Cloud archive decoy", "Cloud object", "Demo storage", "medium"),
        ("Customer DB canary", "Database record", "Demo database", "high"),
    ]
    for name, kind, env, severity in seeds:
        create_token(db, name, kind, env, severity)
    return {"status": "initialized", "created": len(seeds)}

@app.websocket("/api/v1/ws/alerts")
async def websocket_alerts(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.discard(ws)
