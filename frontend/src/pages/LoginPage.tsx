import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../services/api'
import { useAuthStore } from '../hooks/useAuthStore'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setToken } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await authApi.login(email, password)
      setToken(res.data.access_token)
      navigate('/')
    } catch {
      setError('Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: '#f7f8fa', fontFamily: 'system-ui, sans-serif',
    }}>
      <div style={{
        background: '#fff', border: '1px solid #e5e7eb', borderRadius: '12px',
        padding: '40px', width: '360px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
      }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '4px', textAlign: 'center' }}>
          Road Safety AI
        </h1>
        <p style={{ fontSize: '13px', color: '#57606a', textAlign: 'center', marginBottom: '24px' }}>
          AI-Powered Accident Prediction System
        </p>
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
              Email
            </label>
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: '100%', padding: '10px 12px', border: '1px solid #e5e7eb',
                borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ marginBottom: '24px' }}>
            <label style={{ fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
              Password
            </label>
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%', padding: '10px 12px', border: '1px solid #e5e7eb',
                borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box',
              }}
            />
          </div>
          {error && (
            <div style={{ color: '#dc2626', fontSize: '13px', marginBottom: '16px' }}>{error}</div>
          )}
          <button
            type="submit" disabled={loading}
            style={{
              width: '100%', padding: '12px', background: '#3b82d4', color: '#fff',
              border: 'none', borderRadius: '6px', fontSize: '14px', fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}
