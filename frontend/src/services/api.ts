import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API 함수들
export const authAPI = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
}

export const papersAPI = {
  search: (query: string, max_results: number = 20) =>
    api.post('/papers/search', { query, max_results }),
  list: () => api.get('/papers'),
  get: (id: number) => api.get(`/papers/${id}`),
  create: (data: any) => api.post('/papers', data),
  upload: (file: File, title?: string, authors?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    if (authors) formData.append('authors', authors)
    return api.post('/papers/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  delete: (id: number) => api.delete(`/papers/${id}`),
}

export const analysisAPI = {
  question: (question: string, paper_id?: number, k: number = 5) =>
    api.post('/analysis/question', { question, paper_id, k }),
  summarize: (paper_id: number) =>
    api.post(`/analysis/summarize/${paper_id}`),
  compare: (paper_ids: number[]) =>
    api.post('/analysis/compare', { paper_ids }),
  list: () => api.get('/analysis'),
  get: (id: number) => api.get(`/analysis/${id}`),
}

export const subscriptionAPI = {
  getPlans: () => api.get('/subscriptions/plans'),
  getMy: () => api.get('/subscriptions/my'),
  create: (tier: string, payment_method_id?: string) =>
    api.post('/subscriptions', { tier, payment_method_id }),
  cancel: (at_period_end: boolean = true) =>
    api.post('/subscriptions/cancel', { at_period_end }),
}
