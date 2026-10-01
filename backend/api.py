from pathlib import Path
import json
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# BACKEND PATH
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ============================================================
# TRACE MODULES
# ============================================================

from normalizer import normalize_events
from correlation import build_sequence
from evidence_quality import build_evidence_quality
from clustering import build_incident_clusters
from incident import build_incident_analysis
from investigation import build_investigation_report
from hypotheses import build_hypothesis_report


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="TRACE",
    description=(
        "Temporal Reconstruction & Attack Causality Engine"
    ),
    version="1.11.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SCENARIO DIRECTORY
# ============================================================

SCENARIOS_DIR = (
    BACKEND_DIR.parent
    / "data"
    / "scenarios"
)


# ============================================================
# CORE TRACE ANALYSIS PIPELINE
# ============================================================

def analyze_events(raw_events):

    # --------------------------------------------------------
    # 1. Normalize raw telemetry
    # --------------------------------------------------------

    events = normalize_events(raw_events)


    # --------------------------------------------------------
    # 2. Temporal + sequence-aware correlation
    # --------------------------------------------------------

    relationships = build_sequence(events)


    # --------------------------------------------------------
    # 3. Evidence classification / weighting
    # --------------------------------------------------------

    evidence_relationships = build_evidence_quality(
        relationships
    )


    # --------------------------------------------------------
    # 4. Incident clustering
    # --------------------------------------------------------

    incidents = build_incident_clusters(
        events,
        relationships
    )


    # --------------------------------------------------------
    # 5. Incident scoring / severity
    # --------------------------------------------------------

    analyses = [
        build_incident_analysis(
            incident,
            evidence_relationships
        )
        for incident in incidents
    ]


    # --------------------------------------------------------
    # 6. Investigation report
    # --------------------------------------------------------

    report = build_investigation_report(
        events,
        relationships,
        evidence_relationships,
        incidents,
        analyses
    )


    # --------------------------------------------------------
    # 7. Competing incident hypotheses
    # --------------------------------------------------------

    hypothesis_reports = build_hypothesis_report(
        incidents,
        evidence_relationships
    )


    # --------------------------------------------------------
    # 8. Attach hypotheses to corresponding incidents
    # --------------------------------------------------------

    hypothesis_map = {
        item["incident_id"]: item["hypotheses"]
        for item in hypothesis_reports
    }

    for incident_report in report["incidents"]:

        incident_id = incident_report[
            "incident_id"
        ]

        incident_report["hypotheses"] = (
            hypothesis_map.get(
                incident_id,
                []
            )
        )


    # --------------------------------------------------------
    # 9. Update report metadata
    # --------------------------------------------------------

    report["trace"]["engine"] = (
        "TRACE v1.11"
    )

    report["trace"]["method"] = (
        "sequence-aware correlation + "
        "evidence-based hypothesis analysis"
    )

    report["trace"]["hypothesis_engine"] = (
        "TRACE v1.11"
    )


    return report


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "TRACE",
        "description": (
            "Temporal Reconstruction & Attack "
            "Causality Engine"
        ),
        "version": "1.11.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "engine": "TRACE v1.11"
    }


# ============================================================
# GET SCENARIO
# ============================================================

@app.get("/scenario/{scenario_id}")
def get_scenario(
    scenario_id: str
):

    scenario_file = (
        SCENARIOS_DIR
        / f"scenario_{scenario_id}.json"
    )


    # --------------------------------------------------------
    # Scenario does not exist
    # --------------------------------------------------------

    if not scenario_file.exists():

        raise HTTPException(
            status_code=404,
            detail="Scenario not found"
        )


    # --------------------------------------------------------
    # Load scenario
    # --------------------------------------------------------

    try:

        with open(
            scenario_file,
            "r",
            encoding="utf-8"
        ) as file:

            raw_events = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ) as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to load scenario: {error}"
            )
        )


    # --------------------------------------------------------
    # Run TRACE
    # --------------------------------------------------------

    try:

        return analyze_events(
            raw_events
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"TRACE analysis failed: {error}"
            )
        )


# ============================================================
# ANALYZE RAW EVENTS
# ============================================================

@app.post("/analyze")
def analyze(
    raw_events: list
):

    # --------------------------------------------------------
    # Validate request
    # --------------------------------------------------------

    if not isinstance(
        raw_events,
        list
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Request body must be "
                "a JSON array of events"
            )
        )


    if not raw_events:

        raise HTTPException(
            status_code=400,
            detail=(
                "Event list cannot be empty"
            )
        )


    # --------------------------------------------------------
    # Run TRACE
    # --------------------------------------------------------

    try:

        return analyze_events(
            raw_events
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"TRACE analysis failed: {error}"
            )
        )