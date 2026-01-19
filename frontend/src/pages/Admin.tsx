import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import type { UserListItem, PlatformStats } from '../types'
import {
  Users,
  Search,
  TrendingUp,
  UserCheck,
  UserX,
  Shield,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  AlertCircle,
  LogOut,
  ArrowLeft,
} from 'lucide-react'

export function Admin() {
  const { user, session, signOut } = useAuth()
  const navigate = useNavigate()

  const [users, setUsers] = useState<UserListItem[]>([])
  const [stats, setStats] = useState<PlatformStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Pagination & filters
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [tierFilter, setTierFilter] = useState<string>('')

  // Check if user is admin based on profile data
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)

  useEffect(() => {
    checkAdminAccess()
  }, [session?.access_token])

  useEffect(() => {
    if (isAdmin === true && session?.access_token) {
      fetchData()
    }
  }, [session?.access_token, page, tierFilter, isAdmin])

  const checkAdminAccess = async () => {
    if (!session?.access_token) {
      setIsAdmin(false)
      return
    }

    try {
      const profile = await api.getMyProfile(session.access_token)
      if (profile.tier !== 'super_admin') {
        setIsAdmin(false)
        navigate('/dashboard')
      } else {
        setIsAdmin(true)
      }
    } catch {
      setIsAdmin(false)
      navigate('/dashboard')
    }
  }

  const fetchData = async () => {
    if (!session?.access_token) return

    setLoading(true)
    setError('')

    try {
      const [usersData, statsData] = await Promise.all([
        api.listUsers(session.access_token, {
          page,
          limit: 20,
          tier: tierFilter || undefined,
          search: searchQuery || undefined,
        }),
        api.getPlatformStats(session.access_token),
      ])

      setUsers(usersData.users)
      setTotalPages(usersData.total_pages)
      setStats(statsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load admin data')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleToggleUserStatus = async (userId: string, currentlyActive: boolean) => {
    if (!session?.access_token) return

    try {
      if (currentlyActive) {
        await api.adminDeactivateUser(session.access_token, userId)
      } else {
        await api.activateUser(session.access_token, userId)
      }
      fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user')
    }
  }

  const handleChangeTier = async (userId: string, newTier: string) => {
    if (!session?.access_token) return

    try {
      await api.updateUser(session.access_token, userId, {
        tier: newTier as 'free' | 'paid' | 'super_admin',
      })
      fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user tier')
    }
  }

  if (isAdmin === null) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900 dark:border-purple-400" />
      </div>
    )
  }

  if (isAdmin === false) {
    return null
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link
                to="/dashboard"
                className="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-600 rounded-xl flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold text-slate-900 dark:text-white">Admin Panel</span>
              </div>
            </div>

            <button
              onClick={signOut}
              className="flex items-center gap-2 px-3 py-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 dark:text-red-400 shrink-0 mt-0.5" />
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                  <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <span className="text-slate-600 dark:text-slate-400 font-medium">Total Users</span>
              </div>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">{stats.total_users}</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-xl">
                  <UserCheck className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <span className="text-slate-600 dark:text-slate-400 font-medium">Active Today</span>
              </div>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">{stats.active_users_today}</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-teal-100 dark:bg-teal-900/30 rounded-xl">
                  <Search className="w-5 h-5 text-teal-600 dark:text-teal-400" />
                </div>
                <span className="text-slate-600 dark:text-slate-400 font-medium">Searches Today</span>
              </div>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">{stats.total_searches_today}</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-xl">
                  <TrendingUp className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                </div>
                <span className="text-slate-600 dark:text-slate-400 font-medium">New This Week</span>
              </div>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">{stats.new_users_week}</p>
            </div>
          </div>
        )}

        {/* Users Table */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          {/* Table Header */}
          <div className="p-6 border-b border-slate-200 dark:border-slate-700">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">User Management</h2>

              <div className="flex gap-3">
                {/* Search */}
                <div className="relative flex-1 sm:flex-none">
                  <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Search by email..."
                    className="w-full sm:w-64 ps-9 pe-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-slate-300 dark:focus:border-slate-500"
                  />
                </div>

                {/* Tier Filter */}
                <select
                  value={tierFilter}
                  onChange={(e) => {
                    setTierFilter(e.target.value)
                    setPage(1)
                  }}
                  className="px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-slate-300 dark:focus:border-slate-500"
                >
                  <option value="">All Tiers</option>
                  <option value="free">Free</option>
                  <option value="paid">Paid</option>
                  <option value="super_admin">Admin</option>
                </select>

                {/* Refresh */}
                <button
                  onClick={fetchData}
                  disabled={loading}
                  className="p-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors disabled:opacity-50"
                >
                  <RefreshCw
                    className={`w-5 h-5 text-slate-600 dark:text-slate-300 ${loading ? 'animate-spin' : ''}`}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 dark:bg-slate-700/50">
                <tr>
                  <th className="px-6 py-3 text-start text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-start text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    Tier
                  </th>
                  <th className="px-6 py-3 text-start text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-start text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    Searches Today
                  </th>
                  <th className="px-6 py-3 text-start text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    Joined
                  </th>
                  <th className="px-6 py-3 text-end text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">
                          {u.display_name || u.email.split('@')[0]}
                        </p>
                        <p className="text-sm text-slate-500 dark:text-slate-400">{u.email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={u.tier}
                        onChange={(e) => handleChangeTier(u.id, e.target.value)}
                        disabled={u.id === user?.id}
                        className={`px-3 py-1 rounded-full text-sm font-medium border-0 cursor-pointer ${
                          u.tier === 'super_admin'
                            ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400'
                            : u.tier === 'paid'
                              ? 'bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400'
                              : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                        } ${u.id === user?.id ? 'cursor-not-allowed opacity-50' : ''}`}
                      >
                        <option value="free">Free</option>
                        <option value="paid">Paid</option>
                        <option value="super_admin">Admin</option>
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
                          u.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                        }`}
                      >
                        {u.is_active ? (
                          <UserCheck className="w-3.5 h-3.5" />
                        ) : (
                          <UserX className="w-3.5 h-3.5" />
                        )}
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-900 dark:text-white">{u.credits_used_today}</td>
                    <td className="px-6 py-4 text-slate-500 dark:text-slate-400 text-sm">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : '-'}
                    </td>
                    <td className="px-6 py-4 text-end">
                      {u.id !== user?.id && (
                        <button
                          onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                          className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                            u.is_active
                              ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30'
                              : 'text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/30'
                          }`}
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-5 h-5 text-slate-600 dark:text-slate-300" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-5 h-5 text-slate-600 dark:text-slate-300" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
