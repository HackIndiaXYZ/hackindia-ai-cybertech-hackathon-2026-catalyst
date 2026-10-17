# CanaryWatch — Trap, Don't Track

A hackathon-ready deception-security prototype. It demonstrates synthetic honeytokens, a real FastAPI trigger pipeline, incident creation, measured latency, WebSocket alerts, token rotation/revocation, a React dashboard, and benchmark scripts.

> **Safety / scope:** This project defaults to a local simulation using synthetic data. Provider adapters are demonstrations, not real AWS/GitHub/cloud integrations. Do not place decoys in systems you do not own or administer. Latency and accuracy claims must be based on measured tests.

## Requirements
- Python 3.11+
- Node.js 20+
- npm

## Run on Windows PowerShell

### 1. Backend
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### 2. Frontend (new terminal)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open the Vite URL printed in the terminal (usually http://localhost:5173).

## Run on macOS/Linux
Backend:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Frontend:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Demo flow
1. Open the dashboard.
2. Click **Create honeytoken** to create a synthetic decoy.
3. Click **Simulate trigger** on a token.
4. Observe the incident, measured processing latency, and WebSocket notification.
5. Click **Rotate** to revoke the old decoy and create a linked replacement.
6. Use **Reset demo** to reset the synthetic dataset.

## API
- `GET /api/v1/health`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/honeytokens`
- `POST /api/v1/honeytokens`
- `POST /api/v1/demo/trigger/{token_id}`
- `POST /api/v1/honeytokens/{token_id}/rotate`
- `POST /api/v1/honeytokens/{token_id}/revoke`
- `GET /api/v1/incidents`
- `POST /api/v1/incidents/{incident_id}/acknowledge`
- `POST /api/v1/incidents/{incident_id}/resolve`
- `GET /api/v1/events`
- `GET /api/v1/analytics/latency`
- `GET /api/v1/integrations`
- `POST /api/v1/demo/reset`
- `GET /api/v1/audit`
- `WS /api/v1/ws/alerts`

## Testing
```bash
cd backend
pytest -q
python ../scripts/benchmark_detection.py
```

## Limitations
- Authentication is not implemented in this starter. It is intended for a controlled local demo, not internet exposure.
- The local placement adapters are simulated and do not alter external resources.
- SQLite is used for portability. Review deployment, secret management, authorization, migrations, and rate limits before production use.
- “Under 3 seconds” is a target; benchmark output is the evidence, not a hardcoded promise.
