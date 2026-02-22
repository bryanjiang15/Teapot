import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useRegisterMutation } from './authApi'
import { useAppDispatch } from '@/app/hooks'
import { setCredentials } from './authSlice'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
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
    } catch (err: unknown) {
      setError((err as { data?: { detail?: string } })?.data?.detail || 'Failed to register. Please try again.')
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
            <CardTitle className="text-2xl font-heading">Create account</CardTitle>
            <CardDescription>Join to start creating amazing games with AI</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="username">Username (optional)</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="GameCreator123"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                />
              </div>

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
                  autoComplete="new-password"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                />
              </div>

              <Button variant="hero" type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Creating account...' : 'Create account'}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{' '}
                <Link to="/login" className="font-medium text-primary hover:underline">
                  Sign in
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
