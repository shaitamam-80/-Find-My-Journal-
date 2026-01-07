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
    let subscription: { unsubscribe: () => void } | null = null
    let timeoutId: NodeJS.Timeout | null = null

    const handleOAuthCallback = async () => {
      try {
        console.log('🔄 AuthCallback: Starting OAuth callback handling...')

        // Wait for Supabase to process the URL hash and establish session
        // This is critical - Supabase needs time to exchange the code for a session
        const { data: { subscription: authSubscription } } = supabase.auth.onAuthStateChange(
          async (event, session) => {
            console.log('🔔 Auth state change:', event, 'User:', session?.user?.email)

            if (event === 'SIGNED_IN' && session) {
              console.log('✅ OAuth session established successfully!')

              // Clean up
              if (subscription) subscription.unsubscribe()
              if (timeoutId) clearTimeout(timeoutId)

              // Redirect to search
              navigate('/search', { replace: true })
            } else if (event === 'SIGNED_OUT') {
              console.error('❌ User signed out during OAuth')

              if (subscription) subscription.unsubscribe()
              if (timeoutId) clearTimeout(timeoutId)

              setError('Authentication failed. Please try again.')
              setTimeout(() => navigate('/login'), 3000)
            }
          }
        )

        subscription = authSubscription

        // Also check if session already exists (in case auth state change fired before we subscribed)
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()

        if (sessionError) {
          console.error('❌ OAuth session error:', sessionError)
          setError(sessionError.message)
          if (subscription) subscription.unsubscribe()
          setTimeout(() => navigate('/login'), 3000)
          return
        }

        if (session) {
          console.log('✅ Session already exists:', session.user.email)
          if (subscription) subscription.unsubscribe()
          navigate('/search', { replace: true })
          return
        }

        // Set timeout for safety (15 seconds)
        timeoutId = setTimeout(() => {
          console.error('⏱️ OAuth timeout - no session established')
          if (subscription) subscription.unsubscribe()
          setError('Authentication timeout. Please try again.')
          setTimeout(() => navigate('/login'), 2000)
        }, 15000)

      } catch (err) {
        console.error('❌ OAuth callback error:', err)
        setError('An unexpected error occurred.')
        if (subscription) subscription.unsubscribe()
        if (timeoutId) clearTimeout(timeoutId)
        setTimeout(() => navigate('/login'), 3000)
      }
    }

    handleOAuthCallback()

    // Cleanup on unmount
    return () => {
      if (subscription) subscription.unsubscribe()
      if (timeoutId) clearTimeout(timeoutId)
    }
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
