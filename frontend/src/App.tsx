import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Provider } from 'react-redux'
import { store } from './app/store'
import { Login } from './features/auth/Login'
import { Register } from './features/auth/Register'
import { ProtectedRoute } from './features/auth/ProtectedRoute'
import { MainLayout } from './layouts/MainLayout'
import { Dashboard } from './features/projects/Dashboard'
import { Workspace } from './features/workspace/Workspace'

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/workspace/:projectId" element={<Workspace />} />
            <Route path="/explore" element={<div className="p-8">Explore Page (Coming Soon)</div>} />
            <Route path="/profile" element={<div className="p-8">Profile Page (Coming Soon)</div>} />
          </Route>
          
          {/* Default Route */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </Provider>
  )
}

export default App
