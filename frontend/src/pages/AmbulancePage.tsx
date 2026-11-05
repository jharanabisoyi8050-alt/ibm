import React, { useState } from 'react'
import { ambulanceApi } from '../services/api'

export default function AmbulancePage() {
  const [lat, setLat] = useState(51.5074)
  const [lng, setLng] = useState(-0.1278)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    setLoading(true)
    try {
      const res = await ambulanceApi.getAvailable(lat, lng)
      setResult(res.data)
    } catch {
      setResult({ error: 'Failed to fetch ambulances' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px' }}>
        Ambulance Coordination Dashboard
      </h1>
      <div style={{ background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: '6px', padding: '10px', marginBottom: '20px', fontSize: '13px' }}>
        <strong>SIMULATED DATA NOTICE:</strong> All ambulance availability shown here is simulated for demonstration purposes.
        It does not represent real emergency vehicle availability or positions.
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', alignItems: 'flex-end' }}>
        <div>
          <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Incident Latitude</label>
          <input type="number" step="any" value={lat} onChange={(e) => setLat(parseFloat(e.target.value))}
            style={{ padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', width: '160px' }} />
        </div>
        <div>
          <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Incident Longitude</label>
          <input type="number" step="any" value={lng} onChange={(e) => setLng(parseFloat(e.target.value))}
            style={{ padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', width: '160px' }} />
        </div>
        <button onClick={handleSearch} disabled={loading}
          style={{ padding: '10px 20px', background: '#3b82d4', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>
          {loading ? 'Finding...' : 'Find Ambulances'}
        </button>
      </div>

      {result && !result.error && (
        <div>
          <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>
            Available Ambulances ({result.available_count})
            <span style={{ fontSize: '11px', fontWeight: 400, color: '#d97706', marginLeft: '8px' }}>
              [SIMULATED]
            </span>
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            {result.ambulances?.map((amb: any) => (
              <div key={amb.unit_code} style={{
                background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '14px',
              }}>
                <div style={{ fontWeight: 700, fontSize: '15px', marginBottom: '4px' }}>{amb.unit_code}</div>
                <div style={{ fontSize: '12px', color: '#57606a' }}>{amb.hospital_base}</div>
                <div style={{ fontSize: '12px', color: '#16a34a', marginTop: '4px' }}>
                  ETA: ~{amb.eta_min?.toFixed(0)} min
                </div>
                <div style={{ fontSize: '10px', color: '#d97706', marginTop: '4px' }}>
                  SIMULATED
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
