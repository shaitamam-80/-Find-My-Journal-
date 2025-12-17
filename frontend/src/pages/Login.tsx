import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { BookOpen, Mail, Lock, ArrowRight } from 'lucide-react'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signIn } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const { error } = await signIn(email, password)

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      navigate('/search')
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Horizontal Gradient Background */}
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-blue-500 to-blue-600" />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-300/30 to-transparent animate-slide-right" style={{ backgroundSize: '200% 100%' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400/25 to-transparent animate-slide-left" style={{ backgroundSize: '200% 100%', animationDelay: '0.5s' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/15 via-transparent to-cyan-500/15 animate-slide-right-slow" style={{ backgroundSize: '300% 100%' }} />
        <div className="absolute inset-0 dot-pattern opacity-70" />
      </div>

      {/* Navigation */}
      <nav className="relative z-20 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-11 h-11 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center group-hover:bg-white/30 transition-all border border-white/30">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">FindMyJournal</span>
          </Link>
          <Link to="/signup" className="px-5 py-2.5 text-white/90 font-semibold hover:text-white bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all">
            Don't have an account? Sign up
          </Link>
        </div>
      </nav>

      {/* Form */}
      <div className="relative z-10 min-h-[calc(100vh-80px)] flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-3xl p-8 shadow-2xl shadow-blue-900/30">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-200">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome Back</h1>
              <p className="text-gray-500">Sign in to your account to continue</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-cyan-600 mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-800 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 transition-all placeholder:text-gray-400"
                    placeholder="you@example.com"
                    required
                    autoComplete="email"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-cyan-600">Password</label>
                  <a href="#" className="text-sm text-blue-500 hover:text-blue-600 font-medium">Forgot password?</a>
                </div>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-800 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 transition-all placeholder:text-gray-400"
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3">
                <input type="checkbox" id="remember" className="w-5 h-5 rounded-lg border-blue-200 text-cyan-500 focus:ring-cyan-200 cursor-pointer" />
                <label htmlFor="remember" className="text-gray-600 cursor-pointer">Remember me</label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold text-lg rounded-xl hover:shadow-lg hover:shadow-blue-300 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-8 text-center">
              <p className="text-gray-500 text-sm">
                Don't have an account yet?{' '}
                <Link to="/signup" className="text-cyan-600 hover:text-cyan-700 font-semibold">
                  Sign up now
                </Link>
              </p>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-white/80 text-sm bg-white/10 backdrop-blur-md rounded-xl px-6 py-4 border border-white/20">
              Join 20,000+ researchers who have already found the perfect journal for their research.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
