import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Lock, Sparkles } from 'lucide-react'
import { ThemeToggle } from '../components/ui/ThemeToggle'

const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
)

export function Login() {
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
      <div className="hidden lg:flex lg:w-1/2 bg-linear-to-br from-slate-50 via-teal-50/30 to-slate-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 relative overflow-hidden">
        {/* Dot pattern */}
        <div
          className="absolute inset-0 opacity-40 dark:opacity-20"
          style={{
            backgroundImage: `radial-gradient(circle, #94a3b8 1px, transparent 1px)`,
            backgroundSize: '24px 24px'
          }}
        />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between w-full p-16">
          {/* Logo */}
          <Link to="/" className="inline-flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-50 dark:bg-teal-900/50 rounded-xl flex items-center justify-center border border-teal-100 dark:border-teal-800">
              <span className="text-teal-600 dark:text-teal-400 font-serif text-lg">√</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="font-semibold text-slate-900 dark:text-white">FIND</span>
              <span className="font-semibold text-teal-600 dark:text-teal-400">MYJOURNAL</span>
            </div>
          </Link>

          {/* Content Card */}
          <div className="flex items-center justify-center">
            <div className="bg-white dark:bg-slate-800 rounded-3xl shadow-xl shadow-slate-200/50 dark:shadow-slate-900/50 p-10 max-w-lg border border-slate-100 dark:border-slate-700">
              {/* Quote marks */}
              <div className="text-4xl text-slate-200 dark:text-slate-600 font-serif mb-4">|||</div>

              {/* Quote */}
              <blockquote className="text-2xl lg:text-3xl font-serif text-slate-800 dark:text-slate-100 leading-relaxed mb-8">
                "Paste your title and abstract, and let AI find the journals that match your research."
              </blockquote>

              {/* Stats */}
              <div className="flex items-center gap-4">
                <div className="flex -space-x-2">
                  <div className="w-10 h-10 rounded-full bg-teal-100 dark:bg-teal-900/50 flex items-center justify-center text-xs font-bold text-teal-700 dark:text-teal-300 border-2 border-white dark:border-slate-800">
                    250K
                  </div>
                  <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/50 flex items-center justify-center text-xs font-bold text-amber-700 dark:text-amber-300 border-2 border-white dark:border-slate-800">
                    40+
                  </div>
                  <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-700 dark:text-slate-300 border-2 border-white dark:border-slate-800">
                    AI
                  </div>
                </div>
                <div className="text-sm text-slate-600 dark:text-slate-400">
                  <span className="font-medium">Journals</span> · <span className="font-medium">Languages</span> · <span className="font-medium">Matching</span>
                </div>
              </div>

              {/* OpenAlex attribution */}
              <div className="mt-8 pt-6 border-t border-slate-100 dark:border-slate-700 flex items-center gap-2 text-sm text-slate-400 dark:text-slate-500">
                <span>Powered by</span>
                <span className="font-medium text-slate-600 dark:text-slate-300">OpenAlex</span>
                <span>· Open academic data</span>
              </div>
            </div>
          </div>

          {/* Footer stats */}
          <div className="flex items-center gap-6 text-sm text-slate-400 dark:text-slate-500">
            <a href="#" className="hover:text-slate-600 dark:hover:text-slate-300 transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-slate-600 dark:hover:text-slate-300 transition-colors">Terms of Use</a>
            <a href="#" className="hover:text-slate-600 dark:hover:text-slate-300 transition-colors">Support</a>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-20 right-20 w-32 h-32 bg-teal-100/50 dark:bg-teal-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-40 h-40 bg-amber-100/30 dark:bg-amber-500/10 rounded-full blur-3xl" />
      </div>

      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex flex-col bg-white dark:bg-slate-900">
        {/* Header */}
        <header className="p-8 flex items-center justify-between">
          {/* Mobile logo */}
          <Link to="/" className="lg:hidden inline-flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-50 dark:bg-teal-900/50 rounded-xl flex items-center justify-center border border-teal-100 dark:border-teal-800">
              <span className="text-teal-600 dark:text-teal-400 font-serif text-lg">√</span>
            </div>
            <span className="font-semibold text-slate-900 dark:text-white">FindMyJournal</span>
          </Link>

          <div className="flex items-center gap-4 ml-auto">
            <ThemeToggle />
            <Link
              to="/signup"
              className="text-sm text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              New researcher? <span className="font-medium text-teal-600 dark:text-teal-400">Create account</span>
            </Link>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center px-8 lg:px-16">
          <div className="w-full max-w-md">
            {/* Title */}
            <div className="mb-10">
              <h1 className="text-4xl lg:text-5xl font-serif text-slate-900 dark:text-white leading-tight mb-2">
                Find Your
              </h1>
              <h1 className="text-4xl lg:text-5xl font-serif text-teal-600 dark:text-teal-400 leading-tight mb-6">
                Perfect Journal
              </h1>
              <p className="text-slate-500 dark:text-slate-400 text-lg leading-relaxed">
                AI-powered journal matching for academic researchers.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border-l-4 border-red-400 dark:border-red-500 rounded-r-lg">
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}

            {/* Google Sign In */}
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full py-4 px-6 bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-2xl hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all flex items-center justify-center gap-3 disabled:opacity-60 disabled:cursor-not-allowed group"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-slate-400" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span className="text-slate-600 dark:text-slate-300 font-medium">Connecting...</span>
                </>
              ) : (
                <>
                  <GoogleIcon />
                  <span className="text-slate-700 dark:text-slate-200 font-medium">Sign in with Google</span>
                </>
              )}
            </button>

            {/* Trust Indicators */}
            <div className="mt-8 pt-8 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center justify-center gap-6 text-sm text-slate-400 dark:text-slate-500">
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  <span>Secure Login</span>
                </div>
                <span className="w-1 h-1 bg-slate-300 dark:bg-slate-600 rounded-full" />
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  <span>AI-Powered</span>
                </div>
              </div>
            </div>

            {/* Sign Up Link */}
            <div className="mt-8 text-center">
              <p className="text-slate-500 dark:text-slate-400">
                New to FindMyJournal?{' '}
                <Link to="/signup" className="text-teal-600 dark:text-teal-400 font-medium hover:underline">
                  Create free account
                </Link>
              </p>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="p-8 flex items-center gap-6 text-sm text-slate-400 dark:text-slate-500">
          <span>Powered by <span className="font-medium text-slate-600 dark:text-slate-300">OpenAlex</span></span>
          <span className="w-1 h-1 bg-slate-300 dark:bg-slate-600 rounded-full" />
          <span>Open academic data</span>
        </footer>
      </div>
    </div>
  )
}
