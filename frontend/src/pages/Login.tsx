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
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="px-6 py-4 border-b border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-11 h-11 bg-slate-900 rounded-2xl flex items-center justify-center group-hover:bg-slate-800 transition-all">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">FindMyJournal</span>
          </Link>
          <Link to="/signup" className="px-5 py-2.5 text-slate-600 font-semibold hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all">
            Don't have an account? Sign up
          </Link>
        </div>
      </nav>

      {/* Form */}
      <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Welcome Back</h1>
              <p className="text-slate-500">Sign in to your account to continue</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute start-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full ps-12 pe-4 py-3.5 bg-white border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all placeholder:text-slate-400"
                    placeholder="you@example.com"
                    required
                    autoComplete="email"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-slate-700">Password</label>
                  <a href="#" className="text-sm text-teal-600 hover:text-teal-700 font-medium">Forgot password?</a>
                </div>
                <div className="relative">
                  <Lock className="absolute start-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full ps-12 pe-4 py-3.5 bg-white border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all placeholder:text-slate-400"
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3">
                <input type="checkbox" id="remember" className="w-5 h-5 rounded-lg border-slate-300 text-teal-600 focus:ring-teal-200 cursor-pointer" />
                <label htmlFor="remember" className="text-slate-600 cursor-pointer">Remember me</label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-slate-900 text-white font-bold text-lg rounded-xl hover:bg-slate-800 transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
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
              <p className="text-slate-500 text-sm">
                Don't have an account yet?{' '}
                <Link to="/signup" className="text-teal-600 hover:text-teal-700 font-semibold">
                  Sign up now
                </Link>
              </p>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-slate-500 text-sm">
              Find the perfect journal for your research with AI-powered matching.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
