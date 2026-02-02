import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import authReducer from '@/features/auth/authSlice'
import workspaceReducer from '@/features/workspace/workspaceSlice'
import { api } from '@/lib/api/apiSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    workspace: workspaceReducer,
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
})

setupListeners(store.dispatch)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
