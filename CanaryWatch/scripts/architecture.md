# Architecture

Browser dashboard -> FastAPI REST / WebSocket -> service layer -> SQLite
                                             -> honeytoken lifecycle
                                             -> event + incident records
                                             -> audit events

A trigger for an active synthetic honeytoken creates a security event and incident, records backend processing latency, and broadcasts an update to connected dashboards. Rotation revokes the old record and creates a replacement linked by `rotation_of`.

The local demo does not connect to cloud services or deploy endpoint agents. External adapters should implement explicit authorization, least-privilege permissions, safe secret handling, retries, auditability, and a review/approval flow before modifying external resources.
