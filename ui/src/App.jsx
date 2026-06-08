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
  Sparkles,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  Trash2,
  Play,
  Square,
  RotateCw,
  FileText,
  Server,
  Filter,
  ArrowUpDown
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
  const [rollingBack, setRollingBack] = useState(null);

  // Tab & Docker manager state variables
  const [activeTab, setActiveTab] = useState('operations'); // 'operations' | 'docker'
  const [dockerData, setDockerData] = useState(null);
  const [dockerLoading, setDockerLoading] = useState(false);
  const [dockerSubTab, setDockerSubTab] = useState('containers'); // 'containers' | 'images' | 'volumes' | 'networks' | 'builds'
  const [dockerLogsContainer, setDockerLogsContainer] = useState(null);
  const [dockerLogsText, setDockerLogsText] = useState('');
  const [dockerLogsLoading, setDockerLogsLoading] = useState(false);
  const [dockerActionLoading, setDockerActionLoading] = useState(null);

  // Scan Inspector detail states
  const [expandedPlans, setExpandedPlans] = useState({}); // { index: boolean }
  const [planSearch, setPlanSearch] = useState({}); // { index: string }
  const [planSort, setPlanSort] = useState({}); // { index: 'name' | 'size' | null }

  const handleRollback = async (rollbackId) => {
    if (window.confirm(`Are you sure you want to trigger this rollback? This will restore files or packages altered by the original operation.`)) {
      setRollingBack(rollbackId);
      try {
        await axios.post(`${API_BASE}/rollback/${rollbackId}`);
        await fetchData();
        alert('Rollback executed successfully!');
      } catch (err) {
        console.error("Error executing rollback:", err);
        alert(`Failed to execute rollback: ${err.response?.data?.detail || err.message}`);
      } finally {
        setRollingBack(null);
      }
    }
  };

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

  const fetchDockerData = async (showLoading = false) => {
    if (showLoading) setDockerLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/docker/status`);
      if (res.data.status === 'success') {
        setDockerData(res.data);
      }
    } catch (err) {
      console.error("Error fetching docker data:", err);
    } finally {
      if (showLoading) setDockerLoading(false);
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

  // Poll Docker stats if Docker tab is active
  useEffect(() => {
    if (activeTab === 'docker') {
      fetchDockerData(dockerData === null);
      const dockerInterval = setInterval(() => fetchDockerData(false), 5000);
      return () => clearInterval(dockerInterval);
    }
  }, [activeTab]);

  const handleScanClick = async () => {
    console.info("[Frontend] Scan System button clicked. Opening modal and fetching plans.");
    setScanning(true);
    setScanModalOpen(true);
    setScanPlans([]);
    setExpandedPlans({});
    setPlanSearch({});
    setPlanSort({});
    try {
      console.log("[Frontend] POST /api/scan/plan ...");
      const res = await axios.post(`${API_BASE}/scan/plan`);
      const plans = (res.data.plans || []).map(plan => ({
        ...plan,
        targets: (plan.targets || []).map(t => {
          if (t.items) {
            return { ...t, checked: true, selectedItems: [...t.items] };
          }
          return { ...t, checked: true };
        })
      }));
      setScanPlans(plans);
    } catch (err) {
      console.error("[Frontend] Failed to generate scan plans via API:", err);
    } finally {
      setScanning(false);
    }
  };

  const handleEnqueueClick = async () => {
    // Reconstruct plans keeping only selected targets
    const processedPlans = scanPlans.map(plan => {
      const activeTargets = plan.targets
        .filter(t => t.checked)
        .map(t => {
          const newTarget = { ...t };
          if (newTarget.items && newTarget.selectedItems) {
            newTarget.items = newTarget.selectedItems;
          }
          delete newTarget.checked;
          delete newTarget.selectedItems;
          return newTarget;
        })
        .filter(t => !t.items || t.items.length > 0);

      return {
        ...plan,
        targets: activeTargets,
        estimated_bytes: activeTargets.reduce((sum, t) => sum + (t.size_bytes || 0), 0)
      };
    }).filter(plan => plan.targets.length > 0);

    if (processedPlans.length === 0) {
      alert("No targets selected to enqueue!");
      return;
    }

    console.info(`[Frontend] Approve & Enqueue clicked. Sending ${processedPlans.length} plans to daemon.`);
    setEnqueuing(true);
    try {
      console.log("[Frontend] POST /api/scan/enqueue payload:", processedPlans);
      await axios.post(`${API_BASE}/scan/enqueue`, { plans: processedPlans });
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

  // Docker Specific Actions
  const handleContainerAction = async (action, id, containerName) => {
    if (action === 'remove' && !window.confirm(`Are you sure you want to remove container "${containerName}"?`)) {
      return;
    }
    setDockerActionLoading(id);
    try {
      await axios.post(`${API_BASE}/docker/container/${action}/${id}`);
      await fetchDockerData(false);
    } catch (err) {
      console.error(`Failed to execute container action ${action}:`, err);
      alert(`Failed to ${action} container: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDockerActionLoading(null);
    }
  };

  const handleDockerClean = async (category) => {
    if (!window.confirm(`Are you sure you want to prune all unused Docker ${category}?`)) {
      return;
    }
    setDockerLoading(true);
    try {
      await axios.post(`${API_BASE}/docker/clean/${category}`);
      await fetchDockerData(false);
      alert(`Successfully pruned ${category}!`);
    } catch (err) {
      console.error(`Failed to prune ${category}:`, err);
      alert(`Failed to prune: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDockerLoading(false);
    }
  };

  const handleRemoveImage = async (id, repoName) => {
    if (!window.confirm(`Are you sure you want to delete image "${repoName}"?`)) {
      return;
    }
    setDockerLoading(true);
    try {
      await axios.post(`${API_BASE}/docker/image/remove/${id}`);
      await fetchDockerData(false);
    } catch (err) {
      console.error("Failed to delete image:", err);
      alert(`Failed to delete image: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDockerLoading(false);
    }
  };

  const viewContainerLogs = async (id, name) => {
    setDockerLogsContainer(name);
    setDockerLogsText('Loading logs...');
    setDockerLogsLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/docker/container/logs/${id}`);
      if (res.data.status === 'success') {
        setDockerLogsText(res.data.logs || 'No logs found.');
      }
    } catch (err) {
      setDockerLogsText(`Failed to fetch logs: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDockerLogsLoading(false);
    }
  };

  // Scan detail check toggles
  const toggleTargetChecked = (planIndex, targetIndex) => {
    const nextPlans = [...scanPlans];
    const target = nextPlans[planIndex].targets[targetIndex];
    target.checked = !target.checked;
    if (target.items) {
      target.selectedItems = target.checked ? [...target.items] : [];
    }
    setScanPlans(nextPlans);
  };

  const toggleSubItemChecked = (planIndex, targetIndex, itemValue) => {
    const nextPlans = [...scanPlans];
    const target = nextPlans[planIndex].targets[targetIndex];
    if (!target.selectedItems) {
      target.selectedItems = [...(target.items || [])];
    }
    if (target.selectedItems.includes(itemValue)) {
      target.selectedItems = target.selectedItems.filter(x => x !== itemValue);
    } else {
      target.selectedItems.push(itemValue);
    }
    target.checked = target.selectedItems.length > 0;
    setScanPlans(nextPlans);
  };

  const toggleAllTargets = (planIndex, checked) => {
    const nextPlans = [...scanPlans];
    nextPlans[planIndex].targets.forEach(t => {
      t.checked = checked;
      if (t.items) {
        t.selectedItems = checked ? [...t.items] : [];
      }
    });
    setScanPlans(nextPlans);
  };

  // Search & Filter target selectors
  const getFilteredTargets = (plan, planIndex) => {
    const search = (planSearch[planIndex] || '').toLowerCase();
    let targets = plan.targets || [];
    if (search) {
      targets = targets.filter(t => 
        (t.display_name || '').toLowerCase().includes(search) || 
        (t.service || '').toLowerCase().includes(search) || 
        (t.path || '').toLowerCase().includes(search)
      );
    }
    const sort = planSort[planIndex];
    if (sort === 'name') {
      targets = [...targets].sort((a, b) => (a.display_name || '').localeCompare(b.display_name || ''));
    } else if (sort === 'size') {
      targets = [...targets].sort((a, b) => (b.size_bytes || 0) - (a.size_bytes || 0));
    }
    return targets;
  };

  // Calculations for dynamic header sizes
  const getPlanSummary = (plan) => {
    const total = plan.targets.length;
    const selected = plan.targets.filter(t => t.checked).length;
    const size = plan.targets.reduce((sum, t) => sum + (t.checked ? (t.size_bytes || 0) : 0), 0);
    return `${selected} / ${total} selected (${formatBytes(size)})`;
  };

  const getTotalSavings = () => {
    return scanPlans.reduce((acc, plan) => {
      const planSize = plan.targets.reduce((sum, t) => sum + (t.checked ? (t.size_bytes || 0) : 0), 0);
      return acc + planSize;
    }, 0);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
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
            onClick={() => { fetchData(); if (activeTab === 'docker') fetchDockerData(true); }}
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
            <RefreshCw size={16} className={loading || dockerLoading ? "spin" : ""} />
            Refresh
          </button>
        </div>
      </header>

      {/* Main Tabs Navigation */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem' }}>
        <button 
          onClick={() => setActiveTab('operations')} 
          className={`tab-button ${activeTab === 'operations' ? 'active' : ''}`}
        >
          <Activity size={18} />
          Operations Dashboard
        </button>
        <button 
          onClick={() => setActiveTab('docker')} 
          className={`tab-button ${activeTab === 'docker' ? 'active' : ''}`}
        >
          <Server size={18} />
          Docker Manager
        </button>
      </div>

      {/* RENDER OPERATIONS DASHBOARD */}
      {activeTab === 'operations' && (
        <div>
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
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rollbacks.length === 0 ? (
                      <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No rollback history</td></tr>
                    ) : rollbacks.map((item, i) => (
                      <tr key={i}>
                        <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{(item.id || '').substring(0, 8)}</td>
                        <td style={{ fontWeight: 500 }}>{item.module}</td>
                        <td><span className="badge badge-info">{item.type}</span></td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{new Date(item.date).toLocaleString()}</td>
                        <td style={{ textAlign: 'right' }}>
                          <button
                            onClick={() => handleRollback(item.id)}
                            disabled={rollingBack !== null}
                            style={{
                              background: 'rgba(245, 158, 11, 0.15)',
                              border: '1px solid rgba(245, 158, 11, 0.3)',
                              color: '#f59e0b',
                              padding: '0.25rem 0.75rem',
                              borderRadius: '6px',
                              cursor: (rollingBack !== null) ? 'not-allowed' : 'pointer',
                              fontSize: '0.8rem',
                              fontWeight: 600,
                              transition: 'all 0.2s',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.25rem',
                              opacity: (rollingBack !== null) ? 0.5 : 1
                            }}
                            onMouseEnter={(e) => {
                              if (rollingBack === null) {
                                e.currentTarget.style.background = 'rgba(245, 158, 11, 0.25)';
                                e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.5)';
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (rollingBack === null) {
                                e.currentTarget.style.background = 'rgba(245, 158, 11, 0.15)';
                                e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.3)';
                              }
                            }}
                          >
                            <RotateCcw size={12} className={rollingBack === item.id ? "spin" : ""} />
                            {rollingBack === item.id ? 'Reverting...' : 'Rollback'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* RENDER DOCKER MANAGER */}
      {activeTab === 'docker' && (
        <div className="animate-fade-in">
          {/* Docker KPIs */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
            
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.25rem 0', fontSize: '0.85rem' }}>Containers</p>
              <h3 style={{ fontSize: '1.75rem', margin: 0 }}>
                {dockerData?.containers?.filter(c => c.State === 'running').length || 0}
                <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                  {' '}/ {dockerData?.containers?.length || 0} running
                </span>
              </h3>
            </div>

            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.25rem 0', fontSize: '0.85rem' }}>Images footprint</p>
              <h3 style={{ fontSize: '1.75rem', margin: 0, color: '#38bdf8' }}>
                {dockerData?.images?.reduce((acc, img) => {
                  // Sum up sizes (this is rough since size includes unit, but we display count as well)
                  return acc;
                }, 0) || ''}
                {dockerData?.images?.length || 0}
                <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                  {' '}images ({dockerData?.images?.filter(img => img.dangling).length || 0} dangling)
                </span>
              </h3>
            </div>

            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.25rem 0', fontSize: '0.85rem' }}>Volumes</p>
              <h3 style={{ fontSize: '1.75rem', margin: 0 }}>
                {dockerData?.volumes?.length || 0}
              </h3>
            </div>

            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.25rem 0', fontSize: '0.85rem' }}>Networks</p>
              <h3 style={{ fontSize: '1.75rem', margin: 0 }}>
                {dockerData?.networks?.length || 0}
              </h3>
            </div>

            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.25rem 0', fontSize: '0.85rem' }}>Build Cache footprint</p>
              <h3 style={{ fontSize: '1.75rem', margin: 0, color: 'var(--status-warning)' }}>
                {dockerData?.builder?.size || '0 B'}
              </h3>
            </div>

          </div>

          {/* Docker Sub Tab bar */}
          <div className="glass-panel" style={{ padding: '0.5rem 1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', gap: '1rem', background: 'rgba(255,255,255,0.01)' }}>
            <button onClick={() => setDockerSubTab('containers')} className={`sub-tab-button ${dockerSubTab === 'containers' ? 'active' : ''}`}>Containers</button>
            <button onClick={() => setDockerSubTab('images')} className={`sub-tab-button ${dockerSubTab === 'images' ? 'active' : ''}`}>Images</button>
            <button onClick={() => setDockerSubTab('volumes')} className={`sub-tab-button ${dockerSubTab === 'volumes' ? 'active' : ''}`}>Volumes</button>
            <button onClick={() => setDockerSubTab('networks')} className={`sub-tab-button ${dockerSubTab === 'networks' ? 'active' : ''}`}>Networks</button>
            <button onClick={() => setDockerSubTab('builds')} className={`sub-tab-button ${dockerSubTab === 'builds' ? 'active' : ''}`}>Build Cache</button>
          </div>

          {/* Docker Content Panels */}
          {dockerLoading ? (
            <div className="glass-panel animate-fade-in" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <RefreshCw className="spin" size={32} style={{ marginBottom: '1rem' }} />
              <p>Querying Docker daemon statistics...</p>
            </div>
          ) : (
            <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem', minHeight: '350px' }}>
              
              {/* CONTAINERS SUB-TAB */}
              {dockerSubTab === 'containers' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 style={{ margin: 0 }}>Active and Exited Containers</h3>
                    <button onClick={() => handleDockerClean('containers')} style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--status-error)', padding: '0.4rem 0.8rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>
                      Prune Stopped Containers
                    </button>
                  </div>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Status</th>
                          <th>Name</th>
                          <th>Image</th>
                          <th>Ports</th>
                          <th>CPU %</th>
                          <th>Memory Usage</th>
                          <th style={{ textAlign: 'right' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {!dockerData?.containers || dockerData.containers.length === 0 ? (
                          <tr><td colSpan="7" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No containers found</td></tr>
                        ) : dockerData.containers.map((c, i) => (
                          <tr key={i}>
                            <td>
                              {c.State === 'running' ? (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                  <span className="pulse-dot"></span>
                                  <span style={{ color: 'var(--status-success)', fontSize: '0.8rem', fontWeight: 600 }}>Running</span>
                                </div>
                              ) : (
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Stopped</span>
                              )}
                            </td>
                            <td style={{ fontWeight: 600 }}>{c.Names}</td>
                            <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{c.Image}</td>
                            <td style={{ fontSize: '0.8rem' }}>{c.Ports || '-'}</td>
                            <td style={{ fontFamily: 'monospace', color: c.cpu !== '0.00%' ? '#38bdf8' : 'inherit' }}>{c.cpu || '0.00%'}</td>
                            <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{c.memory || '0B / 0B'}</td>
                            <td style={{ textAlign: 'right' }}>
                              <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                                {c.State === 'running' ? (
                                  <button onClick={() => handleContainerAction('stop', c.ID, c.Names)} disabled={dockerActionLoading === c.ID} style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', color: 'var(--status-warning)', padding: '0.25rem 0.5rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                    <Square size={12} /> Stop
                                  </button>
                                ) : (
                                  <button onClick={() => handleContainerAction('start', c.ID, c.Names)} disabled={dockerActionLoading === c.ID} style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', color: 'var(--status-success)', padding: '0.25rem 0.5rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                    <Play size={12} /> Start
                                  </button>
                                )}
                                <button onClick={() => handleContainerAction('restart', c.ID, c.Names)} disabled={dockerActionLoading === c.ID} style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', color: 'var(--status-info)', padding: '0.25rem 0.5rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                  <RotateCw size={12} /> Restart
                                </button>
                                <button onClick={() => viewContainerLogs(c.ID, c.Names)} style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)', padding: '0.25rem 0.5rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                  <FileText size={12} /> Logs
                                </button>
                                <button onClick={() => handleContainerAction('remove', c.ID, c.Names)} disabled={dockerActionLoading === c.ID} style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--status-error)', padding: '0.25rem 0.5rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                  <Trash2 size={12} /> Remove
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* IMAGES SUB-TAB */}
              {dockerSubTab === 'images' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 style={{ margin: 0 }}>Docker Images</h3>
                    <button onClick={() => handleDockerClean('images')} style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--status-error)', padding: '0.4rem 0.8rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>
                      Prune Dangling Images
                    </button>
                  </div>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Image ID</th>
                          <th>Repository</th>
                          <th>Tag</th>
                          <th>Size</th>
                          <th>Created At</th>
                          <th style={{ textAlign: 'right' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {!dockerData?.images || dockerData.images.length === 0 ? (
                          <tr><td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No images found</td></tr>
                        ) : dockerData.images.map((img, i) => (
                          <tr key={i}>
                            <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{img.ID.substring(0, 12)}</td>
                            <td style={{ fontWeight: 600 }}>
                              {img.Repository}
                              {img.dangling && <span className="badge badge-warning" style={{ marginLeft: '0.5rem', fontSize: '0.65rem', padding: '2px 6px' }}>dangling</span>}
                            </td>
                            <td><span className="badge badge-info" style={{ textTransform: 'none' }}>{img.Tag}</span></td>
                            <td style={{ fontWeight: 500 }}>{img.Size}</td>
                            <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{img.CreatedAt}</td>
                            <td style={{ textAlign: 'right' }}>
                              <button onClick={() => handleRemoveImage(img.ID, img.Repository)} style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--status-error)', padding: '0.25rem 0.5rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                <Trash2 size={12} /> Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* VOLUMES SUB-TAB */}
              {dockerSubTab === 'volumes' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 style={{ margin: 0 }}>Local Storage Volumes</h3>
                    <button onClick={() => handleDockerClean('volumes')} style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--status-error)', padding: '0.4rem 0.8rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>
                      Prune Unused Volumes
                    </button>
                  </div>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Volume Name</th>
                          <th>Driver</th>
                        </tr>
                      </thead>
                      <tbody>
                        {!dockerData?.volumes || dockerData.volumes.length === 0 ? (
                          <tr><td colSpan="2" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No volumes found</td></tr>
                        ) : dockerData.volumes.map((vol, i) => (
                          <tr key={i}>
                            <td style={{ fontFamily: 'monospace', fontWeight: 500 }}>{vol.Name}</td>
                            <td><span className="badge badge-info">{vol.Driver}</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* NETWORKS SUB-TAB */}
              {dockerSubTab === 'networks' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 style={{ margin: 0 }}>Docker Networks</h3>
                    <button onClick={() => handleDockerClean('networks')} style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--status-error)', padding: '0.4rem 0.8rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>
                      Prune Unused Networks
                    </button>
                  </div>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Network ID</th>
                          <th>Name</th>
                          <th>Driver</th>
                          <th>Scope</th>
                        </tr>
                      </thead>
                      <tbody>
                        {!dockerData?.networks || dockerData.networks.length === 0 ? (
                          <tr><td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No networks found</td></tr>
                        ) : dockerData.networks.map((net, i) => (
                          <tr key={i}>
                            <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{net.ID.substring(0, 12)}</td>
                            <td style={{ fontWeight: 600 }}>{net.Name}</td>
                            <td><span className="badge badge-info">{net.Driver}</span></td>
                            <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{net.Scope}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* BUILD CACHE SUB-TAB */}
              {dockerSubTab === 'builds' && (
                <div>
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{ margin: 0, marginBottom: '0.5rem' }}>Build Cache Footprint</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Docker builder cache stores intermediate layers of builds that can be cleaned to reclaim disk space.</p>
                  </div>
                  
                  <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: '12px', padding: '2rem', textAlign: 'center', border: '1px solid var(--glass-border)', maxWidth: '500px', margin: '2rem auto' }}>
                    <HardDrive size={48} color="var(--status-warning)" style={{ marginBottom: '1rem' }} />
                    <h4 style={{ fontSize: '1.5rem', margin: '0 0 0.5rem 0' }}>{dockerData?.builder?.size || '0 B'}</h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                      Reclaimable Space: {dockerData?.builder?.reclaimable || '0B (0%)'} ({dockerData?.builder?.count || 0} cache items)
                    </p>
                    <button onClick={() => handleDockerClean('builder')} style={{ background: 'var(--accent-gradient)', border: 'none', color: '#fff', padding: '0.6rem 1.5rem', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, transition: 'all 0.2s' }}>
                      Prune Builder Cache
                    </button>
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      )}

      {/* SYSTEM SCAN RESULTS MODAL */}
      {scanModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '900px', maxWidth: '95%', padding: '2rem', display: 'flex', flexDirection: 'column', maxHeight: '90vh' }}>
            <h2 style={{ marginTop: 0, marginBottom: '1rem' }}>System Scan Results</h2>
            
            {scanning ? (
              <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-secondary)', flex: 1 }}>
                <Search size={54} className="spin" style={{ marginBottom: '1rem', color: 'var(--accent-primary)' }} />
                <p style={{ fontSize: '1.1rem', fontWeight: 500 }}>Analyzing system caches, packages, logs, and tempfiles...</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
                {scanPlans.length === 0 ? (
                  <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '4rem 0', flex: 1 }}>
                    No actionable cleanups found.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
                    <p style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)' }}>
                      Select the items you would like to delete or remove from each module:
                    </p>
                    
                    {/* ACCORDION MODULES LIST */}
                    <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem', marginBottom: '1.5rem' }}>
                      {scanPlans.map((plan, planIdx) => {
                        const isExpanded = !!expandedPlans[planIdx];
                        const searchVal = planSearch[planIdx] || '';
                        const sortVal = planSort[planIdx] || null;
                        const filteredTargets = getFilteredTargets(plan, planIdx);
                        const hasSelected = plan.targets.some(t => t.checked);
                        const allSelected = plan.targets.every(t => t.checked);

                        return (
                          <div key={planIdx} className="accordion-item">
                            
                            {/* ACCORDION HEADER */}
                            <div className="accordion-header">
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }} onClick={(e) => e.stopPropagation()}>
                                <input 
                                  type="checkbox" 
                                  checked={allSelected} 
                                  ref={el => {
                                    if (el) el.indeterminate = hasSelected && !allSelected;
                                  }}
                                  onChange={(e) => toggleAllTargets(planIdx, e.target.checked)}
                                  style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                                />
                                <span style={{ fontWeight: 600, fontSize: '1.1rem', textTransform: 'capitalize' }} onClick={() => setExpandedPlans({ ...expandedPlans, [planIdx]: !isExpanded })}>
                                  {plan.module}
                                </span>
                                <span className={`badge ${getRiskBadge(plan.risk_level)}`}>{plan.risk_level}</span>
                              </div>
                              
                              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }} onClick={() => setExpandedPlans({ ...expandedPlans, [planIdx]: !isExpanded })}>
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                  {getPlanSummary(plan)}
                                </span>
                                <button style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                                  {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                                </button>
                              </div>
                            </div>
                            
                            {/* ACCORDION BODY */}
                            {isExpanded && (
                              <div className="accordion-body">
                                
                                {/* Search and Toolbar */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', marginBottom: '1rem' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)', borderRadius: '6px', padding: '2px 8px', flex: 1, maxWidth: '300px' }}>
                                    <Search size={14} color="var(--text-secondary)" />
                                    <input 
                                      type="text" 
                                      placeholder="Filter files..." 
                                      value={searchVal}
                                      onChange={(e) => setPlanSearch({ ...planSearch, [planIdx]: e.target.value })}
                                      style={{ background: 'transparent', border: 'none', color: 'var(--text-primary)', outline: 'none', fontSize: '0.8rem', width: '100%' }}
                                    />
                                  </div>
                                  
                                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button 
                                      onClick={() => setPlanSort({ ...planSort, [planIdx]: sortVal === 'name' ? null : 'name' })}
                                      style={{ background: sortVal === 'name' ? 'rgba(255,255,255,0.1)' : 'transparent', border: '1px solid var(--glass-border)', borderRadius: '6px', color: 'var(--text-primary)', padding: '0.25rem 0.5rem', fontSize: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                                    >
                                      <ArrowUpDown size={12} /> Sort Name
                                    </button>
                                    <button 
                                      onClick={() => setPlanSort({ ...planSort, [planIdx]: sortVal === 'size' ? null : 'size' })}
                                      style={{ background: sortVal === 'size' ? 'rgba(255,255,255,0.1)' : 'transparent', border: '1px solid var(--glass-border)', borderRadius: '6px', color: 'var(--text-primary)', padding: '0.25rem 0.5rem', fontSize: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                                    >
                                      <ArrowUpDown size={12} /> Sort Size
                                    </button>
                                  </div>
                                </div>
                                
                                {/* Targets Table */}
                                <div style={{ maxHeight: '250px', overflowY: 'auto', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'rgba(0,0,0,0.1)' }}>
                                  <table style={{ minWidth: '100%' }}>
                                    <thead>
                                      <tr>
                                        <th style={{ width: '40px', padding: '8px 12px' }}></th>
                                        <th style={{ padding: '8px 12px' }}>Name / Location</th>
                                        <th style={{ padding: '8px 12px' }}>Origin</th>
                                        <th style={{ padding: '8px 12px', textAlign: 'right' }}>Size</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {filteredTargets.length === 0 ? (
                                        <tr><td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '1.5rem' }}>No matching items</td></tr>
                                      ) : filteredTargets.map((target, targetIdx) => {
                                        // Find index of target in original plan array to toggle correctly
                                        const origIdx = plan.targets.findIndex(t => t.id === target.id);
                                        
                                        return (
                                          <React.Fragment key={target.id}>
                                            <tr>
                                              <td style={{ padding: '10px 12px' }}>
                                                <input 
                                                  type="checkbox" 
                                                  checked={!!target.checked}
                                                  onChange={() => toggleTargetChecked(planIdx, origIdx)}
                                                  style={{ width: '15px', height: '15px', cursor: 'pointer' }}
                                                />
                                              </td>
                                              <td style={{ padding: '10px 12px', fontWeight: 500, maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={target.path || target.id}>
                                                {target.display_name || target.id}
                                              </td>
                                              <td style={{ padding: '10px 12px' }}>
                                                <span className={`service-badge service-badge-${target.service || 'generic'}`}>
                                                  {target.service || 'system'}
                                                </span>
                                              </td>
                                              <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'monospace', color: '#38bdf8' }}>
                                                {target.size_bytes ? formatBytes(target.size_bytes) : '-'}
                                              </td>
                                            </tr>
                                            
                                            {/* Sub-items (nested list e.g. packages / docker images) */}
                                            {target.checked && target.items && target.items.length > 0 && (
                                              <tr>
                                                <td></td>
                                                <td colSpan="3" style={{ padding: '0 12px 10px 12px', background: 'rgba(255,255,255,0.01)' }}>
                                                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '0.5rem', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.02)' }}>
                                                    {target.items.map((item, itemIdx) => {
                                                      const isChecked = !target.selectedItems || target.selectedItems.includes(item);
                                                      return (
                                                        <label key={itemIdx} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: isChecked ? 'var(--text-primary)' : 'var(--text-secondary)', cursor: 'pointer' }}>
                                                          <input 
                                                            type="checkbox" 
                                                            checked={isChecked}
                                                            onChange={() => toggleSubItemChecked(planIdx, origIdx, item)}
                                                            style={{ width: '13px', height: '13px' }}
                                                          />
                                                          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item}>{item}</span>
                                                        </label>
                                                      );
                                                    })}
                                                  </div>
                                                </td>
                                              </tr>
                                            )}
                                          </React.Fragment>
                                        );
                                      })}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            )}

                          </div>
                        );
                      })}
                    </div>
                    
                    {/* SAVINGS SUMMARY & CONTROL BUTTONS */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--glass-border)', paddingTop: '1.25rem' }}>
                      <div>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Total Selected Savings:</span>
                        <span style={{ marginLeft: '0.5rem', fontSize: '1.4rem', color: '#38bdf8', fontWeight: 'bold' }}>
                          {formatBytes(getTotalSavings())}
                        </span>
                      </div>
                      
                      <div style={{ display: 'flex', gap: '1rem' }}>
                        <button 
                          onClick={() => setScanModalOpen(false)}
                          disabled={enqueuing}
                          style={{ 
                            background: 'transparent', 
                            border: '1px solid var(--glass-border)', 
                            color: 'var(--text-primary)',
                            padding: '0.6rem 1.25rem',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: 500
                          }}
                        >
                          Cancel
                        </button>
                        <button 
                          onClick={handleEnqueueClick}
                          disabled={enqueuing || getTotalSavings() === 0}
                          style={{ 
                            background: 'var(--status-warning)', 
                            border: 'none', 
                            color: '#000',
                            fontWeight: 'bold',
                            padding: '0.6rem 1.75rem',
                            borderRadius: '8px',
                            cursor: (enqueuing || getTotalSavings() === 0) ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            opacity: (enqueuing || getTotalSavings() === 0) ? 0.6 : 1
                          }}
                        >
                          {enqueuing ? <RefreshCw size={16} className="spin" /> : null}
                          Approve & Enqueue
                        </button>
                      </div>
                    </div>

                  </div>
                )}
              </div>
            )}

          </div>
        </div>
      )}

      {/* DOCKER CONTAINER LOGS SCREEN OVERLAY */}
      {dockerLogsContainer && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1100
        }}>
          <div className="glass-panel" style={{ width: '800px', maxWidth: '90%', padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '550px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={18} color="var(--accent-secondary)" />
                Container Logs: {dockerLogsContainer}
              </h3>
              <button 
                onClick={() => setDockerLogsContainer(null)} 
                style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.5rem' }}
              >&times;</button>
            </div>
            
            <div className="console-log-box" style={{ flex: 1 }}>
              {dockerLogsLoading ? 'Loading logs...' : dockerLogsText}
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
              <button onClick={() => setDockerLogsContainer(null)} style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)', padding: '0.5rem 1.25rem', borderRadius: '6px', cursor: 'pointer' }}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI ADVISORY MODAL */}
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
