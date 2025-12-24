import type { Journal } from '../types'
import { Award, Users, Leaf, Lightbulb, Unlock, TrendingUp, FileText, DollarSign, ExternalLink } from 'lucide-react'
import { VerificationBadge } from './ui/VerificationBadge'

interface JournalCardProps {
  journal: Journal
}

const categoryConfig = {
  top_tier: {
    label: 'Top Tier',
    Icon: Award,
    gradient: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
    border: '#fcd34d',
    text: '#92400e',
    iconColor: '#b45309',
  },
  broad_audience: {
    label: 'Broad Audience',
    Icon: Users,
    gradient: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)',
    border: '#7dd3fc',
    text: '#0369a1',
    iconColor: '#0284c7',
  },
  niche: {
    label: 'Niche',
    Icon: Leaf,
    gradient: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
    border: '#86efac',
    text: '#166534',
    iconColor: '#22c55e',
  },
  emerging: {
    label: 'Emerging',
    Icon: Lightbulb,
    gradient: 'linear-gradient(135deg, #fae8ff 0%, #f5d0fe 100%)',
    border: '#e879f9',
    text: '#86198f',
    iconColor: '#a855f7',
  },
}

export function JournalCard({ journal }: JournalCardProps) {
  const category = journal.category ? categoryConfig[journal.category] : null

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-100/50 overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-blue-100/50 hover:-translate-y-1">
      {/* Category Header */}
      {category && (
        <div
          className="px-5 py-3 flex items-center gap-2"
          style={{ background: category.gradient, borderBottom: `1px solid ${category.border}` }}
        >
          <category.Icon className="w-4 h-4" style={{ color: category.iconColor }} />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: category.text }}>
            {category.label}
          </span>
        </div>
      )}

      {/* Main Content */}
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <h3 className="text-lg font-semibold leading-tight text-gray-800 hover:text-blue-600 transition-colors">
            {journal.name}
          </h3>
          <div className="shrink-0 flex items-center gap-2">
            {/* Verification Badge */}
            {journal.verification && (
              <VerificationBadge verification={journal.verification} />
            )}
            {/* Open Access Badge */}
            {journal.is_oa && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-100">
                <Unlock className="w-3.5 h-3.5 text-green-600" />
                <span className="text-xs font-semibold text-green-700">
                  Open Access
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Match Details (Story 1.1 - Why it's a good fit) */}
        {(journal.match_details?.length || journal.match_reason) && (
          <div
            className="mb-4 p-3.5 rounded-xl"
            style={{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', border: '1px solid #bae6fd' }}
          >
            <div className="flex items-start gap-2.5">
              <div className="shrink-0 w-6 h-6 rounded-lg flex items-center justify-center mt-0.5 bg-blue-200">
                <Lightbulb className="w-3.5 h-3.5 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-xs font-semibold mb-1.5 text-blue-800">
                  Why it's a good fit
                </p>
                {journal.match_details?.length ? (
                  <ul className="space-y-1">
                    {journal.match_details.slice(0, 3).map((detail, i) => (
                      <li key={i} className="text-sm leading-relaxed text-blue-700 flex items-start gap-1.5">
                        <span className="text-blue-400 mt-0.5">•</span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                ) : journal.match_reason ? (
                  <p className="text-sm leading-relaxed text-blue-700">
                    {journal.match_reason}
                  </p>
                ) : null}
              </div>
            </div>
          </div>
        )}

        {/* Matched Topics (Story 1.2 - Topic Badges) */}
        {journal.matched_topics && journal.matched_topics.length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-medium mb-2 text-gray-500">Matching Topics</p>
            <div className="flex flex-wrap gap-1.5">
              {journal.matched_topics.slice(0, 5).map((topic, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200"
                >
                  ✓ {topic}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Publisher */}
        {journal.publisher && (
          <p className="text-sm mb-4 text-gray-500">
            <span className="font-medium text-gray-600">Publisher:</span>{' '}
            {journal.publisher}
          </p>
        )}

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
          {journal.metrics.h_index !== null && (
            <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-3.5 h-3.5 text-gray-400" />
                <span className="text-xs font-medium text-gray-500">H-Index</span>
              </div>
              <p className="text-xl font-bold text-blue-600">
                {journal.metrics.h_index}
              </p>
            </div>
          )}

          {journal.metrics.works_count !== null && (
            <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100">
              <div className="flex items-center gap-2 mb-1">
                <FileText className="w-3.5 h-3.5 text-gray-400" />
                <span className="text-xs font-medium text-gray-500">Works</span>
              </div>
              <p className="text-xl font-bold text-gray-800">
                {journal.metrics.works_count.toLocaleString()}
              </p>
            </div>
          )}

          {journal.apc_usd !== null && (
            <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100">
              <div className="flex items-center gap-2 mb-1">
                <DollarSign className="w-3.5 h-3.5 text-gray-400" />
                <span className="text-xs font-medium text-gray-500">APC</span>
              </div>
              <p className="text-xl font-bold text-gray-800">
                ${journal.apc_usd}
              </p>
            </div>
          )}
        </div>

        {/* Topics */}
        {journal.topics.length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-medium mb-2 text-gray-500">Topics</p>
            <div className="flex flex-wrap gap-1.5">
              {journal.topics.slice(0, 4).map((topic, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-600 border border-blue-100"
                >
                  {topic}
                </span>
              ))}
              {journal.topics.length > 4 && (
                <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-400">
                  +{journal.topics.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        {journal.homepage_url && (
          <a
            href={journal.homepage_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-all group"
          >
            <span className="group-hover:underline">Visit Journal</span>
            <ExternalLink className="w-4 h-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </a>
        )}
      </div>
    </div>
  )
}
