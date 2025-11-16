import axios from 'axios';
import Constants from 'expo-constants';
import { useAuthStore } from '../store/authStore';

const API_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await useAuthStore.getState().clearAuth();
    }
    return Promise.reject(error);
  }
);

export default api;

// API 함수들
export const authAPI = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
};

export const papersAPI = {
  search: (query: string, max_results: number = 20) =>
    api.post('/papers/search', { query, max_results }),
  list: () => api.get('/papers'),
  get: (id: number) => api.get(`/papers/${id}`),
  delete: (id: number) => api.delete(`/papers/${id}`),
};

export const analysisAPI = {
  question: (question: string, paper_id?: number) =>
    api.post('/analysis/question', { question, paper_id }),
  summarize: (paper_id: number) =>
    api.post(`/analysis/summarize/${paper_id}`),
  compare: (paper_ids: number[]) =>
    api.post('/analysis/compare', { paper_ids }),
};
