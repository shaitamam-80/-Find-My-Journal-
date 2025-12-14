import { useState, useMemo } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import type { SearchResponse } from '../types'
import { JournalCard } from '../components/JournalCard'
import { Trash2, Download, Printer } from 'lucide-react'

export function Search() {
  const { user, session, limits, signOut, refreshLimits } = useAuth()
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [keywords, setKeywords] = useState('')
  const [preferOA, setPreferOA] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)

  // Filter state
  const [filterOAOnly, setFilterOAOnly] = useState(false)
  const [minCategory, setMinCategory] = useState<'all' | 'top_tier' | 'top_tier_broad'>('all')

  // Filtered results based on client-side filters
  const filteredJournals = useMemo(() => {
    if (!results?.journals) return []

    return results.journals.filter((journal) => {
      // Open Access filter
      if (filterOAOnly && !journal.is_oa) return false

      // Category filter (using category as proxy for quartile)
      if (minCategory === 'top_tier' && journal.category !== 'top_tier') return false
      if (minCategory === 'top_tier_broad' &&
          journal.category !== 'top_tier' &&
          journal.category !== 'broad_audience') return false

      return true
    })
  }, [results?.journals, filterOAOnly, minCategory])

  const handleClearForm = () => {
    setTitle('')
    setAbstract('')
    setKeywords('')
    setPreferOA(false)
    setError('')
  }

  const handleExportCSV = () => {
    if (!filteredJournals.length) return

    const headers = ['Name', 'Publisher', 'ISSN', 'H-Index', 'Category', 'Open Access']
    const rows = filteredJournals.map((journal) => [
      `"${journal.name.replace(/"/g, '""')}"`,
      `"${(journal.publisher || '').replace(/"/g, '""')}"`,
      journal.issn || journal.issn_l || '',
      journal.metrics.h_index?.toString() || '',
      journal.category || '',
      journal.is_oa ? 'Yes' : 'No',
    ])

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'results.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const handlePrint = () => {
    window.print()
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResults(null)

    if (title.length < 5) {
      setError('Title must be at least 5 characters')
      return
    }

    if (abstract.length < 50) {
      setError('Abstract must be at least 50 characters')
      return
    }

    if (!session?.access_token) {
      setError('Please log in to search')
      return
    }

    setLoading(true)

    try {
      const keywordList = keywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0)

      const response = await api.searchJournals(session.access_token, {
        title,
        abstract,
        keywords: keywordList,
        prefer_open_access: preferOA,
      })

      setResults(response)
      await refreshLimits()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-900">Find My Journal</h1>
          <div className="flex items-center gap-4">
            {limits && (
              <div className="text-sm text-gray-600">
                {limits.daily_limit !== null ? (
                  <span>
                    Searches today:{' '}
                    <span className="font-semibold text-indigo-600">
                      {limits.used_today}/{limits.daily_limit}
                    </span>
                  </span>
                ) : (
                  <span className="text-green-600 font-medium">Unlimited searches</span>
                )}
              </div>
            )}
            <span className="text-sm text-gray-500">{user?.email}</span>
            <button
              onClick={signOut}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Find the Right Journal for Your Research
          </h2>
          <form onSubmit={handleSearch} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                Article Title *
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter your article title"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>

            <div>
              <label htmlFor="abstract" className="block text-sm font-medium text-gray-700 mb-1">
                Abstract *
              </label>
              <textarea
                id="abstract"
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                placeholder="Paste your article abstract here..."
                rows={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-y"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                {abstract.length} characters
              </p>
            </div>

            <div>
              <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 mb-1">
                Keywords <span className="text-gray-400">(comma-separated, optional)</span>
              </label>
              <input
                id="keywords"
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="machine learning, neural networks, deep learning"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center">
              <input
                id="preferOA"
                type="checkbox"
                checked={preferOA}
                onChange={(e) => setPreferOA(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="preferOA" className="ml-2 text-sm text-gray-700">
                Prefer Open Access journals
              </label>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                type="submit"
                disabled={loading || (limits?.can_search === false)}
                className="w-full sm:w-auto px-8 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Searching...
                  </span>
                ) : (
                  'Find Journals'
                )}
              </button>
              <button
                type="button"
                onClick={handleClearForm}
                className="w-full sm:w-auto px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors flex items-center justify-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Clear Form
              </button>
            </div>

            {limits?.can_search === false && (
              <p className="text-sm text-amber-600">
                You've reached your daily search limit. Upgrade for unlimited searches!
              </p>
            )}
          </form>
        </div>

        {/* Results */}
        {results && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 print:text-xl">
                Found {results.total_found} journals
                {filteredJournals.length !== results.journals.length && (
                  <span className="text-sm font-normal text-gray-500 ml-2">
                    (showing {filteredJournals.length} after filters)
                  </span>
                )}
              </h3>
              {results.discipline && (
                <span className="text-sm text-gray-500">
                  Detected field: <span className="font-medium capitalize">{results.discipline.replace('_', ' ')}</span>
                </span>
              )}
            </div>

            {/* Actions Bar */}
            {results.journals.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4 no-print">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  {/* Filter Bar */}
                  <div className="flex flex-wrap items-center gap-4">
                    <label className="flex items-center gap-2 text-sm text-gray-700">
                      <input
                        type="checkbox"
                        checked={filterOAOnly}
                        onChange={(e) => setFilterOAOnly(e.target.checked)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      />
                      Open Access Only
                    </label>
                    <div className="flex items-center gap-2">
                      <label htmlFor="minCategory" className="text-sm text-gray-700">
                        Category:
                      </label>
                      <select
                        id="minCategory"
                        value={minCategory}
                        onChange={(e) => setMinCategory(e.target.value as 'all' | 'top_tier' | 'top_tier_broad')}
                        className="text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="all">All Categories</option>
                        <option value="top_tier">Top Tier Only</option>
                        <option value="top_tier_broad">Top Tier + Broad Audience</option>
                      </select>
                    </div>
                  </div>

                  {/* Export Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleExportCSV}
                      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Export CSV
                    </button>
                    <button
                      onClick={handlePrint}
                      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                    >
                      <Printer className="w-4 h-4" />
                      Print Report
                    </button>
                  </div>
                </div>
              </div>
            )}

            {filteredJournals.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 print:grid-cols-1">
                {filteredJournals.map((journal) => (
                  <JournalCard key={journal.id} journal={journal} />
                ))}
              </div>
            ) : results.journals.length > 0 ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                <p className="text-yellow-800">
                  No journals match the current filters. Try adjusting your filter settings.
                </p>
              </div>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                <p className="text-yellow-800">
                  No journals found matching your criteria. Try adjusting your keywords or abstract.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
