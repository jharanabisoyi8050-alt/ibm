import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../services/api'

export default function AdminPage() {
  const { data: dashboard } = useQuery({ queryKey: ['admin-dashboard'], queryFn: () => adminApi.getDashboard().then((r) => r.data) })
  const { data: tokenUsage } = useQuery({ queryKey: ['token-usage'], queryFn: () => adminApi.getTokenUsage().then((r) => r.data) })

  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px' }}>Admin Dashboard</h1>

      {dashboard && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
          {[
            { label: 'Total Accident Reports', value: dashboard.total_accident_reports },
            { label: 'Confirmed Accidents', value: dashboard.confirmed_accidents },
            { label: 'AI Predicted Risks', value: dashboard.ai_predicted_risks },
            { label: 'Total LLM Cost (USD)', value: `$${dashboard.total_llm_cost_usd?.toFixed(4)}` },
            { label: 'Total Tokens Used', value: dashboard.total_tokens_used?.toLocaleString() },
            { label: 'System Status', value: dashboard.system_status?.toUpperCase() },
          ].map((s) => (
            <div key={s.label} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px' }}>
              <div style={{ fontSize: '12px', color: '#57606a' }}>{s.label}</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '4px' }}>{s.value}</div>
            </div>
          ))}
        </div>
      )}

      {tokenUsage && (
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>LLM Token Usage by Agent</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ background: '#f7f8fa' }}>
                {['Agent', 'Provider', 'Total Tokens', 'Cost (USD)', 'Requests'].map((h) => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tokenUsage.map((row: any) => (
                <tr key={`${row.agent_id}-${row.provider}`}>
                  <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6' }}>{row.agent_id}</td>
                  <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6' }}>{row.provider}</td>
                  <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6' }}>{row.total_tokens?.toLocaleString()}</td>
                  <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6' }}>${row.total_cost_usd}</td>
                  <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6' }}>{row.request_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
