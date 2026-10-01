import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  Database,
  FileSearch,
  GitBranch,
  Shield,
  User,
  Brain,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import EvidenceGraph from "./EvidenceGraph";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

type TimelineEvent = {
  event_id: string;
  timestamp: string;
  event_type: string;
  source: string;
  user: string;
  device: string;
  process: string | null;
  resource: string | null;
};

type Relationship = {
  source: string;
  target: string;
  event_type?: string;
  correlation_score: number;
  evidence_type: string;
  evidence_weight: number;
  reasons?: string[];
};

type HypothesisEvidence = {
  relationship: string;
  reason: string;
  weight: number;
};

type ContradictingEvidence = {
  reason: string;
  relationships: string[];
};

type Hypothesis = {
  id: string;
  title: string;
  score: number;
  supporting_evidence: HypothesisEvidence[];
  contradicting_evidence: ContradictingEvidence[];
  missing_evidence: string[];
};

type Incident = {
  incident_id: string;
  severity: string;
  risk_score: number;
  event_count: number;
  users: string[];
  devices: string[];
  event_types: string[];
  timeline: TimelineEvent[];
  relationships: Relationship[];
  indicators: string[];
  hypotheses: Hypothesis[];
};

type Report = {
  trace: {
    engine: string;
    method: string;
    report_type: string;
    hypothesis_engine?: string;
  };
  summary: {
    total_events: number;
    reconstructed_relationships: number;
    incident_count: number;
    high_severity_incidents: number;
  };
  incidents: Incident[];
};

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatScore(score: number) {
  return score.toFixed(2);
}

function severityClass(severity: string) {
  return severity.toLowerCase();
}

function App() {
  const [report, setReport] = useState<Report | null>(null);
  const [selectedIncidentId, setSelectedIncidentId] =
    useState<string | null>(null);

  const [expandedHypothesis, setExpandedHypothesis] =
    useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadReport() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          `${API_URL}/scenario/01`
        );

        if (!response.ok) {
          throw new Error(
            `TRACE API returned ${response.status}`
          );
        }

        const data: Report = await response.json();

        setReport(data);

        if (data.incidents.length > 0) {
          setSelectedIncidentId(
            data.incidents[0].incident_id
          );
        }
      } catch (err) {
        console.error(err);

        setError(
          "Unable to connect to the TRACE API. Make sure FastAPI is running on port 8000."
        );
      } finally {
        setLoading(false);
      }
    }

    loadReport();
  }, []);

  const selectedIncident = useMemo(() => {
    if (!report || !selectedIncidentId) {
      return null;
    }

    return (
      report.incidents.find(
        (incident) =>
          incident.incident_id === selectedIncidentId
      ) ?? null
    );
  }, [report, selectedIncidentId]);

  if (loading) {
    return (
      <div className="app-shell center-screen">
        <div className="loading-card">
          <Activity
            size={28}
            className="loading-icon"
          />

          <h2>TRACE</h2>

          <p>
            Reconstructing security telemetry...
          </p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="app-shell center-screen">
        <div className="error-card">
          <AlertTriangle size={32} />

          <h2>TRACE API unavailable</h2>

          <p>{error}</p>

          <code>
            http://127.0.0.1:8000/scenario/01
          </code>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-icon">
            <Shield size={21} />
          </div>

          <div>

            <div className="brand-name">
              TRACE
            </div>

            <div className="brand-subtitle">
              Temporal Reconstruction & Attack
              Causality Engine
            </div>

          </div>

        </div>

        <div className="system-status">

          <span className="status-dot" />

          <span>
            ENGINE ONLINE
          </span>

          <span className="engine-version">
            {report.trace.engine}
          </span>

        </div>

      </header>


      <main className="main-content">

        {/* ================================================== */}
        {/* SUMMARY */}
        {/* ================================================== */}

        <section className="summary-grid">

          <div className="summary-card">

            <div className="summary-icon">
              <Database size={19} />
            </div>

            <div>

              <span className="summary-label">
                EVENTS
              </span>

              <strong>
                {report.summary.total_events}
              </strong>

              <small>
                Raw telemetry
              </small>

            </div>

          </div>


          <div className="summary-card">

            <div className="summary-icon">
              <GitBranch size={19} />
            </div>

            <div>

              <span className="summary-label">
                RELATIONSHIPS
              </span>

              <strong>
                {
                  report.summary
                    .reconstructed_relationships
                }
              </strong>

              <small>
                Reconstructed
              </small>

            </div>

          </div>


          <div className="summary-card">

            <div className="summary-icon">
              <FileSearch size={19} />
            </div>

            <div>

              <span className="summary-label">
                INCIDENTS
              </span>

              <strong>
                {report.summary.incident_count}
              </strong>

              <small>
                Reconstructed clusters
              </small>

            </div>

          </div>


          <div className="summary-card high-card">

            <div className="summary-icon">
              <AlertTriangle size={19} />
            </div>

            <div>

              <span className="summary-label">
                HIGH SEVERITY
              </span>

              <strong>
                {
                  report.summary
                    .high_severity_incidents
                }
              </strong>

              <small>
                Requires investigation
              </small>

            </div>

          </div>

        </section>


        {/* ================================================== */}
        {/* WORKSPACE */}
        {/* ================================================== */}

        <section className="workspace">

          {/* ================================================== */}
          {/* INCIDENT LIST */}
          {/* ================================================== */}

          <aside className="incident-sidebar">

            <div className="section-heading">

              <div>

                <h2>
                  Incidents
                </h2>

                <p>
                  Reconstructed activity
                </p>

              </div>

              <span className="count-badge">
                {report.incidents.length}
              </span>

            </div>


            <div className="incident-list">

              {report.incidents.map(
                (incident) => (

                  <button
                    key={incident.incident_id}
                    className={`incident-item ${
                      selectedIncidentId ===
                      incident.incident_id
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      setSelectedIncidentId(
                        incident.incident_id
                      )
                    }
                  >

                    <div className="incident-item-top">

                      <span>
                        {incident.incident_id}
                      </span>

                      <span
                        className={`severity-pill ${severityClass(
                          incident.severity
                        )}`}
                      >
                        {incident.severity}
                      </span>

                    </div>


                    <div className="incident-item-bottom">

                      <span>
                        {incident.event_count} events
                      </span>

                      <span>
                        Risk{" "}
                        {formatScore(
                          incident.risk_score
                        )}
                      </span>

                    </div>

                  </button>

                )
              )}

            </div>

          </aside>


          {/* ================================================== */}
          {/* MAIN INVESTIGATION */}
          {/* ================================================== */}

          {selectedIncident && (

            <section className="investigation">

              {/* ================================================== */}
              {/* INCIDENT HEADER */}
              {/* ================================================== */}

              <div className="incident-header">

                <div>

                  <div className="eyebrow">
                    INCIDENT INVESTIGATION
                  </div>

                  <h1>
                    {selectedIncident.incident_id}
                  </h1>

                  <p>
                    TRACE reconstructed{" "}
                    {selectedIncident.event_count}{" "}
                    related security events.
                  </p>

                </div>


                <div className="risk-box">

                  <span>
                    RISK SCORE
                  </span>

                  <strong>
                    {formatScore(
                      selectedIncident.risk_score
                    )}
                  </strong>

                  <span
                    className={`severity-pill large ${severityClass(
                      selectedIncident.severity
                    )}`}
                  >
                    {selectedIncident.severity}
                  </span>

                </div>

              </div>


              {/* ================================================== */}
              {/* CONTEXT */}
              {/* ================================================== */}

              <div className="context-row">

                <div className="context-card">

                  <User size={16} />

                  <div>

                    <span>
                      USER
                    </span>

                    <strong>
                      {selectedIncident.users.join(
                        ", "
                      )}
                    </strong>

                  </div>

                </div>


                <div className="context-card">

                  <Database size={16} />

                  <div>

                    <span>
                      DEVICES
                    </span>

                    <strong>
                      {selectedIncident.devices.join(
                        ", "
                      )}
                    </strong>

                  </div>

                </div>


                <div className="context-card">

                  <GitBranch size={16} />

                  <div>

                    <span>
                      RELATIONSHIPS
                    </span>

                    <strong>
                      {
                        selectedIncident
                          .relationships.length
                      }
                    </strong>

                  </div>

                </div>

              </div>


              {/* ================================================== */}
              {/* EVIDENCE GRAPH */}
              {/* ================================================== */}

              <EvidenceGraph
                events={selectedIncident.timeline}
                relationships={
                  selectedIncident.relationships
                }
              />


              {/* ================================================== */}
              {/* COMPETING HYPOTHESES */}
              {/* ================================================== */}

              <section className="panel hypotheses-panel">

                <div className="panel-header">

                  <div>

                    <div className="panel-title-row">

                      <Brain size={18} />

                      <h2>
                        Competing Incident Hypotheses
                      </h2>

                    </div>

                    <p>
                      Deterministic explanations
                      generated from reconstructed
                      evidence
                    </p>

                  </div>

                  <span className="hypothesis-engine-badge">
                    {report.trace.hypothesis_engine ??
                      "TRACE v1.11"}
                  </span>

                </div>


                <div className="hypothesis-note">

                  <span>
                    Evidence score
                  </span>

                  <p>
                    Scores represent the strength of
                    reconstructed evidence, not
                    statistical probability.
                  </p>

                </div>


                {selectedIncident.hypotheses.length >
                0 ? (

                  <div className="hypothesis-list">

                    {selectedIncident.hypotheses.map(
                      (hypothesis) => {

                        const isExpanded =
                          expandedHypothesis ===
                          hypothesis.id;

                        return (

                          <div
                            className={`hypothesis-card ${
                              isExpanded
                                ? "expanded"
                                : ""
                            }`}
                            key={hypothesis.id}
                          >

                            {/* HYPOTHESIS HEADER */}

                            <button
                              className="hypothesis-header"
                              onClick={() =>
                                setExpandedHypothesis(
                                  isExpanded
                                    ? null
                                    : hypothesis.id
                                )
                              }
                            >

                              <div className="hypothesis-id">
                                {
                                  hypothesis.id
                                }
                              </div>


                              <div className="hypothesis-main">

                                <strong>
                                  {
                                    hypothesis.title
                                  }
                                </strong>

                                <span>
                                  {
                                    hypothesis
                                      .supporting_evidence
                                      .length
                                  }{" "}
                                  supporting evidence
                                  item
                                  {
                                    hypothesis
                                      .supporting_evidence
                                      .length ===
                                    1
                                      ? ""
                                      : "s"
                                  }
                                </span>

                              </div>


                              <div className="hypothesis-score">

                                <span>
                                  EVIDENCE
                                </span>

                                <strong>
                                  {formatScore(
                                    hypothesis.score
                                  )}
                                </strong>

                              </div>


                              {isExpanded ? (
                                <ChevronUp
                                  size={18}
                                />
                              ) : (
                                <ChevronDown
                                  size={18}
                                />
                              )}

                            </button>


                            {/* EXPANDED DETAILS */}

                            {isExpanded && (

                              <div className="hypothesis-details">

                                {/* SUPPORTING */}

                                <div className="hypothesis-section">

                                  <div className="hypothesis-section-title supporting">

                                    <CheckCircle2
                                      size={16}
                                    />

                                    <span>
                                      Supporting
                                      Evidence
                                    </span>

                                  </div>


                                  {hypothesis
                                    .supporting_evidence
                                    .length > 0 ? (

                                    <div className="hypothesis-evidence-list">

                                      {hypothesis.supporting_evidence.map(
                                        (
                                          evidence,
                                          index
                                        ) => (

                                          <div
                                            className="hypothesis-evidence"
                                            key={`${evidence.relationship}-${index}`}
                                          >

                                            <div>

                                              <strong>
                                                {
                                                  evidence.relationship
                                                }
                                              </strong>

                                              <span>
                                                {
                                                  evidence.reason
                                                }
                                              </span>

                                            </div>

                                            <span className="evidence-weight">
                                              {formatScore(
                                                evidence.weight
                                              )}
                                            </span>

                                          </div>

                                        )
                                      )}

                                    </div>

                                  ) : (

                                    <div className="hypothesis-empty">
                                      No supporting
                                      evidence
                                      reconstructed.
                                    </div>

                                  )}

                                </div>


                                {/* CONTRADICTING */}

                                <div className="hypothesis-section">

                                  <div className="hypothesis-section-title contradicting">

                                    <AlertTriangle
                                      size={16}
                                    />

                                    <span>
                                      Contradicting
                                      Evidence
                                    </span>

                                  </div>


                                  {hypothesis
                                    .contradicting_evidence
                                    .length > 0 ? (

                                    <div className="hypothesis-evidence-list">

                                      {hypothesis.contradicting_evidence.map(
                                        (
                                          evidence,
                                          index
                                        ) => (

                                          <div
                                            className="hypothesis-evidence"
                                            key={`contradiction-${index}`}
                                          >

                                            <div>

                                              <strong>
                                                {
                                                  evidence.reason
                                                }
                                              </strong>

                                              {evidence.relationships.length >
                                                0 && (
                                                <span>
                                                  {
                                                    evidence.relationships.join(
                                                      " • "
                                                    )
                                                  }
                                                </span>
                                              )}

                                            </div>

                                          </div>

                                        )
                                      )}

                                    </div>

                                  ) : (

                                    <div className="hypothesis-empty">
                                      No contradicting
                                      evidence
                                      identified.
                                    </div>

                                  )}

                                </div>


                                {/* MISSING */}

                                <div className="hypothesis-section">

                                  <div className="hypothesis-section-title missing">

                                    <Clock3
                                      size={16}
                                    />

                                    <span>
                                      Missing Evidence
                                    </span>

                                  </div>


                                  {hypothesis
                                    .missing_evidence
                                    .length > 0 ? (

                                    <ul className="missing-evidence-list">

                                      {hypothesis.missing_evidence.map(
                                        (
                                          item,
                                          index
                                        ) => (

                                          <li
                                            key={`${item}-${index}`}
                                          >
                                            {item}
                                          </li>

                                        )
                                      )}

                                    </ul>

                                  ) : (

                                    <div className="hypothesis-empty">
                                      No major missing
                                      evidence identified.
                                    </div>

                                  )}

                                </div>

                              </div>

                            )}

                          </div>

                        );
                      }
                    )}

                  </div>

                ) : (

                  <div className="hypothesis-empty large">
                    TRACE could not generate a
                    supported hypothesis from the
                    reconstructed evidence.
                  </div>

                )}

              </section>


              {/* ================================================== */}
              {/* TIMELINE */}
              {/* ================================================== */}

              <section className="panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Investigation Timeline
                    </h2>

                    <p>
                      Chronological reconstruction
                      of the selected incident
                    </p>

                  </div>

                  <Clock3 size={18} />

                </div>


                <div className="timeline">

                  {selectedIncident.timeline.map(
                    (event, index) => (

                      <div
                        className="timeline-row"
                        key={event.event_id}
                      >

                        <div className="timeline-time">

                          {formatTime(
                            event.timestamp
                          )}

                        </div>


                        <div className="timeline-line">

                          <div className="timeline-dot">
                            {index + 1}
                          </div>

                          {index !==
                            selectedIncident.timeline
                              .length - 1 && (

                            <div className="timeline-connector" />

                          )}

                        </div>


                        <div className="timeline-event">

                          <div className="event-title-row">

                            <strong>
                              {event.event_type}
                            </strong>

                            <span className="event-id">
                              {event.event_id}
                            </span>

                          </div>


                          <div className="event-details">

                            <span>
                              Source:{" "}
                              {event.source}
                            </span>

                            <span>
                              Device:{" "}
                              {event.device}
                            </span>

                            {event.process && (
                              <span>
                                Process:{" "}
                                {event.process}
                              </span>
                            )}

                            {event.resource && (
                              <span>
                                Resource:{" "}
                                {event.resource}
                              </span>
                            )}

                          </div>

                        </div>

                      </div>

                    )
                  )}

                </div>

              </section>


              {/* ================================================== */}
              {/* EVIDENCE CHAIN */}
              {/* ================================================== */}

              <section className="panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Evidence Chain
                    </h2>

                    <p>
                      Why TRACE connected the events
                    </p>

                  </div>

                  <FileSearch size={18} />

                </div>


                <div className="evidence-list">

                  {selectedIncident.relationships.map(
                    (relationship, index) => {

                      const sourceEvent =
                        selectedIncident.timeline.find(
                          (event) =>
                            event.event_id ===
                            relationship.source
                        );

                      const targetEvent =
                        selectedIncident.timeline.find(
                          (event) =>
                            event.event_id ===
                            relationship.target
                        );

                      return (

                        <div
                          className="evidence-row"
                          key={`${relationship.source}-${relationship.target}`}
                        >

                          <div className="evidence-number">
                            {String(index + 1).padStart(
                              2,
                              "0"
                            )}
                          </div>


                          <div className="evidence-events">

                            <div>

                              <strong>
                                {sourceEvent?.event_type ??
                                  relationship.source}
                              </strong>

                              <span>
                                {relationship.source}
                              </span>

                            </div>


                            <ArrowRight size={17} />


                            <div>

                              <strong>
                                {targetEvent?.event_type ??
                                  relationship.target}
                              </strong>

                              <span>
                                {relationship.target}
                              </span>

                            </div>

                          </div>


                          <div className="evidence-meta">

                            <span
                              className={`evidence-type ${relationship.evidence_type.toLowerCase()}`}
                            >
                              {
                                relationship.evidence_type
                              }
                            </span>

                            <span className="correlation-score">
                              {formatScore(
                                relationship.correlation_score
                              )}
                            </span>

                          </div>

                        </div>

                      );
                    }
                  )}

                </div>

              </section>


              {/* ================================================== */}
              {/* INDICATORS */}
              {/* ================================================== */}

              <section className="panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Investigation Indicators
                    </h2>

                    <p>
                      Evidence observed in this
                      incident
                    </p>

                  </div>

                  <CheckCircle2 size={18} />

                </div>


                <div className="indicator-list">

                  {selectedIncident.indicators.length >
                  0 ? (

                    selectedIncident.indicators.map(
                      (indicator) => (

                        <div
                          className="indicator"
                          key={indicator}
                        >

                          <CheckCircle2 size={16} />

                          <span>
                            {indicator}
                          </span>

                        </div>

                      )
                    )

                  ) : (

                    <div className="empty-indicator">
                      No high-value indicators
                      identified.
                    </div>

                  )}

                </div>

              </section>

            </section>

          )}

        </section>

      </main>

    </div>
  );
}

export default App;