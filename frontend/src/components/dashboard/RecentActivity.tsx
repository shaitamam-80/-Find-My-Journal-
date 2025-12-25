import { Search, Bookmark, ThumbsUp, Clock } from 'lucide-react'

interface Activity {
  id: string
  type: 'search' | 'save' | 'feedback'
  description: string
  created_at: string
  metadata?: Record<string, unknown>
}

interface RecentActivityProps {
  activities: Activity[]
  loading?: boolean
}

function getActivityIcon(type: string) {
  switch (type) {
    case 'search':
      return { icon: Search, color: 'text-teal-600', bgColor: 'bg-teal-100' }
    case 'save':
      return { icon: Bookmark, color: 'text-blue-600', bgColor: 'bg-blue-100' }
    case 'feedback':
      return { icon: ThumbsUp, color: 'text-amber-600', bgColor: 'bg-amber-100' }
    default:
      return { icon: Clock, color: 'text-slate-600', bgColor: 'bg-slate-100' }
  }
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString()
}

export function RecentActivity({ activities, loading }: RecentActivityProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-start gap-4 animate-pulse">
              <div className="w-10 h-10 bg-slate-200 rounded-xl" />
              <div className="flex-1">
                <div className="h-4 bg-slate-200 rounded w-3/4 mb-2" />
                <div className="h-3 bg-slate-100 rounded w-1/4" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (activities.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h2>
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Clock className="w-8 h-8 text-slate-400" />
          </div>
          <p className="text-slate-500">No activity yet</p>
          <p className="text-sm text-slate-400 mt-1">
            Start searching for journals to see your activity here
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h2>
      <div className="space-y-4">
        {activities.map((activity) => {
          const { icon: Icon, color, bgColor } = getActivityIcon(activity.type)

          return (
            <div
              key={activity.id}
              className="flex items-start gap-4 p-3 rounded-xl hover:bg-slate-50 transition-colors"
            >
              <div className={`p-2.5 rounded-xl ${bgColor}`}>
                <Icon className={`w-5 h-5 ${color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-700 truncate">{activity.description}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {formatRelativeTime(activity.created_at)}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
