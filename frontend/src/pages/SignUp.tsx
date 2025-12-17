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
      <div className="min-h-screen bg-slate-50 flex items-center justify-center px-6">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-10 text-center">
            {/* Success Icon */}
            <div className="mb-6 inline-flex p-4 rounded-full bg-emerald-50 border border-emerald-200">
              <CheckCircle className="w-12 h-12 text-emerald-600" />
            </div>

            <h2 className="text-2xl font-bold text-slate-900 mb-3">
              Check your email!
            </h2>
            <p className="text-slate-600 mb-2">
              We've sent a confirmation link to
            </p>
            <p className="font-semibold mb-6 text-lg text-teal-600">
              {email}
            </p>
            <p className="text-sm text-slate-500 mb-8">
              Click the link in your email to activate your account and start discovering journals.
            </p>

            <Link
              to="/login"
              className="inline-flex items-center gap-2 py-3.5 px-6 bg-slate-900 text-white font-semibold rounded-xl transition-all hover:bg-slate-800"
            >
              Go to Login
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>
    )
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
          <Link to="/login" className="px-5 py-2.5 text-slate-600 font-semibold hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all">
            Already have an account? Log in
          </Link>
        </div>
      </nav>

      {/* Form */}
      <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Create Your Account</h1>
              <p className="text-slate-500">Join researchers using our platform</p>
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
                <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute start-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full ps-12 pe-4 py-3.5 bg-white border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all placeholder:text-slate-400"
                    placeholder="At least 6 characters"
                    required
                    autoComplete="new-password"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute start-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full ps-12 pe-4 py-3.5 bg-white border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all placeholder:text-slate-400"
                    placeholder="Repeat your password"
                    required
                    autoComplete="new-password"
                  />
                </div>
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
              <p className="text-slate-500 text-sm">
                By signing up, you agree to our{' '}
                <a href="#" className="text-teal-600 font-medium">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-teal-600 font-medium">Privacy Policy</a>
              </p>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-3 gap-4">
            {[
              { icon: <CheckCircle className="w-5 h-5" />, text: 'Free to try' },
              { icon: <Shield className="w-5 h-5" />, text: 'Fully secure' },
              { icon: <Zap className="w-5 h-5" />, text: 'Start instantly' }
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center gap-2 text-slate-600 bg-white rounded-xl p-4 border border-slate-200">
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
