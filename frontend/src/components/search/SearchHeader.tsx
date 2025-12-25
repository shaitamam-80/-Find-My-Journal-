import { Link } from 'react-router-dom'
import { BookOpen, LogOut, Zap, Infinity as InfinityIcon } from 'lucide-react'

interface SearchLimits {
  used_today: number
  daily_limit: number | null
  can_search: boolean
}

interface SearchHeaderProps {
  userEmail?: string
  limits?: SearchLimits | null
  onSignOut: () => void
}

export function SearchHeader({ userEmail, limits, onSignOut }: SearchHeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center group-hover:bg-slate-800 transition-colors">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-slate-900 tracking-tight">
              FindMyJournal
            </span>
          </Link>

          {/* Right side */}
          <div className="flex items-center gap-6">
            {/* Search limits */}
            {limits && (
              <div
                className={`hidden sm:flex items-center gap-2 px-4 py-2 rounded-full ${
                  limits.daily_limit !== null
                    ? 'bg-amber-50 border border-amber-200'
                    : 'bg-teal-50 border border-teal-200'
                }`}
              >
                {limits.daily_limit !== null ? (
                  <>
                    <Zap className="w-4 h-4 text-amber-600" />
                    <span className="text-sm font-medium text-amber-700">
                      Searches today: {limits.used_today}/{limits.daily_limit}
                    </span>
                  </>
                ) : (
                  <>
                    <InfinityIcon className="w-4 h-4 text-teal-600" />
                    <span className="text-sm font-medium text-teal-700">Unlimited</span>
                  </>
                )}
              </div>
            )}

            {/* User menu */}
            <div className="flex items-center gap-3">
              <span className="hidden md:block text-sm text-gray-500">{userEmail}</span>
              <button
                onClick={onSignOut}
                className="flex items-center gap-2 px-3 py-2 rounded-xl transition-all text-gray-600 hover:bg-gray-100 hover:text-gray-800"
                title="Sign out"
              >
                <LogOut className="w-5 h-5" />
                <span className="hidden sm:inline text-sm font-medium">Sign out</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
