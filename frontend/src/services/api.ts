import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Accident APIs
export const accidentApi = {
  list: (params?: { lat?: number; lng?: number }) => api.get('/accidents/', { params }),
  create: (data: { lat: number; lng: number; severity: string; description: string }) =>
    api.post('/accidents/', data),
  getHotspots: () => api.get('/accidents/hotspots'),
}

// Traffic APIs
export const trafficApi = {
  getCurrent: (lat: number, lng: number) => api.get('/traffic/current', { params: { lat, lng } }),
  getDensityMap: () => api.get('/traffic/density-map'),
  getRiskPrediction: (lat: number, lng: number) =>
    api.get('/traffic/risk-prediction', { params: { lat, lng } }),
}

// Emergency APIs
export const emergencyApi = {
  recommend: (data: { lat: number; lng: number; risk_score: number; risk_level: string }) =>
    api.post('/emergency/recommend', data),
  getPendingApprovals: () => api.get('/emergency/pending-approvals'),
  approve: (approvalId: string, approved: boolean) =>
    api.post(`/emergency/approve/${approvalId}`, null, { params: { approved } }),
}

// Ambulance APIs
export const ambulanceApi = {
  getAvailable: (lat: number, lng: number) =>
    api.get('/ambulance/available', { params: { lat, lng } }),
  dispatch: (unitCode: string, lat: number, lng: number, incidentId: string) =>
    api.post('/ambulance/dispatch', null, {
      params: { unit_code: unitCode, incident_lat: lat, incident_lng: lng, incident_id: incidentId },
    }),
}

// Admin APIs
export const adminApi = {
  getDashboard: () => api.get('/admin/dashboard'),
  getTokenUsage: () => api.get('/admin/token-usage'),
}

// Auth APIs
export const authApi = {
  login: (email: string, password: string) => {
    const form = new FormData()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form)
  },
  register: (data: { email: string; password: string; name: string }) =>
    api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
}

export default api
