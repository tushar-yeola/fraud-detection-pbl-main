import { useState, useRef } from 'react'
import { UploadCloud, FileText, CheckCircle, AlertTriangle, Download } from 'lucide-react'
import axios from 'axios'

export default function BatchUpload() {
  const [drag, setDrag] = useState(false)
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const ref = useRef()

  const handleFile = f => {
    if (!f?.name.endsWith('.csv')) { setError('Please upload a CSV file.'); return }
    setFile(f); setError(''); setResult(null)
  }

  const upload = async () => {
    if (!file) { setError('Please select a file first.'); return }
    setLoading(true); setError('')
    const fd = new FormData()
    fd.append('file', file)
    try {
      const r = await axios.post('/api/predict/batch', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(r.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Upload failed.')
    }
    setLoading(false)
  }

  const downloadResults = () => {
    if (!result) return
    const rows = [['Row', 'IsFraud', 'FraudProbability', 'RFProb', 'LRProb', 'RiskLevel'],
      ...result.results.map(r => [r.row, r.is_fraud ? 1 : 0, r.fraud_probability, r.rf_probability, r.lr_probability, r.risk_level])]
    const csv = rows.map(r => r.join(',')).join('\n')
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
    a.download = 'fraud_predictions.csv'
    a.click()
  }

  return (
    <div className="fade-in">
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header"><span className="card-title">Batch CSV Upload</span></div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
          Upload a CSV with transaction columns matching the training data format.
          Results will be saved to the database and downloadable.
        </p>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, padding: '10px 14px', marginBottom: 14, color: 'var(--accent-red)', fontSize: 13 }}>
            {error}
          </div>
        )}

        <div
          id="upload-zone"
          className={`upload-zone${drag ? ' drag-over' : ''}`}
          onClick={() => ref.current?.click()}
          onDragOver={e => { e.preventDefault(); setDrag(true) }}
          onDragLeave={() => setDrag(false)}
          onDrop={e => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]) }}
        >
          <UploadCloud size={40} style={{ color: 'var(--accent-blue)', opacity: 0.6, marginBottom: 12 }} />
          <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
            {file ? file.name : 'Drop your CSV here or click to browse'}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Supports: .csv files with transaction data</div>
          <input ref={ref} type="file" accept=".csv" style={{ display: 'none' }} onChange={e => handleFile(e.target.files[0])} />
        </div>

        <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
          <button id="btn-upload" className="btn btn-primary" onClick={upload} disabled={loading || !file} style={{ flex: 1 }}>
            {loading
              ? <><div className="spinner" style={{ width: 15, height: 15, borderWidth: 2 }} /> Processing...</>
              : <><FileText size={15} /> Run Fraud Detection</>}
          </button>
          {result && (
            <button className="btn btn-ghost" onClick={downloadResults}><Download size={14} /> Download Results</button>
          )}
        </div>
      </div>

      {result && (
        <div className="fade-in">
          <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 20 }}>
            <div className="kpi-card blue">
              <div className="kpi-label">Total Processed</div>
              <div className="kpi-value">{result.total.toLocaleString()}</div>
            </div>
            <div className="kpi-card red">
              <div className="kpi-label">Fraud Detected</div>
              <div className="kpi-value">{result.fraud_detected.toLocaleString()}</div>
            </div>
            <div className="kpi-card orange">
              <div className="kpi-label">Fraud Rate</div>
              <div className="kpi-value">{result.fraud_rate}%</div>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><span className="card-title">Prediction Results</span></div>
            <div className="table-wrap" style={{ maxHeight: 420, overflowY: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Row / Transaction ID</th><th>Status</th><th>RF Prob</th><th>LR Prob</th><th>Fraud Prob</th><th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {result.results.slice(0, 200).map((r, i) => (
                    <tr key={i}>
                      <td style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--text-muted)' }}>{String(r.row).slice(0, 20)}</td>
                      <td><span className={`badge ${r.is_fraud ? 'fraud' : 'safe'}`}>{r.is_fraud ? '⚠ Fraud' : '✓ Safe'}</span></td>
                      <td style={{ fontSize: 12 }}>{(r.rf_probability * 100).toFixed(1)}%</td>
                      <td style={{ fontSize: 12 }}>{(r.lr_probability * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 600, color: r.is_fraud ? 'var(--accent-red)' : 'var(--accent-green)', fontSize: 13 }}>
                        {(r.fraud_probability * 100).toFixed(2)}%
                      </td>
                      <td><span className={`badge ${r.risk_level?.toLowerCase()}`}>{r.risk_level}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
