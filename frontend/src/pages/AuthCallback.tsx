import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { BookOpen } from 'lucide-react'

/**
 * OAuth Callback Handler
 *
 * This page handles the OAuth redirect after Google authentication.
 * Supabase automatically exchanges the auth code for a session.
 * We wait for the session to be established, then redirect to /search.
 */
export function AuthCallback() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Check if we have a session (Supabase client handles token exchange automatically)
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()

        if (sessionError) {
          console.error('OAuth session error:', sessionError)
          setError(sessionError.message)
          // Redirect to login after 3 seconds
          setTimeout(() => navigate('/login'), 3000)
          return
        }

        if (session) {
          // Session established successfully! Redirect to search
          console.log('✅ OAuth session established:', session.user.email)
          navigate('/search', { replace: true })
        } else {
          // No session yet, wait for auth state change
          console.log('⏳ Waiting for OAuth session...')

          const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
            console.log('🔔 Auth state change:', event, session?.user?.email)

            if (event === 'SIGNED_IN' && session) {
              subscription.unsubscribe()
              navigate('/search', { replace: true })
            } else if (event === 'SIGNED_OUT') {
              subscription.unsubscribe()
              setError('Authentication failed. Please try again.')
              setTimeout(() => navigate('/login'), 3000)
            }
          })

          // Timeout after 10 seconds if no session
          setTimeout(() => {
            subscription.unsubscribe()
            setError('Authentication timeout. Please try again.')
            setTimeout(() => navigate('/login'), 2000)
          }, 10000)
        }
      } catch (err) {
        console.error('OAuth callback error:', err)
        setError('An unexpected error occurred.')
        setTimeout(() => navigate('/login'), 3000)
      }
    }

    handleOAuthCallback()
  }, [navigate])

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-6">
      <div className="w-full max-w-md text-center">
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200">
          <div className="w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-8 h-8 text-white" />
          </div>

          {error ? (
            <>
              <h1 className="text-2xl font-bold text-red-600 mb-2">Authentication Error</h1>
              <p className="text-slate-600 mb-4">{error}</p>
              <p className="text-sm text-slate-500">Redirecting to login page...</p>
            </>
          ) : (
            <>
              <h1 className="text-2xl font-bold text-slate-900 mb-2">Completing Sign In</h1>
              <p className="text-slate-600 mb-6">Please wait while we finish authenticating your account...</p>
              <div className="flex justify-center">
                <svg className="animate-spin h-8 w-8 text-teal-600" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
