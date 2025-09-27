import { reactive } from 'vue'

const state = reactive({
  user: null,
  token: null,
})

function initFromStorage() {
  try { state.user = JSON.parse(localStorage.getItem('user') || 'null') } catch { state.user = null }
  state.token = localStorage.getItem('token') || null
}

function login(user, token) {
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('token', token)
  state.user = user
  state.token = token
}

function logout() {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  state.user = null
  state.token = null
}

initFromStorage()

export function useAuthStore() {
  return { state, login, logout }
}


