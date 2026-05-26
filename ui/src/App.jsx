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
  HardDrive
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

  const fetchData = async () => {
    try {
      const [queueRes, activeRes, rollbacksRes, storageRes, healthRes] = await Promise.all([
        axios.get(`${API_BASE}/queue`).catch(() => ({ data: [] })),
        axios.get(`${API_BASE}/active`).catch(() => ({ data: [] })),
        axios.get(`${API_BASE}/rollbacks`).catch(() => ({ data: [] })),
        axios.get(`${API_BASE}/storage`).catch(() => ({ data: { reclaimable_bytes: 0 } })),
        axios.get(`${API_BASE}/health`).catch(() => ({ data: { status: 'error' } }))
      ]);

      setQueue(queueRes.data);
      setActive(activeRes.data);
      setRollbacks(rollbacksRes.data);
      setStorage(storageRes.data);
      setHealth(healthRes.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

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

    </div>
  );
}

export default App;
