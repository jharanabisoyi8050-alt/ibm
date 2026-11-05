import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { trafficApi, adminApi } from '../../services/api'

const MOCK_TRAFFIC_TREND = [
  { time: '00:00', density: 15 }, { time: '04:00', density: 10 },
  { time: '08:00', density: 85 }, { time: '12:00', density: 60 },
  { time: '16:00', density: 90 }, { time: '20:00', density: 45 },
  { time: '23:59', density: 20 },
]

const MOCK_RISK_BY_ZONE = [
  { zone: 'North', risk: 72 }, { zone: 'South', risk: 45 },
  { zone: 'East', risk: 88 }, { zone: 'West', risk: 33 },
  { zone: 'Central', risk: 91 },
]

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    VERY_LOW: '#16a34a', LOW: '#65a30d', MODERATE: '#d97706',
    HIGH: '#dc2626', CRITICAL: '#7f1d1d',
  }
  return (
    <span style={{
      background: colors[level] || '#6b7280',
      color: '#fff', padding: '2px 8px', borderRadius: '12px',
      fontSize: '11px', fontWeight: 700,
    }}>
      {level}
    </span>
  )
}

function StatCard({ title, value, sub, color }: { title: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div style={{
      background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px',
      padding: '16px', borderLeft: `4px solid ${color || '#3b82d4'}`,
    }}>
      <div style={{ fontSize: '12px', color: '#57606a', marginBottom: '4px' }}>{title}</div>
      <div style={{ fontSize: '24px', fontWeight: 700, color: '#1f2328' }}>{value}</div>
      {sub && <div style={{ fontSize: '11px', color: '#57606a', marginTop: '2px' }}>{sub}</div>}
    </div>
  )
}

export default function Dashboard() {
  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '24px', color: '#1f2328' }}>
        Road Safety AI Dashboard
      </h1>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <StatCard title="Active Risk Alerts" value={7} sub="AI-predicted" color="#dc2626" />
        <StatCard title="Traffic Density" value="72%" sub="SIMULATED data" color="#d97706" />
        <StatCard title="Confirmed Accidents Today" value={3} sub="Verified reports" color="#16a34a" />
        <StatCard title="Pending HITL Approvals" value={2} sub="Awaiting review" color="#7c5cd8" />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>Traffic Density (24h)</h3>
          <div style={{ fontSize: '11px', color: '#d97706', marginBottom: '8px' }}>
            ⚠ Data is SIMULATED — not live traffic
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={MOCK_TRAFFIC_TREND}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="density" stroke="#3b82d4" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>AI Risk Score by Zone</h3>
          <div style={{ fontSize: '11px', color: '#7c5cd8', marginBottom: '8px' }}>
            AI_PREDICTED — not confirmed accidents
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={MOCK_RISK_BY_ZONE}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="zone" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="risk" fill="#dc2626" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Alerts */}
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>Recent Risk Alerts</h3>
        {[
          { id: 1, location: 'East Zone, Junction 14', risk: 'HIGH', source: 'AI_PREDICTED', time: '2 min ago' },
          { id: 2, location: 'Central Ring Road, Km 8', risk: 'CRITICAL', source: 'AI_PREDICTED', time: '5 min ago' },
          { id: 3, location: 'North Bridge Approach', risk: 'MODERATE', source: 'CONFIRMED', time: '12 min ago' },
        ].map((alert) => (
          <div key={alert.id} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '10px 0', borderBottom: '1px solid #f3f4f6',
          }}>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600 }}>{alert.location}</div>
              <div style={{ fontSize: '11px', color: '#57606a' }}>
                {alert.source === 'AI_PREDICTED' ? '🤖 AI Prediction' : '✅ Confirmed'} · {alert.time}
              </div>
            </div>
            <RiskBadge level={alert.risk} />
          </div>
        ))}
      </div>
    </div>
  )
}
