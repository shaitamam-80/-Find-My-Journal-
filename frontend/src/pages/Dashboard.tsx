import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { StatsOverview } from '../components/dashboard/StatsOverview'
import { RecentActivity } from '../components/dashboard/RecentActivity'
import { SkeletonStats, SkeletonCard } from '../components/ui/Skeleton'
import {
  BookOpen,
  Search,
  LogOut,
  AlertCircle,
  RefreshCw,
  Settings,
  Shield,
} from 'lucide-react'

interface DashboardStats {
  searches_today: number
  searches_total: number
  saved_searches_count: number
  daily_limit: number | null
  tier: string
}

interface Activity {
  id: string
  type: 'search' | 'save' | 'feedback'
  description: string
  created_at: string
  metadata?: Record<string, unknown>
}

export function Dashboard() {
  const { user, session, profile, signOut } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchDashboardData = async () => {
    if (!session?.access_token) return

    setLoading(true)
    setError('')

    try {
      const [statsData, activityData] = await Promise.all([
        api.getDashboardStats(session.access_token),
        api.getRecentActivity(session.access_token, 10),
      ])

      setStats(statsData)
      setActivities(activityData.activities)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'לא הצלחנו לטעון את הדשבורד')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [session?.access_token])

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 bg-slate-900 dark:bg-teal-600 rounded-xl flex items-center justify-center group-hover:bg-slate-800 dark:group-hover:bg-teal-500 transition-colors">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                FindMyJournal
              </span>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center gap-4">
              <Link
                to="/search"
                className="flex items-center gap-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors"
              >
                <Search className="w-5 h-5" />
                <span className="hidden sm:inline">Search</span>
              </Link>

              <Link
                to="/settings"
                className="flex items-center gap-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors"
              >
                <Settings className="w-5 h-5" />
                <span className="hidden sm:inline">Settings</span>
              </Link>

              {profile?.tier === 'super_admin' && (
                <Link
                  to="/admin"
                  className="flex items-center gap-2 px-4 py-2 text-purple-600 dark:text-purple-400 hover:text-purple-900 dark:hover:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-900/30 rounded-xl transition-colors"
                >
                  <Shield className="w-5 h-5" />
                  <span className="hidden sm:inline">Admin</span>
                </Link>
              )}

              <div className="flex items-center gap-3">
                <span className="hidden md:block text-sm text-gray-500 dark:text-slate-400">
                  {user?.email}
                </span>
                <button
                  onClick={signOut}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl transition-all text-gray-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 hover:text-gray-800 dark:hover:text-white"
                  title="Sign out"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="hidden sm:inline text-sm font-medium">Sign out</span>
                </button>
              </div>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Dashboard</h1>
            <p className="text-slate-500 dark:text-slate-400 mt-1">
              Welcome back, {user?.email?.split('@')[0]}
            </p>
          </div>

          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 dark:text-red-400 shrink-0 mt-0.5" />
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Stats Overview */}
        {loading && !stats ? (
          <div className="mb-8">
            <SkeletonStats />
          </div>
        ) : stats ? (
          <div className="mb-8">
            <StatsOverview
              searchesToday={stats.searches_today}
              searchesTotal={stats.searches_total}
              savedSearchesCount={stats.saved_searches_count}
              dailyLimit={stats.daily_limit}
              tier={stats.tier}
            />
          </div>
        ) : null}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity - 2 columns */}
          <div className="lg:col-span-2">
            <RecentActivity activities={activities} loading={loading && activities.length === 0} />
          </div>

          {/* Quick Actions - 1 column */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <Link
                  to="/search"
                  className="flex items-center gap-3 p-4 bg-slate-900 dark:bg-teal-600 text-white rounded-xl hover:bg-slate-800 dark:hover:bg-teal-500 transition-colors"
                >
                  <Search className="w-5 h-5" />
                  <span className="font-medium">New Search</span>
                </Link>

                <Link
                  to="/search"
                  className="flex items-center gap-3 p-4 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 border border-teal-200 dark:border-teal-700 rounded-xl hover:bg-teal-100 dark:hover:bg-teal-900/50 transition-colors"
                >
                  <BookOpen className="w-5 h-5" />
                  <span className="font-medium">Browse Saved Searches</span>
                </Link>
              </div>
            </div>

            {/* Upgrade CTA for free users */}
            {stats?.tier === 'free' && (
              <div className="bg-gradient-to-br from-slate-900 to-slate-800 dark:from-teal-700 dark:to-teal-800 rounded-2xl p-6 text-white">
                <h3 className="font-bold text-lg mb-2">Upgrade to Pro</h3>
                <p className="text-slate-300 dark:text-teal-200 text-sm mb-4">
                  Get unlimited searches and AI explanations
                </p>
                <button className="w-full py-3 bg-white text-slate-900 dark:text-teal-700 font-semibold rounded-xl hover:bg-slate-100 dark:hover:bg-teal-50 transition-colors">
                  Upgrade Now
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
