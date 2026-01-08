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
      color: 'text-amber-600 dark:text-amber-400',
      bgColor: 'bg-amber-50 dark:bg-amber-900/30',
      borderColor: 'border-amber-200 dark:border-amber-700',
    },
    {
      label: 'Total Searches',
      value: searchesTotal.toLocaleString(),
      icon: Search,
      color: 'text-teal-600 dark:text-teal-400',
      bgColor: 'bg-teal-50 dark:bg-teal-900/30',
      borderColor: 'border-teal-200 dark:border-teal-700',
    },
    {
      label: 'Saved Searches',
      value: savedSearchesCount.toString(),
      icon: Bookmark,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/30',
      borderColor: 'border-blue-200 dark:border-blue-700',
    },
    {
      label: 'Account Tier',
      value: tier.charAt(0).toUpperCase() + tier.slice(1),
      icon: TrendingUp,
      color: tier === 'paid' ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-600 dark:text-slate-400',
      bgColor: tier === 'paid' ? 'bg-emerald-50 dark:bg-emerald-900/30' : 'bg-slate-50 dark:bg-slate-700/50',
      borderColor: tier === 'paid' ? 'border-emerald-200 dark:border-emerald-700' : 'border-slate-200 dark:border-slate-600',
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
          <div className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{stat.value}</div>
          <div className="text-sm text-slate-500 dark:text-slate-400">{stat.label}</div>
        </div>
      ))}
    </div>
  )
}
