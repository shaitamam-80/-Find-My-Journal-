import type { Journal } from '../types'

interface JournalCardProps {
  journal: Journal
}

const categoryConfig = {
  top_tier: {
    label: 'Top Tier',
    icon: 'workspace_premium',
    gradient: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
    border: '#fcd34d',
    text: '#92400e',
    iconColor: '#b45309',
  },
  broad_audience: {
    label: 'Broad Audience',
    icon: 'groups',
    gradient: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)',
    border: '#7dd3fc',
    text: '#0369a1',
    iconColor: '#0284c7',
  },
  niche: {
    label: 'Niche',
    icon: 'eco',
    gradient: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
    border: '#86efac',
    text: '#166534',
    iconColor: '#22c55e',
  },
  emerging: {
    label: 'Emerging',
    icon: 'lightbulb',
    gradient: 'linear-gradient(135deg, #fae8ff 0%, #f5d0fe 100%)',
    border: '#e879f9',
    text: '#86198f',
    iconColor: '#a855f7',
  },
}

export function JournalCard({ journal }: JournalCardProps) {
  const category = journal.category ? categoryConfig[journal.category] : null

  return (
    <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
      {/* Category Header */}
      {category && (
        <div
          className="px-5 py-3 flex items-center gap-2"
          style={{ background: category.gradient, borderBottom: `1px solid ${category.border}` }}
        >
          <span className="material-symbols-outlined" style={{ color: category.iconColor, fontSize: '18px' }}>
            {category.icon}
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: category.text }}>
            {category.label}
          </span>
        </div>
      )}

      {/* Main Content */}
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <h3 className="text-lg font-semibold leading-tight text-neutral-800 hover:text-sky-600 transition-colors">
            {journal.name}
          </h3>
          {journal.is_oa && (
            <div className="shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-100">
              <span className="material-symbols-outlined" style={{ color: '#22c55e', fontSize: '14px' }}>lock_open</span>
              <span className="text-xs font-semibold text-green-700">
                Open Access
              </span>
            </div>
          )}
        </div>

        {/* Match Reason */}
        {journal.match_reason && (
          <div
            className="mb-4 p-3.5 rounded-xl"
            style={{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', border: '1px solid #bae6fd' }}
          >
            <div className="flex items-start gap-2.5">
              <div className="shrink-0 w-6 h-6 rounded-lg flex items-center justify-center mt-0.5 bg-sky-200">
                <span className="material-symbols-outlined" style={{ color: '#0284c7', fontSize: '14px' }}>lightbulb</span>
              </div>
              <div>
                <p className="text-xs font-semibold mb-0.5 text-sky-800">
                  Why this match?
                </p>
                <p className="text-sm leading-relaxed text-sky-700">
                  {journal.match_reason}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Publisher */}
        {journal.publisher && (
          <p className="text-sm mb-4 text-neutral-500">
            <span className="font-medium text-neutral-600">Publisher:</span>{' '}
            {journal.publisher}
          </p>
        )}

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
          {journal.metrics.h_index !== null && (
            <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-100">
              <div className="flex items-center gap-2 mb-1">
                <span className="material-symbols-outlined text-neutral-400" style={{ fontSize: '14px' }}>trending_up</span>
                <span className="text-xs font-medium text-neutral-500">H-Index</span>
              </div>
              <p className="text-xl font-bold text-sky-600">
                {journal.metrics.h_index}
              </p>
            </div>
          )}

          {journal.metrics.works_count !== null && (
            <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-100">
              <div className="flex items-center gap-2 mb-1">
                <span className="material-symbols-outlined text-neutral-400" style={{ fontSize: '14px' }}>article</span>
                <span className="text-xs font-medium text-neutral-500">Works</span>
              </div>
              <p className="text-xl font-bold text-neutral-800">
                {journal.metrics.works_count.toLocaleString()}
              </p>
            </div>
          )}

          {journal.apc_usd !== null && (
            <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-100">
              <div className="flex items-center gap-2 mb-1">
                <span className="material-symbols-outlined text-neutral-400" style={{ fontSize: '14px' }}>payments</span>
                <span className="text-xs font-medium text-neutral-500">APC</span>
              </div>
              <p className="text-xl font-bold text-neutral-800">
                ${journal.apc_usd}
              </p>
            </div>
          )}
        </div>

        {/* Topics */}
        {journal.topics.length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-medium mb-2 text-neutral-500">Topics</p>
            <div className="flex flex-wrap gap-1.5">
              {journal.topics.slice(0, 4).map((topic, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-full text-xs font-medium bg-neutral-100 text-neutral-600 border border-neutral-200"
                >
                  {topic}
                </span>
              ))}
              {journal.topics.length > 4 && (
                <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-neutral-100 text-neutral-400">
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
            className="inline-flex items-center gap-2 text-sm font-medium text-sky-600 hover:text-sky-700 transition-all group"
          >
            <span className="group-hover:underline">Visit Journal</span>
            <span className="material-symbols-outlined transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" style={{ fontSize: '16px' }}>
              open_in_new
            </span>
          </a>
        )}
      </div>
    </div>
  )
}
