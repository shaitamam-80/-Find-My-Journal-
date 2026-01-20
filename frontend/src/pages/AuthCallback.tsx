import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { BookOpen } from 'lucide-react'

export function AuthCallback() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Check URL hash for error first (implicit flow returns errors in hash)
        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const errorDescription = hashParams.get('error_description')

        if (errorDescription) {
          setError(decodeURIComponent(errorDescription))
          return
        }

        // For implicit flow, Supabase auto-detects tokens in URL hash
        // when detectSessionInUrl is true. We just need to wait for it.

        // Set up auth state listener first
        const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
          console.log('Auth state changed:', event, !!session)
          if (event === 'SIGNED_IN' && session) {
            subscription.unsubscribe()
            navigate('/search', { replace: true })
          }
        })

        // Check if session already exists (might have been set by detectSessionInUrl)
        const { data, error: sessionError } = await supabase.auth.getSession()

        if (sessionError) {
          console.error('Auth callback error:', sessionError)
          setError(sessionError.message)
          subscription.unsubscribe()
          return
        }

        if (data.session) {
          console.log('Session found immediately')
          subscription.unsubscribe()
          navigate('/search', { replace: true })
        } else {
          // Give Supabase time to process the hash tokens
          setTimeout(async () => {
            const { data: retryData } = await supabase.auth.getSession()
            console.log('Retry session check:', !!retryData.session)
            if (retryData.session) {
              navigate('/search', { replace: true })
            } else {
              navigate('/login', { replace: true })
            }
            subscription.unsubscribe()
          }, 1500)
        }
      } catch (err) {
        console.error('Unexpected auth callback error:', err)
        setError('An unexpected error occurred during authentication')
      }
    }

    handleAuthCallback()
  }, [navigate])

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center px-6">
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Authentication Error</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-6">{error}</p>
          <button
            onClick={() => navigate('/login', { replace: true })}
            className="px-6 py-3 bg-slate-900 dark:bg-teal-600 text-white font-semibold rounded-xl hover:bg-slate-800 dark:hover:bg-teal-500 transition-all"
          >
            Back to Login
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-slate-900 dark:bg-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <BookOpen className="w-8 h-8 text-white" />
        </div>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900 dark:border-teal-400 mx-auto mb-4"></div>
        <p className="text-slate-600 dark:text-slate-400">Completing sign in...</p>
      </div>
    </div>
  )
}
