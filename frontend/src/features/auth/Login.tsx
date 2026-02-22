import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useLoginMutation } from './authApi'
import { useAppDispatch } from '@/app/hooks'
import { setCredentials } from './authSlice'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
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
    } catch (err: unknown) {
      setError((err as { data?: { detail?: string } })?.data?.detail || 'Failed to login. Please try again.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background wood-texture p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="gradient-primary p-3 rounded-xl shadow-sm">
              <Gamepad2 className="w-8 h-8 text-primary-foreground" />
            </div>
            <h1 className="text-3xl font-heading font-bold text-foreground">TCG Creator</h1>
          </div>
          <p className="text-muted-foreground">AI-Powered Game Studio</p>
        </div>

        <Card className="gradient-card border border-card-border shadow-lg card-hover overflow-hidden">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-heading">Welcome back</CardTitle>
            <CardDescription>Sign in to continue creating amazing games</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>

              <Button variant="hero" type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Signing in...' : 'Sign in'}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                Don&apos;t have an account?{' '}
                <Link to="/register" className="font-medium text-primary hover:underline">
                  Register
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
