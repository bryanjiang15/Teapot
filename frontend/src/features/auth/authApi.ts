import { api } from '@/lib/api/apiSlice'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  username?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: {
    id: string
    email: string
    username?: string
  }
}

export const authApi = api.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    register: builder.mutation<AuthResponse, RegisterRequest>({
      query: (credentials) => ({
        url: '/auth/register',
        method: 'POST',
        body: credentials,
      }),
    }),
    refreshToken: builder.mutation<{ access_token: string }, { refresh_token: string }>({
      query: (body) => ({
        url: '/auth/refresh',
        method: 'POST',
        body,
      }),
    }),
  }),
})

export const { useLoginMutation, useRegisterMutation, useRefreshTokenMutation } = authApi
