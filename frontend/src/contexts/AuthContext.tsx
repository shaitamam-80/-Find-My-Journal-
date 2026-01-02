import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { User as SupabaseUser, Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { logger } from '../lib/logger'
import type { User, UserLimits } from '../types'

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/v1`
  : '/api/v1'

interface AuthContextType {
  user: SupabaseUser | null
  profile: User | null
  limits: UserLimits | null
  session: Session | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>
  signUp: (email: string, password: string) => Promise<{ error: Error | null }>
  signOut: () => Promise<void>
  refreshLimits: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [profile, setProfile] = useState<User | null>(null)
  const [limits, setLimits] = useState<UserLimits | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchProfile = async (accessToken: string, signal?: AbortSignal) => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        signal,
      })
      if (response.ok) {
        const data = await response.json()
        setProfile(data)
      }
    } catch (error) {
      // Ignore abort errors - expected when component unmounts
      if (error instanceof Error && error.name === 'AbortError') return
      logger.error('Error fetching profile', error)
    }
  }

  const fetchLimits = async (accessToken: string, signal?: AbortSignal) => {
    try {
      const response = await fetch(`${API_BASE}/auth/limits`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        signal,
      })
      if (response.ok) {
        const data = await response.json()
        setLimits(data)
      }
    } catch (error) {
      // Ignore abort errors - expected when component unmounts
      if (error instanceof Error && error.name === 'AbortError') return
      logger.error('Error fetching limits', error)
    }
  }

  const refreshLimits = async () => {
    if (session?.access_token) {
      await fetchLimits(session.access_token)
    }
  }

  useEffect(() => {
    let isMounted = true
    const abortController = new AbortController()

    const initializeAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()

        if (!isMounted) return

        setSession(session)
        setUser(session?.user ?? null)

        if (session?.access_token) {
          await Promise.all([
            fetchProfile(session.access_token, abortController.signal),
            fetchLimits(session.access_token, abortController.signal),
          ])
        }
      } catch (error) {
        if (!isMounted) return
        logger.error('Auth initialization error', error)
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    initializeAuth()

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (!isMounted) return

      setSession(session)
      setUser(session?.user ?? null)

      if (session?.access_token) {
        await Promise.all([
          fetchProfile(session.access_token, abortController.signal),
          fetchLimits(session.access_token, abortController.signal),
        ])
      } else {
        setProfile(null)
        setLimits(null)
      }
    })

    return () => {
      isMounted = false
      abortController.abort()
      subscription.unsubscribe()
    }
  }, [])

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { error }
  }

  const signUp = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
    })
    return { error }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setProfile(null)
    setLimits(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        limits,
        session,
        loading,
        signIn,
        signUp,
        signOut,
        refreshLimits,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
