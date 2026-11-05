import React from 'react'
import HeatMap from '../components/HeatMap/HeatMap'
import { useQuery } from '@tanstack/react-query'
import { accidentApi } from '../services/api'

export default function HotspotPage() {
  const { data } = useQuery({
    queryKey: ['hotspots'],
    queryFn: () => accidentApi.getHotspots().then((r) => r.data),
  })

  const points = (data || []).map((h: any) => ({
    lat: h.lat, lng: h.lng,
    intensity: h.risk_level === 'CRITICAL' ? 1.0 : h.risk_level === 'HIGH' ? 0.75 : 0.5,
  }))

  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px' }}>
        Accident Hotspot Heatmap
      </h1>
      <p style={{ fontSize: '13px', color: '#57606a', marginBottom: '16px' }}>
        Hotspot zones identified using DBSCAN clustering on historical accident data.
        Red = CRITICAL, Orange = HIGH, Yellow = MODERATE.
      </p>
      <HeatMap points={points.length ? points : [
        { lat: 51.515, lng: -0.12, intensity: 0.9 },
        { lat: 51.510, lng: -0.13, intensity: 0.6 },
        { lat: 51.520, lng: -0.11, intensity: 1.0 },
      ]} />
    </div>
  )
}
