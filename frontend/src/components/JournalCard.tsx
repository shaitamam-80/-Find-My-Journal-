import type { Journal } from '../types'
import { Info } from 'lucide-react'

interface JournalCardProps {
  journal: Journal
}

const categoryColors = {
  top_tier: 'bg-purple-100 text-purple-800 border-purple-200',
  broad_audience: 'bg-blue-100 text-blue-800 border-blue-200',
  niche: 'bg-green-100 text-green-800 border-green-200',
  emerging: 'bg-yellow-100 text-yellow-800 border-yellow-200',
}

const categoryLabels = {
  top_tier: 'Top Tier',
  broad_audience: 'Broad Audience',
  niche: 'Niche',
  emerging: 'Emerging',
}

export function JournalCard({ journal }: JournalCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6 border border-gray-100">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900 flex-1 pr-4">
          {journal.name}
        </h3>
        {journal.is_oa && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Open Access
          </span>
        )}
      </div>

      {journal.category && (
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${categoryColors[journal.category]} mb-3`}>
          {categoryLabels[journal.category]}
        </span>
      )}

      {journal.match_reason && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
            <div>
              <p className="text-xs font-medium text-blue-800 mb-1">Why this match?</p>
              <p className="text-sm text-blue-700">
                {journal.match_reason}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-2 text-sm text-gray-600">
        {journal.publisher && (
          <p>
            <span className="font-medium">Publisher:</span> {journal.publisher}
          </p>
        )}

        <div className="flex flex-wrap gap-4">
          {journal.metrics.h_index !== null && (
            <div>
              <span className="font-medium">H-Index:</span>{' '}
              <span className="text-indigo-600 font-semibold">{journal.metrics.h_index}</span>
            </div>
          )}
          {journal.metrics.works_count !== null && (
            <div>
              <span className="font-medium">Works:</span>{' '}
              {journal.metrics.works_count.toLocaleString()}
            </div>
          )}
          {journal.apc_usd !== null && (
            <div>
              <span className="font-medium">APC:</span> ${journal.apc_usd}
            </div>
          )}
        </div>

        {journal.topics.length > 0 && (
          <div className="mt-3">
            <span className="font-medium">Topics:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {journal.topics.slice(0, 3).map((topic, i) => (
                <span
                  key={i}
                  className="inline-block px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {journal.homepage_url && (
        <a
          href={journal.homepage_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-flex items-center text-sm text-indigo-600 hover:text-indigo-800"
        >
          Visit Journal
          <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}
    </div>
  )
}
