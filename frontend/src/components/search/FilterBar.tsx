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
      <div className="flex items-center gap-2 text-slate-600">
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
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-white text-slate-600 border border-slate-200 hover:border-slate-300 hover:bg-slate-50'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>
    </div>
  )
}
