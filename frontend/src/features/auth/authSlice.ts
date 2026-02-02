import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

interface AuthState {
  token: string | null
  refreshToken: string | null
  user: {
    id: string
    email: string
    username?: string
  } | null
  isAuthenticated: boolean
}

const initialState: AuthState = {
  token: localStorage.getItem('token'),
  refreshToken: localStorage.getItem('refreshToken'),
  user: null,
  isAuthenticated: false,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{
        token: string
        refreshToken: string
        user: { id: string; email: string; username?: string }
      }>
    ) => {
      state.token = action.payload.token
      state.refreshToken = action.payload.refreshToken
      state.user = action.payload.user
      state.isAuthenticated = true
      localStorage.setItem('token', action.payload.token)
      localStorage.setItem('refreshToken', action.payload.refreshToken)
    },
    logout: (state) => {
      state.token = null
      state.refreshToken = null
      state.user = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    },
    updateToken: (state, action: PayloadAction<{ token: string }>) => {
      state.token = action.payload.token
      localStorage.setItem('token', action.payload.token)
    },
  },
})

export const { setCredentials, logout, updateToken } = authSlice.actions
export default authSlice.reducer
