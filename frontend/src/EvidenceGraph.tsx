import { useState } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

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
  correlation_score: number;
  evidence_type: string;
  evidence_weight: number;
  reasons?: string[];
};

type EvidenceGraphProps = {
  events: TimelineEvent[];
  relationships: Relationship[];
};

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function EvidenceGraph({
  events,
  relationships,
}: EvidenceGraphProps) {
  const [selectedRelationship, setSelectedRelationship] =
    useState<Relationship | null>(null);

  const [selectedEvent, setSelectedEvent] =
    useState<TimelineEvent | null>(null);

  const sortedEvents = [...events].sort(
    (a, b) =>
      new Date(a.timestamp).getTime() -
      new Date(b.timestamp).getTime()
  );

  const eventMap = new Map(
    sortedEvents.map((event) => [
      event.event_id,
      event,
    ])
  );

  const nodes: Node[] = sortedEvents.map(
    (event, index) => {
      const isSelected =
        selectedEvent?.event_id === event.event_id;

      return {
        id: event.event_id,

        position: {
          x: 80,
          y: index * 125,
        },

        data: {
          label: (
            <div className="trace-chain-node">

              <div className="trace-chain-number">
                {String(index + 1).padStart(2, "0")}
              </div>

              <div className="trace-chain-content">

                <div className="trace-chain-top">
                  <strong>
                    {event.event_type}
                  </strong>

                  <span>
                    {formatTime(event.timestamp)}
                  </span>
                </div>

                <div className="trace-chain-id">
                  {event.event_id}
                </div>

                <div className="trace-chain-meta">

                  <span>
                    {event.device}
                  </span>

                  {event.process && (
                    <span>
                      {event.process}
                    </span>
                  )}

                  {event.resource && (
                    <span>
                      {event.resource}
                    </span>
                  )}

                </div>

              </div>

            </div>
          ),
        },

        style: {
          width: 430,
          padding: 0,
          borderRadius: 13,

          border: isSelected
            ? "1px solid rgba(96,165,250,0.65)"
            : "1px solid rgba(255,255,255,0.10)",

          background: isSelected
            ? "#172554"
            : "#111827",

          color: "#ffffff",

          boxShadow: isSelected
            ? "0 0 0 2px rgba(96,165,250,0.08), 0 10px 30px rgba(0,0,0,0.25)"
            : "0 8px 25px rgba(0,0,0,0.18)",
        },
      };
    }
  );

  const edges: Edge[] = relationships
    .filter(
      (relationship) =>
        eventMap.has(relationship.source) &&
        eventMap.has(relationship.target)
    )
    .map((relationship, index) => {
      const isSelected =
        selectedRelationship?.source ===
          relationship.source &&
        selectedRelationship?.target ===
          relationship.target;

      return {
        id: `relationship-${index}`,

        source: relationship.source,

        target: relationship.target,

        animated: isSelected,

        label: `${relationship.evidence_type} · ${relationship.correlation_score.toFixed(
          2
        )}`,

        labelStyle: {
          fill: isSelected
            ? "#93c5fd"
            : "#94a3b8",
          fontSize: 10,
          fontWeight: 600,
        },

        labelBgStyle: {
          fill: "#0f172a",
          fillOpacity: 0.96,
        },

        style: {
          stroke: isSelected
            ? "#60a5fa"
            : "#475569",

          strokeWidth: isSelected
            ? 3
            : 2,
        },

        markerEnd: {
          type: "arrowclosed",
        },

        data: {
          relationship,
        },
      };
    });

  const selectedSource = selectedRelationship
    ? eventMap.get(selectedRelationship.source)
    : null;

  const selectedTarget = selectedRelationship
    ? eventMap.get(selectedRelationship.target)
    : null;

  /*
   * Find relationships involving the selected event.
   */
  const connectedRelationships = selectedEvent
    ? relationships.filter(
        (relationship) =>
          relationship.source ===
            selectedEvent.event_id ||
          relationship.target ===
            selectedEvent.event_id
      )
    : [];

  return (
    <section className="evidence-graph">

      {/* HEADER */}

      <div className="graph-header">

        <div>

          <div className="graph-eyebrow">
            RECONSTRUCTED ATTACK PATH
          </div>

          <h3>
            Evidence Graph
          </h3>

          <p>
            Click an event or relationship to
            inspect the investigation evidence.
          </p>

        </div>

        <div className="graph-stats">

          <span>
            {sortedEvents.length} events
          </span>

          <span>
            {relationships.length} relationships
          </span>

        </div>

      </div>

      {/* GRAPH */}

      <div className="graph-workspace">

        <div className="graph-container">

          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            fitViewOptions={{
              padding: 0.2,
            }}
            nodesDraggable={false}
            nodesConnectable={false}
            elementsSelectable
            zoomOnScroll
            panOnDrag

            onNodeClick={(_, node) => {
              const event =
                eventMap.get(node.id);

              if (event) {
                setSelectedEvent(event);
                setSelectedRelationship(null);
              }
            }}

            onEdgeClick={(_, edge) => {
              const relationship =
                edge.data?.relationship as
                  | Relationship
                  | undefined;

              if (relationship) {
                setSelectedRelationship(
                  relationship
                );

                setSelectedEvent(null);
              }
            }}
          >

            <Background />

            <Controls />

            <MiniMap />

          </ReactFlow>

        </div>

        {/* INVESTIGATION DETAIL */}

        <aside className="evidence-detail">

          {/* NOTHING SELECTED */}

          {!selectedRelationship &&
            !selectedEvent && (
              <div className="evidence-empty">

                <div className="evidence-empty-icon">
                  🔎
                </div>

                <h4>
                  Inspect the attack path
                </h4>

                <p>
                  Select an event or relationship
                  to inspect the reconstructed
                  evidence.
                </p>

              </div>
            )}

          {/* EVENT DETAIL */}

          {selectedEvent && (
            <>

              <div className="detail-header">

                <div>

                  <span className="detail-label">
                    EVENT INVESTIGATION
                  </span>

                  <h4>
                    {selectedEvent.event_type}
                  </h4>

                </div>

                <div className="event-detail-index">
                  {selectedEvent.event_id}
                </div>

              </div>

              {/* TIMESTAMP */}

              <div className="event-detail-time">

                <span>
                  TIMESTAMP
                </span>

                <strong>
                  {formatTime(
                    selectedEvent.timestamp
                  )}
                </strong>

              </div>

              {/* EVENT PROPERTIES */}

              <div className="detail-section">

                <div className="detail-section-title">
                  Event properties
                </div>

                <div className="event-property-grid">

                  <div className="event-property">
                    <span>
                      USER
                    </span>

                    <strong>
                      {selectedEvent.user ||
                        "—"}
                    </strong>
                  </div>

                  <div className="event-property">
                    <span>
                      DEVICE
                    </span>

                    <strong>
                      {selectedEvent.device ||
                        "—"}
                    </strong>
                  </div>

                  <div className="event-property">
                    <span>
                      SOURCE
                    </span>

                    <strong>
                      {selectedEvent.source ||
                        "—"}
                    </strong>
                  </div>

                  <div className="event-property">
                    <span>
                      PROCESS
                    </span>

                    <strong>
                      {selectedEvent.process ||
                        "—"}
                    </strong>
                  </div>

                  <div className="event-property event-property-wide">
                    <span>
                      RESOURCE
                    </span>

                    <strong>
                      {selectedEvent.resource ||
                        "—"}
                    </strong>
                  </div>

                </div>

              </div>

              {/* CONNECTED EVENTS */}

              <div className="detail-section">

                <div className="detail-section-title">
                  Connected evidence
                </div>

                {connectedRelationships.length ===
                0 ? (
                  <div className="no-connections">
                    No reconstructed relationships
                    connect to this event.
                  </div>
                ) : (
                  <div className="connected-list">

                    {connectedRelationships.map(
                      (relationship) => {

                        const isSource =
                          relationship.source ===
                          selectedEvent.event_id;

                        const otherEventId =
                          isSource
                            ? relationship.target
                            : relationship.source;

                        const otherEvent =
                          eventMap.get(
                            otherEventId
                          );

                        return (
                          <button
                            className="connected-event"
                            key={`${relationship.source}-${relationship.target}`}
                            onClick={() => {
                              setSelectedRelationship(
                                relationship
                              );
                              setSelectedEvent(
                                null
                              );
                            }}
                          >

                            <div>

                              <strong>
                                {isSource
                                  ? "→"
                                  : "←"}{" "}
                                {otherEvent?.event_type ??
                                  otherEventId}
                              </strong>

                              <span>
                                {otherEventId}
                              </span>

                            </div>

                            <div className="connected-score">
                              {relationship.correlation_score.toFixed(
                                2
                              )}
                            </div>

                          </button>
                        );
                      }
                    )}

                  </div>
                )}

              </div>

              {/* PROVENANCE */}

              <div className="detail-section">

                <div className="detail-section-title">
                  Provenance
                </div>

                <div className="provenance-box">

                  <div>
                    <span>
                      SOURCE
                    </span>

                    <strong>
                      {selectedEvent.source}
                    </strong>
                  </div>

                  <div>
                    <span>
                      EVENT ID
                    </span>

                    <strong>
                      {selectedEvent.event_id}
                    </strong>
                  </div>

                  <div>
                    <span>
                      TIMESTAMP
                    </span>

                    <strong>
                      {selectedEvent.timestamp}
                    </strong>
                  </div>

                </div>

              </div>

            </>
          )}

          {/* RELATIONSHIP DETAIL */}

          {selectedRelationship && (
            <>

              <div className="detail-header">

                <div>

                  <span className="detail-label">
                    CONNECTION EVIDENCE
                  </span>

                  <h4>
                    {selectedRelationship.evidence_type}
                  </h4>

                </div>

                <div className="detail-score">
                  {selectedRelationship.correlation_score.toFixed(
                    2
                  )}
                </div>

              </div>

              <div className="detail-connection">

                <div>

                  <span>
                    {selectedSource?.event_type ??
                      selectedRelationship.source}
                  </span>

                  <small>
                    {selectedRelationship.source}
                  </small>

                </div>

                <span className="detail-arrow">
                  →
                </span>

                <div>

                  <span>
                    {selectedTarget?.event_type ??
                      selectedRelationship.target}
                  </span>

                  <small>
                    {selectedRelationship.target}
                  </small>

                </div>

              </div>

              <div className="detail-section">

                <div className="detail-section-title">
                  Correlation score
                </div>

                <div className="score-bar">

                  <div
                    className="score-fill"
                    style={{
                      width: `${Math.min(
                        selectedRelationship.correlation_score *
                          100,
                        100
                      )}%`,
                    }}
                  />

                </div>

                <div className="score-caption">

                  <span>
                    Relationship strength
                  </span>

                  <strong>
                    {selectedRelationship.correlation_score.toFixed(
                      2
                    )}
                  </strong>

                </div>

              </div>

              <div className="detail-section">

                <div className="detail-section-title">
                  Evidence classification
                </div>

                <div
                  className={`detail-type ${selectedRelationship.evidence_type.toLowerCase()}`}
                >
                  {selectedRelationship.evidence_type}
                </div>

                <div className="detail-weight">
                  Evidence weight:{" "}
                  <strong>
                    {selectedRelationship.evidence_weight.toFixed(
                      2
                    )}
                  </strong>
                </div>

              </div>

              <div className="detail-section">

                <div className="detail-section-title">
                  Why TRACE connected them
                </div>

                <div className="reason-list">

                  {(
                    selectedRelationship.reasons ??
                    []
                  ).map((reason) => (

                    <div
                      className="reason-item"
                      key={reason}
                    >

                      <span>
                        ✓
                      </span>

                      <p>
                        {reason}
                      </p>

                    </div>

                  ))}

                </div>

              </div>

            </>
          )}

        </aside>

      </div>

    </section>
  );
}