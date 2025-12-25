import { Search, Bookmark, TrendingUp, Zap } from 'lucide-react'

interface StatsOverviewProps {
  searchesToday: number
  searchesTotal: number
  savedSearchesCount: number
  dailyLimit: number | null
  tier: string
}

export function StatsOverview({
  searchesToday,
  searchesTotal,
  savedSearchesCount,
  dailyLimit,
  tier,
}: StatsOverviewProps) {
  const stats = [
    {
      label: 'Searches Today',
      value: dailyLimit ? `${searchesToday}/${dailyLimit}` : searchesToday.toString(),
      icon: Zap,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
    },
    {
      label: 'Total Searches',
      value: searchesTotal.toLocaleString(),
      icon: Search,
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      borderColor: 'border-teal-200',
    },
    {
      label: 'Saved Searches',
      value: savedSearchesCount.toString(),
      icon: Bookmark,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
    {
      label: 'Account Tier',
      value: tier.charAt(0).toUpperCase() + tier.slice(1),
      icon: TrendingUp,
      color: tier === 'paid' ? 'text-emerald-600' : 'text-slate-600',
      bgColor: tier === 'paid' ? 'bg-emerald-50' : 'bg-slate-50',
      borderColor: tier === 'paid' ? 'border-emerald-200' : 'border-slate-200',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`${stat.bgColor} ${stat.borderColor} border rounded-2xl p-6 transition-shadow hover:shadow-md`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className={`p-2 rounded-xl ${stat.bgColor}`}>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 mb-1">{stat.value}</div>
          <div className="text-sm text-slate-500">{stat.label}</div>
        </div>
      ))}
    </div>
  )
}
