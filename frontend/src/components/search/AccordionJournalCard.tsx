import { useState } from 'react'
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Lightbulb,
  TrendingUp,
  FileText,
  DollarSign,
  Unlock,
  Sparkles,
  Loader2,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react'
import type { Journal } from '../../types'
import { api } from '../../services/api'
import { logger } from '../../lib/logger'
import {
  type JournalCategoryKey,
  categoryConfig,
  generateAcronym,
  toMatchPercentage,
} from '../../utils/searchResultsMapper'
import { VerificationBadge } from '../ui/VerificationBadge'

interface AccordionJournalCardProps {
  journal: Journal
  categoryKey: JournalCategoryKey
  isExpanded: boolean
  onToggle: () => void
  /** User's abstract for generating AI explanations */
  abstract?: string
  /** Auth token for API calls */
  sessionToken?: string | null
}

export function AccordionJournalCard({
  journal,
  categoryKey,
  isExpanded,
  onToggle,
  abstract,
  sessionToken,
}: AccordionJournalCardProps) {
  const catConfig = categoryConfig[categoryKey]
  const matchScore = toMatchPercentage(journal.relevance_score)
  const acronym = generateAcronym(journal.name)

  // AI Explanation state
  const [explanation, setExplanation] = useState<string | null>(null)
  const [explanationLoading, setExplanationLoading] = useState(false)
  const [explanationError, setExplanationError] = useState<string | null>(null)
  const [isAiGenerated, setIsAiGenerated] = useState(false)

  // Feedback state (Story 5.1)
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null)
  const [feedbackLoading, setFeedbackLoading] = useState(false)

  const handleGetExplanation = async () => {
    if (!sessionToken || !abstract || explanation) return

    setExplanationLoading(true)
    setExplanationError(null)

    try {
      const result = await api.getJournalExplanation(sessionToken, abstract, journal)
      setExplanation(result.explanation)
      setIsAiGenerated(result.is_ai_generated)
    } catch (err) {
      setExplanationError(err instanceof Error ? err.message : 'Failed to generate explanation')
    } finally {
      setExplanationLoading(false)
    }
  }

  // Handle feedback submission with optimistic update (Story 5.1)
  const handleFeedback = async (rating: 'up' | 'down') => {
    if (!sessionToken || feedbackLoading) return

    // Store previous state for rollback
    const previousFeedback = feedback

    // Toggle off if clicking same rating
    const newFeedback = feedback === rating ? null : rating

    // Optimistic update - update UI immediately
    setFeedback(newFeedback)

    // Skip API call if just toggling off
    if (newFeedback === null) return

    setFeedbackLoading(true)
    try {
      await api.submitFeedback(sessionToken, journal.id, rating)
    } catch (err) {
      // Rollback on error
      setFeedback(previousFeedback)
      logger.error('Failed to submit feedback', err, { journalId: journal.id, rating })
    } finally {
      setFeedbackLoading(false)
    }
  }

  return (
    <div
      className={`bg-white dark:bg-slate-800 rounded-2xl border ${
        isExpanded
          ? 'border-teal-200 dark:border-teal-700 shadow-lg'
          : 'border-slate-200 dark:border-slate-700 shadow-sm'
      } overflow-hidden transition-all duration-300`}
    >
      {/* Card Header - Always Visible */}
      <button
        onClick={onToggle}
        className="w-full p-6 text-start hover:bg-gray-50/50 dark:hover:bg-slate-700/50 transition-colors"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <h3 className="text-lg font-bold text-gray-800 dark:text-white">{journal.name}</h3>
              <span className="px-2.5 py-1 bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-slate-300 text-xs font-semibold rounded-full">
                {acronym}
              </span>
              {journal.publisher && (
                <span className="px-2.5 py-1 bg-gray-50 dark:bg-slate-700 text-gray-500 dark:text-slate-400 text-xs rounded-full">
                  {journal.publisher}
                </span>
              )}
              {journal.is_oa && (
                <span className="px-2.5 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-semibold rounded-full flex items-center gap-1">
                  <Unlock className="w-3 h-3" />
                  Open Access
                </span>
              )}
              {/* Verification Badge */}
              {journal.verification && (
                <VerificationBadge verification={journal.verification} />
              )}
            </div>

            {/* Quick Stats Row - REAL DATA ONLY */}
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600 dark:text-slate-300 mt-3">
              {journal.metrics.h_index !== null && (
                <div className="flex items-center gap-1.5 bg-teal-50 dark:bg-teal-900/30 px-3 py-1.5 rounded-lg">
                  <TrendingUp className="w-4 h-4 text-teal-600 dark:text-teal-400" />
                  <span>
                    Journal H-Index: <strong className="text-teal-700 dark:text-teal-400">{journal.metrics.h_index}</strong>
                  </span>
                </div>
              )}
              {journal.metrics.two_yr_mean_citedness !== null && (
                <div
                  className="flex items-center gap-1.5 bg-blue-50 dark:bg-blue-900/30 px-3 py-1.5 rounded-lg"
                  title="Average citations per paper in the last 2 years (similar to Impact Factor)"
                >
                  <TrendingUp className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span>
                    2yr Citations: <strong className="text-blue-700 dark:text-blue-400">{journal.metrics.two_yr_mean_citedness.toFixed(1)}</strong>
                  </span>
                </div>
              )}
              {journal.metrics.works_count !== null && (
                <div className="flex items-center gap-1.5 bg-gray-50 dark:bg-slate-700 px-3 py-1.5 rounded-lg">
                  <FileText className="w-4 h-4 text-gray-500 dark:text-slate-400" />
                  <span>
                    Works: <strong className="text-gray-700 dark:text-slate-300">{journal.metrics.works_count.toLocaleString()}</strong>
                  </span>
                </div>
              )}
              {journal.apc_usd !== null && (
                <div className="flex items-center gap-1.5 bg-amber-50 dark:bg-amber-900/30 px-3 py-1.5 rounded-lg">
                  <DollarSign className="w-4 h-4 text-amber-500 dark:text-amber-400" />
                  <span className="text-amber-700 dark:text-amber-400">APC: ${journal.apc_usd}</span>
                </div>
              )}
              {/* TODO: [FUTURE_DATA] impactFactor - Scimago API */}
              {/* TODO: [FUTURE_DATA] acceptanceRate - external source */}
              {/* TODO: [FUTURE_DATA] timeToDecision - external source */}
              {/* TODO: [FUTURE_DATA] articleType - external source */}
            </div>
          </div>

          {/* Match Score */}
          <div className="flex flex-col items-center flex-shrink-0">
            <div
              className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${catConfig.gradient} flex items-center justify-center shadow-lg`}
            >
              <span className="text-xl font-bold text-white">{matchScore}%</span>
            </div>
            <span className="text-xs text-gray-500 dark:text-slate-400 mt-1 font-medium">Match</span>
          </div>

          {/* Expand Icon */}
          <div
            className={`p-2 rounded-full transition-colors ${
              isExpanded ? 'bg-teal-50 dark:bg-teal-900/30' : 'bg-slate-100 dark:bg-slate-700'
            }`}
          >
            {isExpanded ? (
              <ChevronUp className={`w-5 h-5 ${isExpanded ? 'text-teal-600 dark:text-teal-400' : 'text-slate-400'}`} />
            ) : (
              <ChevronDown className="w-5 h-5 text-slate-400" />
            )}
          </div>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-100 dark:border-slate-700">
          {/* Why It's a Good Fit - AI Explanation Section */}
          <div className={`mt-5 p-5 ${catConfig.bg} dark:bg-slate-700/50 rounded-2xl border ${catConfig.border} dark:border-slate-600`}>
            <div className="flex items-center gap-2 mb-3">
              <div className={`p-1.5 rounded-lg bg-gradient-to-br ${catConfig.gradient}`}>
                <Lightbulb className="w-4 h-4 text-white" />
              </div>
              <h4 className={`font-bold ${catConfig.text}`}>Why It's a Good Fit</h4>
              {isAiGenerated && (
                <span className="px-2 py-0.5 bg-teal-100 dark:bg-teal-900/50 text-teal-700 dark:text-teal-300 text-xs font-medium rounded-full flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  AI Generated
                </span>
              )}
            </div>

            {/* AI Explanation Content */}
            {explanation ? (
              <div className="text-gray-700 dark:text-slate-300 leading-relaxed prose prose-sm dark:prose-invert max-w-none">
                {explanation.split('\n').map((line, i) => (
                  <p key={i} className={line.trim() ? 'mb-2' : ''}>{line}</p>
                ))}
              </div>
            ) : explanationLoading ? (
              <div className="flex items-center gap-2 text-gray-500 dark:text-slate-400 py-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating AI explanation...</span>
              </div>
            ) : explanationError ? (
              <div className="space-y-2">
                <p className="text-red-600 dark:text-red-400 text-sm">{explanationError}</p>
                <button
                  onClick={handleGetExplanation}
                  className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 underline"
                >
                  Try again
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Show detailed match_details (Story 1.1) */}
                {journal.match_details && journal.match_details.length > 0 ? (
                  <ul className="space-y-1.5">
                    {journal.match_details.slice(0, 4).map((detail, i) => (
                      <li key={i} className="text-gray-700 dark:text-slate-300 text-sm flex items-start gap-2">
                        <span className="text-teal-500 dark:text-teal-400 mt-0.5">•</span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                ) : journal.match_reason ? (
                  <p className="text-gray-600 dark:text-slate-400 text-sm italic">{journal.match_reason}</p>
                ) : null}

                {/* Matched Topics (Story 1.2) */}
                {journal.matched_topics && journal.matched_topics.length > 0 && (
                  <div className="pt-2 border-t border-gray-100 dark:border-slate-600">
                    <p className="text-xs font-semibold text-gray-500 dark:text-slate-400 mb-2">Matching Research Topics</p>
                    <div className="flex flex-wrap gap-1.5">
                      {journal.matched_topics.slice(0, 5).map((topic, i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-full border border-green-200 dark:border-green-700"
                        >
                          ✓ {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Explanation Button */}
                {abstract && sessionToken && (
                  <button
                    onClick={handleGetExplanation}
                    className="flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white text-sm font-medium rounded-lg hover:bg-teal-700 dark:hover:bg-teal-500 transition-colors"
                  >
                    <Sparkles className="w-4 h-4" />
                    Get AI explanation
                  </button>
                )}
              </div>
            )}
          </div>

          {/* TODO: [FUTURE_DATA] indexed - Scopus/DOAJ/PubMed APIs */}

          {/* Topics */}
          {journal.topics.length > 0 && (
            <div className="mt-5">
              <h4 className="text-sm font-semibold text-gray-600 dark:text-slate-400 mb-2">Topics:</h4>
              <div className="flex flex-wrap gap-2">
                {journal.topics.slice(0, 6).map((topic, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-300 text-sm font-medium rounded-lg"
                  >
                    {topic}
                  </span>
                ))}
                {journal.topics.length > 6 && (
                  <span className="px-3 py-1.5 bg-gray-50 dark:bg-slate-700/50 text-gray-400 dark:text-slate-500 text-sm rounded-lg">
                    +{journal.topics.length - 6} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-5 flex gap-3">
            {journal.homepage_url && (
              <a
                href={journal.homepage_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 py-3.5 bg-slate-900 dark:bg-teal-600 text-white font-semibold rounded-xl hover:bg-slate-800 dark:hover:bg-teal-500 transition-all flex items-center justify-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Visit Journal Website
              </a>
            )}

            {/* Feedback Buttons (Story 5.1) */}
            {sessionToken && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleFeedback('up')}
                  disabled={feedbackLoading}
                  className={`p-3.5 rounded-xl border transition-all ${
                    feedback === 'up'
                      ? 'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700 text-green-700 dark:text-green-400'
                      : 'bg-white dark:bg-slate-700 border-gray-200 dark:border-slate-600 text-gray-500 dark:text-slate-400 hover:border-green-300 dark:hover:border-green-700 hover:text-green-600 dark:hover:text-green-400'
                  }`}
                  title="Good recommendation"
                >
                  <ThumbsUp className={`w-5 h-5 ${feedback === 'up' ? 'fill-current' : ''}`} />
                </button>
                <button
                  onClick={() => handleFeedback('down')}
                  disabled={feedbackLoading}
                  className={`p-3.5 rounded-xl border transition-all ${
                    feedback === 'down'
                      ? 'bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-700 text-red-700 dark:text-red-400'
                      : 'bg-white dark:bg-slate-700 border-gray-200 dark:border-slate-600 text-gray-500 dark:text-slate-400 hover:border-red-300 dark:hover:border-red-700 hover:text-red-600 dark:hover:text-red-400'
                  }`}
                  title="Poor recommendation"
                >
                  <ThumbsDown className={`w-5 h-5 ${feedback === 'down' ? 'fill-current' : ''}`} />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
