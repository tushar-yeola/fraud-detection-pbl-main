import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Cpu, Target, TrendingUp, Activity } from 'lucide-react'
import axios from 'axios'

export default function ModelInfo() {
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/api/model/info')
      .then(r => { setInfo(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="spinner" /></div>
  if (!info || info.error) return (
    <div className="empty-state">
      <Cpu size={48} />
      <div>Model not trained yet. Run <code>python ml/train.py</code> in the backend directory.</div>
    </div>
  )

  const models = info.models || {}
  const best = info.best_model || 'random_forest'
  const featImportance = Object.entries(info.feature_importances || {}).slice(0, 12)
    .map(([name, value]) => ({ name: name.replace('_', ' '), value: parseFloat((value * 100).toFixed(2)) }))
  const maxFeat = featImportance[0]?.value || 1

  const CT = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '8px 12px', boxShadow: '0 4px 16px rgba(15,23,42,0.10)' }}>
        <div style={{ color: '#64748b', fontSize: 11 }}>{label}</div>
        <div style={{ color: '#3b82f6', fontWeight: 700 }}>{payload[0].value}%</div>
      </div>
    )
  }

  return (
    <div className="fade-in">
      {/* Data Info */}
      <div className="kpi-grid" style={{ marginBottom: 20 }}>
        <div className="kpi-card blue">
          <div className="kpi-icon"><Activity size={20} /></div>
          <div className="kpi-label">Training Samples</div>
          <div className="kpi-value">{(info.data_info?.total_samples || 0).toLocaleString()}</div>
        </div>
        <div className="kpi-card red">
          <div className="kpi-icon"><Target size={20} /></div>
          <div className="kpi-label">Fraud Samples</div>
          <div className="kpi-value">{(info.data_info?.fraud_samples || 0).toLocaleString()}</div>
          <div className="kpi-sub">{info.data_info?.fraud_rate}% of dataset</div>
        </div>
        <div className="kpi-card green">
          <div className="kpi-icon"><TrendingUp size={20} /></div>
          <div className="kpi-label">Best Model</div>
          <div className="kpi-value" style={{ fontSize: 16, textTransform: 'capitalize' }}>
            {best.replace('_', ' ')}
          </div>
        </div>
        <div className="kpi-card purple">
          <div className="kpi-icon"><Cpu size={20} /></div>
          <div className="kpi-label">Features</div>
          <div className="kpi-value">{(info.feature_names || []).length}</div>
        </div>
      </div>

      <div className="charts-grid" style={{ marginBottom: 20 }}>
        {/* Model Comparison */}
        <div className="card">
          <div className="card-header"><span className="card-title">Model Performance Comparison</span></div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Model</th><th>AUC-ROC</th><th>F1 Score</th><th>Precision</th><th>Recall</th><th>Avg Precision</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(models).map(([name, m]) => (
                  <tr key={name} style={{ background: name === best ? '#eff6ff' : 'transparent' }}>
                    <td style={{ color: name === best ? 'var(--accent-blue)' : 'var(--text-primary)', fontWeight: name === best ? 700 : 400, textTransform: 'capitalize' }}>
                      {name.replace('_', ' ')}
                    </td>
                    {[m.auc_roc, m.f1, m.precision, m.recall, m.avg_precision].map((v, i) => (
                      <td key={i} style={{ fontWeight: 600, color: v > 0.8 ? 'var(--accent-green)' : v > 0.6 ? 'var(--accent-orange)' : 'var(--accent-red)' }}>
                        {(v * 100).toFixed(1)}%
                      </td>
                    ))}
                    <td>
                      {name === best
                        ? <span className="badge safe">✓ Best</span>
                        : <span className="badge medium">Compared</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Feature Importances Bar Chart */}
        <div className="card">
          <div className="card-header"><span className="card-title">Top Feature Importances</span></div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={featImportance} layout="vertical" margin={{ left: 60, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} unit="%" />
              <YAxis dataKey="name" type="category" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} width={90} />
              <Tooltip content={<CT />} />
              <Bar dataKey="value" fill="url(#featGrad)" radius={[0, 4, 4, 0]} />
              <defs>
                <linearGradient id="featGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#3b82f6" /><stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Feature List */}
      <div className="card">
        <div className="card-header"><span className="card-title">All Features ({(info.feature_names || []).length})</span></div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {(info.feature_names || []).map(f => (
            <span key={f} style={{
              padding: '4px 10px', borderRadius: 20,
              background: '#eff6ff', border: '1px solid rgba(37,99,235,0.2)',
              fontSize: 12, color: '#2563eb', fontFamily: 'monospace'
            }}>{f}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
