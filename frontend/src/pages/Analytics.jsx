import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area
} from 'recharts'
import axios from 'axios'

const COLORS = ['#3b82f6','#ef4444','#10b981','#f59e0b','#8b5cf6','#06b6d4','#ec4899']

const CT = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '10px 14px', boxShadow: '0 4px 16px rgba(15,23,42,0.10)' }}>
      <div style={{ color: '#64748b', fontSize: 12, marginBottom: 6 }}>{label}</div>
      {payload.map(p => <div key={p.name} style={{ color: p.color, fontSize: 13, fontWeight: 600 }}>{p.name}: {p.value}</div>)}
    </div>
  )
}

export default function Analytics() {
  const [channel, setChannel] = useState([])
  const [occupation, setOccupation] = useState([])
  const [location, setLocation] = useState([])
  const [amtDist, setAmtDist] = useState([])
  const [risk, setRisk] = useState([])
  const [hourly, setHourly] = useState([])
  const [txType, setTxType] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get('/api/analytics/fraud-by-channel'),
      axios.get('/api/analytics/fraud-by-occupation'),
      axios.get('/api/analytics/fraud-by-location'),
      axios.get('/api/analytics/amount-distribution'),
      axios.get('/api/analytics/risk-distribution'),
      axios.get('/api/analytics/hourly-trend'),
      axios.get('/api/analytics/transaction-type-split'),
    ]).then(([ch, oc, lo, am, rk, hr, tx]) => {
      setChannel(ch.data); setOccupation(oc.data); setLocation(lo.data)
      setAmtDist(am.data); setRisk(rk.data); setHourly(hr.data); setTxType(tx.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="spinner" /></div>

  const riskColors = { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#10b981' }

  return (
    <div className="fade-in">
      <div className="charts-grid" style={{ marginBottom: 24 }}>
        {/* Channel Fraud */}
        <div className="card">
          <div className="card-header"><span className="card-title">Fraud by Channel</span></div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={channel} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="channel" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CT />} />
              <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
              <Bar dataKey="total" fill="#3b82f6" name="Total" radius={[4,4,0,0]} />
              <Bar dataKey="fraud" fill="#ef4444" name="Fraud" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Occupation Fraud */}
        <div className="card">
          <div className="card-header"><span className="card-title">Fraud by Occupation</span></div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={occupation} layout="vertical" margin={{ left: 30, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="occupation" type="category" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} width={70} />
              <Tooltip content={<CT />} />
              <Bar dataKey="fraud" fill="#8b5cf6" name="Fraud" radius={[0,4,4,0]} />
              <Bar dataKey="total" fill="#bfdbfe" name="Total" radius={[0,4,4,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="charts-grid" style={{ marginBottom: 24 }}>
        {/* Amount Distribution */}
        <div className="card">
          <div className="card-header"><span className="card-title">Amount Distribution</span></div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={amtDist} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="range" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CT />} />
              <Bar dataKey="total" fill="#06b6d4" name="Total" radius={[4,4,0,0]} />
              <Bar dataKey="fraud" fill="#ef4444" name="Fraud" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution Pie */}
        <div className="card">
          <div className="card-header"><span className="card-title">Risk Level Distribution</span></div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={risk} dataKey="count" nameKey="risk_level" cx="50%" cy="50%" outerRadius={80}
                label={({ risk_level, count }) => `${risk_level}: ${count}`} labelLine={{ stroke: 'var(--text-muted)' }}>
                {risk.map(r => <Cell key={r.risk_level} fill={riskColors[r.risk_level] || '#3b82f6'} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, boxShadow: '0 4px 16px rgba(15,23,42,0.10)' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hourly Trend */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header"><span className="card-title">Hourly Transaction & Fraud Pattern</span></div>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={hourly} margin={{ left: -20 }}>
            <defs>
              <linearGradient id="h1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/><stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="h2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/><stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,155,255,0.08)" />
            <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} interval={3} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CT />} />
            <Area type="monotone" dataKey="total" stroke="#3b82f6" fill="url(#h1)" strokeWidth={2} name="Total" />
            <Area type="monotone" dataKey="fraud" stroke="#ef4444" fill="url(#h2)" strokeWidth={2} name="Fraud" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="charts-grid wide" style={{ '--charts-wide': '1fr 1fr' }}>
        {/* Transaction Type */}
        <div className="card">
          <div className="card-header"><span className="card-title">Transaction Type Split</span></div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={txType} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="type" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CT />} />
              <Bar dataKey="total" fill="#10b981" name="Total" radius={[4,4,0,0]} />
              <Bar dataKey="fraud" fill="#ef4444" name="Fraud" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Locations */}
        <div className="card">
          <div className="card-header"><span className="card-title">Top Locations by Fraud</span></div>
          <div className="table-wrap" style={{ maxHeight: 200, overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr><th>Location</th><th>Total</th><th>Fraud</th><th>Fraud %</th></tr>
              </thead>
              <tbody>
                {location.slice(0,10).map((l, i) => (
                  <tr key={i}>
                    <td style={{ color: 'var(--text-primary)' }}>{l.location}</td>
                    <td>{l.total}</td>
                    <td style={{ color: 'var(--accent-red)', fontWeight: 600 }}>{l.fraud}</td>
                    <td>
                      <span className={`badge ${l.fraud/l.total > 0.15 ? 'high' : l.fraud/l.total > 0.08 ? 'medium' : 'low'}`}>
                        {l.total > 0 ? ((l.fraud / l.total) * 100).toFixed(1) : 0}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
