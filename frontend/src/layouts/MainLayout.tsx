import { Outlet, useNavigate, NavLink } from 'react-router-dom'
import { useAppDispatch } from '@/app/hooks'
import { logout } from '@/features/auth/authSlice'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Gamepad2, Sparkles, Plus, LogOut, Home, Compass, User } from 'lucide-react'

export function MainLayout() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-background wood-texture flex flex-col">
      <nav className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <NavLink to="/dashboard" className="flex items-center space-x-2">
                <div className="gradient-primary p-2 rounded-lg shadow-sm">
                  <Gamepad2 className="h-6 w-6 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="text-xl font-heading font-bold text-foreground">TCG Creator</h1>
                  <p className="text-xs text-muted-foreground">AI-Powered Game Studio</p>
                </div>
              </NavLink>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-1">
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`
                }
              >
                <Home className="h-4 w-4" />
                <span>Workspace</span>
              </NavLink>
              <NavLink
                to="/explore"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`
                }
              >
                <Compass className="h-4 w-4" />
                <span>Explore</span>
              </NavLink>
              <NavLink
                to="/profile"
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`
                }
              >
                <User className="h-4 w-4" />
                <span>Profile</span>
              </NavLink>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-3">
              <Badge variant="secondary" className="hidden sm:flex items-center space-x-1 border-0">
                <Sparkles className="h-3 w-3" />
                <span className="text-xs">AI Powered</span>
              </Badge>
              <Button variant="hero" size="sm">
                <Plus className="h-4 w-4" />
                <span className="hidden sm:inline">New Project</span>
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="text-muted-foreground hover:text-foreground"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="relative flex-1">
        <Outlet />
      </main>
    </div>
  )
}
