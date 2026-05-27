import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, 
  Database, 
  History, 
  ListOrdered, 
  ShieldAlert, 
  TerminalSquare, 
  RefreshCw,
  HardDrive,
  Search,
  Sparkles
} from 'lucide-react';
import './index.css';

// Configure axios base URL for development if needed, else it uses relative path
const API_BASE = import.meta.env.DEV ? 'http://localhost:8000/api' : '/api';

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getStatusBadge = (status) => {
  const s = (status || '').toUpperCase();
  if (s === 'COMPLETED' || s === 'SUCCESS') return 'badge-success';
  if (s === 'FAILED' || s === 'ERROR') return 'badge-error';
  if (s === 'EXECUTING' || s === 'ACTIVE') return 'badge-warning';
  return 'badge-info'; // PROPOSED, APPROVED, etc.
};

const getRiskBadge = (risk) => {
  const r = (risk || '').toLowerCase();
  if (r === 'safe') return 'badge-success';
  if (r === 'balanced') return 'badge-warning';
  if (r === 'aggressive') return 'badge-error';
  return 'badge-info';
};

function App() {
  const [queue, setQueue] = useState([]);
  const [active, setActive] = useState([]);
  const [rollbacks, setRollbacks] = useState([]);
  const [storage, setStorage] = useState({ reclaimable_bytes: 0 });
  const [health, setHealth] = useState({ status: 'unknown' });
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Scan state
  const [scanModalOpen, setScanModalOpen] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [enqueuing, setEnqueuing] = useState(false);
  const [scanPlans, setScanPlans] = useState([]);

  // AI state
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiData, setAiData] = useState(null);
  const [aiTarget, setAiTarget] = useState('storage');

  const fetchData = async () => {
    console.log(`[Frontend] Fetching data from backend API at ${new Date().toISOString()}...`);
    try {
      const [queueRes, activeRes, rollbacksRes, storageRes, healthRes] = await Promise.all([
        axios.get(`${API_BASE}/queue`).catch(err => { console.error("[Frontend] Error fetching queue:", err); return { data: [] }; }),
        axios.get(`${API_BASE}/active`).catch(err => { console.error("[Frontend] Error fetching active executions:", err); return { data: [] }; }),
        axios.get(`${API_BASE}/rollbacks`).catch(err => { console.error("[Frontend] Error fetching rollbacks:", err); return { data: [] }; }),
        axios.get(`${API_BASE}/storage`).catch(err => { console.error("[Frontend] Error fetching storage:", err); return { data: { reclaimable_bytes: 0 } }; }),
        axios.get(`${API_BASE}/health`).catch(err => { console.error("[Frontend] Error fetching health:", err); return { data: { status: 'error' } }; })
      ]);

      console.debug(`[Frontend] Data received: Queue(${queueRes.data.length}), Active(${activeRes.data.length}), Rollbacks(${rollbacksRes.data.length})`);

      setQueue(queueRes.data);
      setActive(activeRes.data);
      setRollbacks(rollbacksRes.data);
      setStorage(storageRes.data);
      setHealth(healthRes.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error("[Frontend] Critical failure during polling:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.info("[Frontend] App Component mounted, starting polling interval.");
    fetchData();
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds
    return () => {
      console.info("[Frontend] App Component unmounting, clearing interval.");
      clearInterval(interval);
    };
  }, []);

  const handleScanClick = async () => {
    console.info("[Frontend] Scan System button clicked. Opening modal and fetching plans.");
    setScanning(true);
    setScanModalOpen(true);
    setScanPlans([]);
    try {
      console.log("[Frontend] POST /api/scan/plan ...");
      const res = await axios.post(`${API_BASE}/scan/plan`);
      console.info(`[Frontend] Scan planning complete. Received ${res.data.plans?.length || 0} plans.`, res.data.plans);
      setScanPlans(res.data.plans || []);
    } catch (err) {
      console.error("[Frontend] Failed to generate scan plans via API:", err);
    } finally {
      setScanning(false);
    }
  };

  const handleEnqueueClick = async () => {
    console.info(`[Frontend] Approve & Enqueue clicked. Sending ${scanPlans.length} plans to daemon.`);
    setEnqueuing(true);
    try {
      console.log("[Frontend] POST /api/scan/enqueue payload:", scanPlans);
      await axios.post(`${API_BASE}/scan/enqueue`, { plans: scanPlans });
      console.info("[Frontend] Enqueue successful. Closing modal and refreshing queue.");
      setScanModalOpen(false);
      fetchData(); // Refresh queue
    } catch (err) {
      console.error("[Frontend] Failed to enqueue plans:", err);
      alert("Failed to enqueue plans");
    } finally {
      setEnqueuing(false);
    }
  };

  const handleAiClick = () => {
    setAiModalOpen(true);
    setAiData(null);
    fetchAiAdvice('storage');
  };

  const fetchAiAdvice = async (target) => {
    setAiTarget(target);
    setAiLoading(true);
    setAiData(null);
    try {
      const res = await axios.get(`${API_BASE}/advise/${target}`);
      setAiData(res.data.recommendation);
    } catch (err) {
      setAiData(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="glass-panel glow-effect" style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(99, 102, 241, 0.2)' }}>
            <TerminalSquare size={32} color="#8b5cf6" />
          </div>
          <div>
            <h1 style={{ fontSize: '2rem', margin: 0, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              SysClean Operations
            </h1>
            <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.9rem' }}>
              Autonomous AI Workstation Remediation
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Last updated: {lastUpdated.toLocaleTimeString()}
          </span>
          <button 
            onClick={handleScanClick}
            disabled={scanning || enqueuing}
            style={{ 
              background: 'var(--accent-primary)', 
              border: 'none', 
              color: '#fff',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: 600,
              transition: 'all 0.2s',
              opacity: (scanning || enqueuing) ? 0.7 : 1
            }}
          >
            <Search size={16} className={scanning ? "spin" : ""} />
            Scan System
          </button>
          <button 
            onClick={handleAiClick}
            style={{ 
              background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)', 
              border: 'none', 
              color: '#fff',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: 600,
              transition: 'all 0.2s',
            }}
          >
            <Sparkles size={16} />
            Ask AI Advisory
          </button>
          <button 
            onClick={fetchData}
            style={{ 
              background: 'var(--glass-bg)', 
              border: '1px solid var(--glass-border)', 
              color: 'var(--text-primary)',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.background = 'var(--glass-bg)'}
          >
            <RefreshCw size={16} className={loading ? "spin" : ""} />
            Refresh
          </button>
        </div>
      </header>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        
        <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', animationDelay: '0.1s' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: 500 }}>System Health</p>
              <h2 style={{ fontSize: '2rem', margin: 0, textTransform: 'capitalize' }}>
                {health.status === 'ok' ? 'Optimal' : health.status}
              </h2>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)' }}>
              <Activity size={24} color="var(--status-success)" />
            </div>
          </div>
        </div>

        <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', animationDelay: '0.2s' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: 500 }}>Reclaimable Storage</p>
              <h2 style={{ fontSize: '2rem', margin: 0, color: '#38bdf8' }}>
                {formatBytes(storage.reclaimable_bytes)}
              </h2>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(56, 189, 248, 0.1)' }}>
              <HardDrive size={24} color="#38bdf8" />
            </div>
          </div>
        </div>

        <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', animationDelay: '0.3s' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: 500 }}>Active Executions</p>
              <h2 style={{ fontSize: '2rem', margin: 0 }}>
                {active.length}
              </h2>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.1)' }}>
              <Database size={24} color="var(--status-warning)" />
            </div>
          </div>
        </div>

        <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', animationDelay: '0.4s' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: 500 }}>Total Rollbacks</p>
              <h2 style={{ fontSize: '2rem', margin: 0 }}>
                {rollbacks.length}
              </h2>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.1)' }}>
              <ShieldAlert size={24} color="var(--status-error)" />
            </div>
          </div>
        </div>

      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '1.5rem' }}>
        
        {/* Queue Table */}
        <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '400px', animationDelay: '0.5s' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <ListOrdered size={20} color="var(--accent-primary)" />
            <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Operation Queue</h3>
          </div>
          <div className="table-container" style={{ flex: 1, overflowY: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Module</th>
                  <th>Status</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {queue.length === 0 ? (
                  <tr><td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No items in queue</td></tr>
                ) : queue.map((item, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{(item.id || '').substring(0, 8)}</td>
                    <td style={{ fontWeight: 500 }}>{item.module}</td>
                    <td><span className={`badge ${getStatusBadge(item.status)}`}>{item.status}</span></td>
                    <td><span className={`badge ${getRiskBadge(item.risk)}`}>{item.risk}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Rollback History Table */}
        <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '400px', animationDelay: '0.6s' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <History size={20} color="var(--accent-secondary)" />
            <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Rollback Registry</h3>
          </div>
          <div className="table-container" style={{ flex: 1, overflowY: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Module</th>
                  <th>Type</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {rollbacks.length === 0 ? (
                  <tr><td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No rollback history</td></tr>
                ) : rollbacks.map((item, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{(item.id || '').substring(0, 8)}</td>
                    <td style={{ fontWeight: 500 }}>{item.module}</td>
                    <td>{item.type}</td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{new Date(item.date).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      {/* Scan Modal */}
      {scanModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '600px', maxWidth: '90%', padding: '2rem' }}>
            <h2 style={{ marginTop: 0, marginBottom: '1.5rem' }}>System Scan Results</h2>
            
            {scanning ? (
              <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-secondary)' }}>
                <Search size={48} className="spin" style={{ marginBottom: '1rem' }} />
                <p>Analyzing system components...</p>
              </div>
            ) : (
              <div>
                {scanPlans.length === 0 ? (
                  <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem 0' }}>
                    No actionable cleanups found.
                  </p>
                ) : (
                  <div>
                    <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                      The following cleanup plans were generated:
                    </p>
                    <div style={{ background: 'var(--bg-secondary)', borderRadius: '8px', padding: '1rem', marginBottom: '1.5rem' }}>
                      {scanPlans.map((plan, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: i < scanPlans.length - 1 ? '1px solid rgba(255,255,255,0.1)' : 'none' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontWeight: 600 }}>{plan.module}</span>
                            <span className={`badge ${getRiskBadge(plan.risk_level)}`}>{plan.risk_level}</span>
                          </div>
                          <span style={{ color: '#38bdf8' }}>{formatBytes(plan.estimated_bytes || 0)}</span>
                        </div>
                      ))}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                      <span style={{ fontWeight: 'bold' }}>Total Estimated Savings:</span>
                      <span style={{ fontSize: '1.25rem', color: '#38bdf8', fontWeight: 'bold' }}>
                        {formatBytes(scanPlans.reduce((acc, p) => acc + (p.estimated_bytes || 0), 0))}
                      </span>
                    </div>
                  </div>
                )}
                
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                  <button 
                    onClick={() => setScanModalOpen(false)}
                    disabled={enqueuing}
                    style={{ 
                      background: 'transparent', 
                      border: '1px solid var(--glass-border)', 
                      color: 'var(--text-primary)',
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                  {scanPlans.length > 0 && (
                    <button 
                      onClick={handleEnqueueClick}
                      disabled={enqueuing}
                      style={{ 
                        background: 'var(--status-warning)', 
                        border: 'none', 
                        color: '#000',
                        fontWeight: 'bold',
                        padding: '0.5rem 1.5rem',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      {enqueuing ? <RefreshCw size={16} className="spin" /> : null}
                      Approve & Enqueue
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Advisory Modal */}
      {aiModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '800px', maxWidth: '90%', padding: '2rem', display: 'flex', flexDirection: 'column', maxHeight: '90vh' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Sparkles size={24} color="#8b5cf6" />
                <h2 style={{ margin: 0 }}>AI Advisory Engine</h2>
              </div>
              <button 
                onClick={() => setAiModalOpen(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.5rem' }}
              >&times;</button>
            </div>
            
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
              {['storage', 'docker', 'apt'].map(t => (
                <button
                  key={t}
                  onClick={() => fetchAiAdvice(t)}
                  style={{
                    background: aiTarget === t ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
                    border: `1px solid ${aiTarget === t ? '#8b5cf6' : 'var(--glass-border)'}`,
                    color: aiTarget === t ? '#8b5cf6' : 'var(--text-primary)',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textTransform: 'capitalize'
                  }}
                >
                  {t === 'storage' ? 'Queue Analysis' : t}
                </button>
              ))}
            </div>

            <div style={{ flex: 1, overflowY: 'auto', background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
              {aiLoading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
                  <RefreshCw size={32} className="spin" style={{ marginBottom: '1rem' }} />
                  <p>Consulting AI Models...</p>
                </div>
              ) : (
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'inherit', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                  {aiData || "No data received."}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
