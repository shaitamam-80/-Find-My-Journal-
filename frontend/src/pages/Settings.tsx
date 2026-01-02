import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import type { ProfileResponse, UsageStats } from '../types'
import {
  BookOpen,
  User,
  Building,
  Microscope,
  Globe,
  Bell,
  Trash2,
  Save,
  AlertCircle,
  CheckCircle,
  LogOut,
  ArrowLeft,
  BarChart2,
  Search,
  Bookmark,
  ThumbsUp,
  Calendar,
} from 'lucide-react'

export function Settings() {
  const { user, session, signOut } = useAuth()
  const [profile, setProfile] = useState<ProfileResponse | null>(null)
  const [usage, setUsage] = useState<UsageStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form state
  const [displayName, setDisplayName] = useState('')
  const [institution, setInstitution] = useState('')
  const [researchField, setResearchField] = useState('')
  const [orcidId, setOrcidId] = useState('')
  const [country, setCountry] = useState('')
  const [emailNotifications, setEmailNotifications] = useState(true)

  // Delete confirmation
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleteConfirmText, setDeleteConfirmText] = useState('')

  useEffect(() => {
    fetchData()
  }, [session?.access_token])

  const fetchData = async () => {
    if (!session?.access_token) return

    setLoading(true)
    try {
      const [profileData, usageData] = await Promise.all([
        api.getMyProfile(session.access_token),
        api.getMyUsage(session.access_token),
      ])

      setProfile(profileData)
      setUsage(usageData)

      // Populate form
      setDisplayName(profileData.display_name || '')
      setInstitution(profileData.institution || '')
      setResearchField(profileData.research_field || '')
      setOrcidId(profileData.orcid_id || '')
      setCountry(profileData.country || '')
      setEmailNotifications(profileData.email_notifications)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!session?.access_token) return

    setSaving(true)
    setError('')
    setSuccess('')

    try {
      await api.updateMyProfile(session.access_token, {
        display_name: displayName || undefined,
        institution: institution || undefined,
        research_field: researchField || undefined,
        orcid_id: orcidId || undefined,
        country: country || undefined,
        email_notifications: emailNotifications,
      })

      setSuccess('Settings saved successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE' || !session?.access_token) return

    try {
      await api.deleteMyAccount(session.access_token)
      await signOut()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete account')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link
                to="/dashboard"
                className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold text-slate-900">Settings</span>
              </div>
            </div>

            <button
              onClick={signOut}
              className="flex items-center gap-2 px-3 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 rounded-xl bg-green-50 border border-green-200 flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
            <p className="text-sm text-green-600">{success}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Form - 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Information */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-6 flex items-center gap-2">
                <User className="w-5 h-5 text-slate-600" />
                Profile Information
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 cursor-not-allowed"
                  />
                  <p className="mt-1 text-xs text-slate-400">Email cannot be changed</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="Dr. Jane Smith"
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    <Building className="w-4 h-4 inline me-1" />
                    Institution
                  </label>
                  <input
                    type="text"
                    value={institution}
                    onChange={(e) => setInstitution(e.target.value)}
                    placeholder="University of Example"
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    <Microscope className="w-4 h-4 inline me-1" />
                    Research Field
                  </label>
                  <input
                    type="text"
                    value={researchField}
                    onChange={(e) => setResearchField(e.target.value)}
                    placeholder="e.g., Molecular Biology, Machine Learning"
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    ORCID ID
                  </label>
                  <input
                    type="text"
                    value={orcidId}
                    onChange={(e) => setOrcidId(e.target.value)}
                    placeholder="0000-0000-0000-0000"
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    <Globe className="w-4 h-4 inline me-1" />
                    Country
                  </label>
                  <input
                    type="text"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    placeholder="e.g., Israel, United States"
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 transition-all"
                  />
                </div>
              </div>
            </div>

            {/* Notification Preferences */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-6 flex items-center gap-2">
                <Bell className="w-5 h-5 text-slate-600" />
                Notifications
              </h2>

              <label className="flex items-center justify-between p-4 bg-slate-50 rounded-xl cursor-pointer">
                <div>
                  <p className="font-medium text-slate-900">Email Notifications</p>
                  <p className="text-sm text-slate-500">
                    Receive updates about new features and tips
                  </p>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={emailNotifications}
                    onChange={(e) => setEmailNotifications(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-200 rounded-full peer peer-checked:bg-teal-600 transition-colors" />
                  <div className="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow peer-checked:translate-x-5 transition-transform" />
                </div>
              </label>
            </div>

            {/* Save Button */}
            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full py-4 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Save Changes
                </>
              )}
            </button>

            {/* Danger Zone */}
            <div className="bg-white rounded-2xl border border-red-200 p-6">
              <h2 className="text-lg font-semibold text-red-600 mb-4 flex items-center gap-2">
                <Trash2 className="w-5 h-5" />
                Danger Zone
              </h2>

              <p className="text-sm text-slate-600 mb-4">
                Permanently delete your account and all associated data. This action cannot be
                undone.
              </p>

              {showDeleteConfirm ? (
                <div className="space-y-4">
                  <p className="text-sm text-red-600 font-medium">Type "DELETE" to confirm:</p>
                  <input
                    type="text"
                    value={deleteConfirmText}
                    onChange={(e) => setDeleteConfirmText(e.target.value)}
                    placeholder="DELETE"
                    className="w-full px-4 py-3 bg-white border border-red-200 rounded-xl focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-100"
                  />
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        setShowDeleteConfirm(false)
                        setDeleteConfirmText('')
                      }}
                      className="flex-1 py-3 bg-slate-100 text-slate-700 font-medium rounded-xl hover:bg-slate-200 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleDeleteAccount}
                      disabled={deleteConfirmText !== 'DELETE'}
                      className="flex-1 py-3 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Delete Account
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="px-6 py-3 bg-red-50 text-red-600 font-medium rounded-xl hover:bg-red-100 transition-colors"
                >
                  Delete My Account
                </button>
              )}
            </div>
          </div>

          {/* Sidebar - Usage Stats */}
          <div className="space-y-6">
            {/* Account Info */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Account</h2>

              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-slate-100">
                  <span className="text-slate-600">Plan</span>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      profile?.tier === 'paid'
                        ? 'bg-teal-100 text-teal-700'
                        : profile?.tier === 'super_admin'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {profile?.tier === 'super_admin'
                      ? 'Admin'
                      : profile?.tier?.charAt(0).toUpperCase() + profile?.tier?.slice(1)}
                  </span>
                </div>

                <div className="flex justify-between items-center py-2 border-b border-slate-100">
                  <span className="text-slate-600">Member since</span>
                  <span className="text-slate-900 font-medium">
                    {usage?.member_since ? new Date(usage.member_since).toLocaleDateString() : '-'}
                  </span>
                </div>

                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">Status</span>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      profile?.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {profile?.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>

            {/* Usage Stats */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-slate-600" />
                Usage Statistics
              </h2>

              <div className="space-y-4">
                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                  <div className="p-2 bg-teal-100 rounded-lg">
                    <Search className="w-4 h-4 text-teal-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">
                      {usage?.total_searches || 0}
                    </p>
                    <p className="text-sm text-slate-500">Total Searches</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Bookmark className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">
                      {usage?.total_saved_searches || 0}
                    </p>
                    <p className="text-sm text-slate-500">Saved Searches</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                  <div className="p-2 bg-amber-100 rounded-lg">
                    <ThumbsUp className="w-4 h-4 text-amber-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">
                      {usage?.total_feedback_given || 0}
                    </p>
                    <p className="text-sm text-slate-500">Feedback Given</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Calendar className="w-4 h-4 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">
                      {usage?.searches_this_month || 0}
                    </p>
                    <p className="text-sm text-slate-500">Searches This Month</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Upgrade CTA */}
            {profile?.tier === 'free' && (
              <div className="bg-gradient-to-br from-teal-600 to-teal-700 rounded-2xl p-6 text-white">
                <h3 className="font-bold text-lg mb-2">Upgrade to Pro</h3>
                <p className="text-teal-100 text-sm mb-4">
                  Get unlimited searches and AI explanations
                </p>
                <button className="w-full py-3 bg-white text-teal-700 font-semibold rounded-xl hover:bg-teal-50 transition-colors">
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
