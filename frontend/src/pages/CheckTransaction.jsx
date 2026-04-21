import { useState } from 'react'
import { Send, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react'
import axios from 'axios'

const DEFAULTS = {
  AccountID: 'ACC12345',
  TransactionAmount: '',
  TransactionDate: new Date().toISOString().slice(0, 16),
  TransactionType: 'Debit',
  Location: 'New York',
  AccountBalance: '',
  PreviousTransactionDate: '',
  Channel: 'Online',
  CustomerAge: 35,
  CustomerOccupation: 'Engineer',
  TransactionDuration: 120,
  LoginAttempts: 1,
}

function GaugeDisplay({ probability }) {
  const pct = Math.round(probability * 100)
  const color = pct >= 50 ? '#ef4444' : pct >= 30 ? '#f59e0b' : '#10b981'
  const angle = -90 + (pct / 100) * 180

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <svg width={180} height={100} style={{ overflow: 'visible' }}>
        <path d="M 20 90 A 70 70 0 0 1 160 90" fill="none" stroke="#e2e8f0" strokeWidth={14} strokeLinecap="round" />
        <path d="M 20 90 A 70 70 0 0 1 160 90" fill="none" stroke={color} strokeWidth={14}
          strokeLinecap="round"
          strokeDasharray={`${(pct / 100) * 220} 220`} />
        <g transform={`rotate(${angle}, 90, 90)`}>
          <line x1={90} y1={90} x2={90} y2={30} stroke={color} strokeWidth={3} strokeLinecap="round" />
          <circle cx={90} cy={90} r={5} fill={color} />
        </g>
        <text x={90} y={75} textAnchor="middle" fill={color} fontSize={22} fontWeight={800}>{pct}%</text>
        <text x={20} y={108} textAnchor="middle" fill="#4b6080" fontSize={10}>LOW</text>
        <text x={90} y={25} textAnchor="middle" fill="#4b6080" fontSize={10}>MED</text>
        <text x={160} y={108} textAnchor="middle" fill="#4b6080" fontSize={10}>HIGH</text>
      </svg>
      <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Fraud Probability</div>
    </div>
  )
}

export default function CheckTransaction() {
  const [form, setForm] = useState(DEFAULTS)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async () => {
    if (!form.TransactionAmount || !form.AccountBalance) {
      setError('Transaction Amount and Account Balance are required.')
      return
    }
    setError(''); setLoading(true); setResult(null)
    try {
      const r = await axios.post('/api/transactions/predict', {
        ...form,
        TransactionAmount: parseFloat(form.TransactionAmount),
        AccountBalance: parseFloat(form.AccountBalance),
        CustomerAge: parseInt(form.CustomerAge),
        TransactionDuration: parseInt(form.TransactionDuration),
        LoginAttempts: parseInt(form.LoginAttempts),
      })
      setResult(r.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Prediction failed. Is the backend running?')
    }
    setLoading(false)
  }

  return (
    <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 20, alignItems: 'start' }}>
      <div className="card">
        <div className="card-header">
          <span className="card-title">Transaction Details</span>
        </div>

        {error && (
          <div style={{ background: '#fff1f2', border: '1px solid rgba(220,38,38,0.25)', borderRadius: 8, padding: '10px 14px', marginBottom: 16, color: '#dc2626', fontSize: 13 }}>
            {error}
          </div>
        )}

        <div className="form-grid">
          {[
            ['Account ID', 'AccountID', 'text'],
            ['Transaction Amount ($)', 'TransactionAmount', 'number'],
            ['Account Balance ($)', 'AccountBalance', 'number'],
            ['Customer Age', 'CustomerAge', 'number'],
            ['Transaction Duration (sec)', 'TransactionDuration', 'number'],
            ['Login Attempts', 'LoginAttempts', 'number'],
          ].map(([label, key, type]) => (
            <div className="form-group" key={key}>
              <label className="form-label">{label}</label>
              <input
                id={`field-${key}`}
                className="form-input" type={type} value={form[key]}
                onChange={e => set(key, e.target.value)}
                min={type === 'number' ? 0 : undefined}
              />
            </div>
          ))}
        </div>

        <div className="form-grid" style={{ marginTop: 14 }}>
          {[
            ['Transaction Type', 'TransactionType', ['Credit', 'Debit']],
            ['Channel', 'Channel', ['Online', 'ATM', 'Branch']],
            ['Occupation', 'CustomerOccupation', ['Doctor', 'Engineer', 'Student', 'Retired', 'Other']],
          ].map(([label, key, opts]) => (
            <div className="form-group" key={key}>
              <label className="form-label">{label}</label>
              <select id={`field-${key}`} className="form-input" value={form[key]} onChange={e => set(key, e.target.value)}>
                {opts.map(o => <option key={o}>{o}</option>)}
              </select>
            </div>
          ))}

          <div className="form-group">
            <label className="form-label">Location</label>
            <input id="field-Location" className="form-input" value={form.Location} onChange={e => set('Location', e.target.value)} />
          </div>

          <div className="form-group">
            <label className="form-label">Transaction Date</label>
            <input id="field-TransactionDate" className="form-input" type="datetime-local" value={form.TransactionDate} onChange={e => set('TransactionDate', e.target.value)} />
          </div>

          <div className="form-group">
            <label className="form-label">Previous Transaction Date</label>
            <input id="field-PreviousTransactionDate" className="form-input" type="datetime-local" value={form.PreviousTransactionDate} onChange={e => set('PreviousTransactionDate', e.target.value)} />
          </div>
        </div>

        <div style={{ marginTop: 20, display: 'flex', gap: 10 }}>
          <button id="btn-predict" className="btn btn-primary" onClick={submit} disabled={loading} style={{ flex: 1 }}>
            {loading ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analyzing...</> : <><Send size={15} /> Analyze Transaction</>}
          </button>
          <button className="btn btn-ghost" onClick={() => { setForm(DEFAULTS); setResult(null); setError('') }}>Reset</button>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><span className="card-title">Analysis Result</span></div>

        {!result ? (
          <div className="empty-state" style={{ padding: '40px 20px' }}>
            <ShieldAlert size={40} style={{ opacity: 0.3, color: 'var(--accent-blue)' }} />
            <div style={{ fontSize: 13, color: 'var(--text-muted)', textAlign: 'center' }}>
              Fill in the form and click Analyze to get a fraud prediction.
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <GaugeDisplay probability={result.fraud_probability} />

            <div style={{
              background: result.is_fraud ? '#fff1f2' : '#ecfdf5',
              border: `1px solid ${result.is_fraud ? 'rgba(220,38,38,0.25)' : 'rgba(5,150,105,0.25)'}`,
              borderRadius: 10, padding: '16px',
              display: 'flex', alignItems: 'center', gap: 12,
            }}>
              {result.is_fraud
                ? <AlertTriangle size={24} style={{ color: 'var(--accent-red)', flexShrink: 0 }} />
                : <CheckCircle size={24} style={{ color: 'var(--accent-green)', flexShrink: 0 }} />}
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: result.is_fraud ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                  {result.is_fraud ? 'FRAUD DETECTED' : 'TRANSACTION SAFE'}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
                  {result.is_fraud ? 'This transaction shows fraud indicators.' : 'No suspicious patterns detected.'}
                </div>
              </div>
            </div>

            {(result.fraud_reasons && result.fraud_reasons.length > 0) && (
              <div style={{ padding: '14px', background: 'var(--accent-red-faint)', borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                <div style={{ color: 'var(--accent-red)', fontSize: 13, fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <ShieldAlert size={14} /> Risk Factors Identified:
                </div>
                <ul style={{ margin: 0, paddingLeft: 22, fontSize: 12, color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {result.fraud_reasons.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            )}

            <div>
              {[
                ['Risk Level', <span className={`badge ${result.risk_level?.toLowerCase()}`}>{result.risk_level}</span>],
                ['Fraud Probability', `${(result.fraud_probability * 100).toFixed(2)}%`],
                ['Random Forest', `${(result.rf_probability * 100).toFixed(2)}%`],
                ['Logistic Regression', `${(result.lr_probability * 100).toFixed(2)}%`],
                ['Transaction ID', <span style={{ fontFamily: 'monospace', fontSize: 10 }}>{result.transaction_id?.slice(0, 20)}...</span>],
              ].map(([k, v]) => (
                <div key={k} className="metric-row">
                  <span className="metric-name">{k}</span>
                  <span className="metric-val">{v}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
