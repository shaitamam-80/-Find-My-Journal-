import { cn } from '../../lib/utils'

type CategoryType = 'top-tier' | 'niche' | 'methodology' | 'broad'

interface StatusBadgeProps {
  category: CategoryType
  className?: string
}

const categoryStyles: Record<CategoryType, string> = {
  'top-tier': 'bg-emerald-100 text-emerald-800 border-emerald-200',
  'niche': 'bg-blue-100 text-blue-800 border-blue-200',
  'methodology': 'bg-purple-100 text-purple-800 border-purple-200',
  'broad': 'bg-amber-100 text-amber-800 border-amber-200',
}

const categoryLabels: Record<CategoryType, string> = {
  'top-tier': 'Top-Tier',
  'niche': 'Niche Specialist',
  'methodology': 'Methodology',
  'broad': 'Broad Scope',
}

export function StatusBadge({ category, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        categoryStyles[category],
        className
      )}
    >
      {categoryLabels[category]}
    </span>
  )
}
