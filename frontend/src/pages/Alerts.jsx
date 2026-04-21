import { useState, useEffect } from 'react'
import { ShieldAlert, ShieldCheck, MapPin, Users, Clock, DollarSign } from 'lucide-react'
import axios from 'axios'

export default function Alerts({ onCountChange }) {
  const [data, setData] = useState({ items: [], total: 0 })
  const [page, setPage] = useState(1)
  const [showResolved, setShowResolved] = useState(false)
  const [loading, setLoading] = useState(true)
  const [resolving, setResolving] = useState(null)

  const load = () => {
    setLoading(true)
    axios.get(`/api/alerts?resolved=${showResolved}&page=${page}&limit=15`)
      .then(r => {
        setData(r.data)
        if (!showResolved) onCountChange?.(r.data.total)
        setLoading(false)
      }).catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [page, showResolved])

  const resolve = async (txId) => {
    setResolving(txId)
    await axios.patch(`/api/alerts/${txId}/resolve`)
    await load()
    setResolving(null)
  }

  const riskStyle = { HIGH: 'var(--accent-red)', MEDIUM: 'var(--accent-orange)', LOW: 'var(--accent-green)' }

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            id="btn-active-alerts"
            className={`btn ${!showResolved ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => { setShowResolved(false); setPage(1) }}
          >
            <ShieldAlert size={14} /> Active ({!showResolved ? data.total : '?'})
          </button>
          <button
            id="btn-resolved-alerts"
            className={`btn ${showResolved ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => { setShowResolved(true); setPage(1) }}
          >
            <ShieldCheck size={14} /> Resolved
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading"><div className="spinner" /></div>
      ) : data.items.length === 0 ? (
        <div className="empty-state">
          <ShieldCheck size={48} />
          <div>{showResolved ? 'No resolved alerts' : '🎉 No active fraud alerts!'}</div>
        </div>
      ) : (
        <>
          {data.items.map(a => (
            <div key={a.transaction_id} className={`alert-card${a.is_resolved ? ' resolved' : ''}`}>
              <div style={{
                width: 48, height: 48, borderRadius: 12, flexShrink: 0,
                background: `rgba(${a.risk_level === 'HIGH' ? '239,68,68' : a.risk_level === 'MEDIUM' ? '245,158,11' : '16,185,129'},0.15)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <ShieldAlert size={22} style={{ color: riskStyle[a.risk_level] }} />
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                  <span style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--text-secondary)' }}>
                    {a.transaction_id.slice(0, 22)}...
                  </span>
                  <span className={`badge ${a.risk_level?.toLowerCase()}`}>{a.risk_level} RISK</span>
                  {a.is_reviewed && <span className="badge safe">Reviewed</span>}
                </div>
                <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
                  {[
                    [<DollarSign size={12}/>, `$${a.amount?.toFixed(2)}`],
                    [<Users size={12}/>, a.customer_occupation],
                    [<MapPin size={12}/>, a.location],
                    [<Clock size={12}/>, `${a.login_attempts} login attempts`],
                  ].map(([icon, text], i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'var(--text-secondary)' }}>
                      {icon} {text}
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8, flexShrink: 0 }}>
                <div style={{ fontSize: 18, fontWeight: 800, color: riskStyle[a.risk_level] }}>
                  {(a.fraud_probability * 100).toFixed(1)}%
                </div>
                {!a.is_resolved && (
                  <button
                    className="btn btn-success"
                    style={{ fontSize: 11, padding: '5px 12px' }}
                    disabled={resolving === a.transaction_id}
                    onClick={() => resolve(a.transaction_id)}
                  >
                    {resolving === a.transaction_id ? 'Resolving...' : '✓ Resolve'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  )
}
