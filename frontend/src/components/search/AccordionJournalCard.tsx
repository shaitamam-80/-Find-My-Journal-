import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Lightbulb,
  TrendingUp,
  FileText,
  DollarSign,
  Unlock,
} from 'lucide-react'
import type { Journal } from '../../types'
import {
  type JournalCategoryKey,
  categoryConfig,
  generateAcronym,
  toMatchPercentage,
} from '../../utils/searchResultsMapper'

interface AccordionJournalCardProps {
  journal: Journal
  categoryKey: JournalCategoryKey
  isExpanded: boolean
  onToggle: () => void
}

export function AccordionJournalCard({
  journal,
  categoryKey,
  isExpanded,
  onToggle,
}: AccordionJournalCardProps) {
  const catConfig = categoryConfig[categoryKey]
  const matchScore = toMatchPercentage(journal.relevance_score)
  const acronym = generateAcronym(journal.name)

  return (
    <div
      className={`bg-white rounded-2xl border-2 ${
        isExpanded
          ? 'border-blue-300 shadow-xl shadow-blue-100/50'
          : 'border-gray-100 shadow-md'
      } overflow-hidden transition-all duration-300`}
    >
      {/* Card Header - Always Visible */}
      <button
        onClick={onToggle}
        className="w-full p-6 text-start hover:bg-gray-50/50 transition-colors"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <h3 className="text-lg font-bold text-gray-800">{journal.name}</h3>
              <span className="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs font-semibold rounded-full">
                {acronym}
              </span>
              {journal.publisher && (
                <span className="px-2.5 py-1 bg-gray-50 text-gray-500 text-xs rounded-full">
                  {journal.publisher}
                </span>
              )}
              {journal.is_oa && (
                <span className="px-2.5 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full flex items-center gap-1">
                  <Unlock className="w-3 h-3" />
                  Open Access
                </span>
              )}
            </div>

            {/* Quick Stats Row - REAL DATA ONLY */}
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mt-3">
              {journal.metrics.h_index !== null && (
                <div className="flex items-center gap-1.5 bg-blue-50 px-3 py-1.5 rounded-lg">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <span>
                    Journal H-Index: <strong className="text-blue-700">{journal.metrics.h_index}</strong>
                  </span>
                </div>
              )}
              {journal.metrics.works_count !== null && (
                <div className="flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-lg">
                  <FileText className="w-4 h-4 text-gray-500" />
                  <span>
                    Works: <strong className="text-gray-700">{journal.metrics.works_count.toLocaleString()}</strong>
                  </span>
                </div>
              )}
              {journal.apc_usd !== null && (
                <div className="flex items-center gap-1.5 bg-amber-50 px-3 py-1.5 rounded-lg">
                  <DollarSign className="w-4 h-4 text-amber-500" />
                  <span className="text-amber-700">APC: ${journal.apc_usd}</span>
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
            <span className="text-xs text-gray-500 mt-1 font-medium">Match</span>
          </div>

          {/* Expand Icon */}
          <div
            className={`p-2 rounded-full transition-colors ${
              isExpanded ? 'bg-blue-100' : 'bg-gray-100'
            }`}
          >
            {isExpanded ? (
              <ChevronUp className={`w-5 h-5 ${isExpanded ? 'text-blue-600' : 'text-gray-400'}`} />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-100">
          {/* Why It's a Good Fit - uses match_reason */}
          {journal.match_reason && (
            <div className={`mt-5 p-5 ${catConfig.bg} rounded-2xl border ${catConfig.border}`}>
              <div className="flex items-center gap-2 mb-3">
                <div className={`p-1.5 rounded-lg bg-gradient-to-br ${catConfig.gradient}`}>
                  <Lightbulb className="w-4 h-4 text-white" />
                </div>
                <h4 className={`font-bold ${catConfig.text}`}>Why It's a Good Fit</h4>
              </div>
              <p className="text-gray-700 leading-relaxed">{journal.match_reason}</p>

              {/* TODO: [FUTURE_DATA] considerations - AI-generated strategic advice */}
            </div>
          )}

          {/* TODO: [FUTURE_DATA] indexed - Scopus/DOAJ/PubMed APIs */}

          {/* Topics */}
          {journal.topics.length > 0 && (
            <div className="mt-5">
              <h4 className="text-sm font-semibold text-gray-600 mb-2">Topics:</h4>
              <div className="flex flex-wrap gap-2">
                {journal.topics.slice(0, 6).map((topic, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg"
                  >
                    {topic}
                  </span>
                ))}
                {journal.topics.length > 6 && (
                  <span className="px-3 py-1.5 bg-gray-50 text-gray-400 text-sm rounded-lg">
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
                className="flex-1 py-3.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-200 transition-all flex items-center justify-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Visit Journal Website
              </a>
            )}
            {/* TODO: [FUTURE_DATA] Save button - requires backend support */}
          </div>
        </div>
      )}
    </div>
  )
}
