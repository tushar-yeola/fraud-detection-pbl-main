import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, ShieldAlert, List, Search, UploadCloud, BarChart2, Cpu, Shield, Menu, X } from 'lucide-react'
import Dashboard from './pages/Dashboard.jsx'
import Analytics from './pages/Analytics.jsx'
import Transactions from './pages/Transactions.jsx'
import CheckTransaction from './pages/CheckTransaction.jsx'
import BatchUpload from './pages/BatchUpload.jsx'
import Alerts from './pages/Alerts.jsx'
import ModelInfo from './pages/ModelInfo.jsx'

const NAV = [
  { label: 'Overview', section: true },
  { to: '/', icon: <LayoutDashboard size={16}/>, label: 'Dashboard' },
  { to: '/analytics', icon: <BarChart2 size={16}/>, label: 'Analytics' },
  { label: 'Transactions', section: true },
  { to: '/transactions', icon: <List size={16}/>, label: 'All Transactions' },
  { to: '/check', icon: <Search size={16}/>, label: 'Check Transaction' },
  { to: '/batch', icon: <UploadCloud size={16}/>, label: 'Batch Upload' },
  { label: 'Monitoring', section: true },
  { to: '/alerts', icon: <ShieldAlert size={16}/>, label: 'Fraud Alerts', badge: true },
  { to: '/model', icon: <Cpu size={16}/>, label: 'Model Info' },
]

function PageTitle() {
  const loc = useLocation()
  const map = {
    '/': 'Dashboard', '/analytics': 'Analytics', '/transactions': 'Transactions',
    '/check': 'Check Transaction', '/batch': 'Batch Upload',
    '/alerts': 'Fraud Alerts', '/model': 'Model Info'
  }
  return <span>{map[loc.pathname] || 'TransactGuard'}</span>
}

function Sidebar({ alertCount, isOpen, onClose }) {
  const loc = useLocation()
  
  React.useEffect(() => {
    onClose()
  }, [loc.pathname])

  return (
    <>
      <div className={`sidebar-overlay ${isOpen ? 'show' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
        <div className="logo-icon">🛡️</div>
        <div>
          <div className="logo-text">TransactGuard</div>
          <div className="logo-sub">AI Fraud Detection</div>
        </div>
      </div>
      <nav className="sidebar-nav">
        {NAV.map((item, i) =>
          item.section ? (
            <div key={i} className="nav-section">{item.label}</div>
          ) : (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
              {item.badge && alertCount > 0 && <span className="nav-badge">{alertCount}</span>}
            </NavLink>
          )
        )}
      </nav>
      <div className="sidebar-footer">
        <div style={{ fontSize: '11px', color: 'var(--text-sidebar-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <div className="status-dot" />
          <span style={{ color: '#64748b' }}>API Connected</span>
        </div>
        </div>
      </aside>
    </>
  )
}

export default function App() {
  const [alertCount, setAlertCount] = React.useState(0)
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false)

  React.useEffect(() => {
    fetch('/api/alerts?resolved=false&limit=1')
      .then(r => r.json())
      .then(d => setAlertCount(d.total || 0))
      .catch(() => {})
  }, [])

  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar alertCount={alertCount} isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        <div className="main-content">
          <header className="top-bar">
            <button className="mobile-menu-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
              <Menu size={20} />
            </button>
            <Shield size={20} className="desktop-shield-icon" style={{ color: 'var(--accent-blue)' }} />
            <div className="top-bar-title">
              <PageTitle />
              <span className="top-bar-subtitle">Banking Fraud Detection System</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div className="status-dot" />
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Live</span>
            </div>
          </header>
          <main className="page-content fade-in">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/check" element={<CheckTransaction />} />
              <Route path="/batch" element={<BatchUpload />} />
              <Route path="/alerts" element={<Alerts onCountChange={setAlertCount} />} />
              <Route path="/model" element={<ModelInfo />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

import React from 'react'
