import axios from 'axios'
import { useAuthStore } from '../store/auth'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      const { logout } = useAuthStore()
      logout()
      if (location.pathname !== '/login') {
        window.location.assign('/login')
      }
    }
    return Promise.reject(err)
  }
)

export default api


