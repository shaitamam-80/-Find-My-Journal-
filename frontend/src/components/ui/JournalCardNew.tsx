import { useState, useCallback, memo } from 'react'
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  TrendingUp,
  FileText,
  DollarSign,
  Unlock,
  Sparkles,
  Loader2,
  Bookmark,
  BookmarkCheck,
} from 'lucide-react'
import type { Journal, VerificationStatus } from '../../types'
import { VerificationBadge } from './VerificationBadge'

// ============================================================================
// Types
// ============================================================================

/** Category configuration for visual styling */
interface CategoryConfig {
  key: JournalCategoryKey
  label: string
  gradient: string
  bg: string
  border: string
  text: string
}

type JournalCategoryKey = 'topTier' | 'niche' | 'methodology' | 'broad'

/** Props for the JournalCard component */
interface JournalCardProps {
  /** Journal data from API */
  journal: Journal
  /** Category key for styling */
  category: JournalCategoryKey
  /** Whether the card is expanded */
  isExpanded?: boolean
  /** Callback when card expansion is toggled */
  onToggle?: () => void
  /** Whether this journal is saved by the user */
  isSaved?: boolean
  /** Callback when save button is clicked */
  onSave?: (journalId: string) => void
  /** User's abstract for AI explanations */
  abstract?: string
  /** Session token for API calls */
  sessionToken?: string | null
}

// ============================================================================
// Constants
// ============================================================================

const CATEGORY_CONFIG: Record<JournalCategoryKey, CategoryConfig> = {
  topTier: {
    key: 'topTier',
    label: 'Top Tier',
    gradient: 'from-emerald-500 to-emerald-600',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-700',
  },
  niche: {
    key: 'niche',
    label: 'Niche Specialist',
    gradient: 'from-blue-500 to-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-700',
  },
  methodology: {
    key: 'methodology',
    label: 'Methodology Focus',
    gradient: 'from-purple-500 to-purple-600',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    text: 'text-purple-700',
  },
  broad: {
    key: 'broad',
    label: 'Broad Scope',
    gradient: 'from-amber-500 to-amber-600',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
  },
}

// ============================================================================
// Utility Functions
// ============================================================================

/** Generate journal acronym from name */
function generateAcronym(name: string): string {
  return name
    .split(/[\s-]+/)
    .filter((word) => word.length > 2 && word[0] === word[0].toUpperCase())
    .map((word) => word[0])
    .join('')
    .slice(0, 4)
}

/** Convert relevance score to display percentage */
function toMatchPercentage(score: number): number {
  // Score is already 0-1, convert to 0-100
  return Math.round(Math.min(1, Math.max(0, score)) * 100)
}

// ============================================================================
// Sub-components
// ============================================================================

/** Badge displaying match score with color coding */
const MatchScoreBadge = memo(function MatchScoreBadge({
  score,
  gradient,
}: {
  score: number
  gradient: string
}) {
  return (
    <div className="flex flex-col items-center flex-shrink-0">
      <div
        className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}
      >
        <span className="text-xl font-bold text-white">{score}%</span>
      </div>
      <span className="text-xs text-gray-500 mt-1 font-medium">Match</span>
    </div>
  )
})

/** Row of journal metadata badges */
const JournalBadges = memo(function JournalBadges({
  acronym,
  publisher,
  isOA,
  verification,
}: {
  acronym: string
  publisher: string | null
  isOA: boolean
  verification?: VerificationStatus
}) {
  return (
    <div className="flex items-center gap-3 mb-2 flex-wrap">
      <span className="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs font-semibold rounded-full">
        {acronym}
      </span>

      {publisher && (
        <span className="px-2.5 py-1 bg-gray-50 text-gray-500 text-xs rounded-full">
          {publisher}
        </span>
      )}

      {isOA && (
        <span className="px-2.5 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full flex items-center gap-1">
          <Unlock className="w-3 h-3" />
          Open Access
        </span>
      )}

      {verification && <VerificationBadge verification={verification} />}
    </div>
  )
})

/** Quick stats row showing journal metrics */
const MetricsRow = memo(function MetricsRow({
  metrics,
  apcUsd,
}: {
  metrics: Journal['metrics']
  apcUsd: number | null
}) {
  return (
    <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600 mt-3">
      {metrics.h_index !== null && (
        <div className="flex items-center gap-1.5 bg-teal-50 px-3 py-1.5 rounded-lg">
          <TrendingUp className="w-4 h-4 text-teal-600" />
          <span>
            Journal H-Index:{' '}
            <strong className="text-teal-700">{metrics.h_index}</strong>
          </span>
        </div>
      )}

      {metrics.two_yr_mean_citedness !== null && (
        <div
          className="flex items-center gap-1.5 bg-blue-50 px-3 py-1.5 rounded-lg"
          title="Average citations per paper in the last 2 years"
        >
          <TrendingUp className="w-4 h-4 text-blue-600" />
          <span>
            2yr Citations:{' '}
            <strong className="text-blue-700">
              {metrics.two_yr_mean_citedness.toFixed(1)}
            </strong>
          </span>
        </div>
      )}

      {metrics.works_count !== null && (
        <div className="flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-lg">
          <FileText className="w-4 h-4 text-gray-500" />
          <span>
            Works:{' '}
            <strong className="text-gray-700">
              {metrics.works_count.toLocaleString()}
            </strong>
          </span>
        </div>
      )}

      {apcUsd !== null && (
        <div className="flex items-center gap-1.5 bg-amber-50 px-3 py-1.5 rounded-lg">
          <DollarSign className="w-4 h-4 text-amber-500" />
          <span className="text-amber-700">APC: ${apcUsd}</span>
        </div>
      )}
    </div>
  )
})

/** Topics list with "show more" truncation */
const TopicsList = memo(function TopicsList({ topics }: { topics: string[] }) {
  const MAX_VISIBLE = 6

  if (topics.length === 0) return null

  return (
    <div className="mt-5">
      <h4 className="text-sm font-semibold text-gray-600 mb-2">Topics:</h4>
      <div className="flex flex-wrap gap-2">
        {topics.slice(0, MAX_VISIBLE).map((topic, i) => (
          <span
            key={i}
            className="px-3 py-1.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg"
          >
            {topic}
          </span>
        ))}
        {topics.length > MAX_VISIBLE && (
          <span className="px-3 py-1.5 bg-gray-50 text-gray-400 text-sm rounded-lg">
            +{topics.length - MAX_VISIBLE} more
          </span>
        )}
      </div>
    </div>
  )
})

/** Save button with loading and saved states */
const SaveButton = memo(function SaveButton({
  isSaved,
  isLoading,
  onClick,
}: {
  isSaved: boolean
  isLoading: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={`flex items-center gap-2 px-4 py-3.5 font-semibold rounded-xl transition-all ${
        isSaved
          ? 'bg-teal-100 text-teal-700 hover:bg-teal-200'
          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
      } disabled:opacity-50`}
      aria-label={isSaved ? 'Remove from saved' : 'Save journal'}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : isSaved ? (
        <BookmarkCheck className="w-4 h-4" />
      ) : (
        <Bookmark className="w-4 h-4" />
      )}
      {isSaved ? 'Saved' : 'Save'}
    </button>
  )
})

// ============================================================================
// Main Component
// ============================================================================

/**
 * Expandable journal card displaying journal information and metrics.
 *
 * Features:
 * - Collapsed view with name, badges, and match score
 * - Expanded view with full metrics, topics, and actions
 * - Save to favorites functionality
 * - AI explanation generation (when abstract provided)
 * - Accessibility-friendly with keyboard navigation
 *
 * @example
 * ```tsx
 * <JournalCard
 *   journal={journal}
 *   category="topTier"
 *   isExpanded={expandedId === journal.id}
 *   onToggle={() => setExpandedId(journal.id)}
 *   isSaved={savedJournals.has(journal.id)}
 *   onSave={handleSaveJournal}
 * />
 * ```
 */
export const JournalCard = memo(function JournalCard({
  journal,
  category,
  isExpanded = false,
  onToggle,
  isSaved = false,
  onSave,
}: JournalCardProps) {
  const [saveLoading, setSaveLoading] = useState(false)

  const config = CATEGORY_CONFIG[category]
  const matchScore = toMatchPercentage(journal.relevance_score)
  const acronym = generateAcronym(journal.name)

  const handleSave = useCallback(async () => {
    if (!onSave || saveLoading) return

    setSaveLoading(true)
    try {
      await onSave(journal.id)
    } finally {
      setSaveLoading(false)
    }
  }, [journal.id, onSave, saveLoading])

  return (
    <article
      className={`bg-white rounded-2xl border ${
        isExpanded
          ? 'border-teal-200 shadow-lg'
          : 'border-slate-200 shadow-sm hover:shadow-md'
      } overflow-hidden transition-all duration-300`}
      aria-expanded={isExpanded}
    >
      {/* Header - Always visible, clickable to expand */}
      <button
        onClick={onToggle}
        className="w-full p-6 text-start hover:bg-gray-50/50 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-inset"
        aria-label={`${isExpanded ? 'Collapse' : 'Expand'} ${journal.name} details`}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-gray-800 truncate mb-1">
              {journal.name}
            </h3>

            <JournalBadges
              acronym={acronym}
              publisher={journal.publisher}
              isOA={journal.is_oa}
              verification={journal.verification}
            />

            <MetricsRow metrics={journal.metrics} apcUsd={journal.apc_usd} />
          </div>

          {/* Match Score */}
          <MatchScoreBadge score={matchScore} gradient={config.gradient} />

          {/* Expand/Collapse Icon */}
          <div
            className={`p-2 rounded-full transition-colors ${
              isExpanded ? 'bg-teal-50' : 'bg-slate-100'
            }`}
            aria-hidden="true"
          >
            {isExpanded ? (
              <ChevronUp
                className={`w-5 h-5 ${isExpanded ? 'text-teal-600' : 'text-slate-400'}`}
              />
            ) : (
              <ChevronDown className="w-5 h-5 text-slate-400" />
            )}
          </div>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-100">
          {/* Category Badge */}
          <div className={`mt-5 inline-flex items-center gap-2 px-3 py-1.5 ${config.bg} ${config.border} border rounded-full`}>
            <Sparkles className={`w-4 h-4 ${config.text}`} />
            <span className={`text-sm font-medium ${config.text}`}>
              {config.label}
            </span>
          </div>

          {/* Match Reason */}
          {journal.match_reason && (
            <p className="mt-4 text-gray-600 text-sm leading-relaxed">
              {journal.match_reason}
            </p>
          )}

          {/* Topics */}
          <TopicsList topics={journal.topics} />

          {/* Action Buttons */}
          <div className="mt-5 flex flex-wrap gap-3">
            {journal.homepage_url && (
              <a
                href={journal.homepage_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 min-w-[200px] py-3.5 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-all flex items-center justify-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Visit Journal Website
              </a>
            )}

            {onSave && (
              <SaveButton
                isSaved={isSaved}
                isLoading={saveLoading}
                onClick={handleSave}
              />
            )}
          </div>
        </div>
      )}
    </article>
  )
})

export default JournalCard
