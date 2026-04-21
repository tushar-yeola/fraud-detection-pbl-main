import { useState, useEffect, useCallback } from 'react'
import { Search, Filter, RefreshCw } from 'lucide-react'
import axios from 'axios'

export default function Transactions() {
  const [data, setData] = useState({ items: [], total: 0, pages: 1 })
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [fraudFilter, setFraudFilter] = useState('')
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(() => {
    setLoading(true)
    const params = new URLSearchParams({ page, limit: 20 })
    if (search) params.append('search', search)
    if (riskFilter) params.append('risk_level', riskFilter)
    if (fraudFilter !== '') params.append('is_fraud', fraudFilter)
    axios.get(`/api/transactions?${params}`)
      .then(r => { setData(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [page, search, riskFilter, fraudFilter])

  useEffect(() => { fetch() }, [fetch])

  const pages = Array.from({ length: Math.min(data.pages, 7) }, (_, i) => i + 1)

  return (
    <div className="fade-in">
      <div className="card">
        <div className="card-header">
          <span className="card-title">All Transactions ({data.total.toLocaleString()})</span>
          <div style={{ display: 'flex', gap: 10 }}>
            <div className="search-bar">
              <Search size={14} style={{ color: 'var(--text-muted)' }} />
              <input
                id="tx-search"
                placeholder="Search by ID, account, location..."
                value={search}
                onChange={e => { setSearch(e.target.value); setPage(1) }}
              />
            </div>
            <select
              id="tx-filter-risk"
              className="form-input" style={{ padding: '8px 12px', fontSize: 12 }}
              value={riskFilter} onChange={e => { setRiskFilter(e.target.value); setPage(1) }}
            >
              <option value="">All Risk</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
            <select
              id="tx-filter-status"
              className="form-input" style={{ padding: '8px 12px', fontSize: 12 }}
              value={fraudFilter} onChange={e => { setFraudFilter(e.target.value); setPage(1) }}
            >
              <option value="">All Status</option>
              <option value="true">Fraud</option>
              <option value="false">Safe</option>
            </select>
            <button className="btn btn-ghost" onClick={fetch}>
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner" /></div>
        ) : (
          <>
            <div className="table-wrap">
              <table id="transactions-table" className="data-table">
                <thead>
                  <tr>
                    <th>ID</th><th>Account</th><th>Amount</th><th>Type</th>
                    <th>Channel</th><th>Location</th><th>Login Attempts</th>
                    <th>Risk</th><th>Status</th><th>Probability</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map(t => (
                    <tr key={t.transaction_id}>
                      <td style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--text-muted)' }}>
                        {t.transaction_id.slice(0, 12)}...
                      </td>
                      <td style={{ color: 'var(--text-primary)' }}>{t.account_id}</td>
                      <td style={{ color: 'var(--accent-green)', fontWeight: 600 }}>${t.amount?.toFixed(2)}</td>
                      <td>{t.transaction_type}</td>
                      <td>{t.channel}</td>
                      <td>{t.location}</td>
                      <td style={{ textAlign: 'center' }}>
                        <span style={{ color: t.login_attempts >= 3 ? 'var(--accent-red)' : 'var(--text-secondary)', fontWeight: t.login_attempts >= 3 ? 700 : 400 }}>
                          {t.login_attempts}
                        </span>
                      </td>
                      <td><span className={`badge ${t.risk_level?.toLowerCase()}`}>{t.risk_level}</span></td>
                      <td><span className={`badge ${t.is_fraud ? 'fraud' : 'safe'}`}>{t.is_fraud ? '⚠ Fraud' : '✓ Safe'}</span></td>
                      <td>
                        <div style={{ minWidth: 80 }}>
                          <div style={{ fontSize: 11, color: t.is_fraud ? 'var(--accent-red)' : 'var(--accent-green)' , fontWeight: 600 }}>
                            {(t.fraud_probability * 100).toFixed(1)}%
                          </div>
                          <div className="prob-bar">
                            <div className={`prob-fill ${t.risk_level?.toLowerCase()}`}
                              style={{ width: `${t.fraud_probability * 100}%` }} />
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {data.items.length === 0 && (
                    <tr><td colSpan={10} style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
                      No transactions found.
                    </td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {data.pages > 1 && (
              <div className="pagination">
                <button className="page-btn" onClick={() => setPage(p => Math.max(1, p-1))} disabled={page === 1}>‹</button>
                {pages.map(p => (
                  <button key={p} className={`page-btn ${p === page ? 'active' : ''}`} onClick={() => setPage(p)}>{p}</button>
                ))}
                <button className="page-btn" onClick={() => setPage(p => Math.min(data.pages, p+1))} disabled={page === data.pages}>›</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
