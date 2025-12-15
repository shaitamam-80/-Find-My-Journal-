import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

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
    <div className="min-h-screen flex">
      {/* Left Side - Dark Panel with Features */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden" style={{ background: '#262626' }}>
        {/* Subtle gradient overlay */}
        <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, #262626 0%, #171717 100%)' }} />

        {/* Decorative circles */}
        <div className="absolute top-20 right-20 w-72 h-72 rounded-full opacity-5" style={{ background: 'radial-gradient(circle, #0ea5e9 0%, transparent 70%)' }} />
        <div className="absolute bottom-32 left-16 w-48 h-48 rounded-full opacity-5" style={{ background: 'radial-gradient(circle, #0ea5e9 0%, transparent 70%)' }} />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-16 py-12">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-16">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: '#0ea5e9' }}>
              <span className="material-symbols-outlined text-white" style={{ fontSize: '24px' }}>menu_book</span>
            </div>
            <span className="text-xl font-bold text-white tracking-tight">
              Find My Journal
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl xl:text-5xl font-bold mb-4 leading-tight" style={{ color: '#ffffff' }}>
            Find the perfect
            <span className="block" style={{ color: '#38bdf8' }}>home for your research</span>
          </h1>

          <p className="text-lg text-neutral-300 mb-12 max-w-md leading-relaxed">
            AI-powered journal matching that analyzes your paper and recommends the best publication venues.
          </p>

          {/* Feature List */}
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(14, 165, 233, 0.15)' }}>
                <span className="material-symbols-outlined" style={{ color: '#0ea5e9', fontSize: '24px' }}>psychology</span>
              </div>
              <div>
                <h3 className="font-semibold mb-1" style={{ color: '#ffffff' }}>Deep Context Analysis</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#d4d4d4' }}>
                  Our AI reads your abstract and understands the nuances of your research topic.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(14, 165, 233, 0.15)' }}>
                <span className="material-symbols-outlined" style={{ color: '#0ea5e9', fontSize: '24px' }}>trending_up</span>
              </div>
              <div>
                <h3 className="font-semibold mb-1" style={{ color: '#ffffff' }}>Real-Time Metrics</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#d4d4d4' }}>
                  Get up-to-date impact factors, h-index, and publication trends from OpenAlex.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(14, 165, 233, 0.15)' }}>
                <span className="material-symbols-outlined" style={{ color: '#0ea5e9', fontSize: '24px' }}>verified_user</span>
              </div>
              <div>
                <h3 className="font-semibold mb-1" style={{ color: '#ffffff' }}>Quality Assurance</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#d4d4d4' }}>
                  We filter results to show only reputable, peer-reviewed journals.
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-neutral-50">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: '#0ea5e9' }}>
              <span className="material-symbols-outlined text-white" style={{ fontSize: '24px' }}>menu_book</span>
            </div>
            <span className="text-xl font-bold text-neutral-800 tracking-tight">
              Find My Journal
            </span>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-neutral-800 mb-2">
              Welcome back
            </h2>
            <p className="text-neutral-500">
              Sign in to continue your research journey
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-white rounded-2xl shadow-xl border border-neutral-100 p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <div className="space-y-1.5">
                <label htmlFor="email" className="block text-sm font-medium text-neutral-700">
                  Email address
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" style={{ fontSize: '20px' }}>
                    mail
                  </span>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 text-neutral-800 bg-white border-2 border-neutral-200 rounded-xl transition-all duration-200 placeholder:text-neutral-400 hover:border-neutral-300 focus:outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="password" className="block text-sm font-medium text-neutral-700">
                  Password
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" style={{ fontSize: '20px' }}>
                    lock
                  </span>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 text-neutral-800 bg-white border-2 border-neutral-200 rounded-xl transition-all duration-200 placeholder:text-neutral-400 hover:border-neutral-300 focus:outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10"
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-6 text-white font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
                style={{
                  background: loading ? '#94a3b8' : '#0ea5e9',
                  boxShadow: loading ? 'none' : '0 4px 14px -3px rgba(14, 165, 233, 0.4)'
                }}
                onMouseEnter={(e) => !loading && (e.currentTarget.style.background = '#0284c7')}
                onMouseLeave={(e) => !loading && (e.currentTarget.style.background = '#0ea5e9')}
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
                    Sign in
                    <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>arrow_forward</span>
                  </>
                )}
              </button>
            </form>

            <div className="flex items-center gap-4 my-6">
              <div className="flex-1 h-px bg-neutral-200" />
              <span className="text-sm text-neutral-400">or</span>
              <div className="flex-1 h-px bg-neutral-200" />
            </div>

            <p className="text-center text-sm text-neutral-500">
              Don't have an account?{' '}
              <Link
                to="/signup"
                className="font-semibold transition-colors"
                style={{ color: '#0ea5e9' }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#0284c7'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#0ea5e9'}
              >
                Create one now
              </Link>
            </p>
          </div>

          {/* Footer */}
          <p className="text-center text-xs text-neutral-400 mt-8">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  )
}
