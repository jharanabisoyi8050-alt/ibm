import React, { useState } from 'react'
import { emergencyApi } from '../services/api'

export default function EmergencyPage() {
  const [form, setForm] = useState({ lat: 51.5074, lng: -0.1278, severity: 'HIGH', description: '' })
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const risk_map: Record<string, number> = { LOW: 30, MEDIUM: 55, HIGH: 75, CRITICAL: 92 }
      const res = await emergencyApi.recommend({
        lat: form.lat, lng: form.lng,
        risk_score: risk_map[form.severity] || 50,
        risk_level: form.severity,
      })
      setResult(res.data)
    } catch (err) {
      setResult({ error: 'Failed to get recommendation' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif', maxWidth: '700px' }}>
      <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px' }}>
        Emergency Accident Reporting
      </h1>
      <p style={{ fontSize: '13px', color: '#57606a', marginBottom: '20px' }}>
        Submit an accident report to receive AI-generated emergency response recommendations.
        HIGH and CRITICAL severity incidents require human approval before dispatch.
      </p>

      <form onSubmit={handleSubmit} style={{ background: '#f7f8fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Latitude</label>
            <input type="number" step="any" value={form.lat}
              onChange={(e) => setForm({ ...form, lat: parseFloat(e.target.value) })}
              style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', boxSizing: 'border-box' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Longitude</label>
            <input type="number" step="any" value={form.lng}
              onChange={(e) => setForm({ ...form, lng: parseFloat(e.target.value) })}
              style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', boxSizing: 'border-box' }}
            />
          </div>
        </div>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Severity</label>
          <select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}
            style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px' }}>
            <option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option>
          </select>
        </div>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Description</label>
          <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
            rows={3} placeholder="Describe the incident..."
            style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', boxSizing: 'border-box' }} />
        </div>
        <button type="submit" disabled={loading}
          style={{ padding: '10px 24px', background: '#dc2626', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>
          {loading ? 'Analyzing...' : 'Get AI Recommendation'}
        </button>
      </form>

      {result && (
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>AI Emergency Response Recommendation</h3>
          {result.requires_hitl && (
            <div style={{ background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: '6px', padding: '10px', marginBottom: '12px', fontSize: '13px' }}>
              <strong>HITL Required:</strong> This HIGH/CRITICAL recommendation requires human approval before dispatch.
            </div>
          )}
          <pre style={{ fontSize: '12px', whiteSpace: 'pre-wrap', color: '#374151' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
