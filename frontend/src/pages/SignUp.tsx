import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { BookOpen, Mail, Lock, ArrowRight, CheckCircle, Shield, Zap } from 'lucide-react'

export function SignUp() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const { signUp } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)

    const { error } = await signUp(email, password)

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      setSuccess(true)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        {/* Animated Horizontal Gradient Background */}
        <div className="fixed inset-0">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-cyan-500 to-blue-600" />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-300/30 to-transparent animate-slide-right" style={{ backgroundSize: '200% 100%' }} />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent animate-slide-left" style={{ backgroundSize: '200% 100%', animationDelay: '1s' }} />
          <div className="absolute inset-0 dot-pattern opacity-60" />
        </div>

        <div className="relative z-10 min-h-screen flex items-center justify-center px-6">
          <div className="max-w-md w-full">
            <div className="bg-white rounded-3xl shadow-2xl shadow-blue-900/30 p-10 text-center">
              {/* Success Icon */}
              <div className="mb-6 inline-flex p-4 rounded-full bg-gradient-to-br from-blue-100 to-cyan-100">
                <CheckCircle className="w-12 h-12 text-cyan-500" />
              </div>

              <h2 className="text-2xl font-bold text-gray-800 mb-3">
                Check your email!
              </h2>
              <p className="text-gray-600 mb-2">
                We've sent a confirmation link to
              </p>
              <p className="font-semibold mb-6 text-lg text-cyan-600">
                {email}
              </p>
              <p className="text-sm text-gray-500 mb-8">
                Click the link in your email to activate your account and start discovering journals.
              </p>

              <Link
                to="/login"
                className="inline-flex items-center gap-2 py-3.5 px-6 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-xl transition-all hover:shadow-lg hover:shadow-blue-300 hover:-translate-y-0.5"
              >
                Go to Login
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Horizontal Gradient Background */}
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-cyan-500 to-blue-600" />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-300/30 to-transparent animate-slide-right" style={{ backgroundSize: '200% 100%' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent animate-slide-left" style={{ backgroundSize: '200% 100%', animationDelay: '1s' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-transparent to-blue-500/20 animate-slide-right-slow" style={{ backgroundSize: '300% 100%' }} />
        <div className="absolute inset-0 dot-pattern opacity-60" />
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
          <Link to="/login" className="px-5 py-2.5 text-white/90 font-semibold hover:text-white bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all">
            Already have an account? Log in
          </Link>
        </div>
      </nav>

      {/* Form */}
      <div className="relative z-10 min-h-[calc(100vh-80px)] flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-3xl p-8 shadow-2xl shadow-blue-900/30">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Create Your Account</h1>
              <p className="text-gray-500">Join thousands of researchers using our platform</p>
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
                <label className="block text-sm font-medium text-cyan-600 mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-800 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 transition-all placeholder:text-gray-400"
                    placeholder="At least 6 characters"
                    required
                    autoComplete="new-password"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-cyan-600 mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-800 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 transition-all placeholder:text-gray-400"
                    placeholder="Repeat your password"
                    required
                    autoComplete="new-password"
                  />
                </div>
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
                    Creating account...
                  </>
                ) : (
                  <>
                    Create Account
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-500 text-sm">
                By signing up, you agree to our{' '}
                <a href="#" className="text-cyan-600 font-medium">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-cyan-600 font-medium">Privacy Policy</a>
              </p>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-3 gap-4">
            {[
              { icon: <CheckCircle className="w-5 h-5" />, text: 'Free to try' },
              { icon: <Shield className="w-5 h-5" />, text: 'Fully secure' },
              { icon: <Zap className="w-5 h-5" />, text: 'Start instantly' }
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center gap-2 text-white bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
                {item.icon}
                <span className="text-sm font-medium text-center">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
