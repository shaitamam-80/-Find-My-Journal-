import { Star, Target, FlaskConical, Globe } from 'lucide-react'
import type { Journal } from '../../types'
import { type JournalCategoryKey, categoryConfig } from '../../utils/searchResultsMapper'
import { AccordionJournalCard } from './AccordionJournalCard'

// Icon mapping for categories
const categoryIcons = {
  topTier: Star,
  niche: Target,
  methodology: FlaskConical,
  broad: Globe,
} as const

interface CategorySectionProps {
  categoryKey: JournalCategoryKey
  journals: Journal[]
  expandedIds: Set<string>
  onToggle: (id: string) => void
}

export function CategorySection({
  categoryKey,
  journals,
  expandedIds,
  onToggle,
}: CategorySectionProps) {
  // Don't render if no journals in this category
  if (!journals || journals.length === 0) return null

  const config = categoryConfig[categoryKey]
  const Icon = categoryIcons[categoryKey]

  return (
    <div className="mb-10">
      {/* Category Header */}
      <div className="flex items-center gap-3 mb-5">
        <div
          className={`p-2.5 rounded-xl bg-gradient-to-br ${config.gradient} text-white shadow-lg`}
        >
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-800">{config.title}</h2>
          <p className="text-sm text-gray-500">{config.subtitle}</p>
        </div>
        <span className="ml-auto px-4 py-1.5 bg-white text-gray-600 text-sm font-semibold rounded-full shadow-sm border border-gray-100">
          {journals.length} {journals.length === 1 ? 'journal' : 'journals'}
        </span>
      </div>

      {/* Journal Cards */}
      <div className="space-y-4">
        {journals.map((journal) => (
          <AccordionJournalCard
            key={journal.id}
            journal={journal}
            categoryKey={categoryKey}
            isExpanded={expandedIds.has(journal.id)}
            onToggle={() => onToggle(journal.id)}
          />
        ))}
      </div>
    </div>
  )
}
