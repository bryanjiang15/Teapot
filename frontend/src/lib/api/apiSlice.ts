import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/app/store'

const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token
    if (token) {
      headers.set('authorization', `Bearer ${token}`)
    }
    return headers
  },
})

export const api = createApi({
  reducerPath: 'api',
  baseQuery,
  tagTypes: ['User', 'Project', 'Card', 'Ruleset'],
  endpoints: () => ({}),
})
