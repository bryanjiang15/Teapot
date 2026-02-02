import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useAppDispatch } from '@/app/hooks'
import { logout } from '@/features/auth/authSlice'
import { OrangeButton } from '@/components/shared/OrangeButton'
import { PastelBadge } from '@/components/shared/PastelBadge'
import { Button } from '@/components/ui/button'
import { Gamepad2, Sparkles, Plus, LogOut } from 'lucide-react'

export function MainLayout() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-cream-bg wood-texture flex flex-col">
      {/* Top Navigation */}
      <header className="bg-white/80 backdrop-blur-sm border-b-2 border-wood-brown shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-lg bg-orange-primary flex items-center justify-center">
                <Gamepad2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-heading text-text-primary">TCG Creator</h1>
                <p className="text-xs text-text-secondary">AI-Powered Game Studio</p>
              </div>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden md:flex items-center gap-6">
              <Link
                to="/dashboard"
                className="text-text-primary hover:text-orange-primary font-medium transition-colors"
              >
                Workspace
              </Link>
              <Link
                to="/explore"
                className="text-text-primary hover:text-orange-primary font-medium transition-colors"
              >
                Explore
              </Link>
              <Link
                to="/profile"
                className="text-text-primary hover:text-orange-primary font-medium transition-colors"
              >
                Profile
              </Link>
            </nav>

            {/* Right Side Actions */}
            <div className="flex items-center gap-4">
              <PastelBadge color="purple" className="hidden sm:flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                AI Powered
              </PastelBadge>
              
              <OrangeButton size="sm" className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">New Project</span>
              </OrangeButton>
              
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="text-text-secondary hover:text-text-primary"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
