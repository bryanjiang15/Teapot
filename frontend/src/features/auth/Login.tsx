import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useLoginMutation } from './authApi'
import { useAppDispatch } from '@/app/hooks'
import { setCredentials } from './authSlice'
import { Input } from '@/components/ui/input'
import { OrangeButton } from '@/components/shared/OrangeButton'
import { WoodCard } from '@/components/shared/WoodCard'
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Gamepad2 } from 'lucide-react'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  
  const [login, { isLoading }] = useLoginMutation()
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    try {
      const response = await login({ email, password }).unwrap()
      dispatch(setCredentials({
        token: response.access_token,
        refreshToken: response.refresh_token,
        user: response.user,
      }))
      navigate('/dashboard')
    } catch (err: any) {
      setError(err?.data?.detail || 'Failed to login. Please try again.')
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
            <CardTitle className="text-2xl font-heading">Welcome Back</CardTitle>
            <CardDescription>Login to continue creating amazing games</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 rounded-md bg-red-50 border border-red-200 text-red-800 text-sm">
                  {error}
                </div>
              )}
              
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
              
              <OrangeButton
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? 'Logging in...' : 'Login'}
              </OrangeButton>
              
              <p className="text-center text-sm text-text-secondary">
                Don't have an account?{' '}
                <Link to="/register" className="text-orange-primary hover:text-orange-hover font-medium">
                  Register here
                </Link>
              </p>
            </form>
          </CardContent>
        </WoodCard>
      </div>
    </div>
  )
}
