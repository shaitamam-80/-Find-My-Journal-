import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Zap, Search, FileText } from 'lucide-react'

const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
)

const steps = [
  {
    icon: <FileText className="w-5 h-5" />,
    title: 'Paste',
    desc: 'Title, abstract & keywords'
  },
  {
    icon: <Search className="w-5 h-5" />,
    title: 'Match',
    desc: 'AI scans 250K+ journals'
  },
  {
    icon: <Zap className="w-5 h-5" />,
    title: 'Discover',
    desc: 'Ranked results in seconds'
  }
]

export function SignUp() {
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signInWithGoogle } = useAuth()

  const handleGoogleSignIn = async () => {
    setError('')
    setLoading(true)
    const { error } = await signInWithGoogle()
    if (error) {
      setError(error.message)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Visual */}
      <div className="hidden lg:flex lg:w-1/2 bg-linear-to-br from-slate-50 via-teal-50/30 to-slate-50 relative overflow-hidden">
        {/* Dot pattern */}
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: `radial-gradient(circle, #94a3b8 1px, transparent 1px)`,
            backgroundSize: '24px 24px'
          }}
        />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between w-full p-16">
          {/* Logo */}
          <Link to="/" className="inline-flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-50 rounded-xl flex items-center justify-center border border-teal-100">
              <span className="text-teal-600 font-serif text-lg">√</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="font-semibold text-slate-900">FIND</span>
              <span className="font-semibold text-teal-600">MYJOURNAL</span>
            </div>
          </Link>

          {/* Main Content */}
          <div className="flex-1 flex items-center justify-center">
            {/* How it works Card */}
            <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-10 max-w-lg border border-slate-100">
              <h3 className="text-xs font-semibold text-teal-600 uppercase tracking-wider mb-2">
                How it works
              </h3>
              <p className="text-2xl font-serif text-slate-900 mb-8">
                Three simple steps to find your journal
              </p>
              <div className="space-y-8">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-start gap-5">
                    <div className="w-12 h-12 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600 shrink-0 border border-teal-100">
                      {step.icon}
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-900 text-lg">{step.title}</h4>
                      <p className="text-slate-500">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Footer stats */}
          <div className="flex items-center gap-8 text-sm text-slate-400">
            <span><strong className="text-slate-600">250K+</strong> journals</span>
            <span className="w-1 h-1 bg-slate-300 rounded-full" />
            <span><strong className="text-slate-600">40+</strong> languages</span>
            <span className="w-1 h-1 bg-slate-300 rounded-full" />
            <span><strong className="text-slate-600">Free</strong> to start</span>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-20 right-20 w-32 h-32 bg-teal-100/50 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-40 h-40 bg-amber-100/30 rounded-full blur-3xl" />
      </div>

      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex flex-col bg-white">
        {/* Header */}
        <header className="p-8 flex items-center justify-between">
          {/* Mobile logo */}
          <Link to="/" className="lg:hidden inline-flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-50 rounded-xl flex items-center justify-center border border-teal-100">
              <span className="text-teal-600 font-serif text-lg">√</span>
            </div>
            <span className="font-semibold text-slate-900">FindMyJournal</span>
          </Link>

          <Link
            to="/login"
            className="text-sm text-slate-500 hover:text-slate-900 transition-colors ml-auto"
          >
            Already have an account? <span className="font-medium text-teal-600">Sign in</span>
          </Link>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center px-8 lg:px-16">
          <div className="w-full max-w-md">
            {/* Title */}
            <div className="mb-10">
              <h1 className="text-4xl lg:text-5xl font-serif text-slate-900 leading-tight mb-2">
                Find Your
              </h1>
              <h1 className="text-4xl lg:text-5xl font-serif text-teal-600 leading-tight mb-6">
                Perfect Journal
              </h1>
              <p className="text-slate-500 text-lg leading-relaxed">
                AI-powered journal matching for academic researchers.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Google Sign Up */}
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full py-4 px-6 bg-white border-2 border-slate-200 rounded-2xl hover:border-slate-300 hover:bg-slate-50 transition-all flex items-center justify-center gap-3 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-slate-400" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span className="text-slate-600 font-medium">Creating account...</span>
                </>
              ) : (
                <>
                  <GoogleIcon />
                  <span className="text-slate-700 font-medium">Sign up with Google</span>
                </>
              )}
            </button>

            {/* Terms */}
            <p className="mt-6 text-sm text-slate-400 text-center leading-relaxed">
              By signing up, you agree to our{' '}
              <a href="#" className="text-teal-600 hover:underline">Terms of Service</a>
              {' '}and{' '}
              <a href="#" className="text-teal-600 hover:underline">Privacy Policy</a>
            </p>

            {/* Mobile: How it works */}
            <div className="lg:hidden mt-12 pt-8 border-t border-slate-100">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
                How it works
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {steps.map((step, index) => (
                  <div key={index} className="text-center">
                    <div className="w-10 h-10 mx-auto rounded-xl bg-teal-50 flex items-center justify-center text-teal-600 mb-2">
                      {step.icon}
                    </div>
                    <p className="text-xs text-slate-600">{step.title}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Sign In Link */}
            <div className="mt-8 text-center lg:hidden">
              <p className="text-slate-500">
                Already have an account?{' '}
                <Link to="/login" className="text-teal-600 font-medium hover:underline">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="p-8 flex items-center gap-6 text-sm text-slate-400">
          <span>Powered by <span className="font-medium text-slate-600">OpenAlex</span></span>
          <span className="w-1 h-1 bg-slate-300 rounded-full" />
          <span>Open academic data</span>
        </footer>
      </div>
    </div>
  )
}
