import { useState, useEffect } from 'react'
import {
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { TrendingUp, AlertTriangle, DollarSign, Shield, Activity, Clock } from 'lucide-react'
import axios from 'axios'

const COLORS = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']

function KpiCard({ label, value, sub, color, icon }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '10px 14px', boxShadow: '0 4px 16px rgba(15,23,42,0.10)' }}>
      <div style={{ color: '#64748b', fontSize: 12, marginBottom: 6 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ color: p.color, fontSize: 13, fontWeight: 600 }}>
          {p.name}: {p.value}
        </div>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [channelData, setChannelData] = useState([])
  const [txns, setTxns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get('/api/dashboard/stats'),
      axios.get('/api/analytics/fraud-by-channel'),
      axios.get('/api/transactions?limit=8'),
    ]).then(([s, c, t]) => {
      setStats(s.data)
      setChannelData(c.data)
      setTxns(t.data.items || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="spinner" /></div>

  const s = stats || {}
  const fraudPct = s.fraud_rate ?? 0

  return (
    <div className="fade-in">
      <div className="kpi-grid">
        <KpiCard label="Total Transactions" value={s.total_transactions?.toLocaleString() ?? 0}
          sub="All time" color="blue" icon={<Activity size={20}/>} />
        <KpiCard label="Fraud Detected" value={s.fraud_count?.toLocaleString() ?? 0}
          sub={`${fraudPct}% fraud rate`} color="red" icon={<AlertTriangle size={20}/>} />
        <KpiCard label="Total Volume" value={`$${(s.total_amount ?? 0).toLocaleString(undefined, {maximumFractionDigits:0})}`}
          sub="Transaction amount" color="green" icon={<DollarSign size={20}/>} />
        <KpiCard label="Amount at Risk" value={`$${(s.fraud_amount ?? 0).toLocaleString(undefined, {maximumFractionDigits:0})}`}
          sub="Fraudulent transactions" color="orange" icon={<TrendingUp size={20}/>} />
        <KpiCard label="High Risk" value={s.high_risk_count ?? 0}
          sub="Flagged transactions" color="purple" icon={<Shield size={20}/>} />
        <KpiCard label="Unresolved Alerts" value={s.unresolved_alerts ?? 0}
          sub="Require attention" color="red" icon={<Clock size={20}/>} />
      </div>

      <div className="charts-grid wide" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">Transaction & Fraud Trend (7 days)</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={s.trend ?? []} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
              <Area type="monotone" dataKey="total" stroke="#3b82f6" fill="url(#totalGrad)" strokeWidth={2} name="Total" />
              <Area type="monotone" dataKey="fraud" stroke="#ef4444" fill="url(#fraudGrad)" strokeWidth={2} name="Fraud" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Fraud by Channel</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={channelData} dataKey="fraud" nameKey="channel" cx="50%" cy="50%" outerRadius={80} label={({channel, fraud})=>`${channel}: ${fraud}`} labelLine={{ stroke: 'var(--text-muted)' }}>
                {channelData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v, name) => [v, name]} contentStyle={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, boxShadow: '0 4px 16px rgba(15,23,42,0.10)' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">Recent Transactions</span>
          <a href="/transactions" style={{ fontSize: 12, color: 'var(--accent-blue)' }}>View all →</a>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Transaction ID</th><th>Account</th><th>Amount</th>
                <th>Channel</th><th>Location</th><th>Risk</th><th>Status</th><th>Flags</th>
              </tr>
            </thead>
            <tbody>
              {txns.map(t => (
                <tr key={t.transaction_id}>
                  <td style={{ color: 'var(--text-primary)', fontFamily: 'monospace', fontSize: 11 }}>{t.transaction_id.slice(0,14)}...</td>
                  <td>{t.account_id}</td>
                  <td style={{ color: 'var(--accent-green)', fontWeight: 600 }}>${t.amount?.toFixed(2)}</td>
                  <td>{t.channel}</td>
                  <td>{t.location}</td>
                  <td><span className={`badge ${t.risk_level?.toLowerCase()}`}>{t.risk_level}</span></td>
                  <td><span className={`badge ${t.is_fraud ? 'fraud' : 'safe'}`}>{t.is_fraud ? '⚠ Fraud' : '✓ Safe'}</span></td>
                  <td style={{ fontSize: 11, color: 'var(--accent-orange)' }}>{t.fraud_reasons?.length ? t.fraud_reasons.join(', ') : '-'}</td>
                </tr>
              ))}
              {txns.length === 0 && (
                <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 30 }}>
                  No transactions yet. Use "Check Transaction" to add some!
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
