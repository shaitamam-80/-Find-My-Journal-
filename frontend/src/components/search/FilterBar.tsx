import { Filter } from 'lucide-react'
import type { FilterType } from '../../utils/searchResultsMapper'

interface FilterBarProps {
  activeFilter: FilterType
  onFilterChange: (filter: FilterType) => void
}

const filters: { key: FilterType; label: string }[] = [
  { key: 'all', label: 'All Results' },
  { key: 'openAccess', label: 'Open Access' },
  { key: 'highHIndex', label: 'High H-Index' },
  // TODO: [FUTURE_DATA] fastReview - requires timeToDecision data
]

export function FilterBar({ activeFilter, onFilterChange }: FilterBarProps) {
  return (
    <div className="flex items-center gap-4 mb-8 flex-wrap">
      <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
        <Filter className="w-5 h-5" />
        <span className="font-semibold">Filter:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {filters.map((filter) => (
          <button
            key={filter.key}
            onClick={() => onFilterChange(filter.key)}
            className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${
              activeFilter === filter.key
                ? 'bg-slate-900 dark:bg-teal-600 text-white shadow-sm'
                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600 hover:border-slate-300 dark:hover:border-slate-500 hover:bg-slate-50 dark:hover:bg-slate-700'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>
    </div>
  )
}
