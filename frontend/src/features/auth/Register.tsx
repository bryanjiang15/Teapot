import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useRegisterMutation } from './authApi'
import { useAppDispatch } from '@/app/hooks'
import { setCredentials } from './authSlice'
import { Input } from '@/components/ui/input'
import { OrangeButton } from '@/components/shared/OrangeButton'
import { WoodCard } from '@/components/shared/WoodCard'
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Gamepad2 } from 'lucide-react'

export function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')
  
  const [register, { isLoading }] = useRegisterMutation()
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    try {
      const response = await register({ email, password, username }).unwrap()
      dispatch(setCredentials({
        token: response.access_token,
        refreshToken: response.refresh_token,
        user: response.user,
      }))
      navigate('/dashboard')
    } catch (err: any) {
      setError(err?.data?.detail || 'Failed to register. Please try again.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-cream-bg wood-texture p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-12 h-12 rounded-lg bg-orange-primary flex items-center justify-center">
              <Gamepad2 className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-heading text-text-primary">TCG Creator</h1>
          </div>
          <p className="text-text-secondary">AI-Powered Game Studio</p>
        </div>
        
        <WoodCard>
          <CardHeader>
            <CardTitle className="text-2xl font-heading">Create Account</CardTitle>
            <CardDescription>Join us to start creating amazing games</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 rounded-md bg-red-50 border border-red-200 text-red-800 text-sm">
                  {error}
                </div>
              )}
              
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium text-text-primary">
                  Username (optional)
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="GameCreator123"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-text-primary">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-text-primary">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="text-sm font-medium text-text-primary">
                  Confirm Password
                </label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
              
              <OrangeButton
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? 'Creating account...' : 'Register'}
              </OrangeButton>
              
              <p className="text-center text-sm text-text-secondary">
                Already have an account?{' '}
                <Link to="/login" className="text-orange-primary hover:text-orange-hover font-medium">
                  Login here
                </Link>
              </p>
            </form>
          </CardContent>
        </WoodCard>
      </div>
    </div>
  )
}
