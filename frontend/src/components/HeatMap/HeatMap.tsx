import React, { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

interface HotspotPoint {
  lat: number
  lng: number
  intensity: number
}

interface HeatMapProps {
  center?: [number, number]
  zoom?: number
  points: HotspotPoint[]
}

function HeatmapLayer({ points }: { points: HotspotPoint[] }) {
  const map = useMap()
  const heatRef = useRef<any>(null)

  useEffect(() => {
    if (!points.length) return
    const heatData = points.map((p) => [p.lat, p.lng, p.intensity])

    if (heatRef.current) {
      map.removeLayer(heatRef.current)
    }
    // @ts-ignore - leaflet.heat
    if ((L as any).heatLayer) {
      heatRef.current = (L as any).heatLayer(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        gradient: { 0.2: 'green', 0.5: 'yellow', 0.8: 'orange', 1.0: 'red' },
      }).addTo(map)
    }
    return () => {
      if (heatRef.current) map.removeLayer(heatRef.current)
    }
  }, [points, map])

  return null
}

export default function HeatMap({ center = [51.5074, -0.1278], zoom = 12, points }: HeatMapProps) {
  return (
    <div style={{ height: '500px', width: '100%', borderRadius: '8px', overflow: 'hidden' }}>
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <HeatmapLayer points={points} />
      </MapContainer>
    </div>
  )
}
