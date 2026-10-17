import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, Archive, ArrowUpRight, Bell, Check, ChevronDown, CircleDot, Cloud, Database, FileCode2, Fingerprint, Gauge, LayoutDashboard, LoaderCircle, LockKeyhole, Plus, RefreshCw, RotateCcw, Search, Shield, ShieldAlert, ShieldCheck, Terminal, Zap } from 'lucide-react'

const API = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
type Token = { id: string; name: string; kind: string; environment: string; status: string; severity: string; created_at: string; triggered_at?: string | null; trigger_count: number; rotation_of?: string | null }
type Incident = { id: string; token_id: string; title: string; severity: string; status: string; latency_ms: number; rationale: string; created_at: string }
type Summary = { active_honeytokens: number; triggered_decoys: number; open_incidents: number; total_events: number; median_latency_ms: number | null; mode: string }
const nav = [
  { label: 'Overview', icon: LayoutDashboard }, { label: 'Live Threats', icon: ShieldAlert },
  { label: 'Honeytokens', icon: Fingerprint }, { label: 'Deployment', icon: Cloud },
  { label: 'Incident Center', icon: AlertTriangle }, { label: 'Threat Analytics', icon: Gauge },
  { label: 'Integrations', icon: Database }, { label: 'Audit Trail', icon: Archive },
]
const kindIcon: Record<string, typeof FileCode2> = { 'API credential': LockKeyhole, 'Config file': FileCode2, 'Cloud object': Cloud, 'Database record': Database, 'Sensitive document': Archive }
function timeAgo(value?: string | null) {
  if (!value) return '—'
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 1000))
  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  return `${Math.floor(seconds / 3600)}h ago`
}
async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) } })
  if (!res.ok) { const body = await res.json().catch(() => ({})); throw new Error(body.detail || `Request failed (${res.status})`) }
  return res.json()
}
function App() {
  const [page, setPage] = useState('Overview')
  const [tokens, setTokens] = useState<Token[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [connected, setConnected] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [toast, setToast] = useState('')
  const [query, setQuery] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState('Repository config decoy')
  const [kind, setKind] = useState('API credential')
  const [severity, setSeverity] = useState('high')
  const [secret, setSecret] = useState('')
  const refresh = useCallback(async () => {
    try {
      const [t, i, s] = await Promise.all([
        api<Token[]>('/api/v1/honeytokens'), api<Incident[]>('/api/v1/incidents'), api<Summary>('/api/v1/dashboard/summary')
      ])
      setTokens(t); setIncidents(i); setSummary(s); setError('')
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to connect to API') }
  }, [])
  useEffect(() => { refresh(); api('/api/v1/demo/start', { method: 'POST', body: '{}' }).then(refresh).catch(() => {}) }, [refresh])
  useEffect(() => {
    let ws: WebSocket | undefined
    let timer: number | undefined
    try {
      ws = new WebSocket(API.replace(/^http/, 'ws') + '/api/v1/ws/alerts')
      ws.onopen = () => setConnected(true)
      ws.onclose = () => setConnected(false)
      ws.onmessage = () => { refresh(); setToast('Live security event received') }
      timer = window.setInterval(() => { if (ws?.readyState === WebSocket.OPEN) ws.send('ping') }, 25000)
    } catch { setConnected(false) }
    const poll = window.setInterval(refresh, 10000)
    return () => { ws?.close(); if (timer) window.clearInterval(timer); window.clearInterval(poll) }
  }, [refresh])
  const action = async (fn: () => Promise<unknown>, message: string) => {
    setBusy(true); setError('')
    try { await fn(); await refresh(); setToast(message); window.setTimeout(() => setToast(''), 4000) }
    catch (e) { setError(e instanceof Error ? e.message : 'Action failed') }
    finally { setBusy(false) }
  }
  const createToken = async () => {
    await action(async () => {
      const created = await api<Token & { demo_secret_once?: string }>('/api/v1/honeytokens', {
        method: 'POST', body: JSON.stringify({ name, kind, environment: 'Local demo', severity })
      })
      setSecret(created.demo_secret_once || '')
      setShowCreate(false)
    }, 'Honeytoken created')
  }
  const filtered = useMemo(() => tokens.filter(t => `${t.name} ${t.kind} ${t.environment} ${t.status}`.toLowerCase().includes(query.toLowerCase())), [tokens, query])
  const activePage = page === 'Overview' ? 'Overview' : page
  const trigger = (t: Token) => action(() => api(`/api/v1/demo/trigger/${t.id}`, { method: 'POST', body: '{}' }), `Triggered ${t.name}`)
  const rotate = (t: Token) => action(() => api(`/api/v1/honeytokens/${t.id}/rotate`, { method: 'POST', body: '{}' }), `Rotated ${t.name}`)
  const reset = () => action(() => api('/api/v1/demo/reset', { method: 'POST', body: '{}' }), 'Demo reset')
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Shield size={21}/><span/></div><div><strong>canary<span>watch</span></strong><small>DECEPTION SECURITY</small></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <div className="environment"><span className="env-dot"/><div><b>Local environment</b><small>Controlled demo</small></div><ChevronDown size={15}/></div>
      <nav>{nav.map(item => { const Icon = item.icon; return <button key={item.label} className={`nav-item ${activePage === item.label ? 'selected' : ''}`} onClick={() => setPage(item.label)}><Icon size={17}/><span>{item.label}</span>{item.label === 'Live Threats' && summary?.open_incidents ? <i>{summary.open_incidents}</i> : null}</button> })}</nav>
      <div className="sidebar-bottom"><div className="mini-status"><span className="pulse-dot"/><div><b>Detection engine</b><small>{connected ? 'WebSocket connected' : 'Polling fallback'}</small></div></div><div className="profile"><div className="avatar">CW</div><div><b>Security Operator</b><small>Local demo account</small></div><ChevronDown size={15}/></div></div>
    </aside>
    <main className="main">
      <header className="topbar"><div className="crumb">Workspace <span>/</span> <b>{page}</b></div><div className="top-actions"><div className={`live-pill ${connected ? 'online' : ''}`}><span/>{connected ? 'LIVE CONNECTION' : 'POLLING MODE'}</div><button className="icon-button" aria-label="Notifications"><Bell size={18}/>{(summary?.open_incidents || 0) > 0 && <i/>}</button><div className="top-avatar">CW</div></div></header>
      <div className="content">
        <div className="page-heading"><div><div className="eyebrow"><span className="eyebrow-dot"/> AUTONOMOUS DECEPTION FRAMEWORK</div><h1>{page === 'Overview' ? 'Security overview' : page}</h1><p>{page === 'Overview' ? 'Catch the breach where it begins. No noisy log pipelines required.' : `Monitor and manage your CanaryWatch ${page.toLowerCase()} workspace.`}</p></div><div className="heading-actions"><button className="button secondary" onClick={refresh}><RefreshCw size={15}/> Refresh</button><button className="button primary" onClick={() => setShowCreate(true)}><Plus size={16}/> Create honeytoken</button></div></div>
        {error && <div className="error-banner"><AlertTriangle size={16}/><span>{error}. Check that the backend is running on {API}.</span></div>}
        {toast && <div className="toast"><Check size={16}/>{toast}<button onClick={() => setToast('')}>×</button></div>}
        {secret && <div className="secret-banner"><div><b>Demo token created — shown once</b><p>{secret}</p><small>This synthetic demo value is not a real service credential.</small></div><button className="button secondary" onClick={() => { navigator.clipboard?.writeText(secret); setToast('Demo secret copied'); setSecret('') }}>Copy & dismiss</button></div>}
        {(page === 'Overview' || page === 'Threat Analytics') && <>
          <div className="metric-grid">
            <Metric icon={<Fingerprint/>} label="Active honeytokens" value={summary?.active_honeytokens ?? '—'} foot="Deception assets deployed" tone="green"/>
            <Metric icon={<ShieldAlert/>} label="Triggered decoys" value={summary?.triggered_decoys ?? '—'} foot="Synthetic access events" tone="amber"/>
            <Metric icon={<AlertTriangle/>} label="Open incidents" value={summary?.open_incidents ?? '—'} foot="Require investigation" tone="red"/>
            <Metric icon={<Zap/>} label="Median processing" value={summary?.median_latency_ms == null ? '—' : `${summary.median_latency_ms.toFixed(2)} ms`} foot="Local backend measurement" tone="blue"/>
          </div>
          <div className="dashboard-grid">
            <section className="panel threat-panel"><PanelTitle title="Live incident stream" sub="Latest events from your deception layer" action="VIEW ALL" onAction={() => setPage('Live Threats')}/>{incidents.length === 0 ? <Empty icon={<ShieldCheck/>} title="No incidents yet" text="Trigger a synthetic decoy to see detection in action."/> : incidents.slice(0, 5).map(i => <div className="incident-row" key={i.id}><div className={`severity-mark ${i.severity}`}/><div className="incident-info"><b>{i.title}</b><small>{i.id} · {timeAgo(i.created_at)}</small></div><div className="incident-right"><span className={`tag ${i.severity}`}>{i.severity}</span><small>{i.latency_ms.toFixed(2)} ms</small></div></div>)}</section>
            <section className="panel demo-panel"><div className="panel-kicker"><span className="kicker-icon"><Terminal size={17}/></span><span>INTERACTIVE DEMO</span><span className="demo-badge">SAFE SIMULATION</span></div><h2>Trigger the trap.</h2><p>Simulate unauthorized access to a synthetic honeytoken and watch CanaryWatch respond in real time.</p><div className="demo-flow"><div><Fingerprint/><small>CANARY</small></div><span/><div><Zap/><small>DETECT</small></div><span/><div><ShieldAlert/><small>ALERT</small></div></div><button className="button primary full" disabled={busy || !tokens.some(t => t.status === 'active')} onClick={() => { const t = tokens.find(x => x.status === 'active'); if (t) trigger(t) }}><Zap size={16}/>{busy ? 'Processing…' : 'Simulate unauthorized access'}</button><button className="reset-link" onClick={reset}><RotateCcw size={13}/> Reset synthetic demo</button></section>
          </div>
        </>}
        {(page === 'Overview' || page === 'Honeytokens') && <section className="panel table-panel"><PanelTitle title="Honeytoken inventory" sub="Manage synthetic deception artifacts" action="VIEW ALL" onAction={() => setPage('Honeytokens')}/><div className="table-toolbar"><div className="search-field"><Search size={15}/><input placeholder="Search honeytokens…" value={query} onChange={e => setQuery(e.target.value)}/></div><span>{filtered.length} artifacts</span></div><div className="table-scroll"><table><thead><tr><th>ARTIFACT</th><th>TYPE</th><th>ENVIRONMENT</th><th>STATUS</th><th>SEVERITY</th><th>TRIGGERS</th><th>ACTIONS</th></tr></thead><tbody>{filtered.map(t => { const Icon = kindIcon[t.kind] || FileCode2; return <tr key={t.id}><td><div className="artifact-cell"><span className="artifact-icon"><Icon size={16}/></span><div><b>{t.name}</b><small>{t.id}</small></div></div></td><td>{t.kind}</td><td><span className="resource-dot"/>{t.environment}</td><td><span className={`status ${t.status}`}><span/>{t.status}</span></td><td><span className={`tag ${t.severity}`}>{t.severity}</span></td><td>{t.trigger_count}</td><td><div className="row-actions"><button title="Simulate trigger" disabled={t.status !== 'active' || busy} onClick={() => trigger(t)}><Zap size={15}/></button><button title="Rotate token" disabled={busy} onClick={() => rotate(t)}><RefreshCw size={15}/></button></div></td></tr> })}</tbody></table>{filtered.length === 0 && <Empty icon={<Fingerprint/>} title="No honeytokens found" text="Create a honeytoken or change your search."/ >}</div></section>}
        {(page === 'Live Threats' || page === 'Incident Center') && <section className="panel table-panel"><PanelTitle title="Incident queue" sub="Investigate events raised by triggered deception assets" action="REFRESH" onAction={refresh}/>{incidents.length === 0 ? <Empty icon={<ShieldCheck/>} title="All quiet" text="No incidents. Trigger a synthetic honeytoken to populate this queue."/> : incidents.map(i => <div className="incident-detail-row" key={i.id}><div className={`severity-mark ${i.severity}`}/><div className="incident-info"><b>{i.title}</b><small>{i.id} · token {i.token_id} · {new Date(i.created_at).toLocaleString()}</small><p>{i.rationale}</p></div><div className="incident-right"><span className={`tag ${i.severity}`}>{i.severity}</span><span className={`status ${i.status}`}>{i.status}</span><small>{i.latency_ms.toFixed(2)} ms measured</small><div className="row-actions"><button title="Acknowledge" onClick={() => action(() => api(`/api/v1/incidents/${i.id}/acknowledge`, { method: 'POST', body: '{}' }), 'Incident acknowledged')}><Check size={15}/></button><button title="Resolve" onClick={() => action(() => api(`/api/v1/incidents/${i.id}/resolve`, { method: 'POST', body: '{}' }), 'Incident resolved')}><ShieldCheck size={15}/></button></div></div></div>)}</section>}
        {page === 'Deployment' && <section className="panel integration-grid"><PanelTitle title="Placement adapters" sub="Local demo adapters are simulated; external systems are not connected."/><Integration icon={<FileCode2/>} title="Repository canary files" status="Simulated" text="Demonstrates repository artifact lifecycle without writing to an external repository."/><Integration icon={<Cloud/>} title="Cloud storage" status="Interface only" text="Adapter boundary is prepared; configure and test a real provider before claiming deployment."/><Integration icon={<Database/>} title="Database records" status="Simulated" text="Synthetic database canary records in the local demo environment."/><Integration icon={<Archive/>} title="Endpoint files" status="Simulated" text="Local placement concept only; no endpoint agent is installed." /></section>}
        {page === 'Integrations' && <section className="panel integration-grid"><PanelTitle title="Integrations" sub="Provider connection status is reported honestly."/><Integration icon={<Cloud/>} title="Cloud provider adapters" status="Not connected" text="No cloud credentials or external changes are required for the demo."/><Integration icon={<FileCode2/>} title="GitHub / repositories" status="Not connected" text="Use a dedicated test repository and least-privilege permissions for a future integration."/><Integration icon={<Database/>} title="Database adapter" status="Local demo" text="Current demo uses SQLite for portability." /></section>}
        {page === 'Threat Analytics' && <section className="panel table-panel"><PanelTitle title="Latency analytics" sub="Measured local backend event-processing samples"/><p className="analytics-note">This measurement does not include browser-to-server network time or real-world attack detection.</p><div className="analytics-bars">{incidents.slice(0, 12).map((i, idx) => <div key={i.id} title={`${i.latency_ms.toFixed(2)} ms`}><span style={{height: `${Math.max(8, Math.min(100, i.latency_ms / Math.max(1, ...incidents.map(x => x.latency_ms)) * 100))}%`}}/><small>{idx + 1}</small></div>)}</div>{incidents.length === 0 && <Empty icon={<Activity/>} title="No benchmark data yet" text="Run the demo to populate measured processing samples."/>}</section>}
        {page === 'Audit Trail' && <AuditView />}
        <footer className="footer"><div><Shield size={14}/> <b>CanaryWatch</b><span>TRAP, DON'T TRACK.</span></div><small>LOCAL DEMO · SYNTHETIC DATA · NOT A PRODUCTION SIEM</small></footer>
      </div>
    </main>
    {showCreate && <div className="modal-backdrop" onClick={() => setShowCreate(false)}><div className="modal" onClick={e => e.stopPropagation()}><div className="modal-head"><div><span className="eyebrow">DECEPTION ASSET</span><h2>Create honeytoken</h2></div><button className="icon-button" onClick={() => setShowCreate(false)}>×</button></div><p className="modal-copy">Create a synthetic decoy for the controlled demo environment.</p><label>Name<input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Payroll API canary"/></label><label>Artifact type<select value={kind} onChange={e => setKind(e.target.value)}>{['API credential','Config file','Cloud object','Database record','Sensitive document'].map(x => <option key={x}>{x}</option>)}</select></label><label>Severity<select value={severity} onChange={e => setSeverity(e.target.value)}>{['low','medium','high','critical'].map(x => <option key={x}>{x}</option>)}</select></label><div className="modal-actions"><button className="button secondary" onClick={() => setShowCreate(false)}>Cancel</button><button className="button primary" disabled={!name.trim() || busy} onClick={createToken}><Plus size={15}/> Create asset</button></div></div></div>}
  </div>
}
function Metric({icon,label,value,foot,tone}:{icon:React.ReactNode;label:string;value:React.ReactNode;foot:string;tone:string}) { return <div className="metric-card"><div className="metric-top"><span>{label}</span><span className={`metric-icon ${tone}`}>{icon}</span></div><strong>{value}</strong><small>{foot}</small></div> }
function PanelTitle({title,sub,action,onAction}:{title:string;sub:string;action?:string;onAction?:()=>void}) { return <div className="panel-title"><div><h2>{title}</h2><p>{sub}</p></div>{action && <button onClick={onAction} className="text-action">{action}<ArrowUpRight size={14}/></button>}</div> }
function Empty({icon,title,text}:{icon:React.ReactNode;title:string;text:string}) { return <div className="empty-state"><span>{icon}</span><b>{title}</b><p>{text}</p></div> }
function Integration({icon,title,status,text}:{icon:React.ReactNode;title:string;status:string;text:string}) { return <div className="integration-card"><span className="integration-icon">{icon}</span><div className="integration-head"><h3>{title}</h3><span className="status neutral">{status}</span></div><p>{text}</p><button className="text-action" onClick={() => alert('This provider is not connected in the local demo.')}>View adapter details <ArrowUpRight size={14}/></button></div> }
function AuditView() { const [items,setItems] = useState<any[]>([]); useEffect(() => { api<any[]>('/api/v1/audit').then(setItems).catch(() => setItems([])) }, []); return <section className="panel table-panel"><PanelTitle title="Audit trail" sub="Append-only application activity records"/>{items.length ? items.map(x => <div className="audit-row" key={x.id}><CircleDot size={15}/><div><b>{x.action}</b><small>{x.target_id || 'System'} · {x.created_at}</small><p>{x.details}</p></div></div>) : <Empty icon={<Archive/>} title="No audit entries" text="Actions will appear here when you create or trigger honeytokens."/>}</section> }
export default App
