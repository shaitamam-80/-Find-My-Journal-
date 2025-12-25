import { useState, useMemo } from 'react'
import {
  Download,
  Printer,
  Share2,
  Check,
  Copy,
  Bookmark,
  Search as SearchIcon,
} from 'lucide-react'
import type { SearchResponse, Journal } from '../../types'
import { AIAnalysisHeader } from './AIAnalysisHeader'
import { FilterBar } from './FilterBar'
import { CategorySection } from './CategorySection'
import {
  type FilterType,
  type JournalCategoryKey,
  buildAIAnalysis,
  groupJournalsByCategory,
  filterJournals,
} from '../../utils/searchResultsMapper'
import { api } from '../../services/api'

interface SearchResultsProps {
  results: SearchResponse
  title: string
  abstract: string
  keywords: string[]
  sessionToken: string | null
  onSaveSearch: (name: string) => Promise<void>
}

export function SearchResults({
  results,
  title,
  abstract,
  keywords,
  sessionToken,
  onSaveSearch,
}: SearchResultsProps) {
  const [expandedCardIds, setExpandedCardIds] = useState<Set<string>>(new Set())
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')

  // Share state
  const [shareLoading, setShareLoading] = useState(false)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const [shareCopied, setShareCopied] = useState(false)

  // Save state
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [saveName, setSaveName] = useState('')

  // Build AI analysis
  const aiAnalysis = useMemo(() => {
    return buildAIAnalysis({ title, keywords }, results)
  }, [results, title, keywords])

  // Filter and group journals
  const filteredJournals = useMemo(() => {
    return filterJournals(results.journals, activeFilter)
  }, [results.journals, activeFilter])

  const groupedJournals = useMemo(() => {
    return groupJournalsByCategory(filteredJournals)
  }, [filteredJournals])

  const categoryOrder: JournalCategoryKey[] = ['topTier', 'niche', 'methodology', 'broad']

  const handleToggleCard = (id: string) => {
    setExpandedCardIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const handleExportCSV = () => {
    if (!filteredJournals.length) return

    const headers = [
      'Name',
      'Publisher',
      'ISSN',
      'H-Index',
      'Category',
      'Open Access',
      'Match Score',
    ]
    const rows = filteredJournals.map((journal) => [
      `"${journal.name.replace(/"/g, '""')}"`,
      `"${(journal.publisher || '').replace(/"/g, '""')}"`,
      journal.issn || journal.issn_l || '',
      journal.metrics.h_index?.toString() || '',
      journal.category || '',
      journal.is_oa ? 'Yes' : 'No',
      `${Math.round(journal.relevance_score * 100)}%`,
    ])

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'journal-results.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const handlePrint = () => {
    window.print()
  }

  const handleShare = async () => {
    if (!sessionToken) return

    setShareLoading(true)
    try {
      const response = await api.createShareLink(
        sessionToken,
        results.query,
        results.discipline,
        results.journals
      )
      const fullUrl = `${window.location.origin}${response.share_url}`
      setShareUrl(fullUrl)

      await navigator.clipboard.writeText(fullUrl)
      setShareCopied(true)
      setTimeout(() => setShareCopied(false), 3000)
    } catch {
      // Handle error silently
    } finally {
      setShareLoading(false)
    }
  }

  const handleCopyShareUrl = async () => {
    if (!shareUrl) return
    await navigator.clipboard.writeText(shareUrl)
    setShareCopied(true)
    setTimeout(() => setShareCopied(false), 3000)
  }

  const handleSaveSearch = async () => {
    if (!saveName.trim()) return

    setSaveLoading(true)
    try {
      await onSaveSearch(saveName.trim())
      setSaveSuccess(true)
      setSaveDialogOpen(false)
      setSaveName('')
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch {
      // Handle error silently
    } finally {
      setSaveLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* AI Analysis Header */}
      <AIAnalysisHeader analysis={aiAnalysis} />

      {/* Filter Bar */}
      <FilterBar activeFilter={activeFilter} onFilterChange={setActiveFilter} />

      {/* Export Actions */}
      {results.journals.length > 0 && (
        <div className="flex items-center justify-end gap-2 mb-6 no-print">
          {/* Save Search Button */}
          {saveSuccess ? (
            <div className="flex items-center gap-2 px-3 py-2 text-sm bg-green-50 border border-green-200 rounded-xl">
              <Check className="w-4 h-4 text-green-600" />
              <span className="text-green-700 font-medium">Saved!</span>
            </div>
          ) : (
            <button
              onClick={() => setSaveDialogOpen(true)}
              className="flex items-center gap-2 px-3 py-2 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-xl font-medium transition-all hover:border-amber-300 hover:bg-amber-100"
            >
              <Bookmark className="w-4 h-4" />
              Save Search
            </button>
          )}

          {/* Share Button */}
          {shareUrl ? (
            <div className="flex items-center gap-2 px-3 py-2 text-sm bg-green-50 border border-green-200 rounded-xl">
              <Check className="w-4 h-4 text-green-600" />
              <span className="text-green-700 font-medium max-w-50 truncate">{shareUrl}</span>
              <button
                onClick={handleCopyShareUrl}
                className="p-1 hover:bg-green-100 rounded transition-colors"
                title="Copy link"
              >
                {shareCopied ? (
                  <Check className="w-4 h-4 text-green-600" />
                ) : (
                  <Copy className="w-4 h-4 text-green-600" />
                )}
              </button>
            </div>
          ) : (
            <button
              onClick={handleShare}
              disabled={shareLoading}
              className="flex items-center gap-2 px-3 py-2 text-sm text-teal-700 bg-teal-50 border border-teal-200 rounded-xl font-medium transition-all hover:border-teal-300 hover:bg-teal-100 disabled:opacity-50"
            >
              {shareLoading ? (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              ) : (
                <Share2 className="w-4 h-4" />
              )}
              Share Results
            </button>
          )}

          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-xl font-medium transition-all hover:border-gray-300 hover:bg-gray-50"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-xl font-medium transition-all hover:border-gray-300 hover:bg-gray-50"
          >
            <Printer className="w-4 h-4" />
            Print
          </button>
        </div>
      )}

      {/* Category Sections */}
      {filteredJournals.length > 0 ? (
        <>
          {categoryOrder.map((categoryKey) => (
            <CategorySection
              key={categoryKey}
              categoryKey={categoryKey}
              journals={groupedJournals[categoryKey]}
              expandedIds={expandedCardIds}
              onToggle={handleToggleCard}
              abstract={abstract}
              sessionToken={sessionToken}
            />
          ))}

          {/* Bottom CTA */}
          <div className="mt-12 bg-slate-900 rounded-2xl p-10 text-center shadow-sm">
            <h3 className="text-2xl font-bold text-white mb-3">
              Need Different Recommendations?
            </h3>
            <p className="text-slate-300 mb-6 max-w-xl mx-auto">
              Try adjusting your abstract, adding more keywords, or specifying different
              criteria for better matches
            </p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="px-8 py-3.5 bg-white text-slate-900 font-bold rounded-xl hover:bg-slate-100 transition-all"
              >
                Refine Search
              </button>
              <button
                onClick={handleExportCSV}
                className="px-8 py-3.5 bg-slate-800 text-white font-bold rounded-xl hover:bg-slate-700 transition-all border border-slate-700"
              >
                Export Results
              </button>
            </div>
          </div>
        </>
      ) : results.journals.length > 0 ? (
        <EmptyFilterResults />
      ) : (
        <NoResultsFound />
      )}

      {/* Save Dialog */}
      {saveDialogOpen && (
        <SaveSearchDialog
          saveName={saveName}
          onNameChange={setSaveName}
          onSave={handleSaveSearch}
          onClose={() => {
            setSaveDialogOpen(false)
            setSaveName('')
          }}
          loading={saveLoading}
        />
      )}
    </div>
  )
}

function EmptyFilterResults() {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center bg-amber-100">
        <SearchIcon className="w-8 h-8 text-amber-600" />
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-2">No journals match filters</h3>
      <p className="text-slate-500">Try adjusting your filter settings to see more results.</p>
    </div>
  )
}

function NoResultsFound() {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center bg-amber-100">
        <SearchIcon className="w-8 h-8 text-amber-600" />
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-2">No journals found</h3>
      <p className="text-slate-500">
        Try adjusting your keywords or abstract for better matches.
      </p>
    </div>
  )
}

interface SaveSearchDialogProps {
  saveName: string
  onNameChange: (name: string) => void
  onSave: () => void
  onClose: () => void
  loading: boolean
}

function SaveSearchDialog({
  saveName,
  onNameChange,
  onSave,
  onClose,
  loading,
}: SaveSearchDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Save This Search</h3>
        <p className="text-sm text-slate-500 mb-4">
          Give this search a name so you can quickly find it later.
        </p>
        <input
          type="text"
          value={saveName}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="e.g., Machine Learning Paper v2"
          className="w-full px-4 py-3 text-slate-900 bg-white border border-slate-200 rounded-xl mb-4 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100"
          autoFocus
        />
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onSave}
            disabled={!saveName.trim() || loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white font-medium rounded-xl hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            ) : (
              <Bookmark className="w-4 h-4" />
            )}
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
