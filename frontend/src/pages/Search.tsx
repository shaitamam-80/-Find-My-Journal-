import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import type { SearchResponse } from '../types'
import { AIAnalysisHeader } from '../components/search/AIAnalysisHeader'
import { FilterBar } from '../components/search/FilterBar'
import { CategorySection } from '../components/search/CategorySection'
import {
  type FilterType,
  type JournalCategoryKey,
  buildAIAnalysis,
  groupJournalsByCategory,
  filterJournals,
} from '../utils/searchResultsMapper'
import {
  BookOpen, Search as SearchIcon, Trash2, FileText, Sparkles, Tag,
  AlertCircle, Download, Printer, LogOut, Infinity as InfinityIcon, Zap
} from 'lucide-react'

export function Search() {
  const { user, session, limits, signOut, refreshLimits } = useAuth()
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [keywords, setKeywords] = useState('')
  const [preferOA, setPreferOA] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)

  // New results view state
  const [expandedCardIds, setExpandedCardIds] = useState<Set<string>>(new Set())
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')

  // Parse keywords for AI analysis
  const keywordList = useMemo(() => {
    return keywords
      .split(',')
      .map((k) => k.trim())
      .filter((k) => k.length > 0)
  }, [keywords])

  // Build AI analysis from search results
  const aiAnalysis = useMemo(() => {
    if (!results) return null
    return buildAIAnalysis({ title, keywords: keywordList }, results)
  }, [results, title, keywordList])

  // Filter and group journals
  const filteredJournals = useMemo(() => {
    if (!results?.journals) return []
    return filterJournals(results.journals, activeFilter)
  }, [results?.journals, activeFilter])

  const groupedJournals = useMemo(() => {
    return groupJournalsByCategory(filteredJournals)
  }, [filteredJournals])

  // Toggle card expansion
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

  const handleClearForm = () => {
    setTitle('')
    setAbstract('')
    setKeywords('')
    setPreferOA(false)
    setError('')
    setResults(null)
    setExpandedCardIds(new Set())
    setActiveFilter('all')
  }

  const handleExportCSV = () => {
    if (!filteredJournals.length) return

    const headers = ['Name', 'Publisher', 'ISSN', 'H-Index', 'Category', 'Open Access', 'Match Score']
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

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResults(null)
    setExpandedCardIds(new Set())
    setActiveFilter('all')

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

  // Category order for display
  const categoryOrder: JournalCategoryKey[] = ['topTier', 'niche', 'methodology', 'broad']

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-blue-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-blue-100/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center shadow-md shadow-blue-200 group-hover:shadow-lg transition-shadow">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-gray-800 tracking-tight">
                Find<span className="text-blue-500">My</span>Journal
              </span>
            </Link>

            {/* Right side */}
            <div className="flex items-center gap-6">
              {/* Search limits */}
              {limits && (
                <div className={`hidden sm:flex items-center gap-2 px-4 py-2 rounded-full ${
                  limits.daily_limit !== null
                    ? 'bg-amber-100/80 border border-amber-200/50'
                    : 'bg-blue-100/80 border border-blue-200/50'
                }`}>
                  {limits.daily_limit !== null ? (
                    <>
                      <Zap className="w-4 h-4 text-amber-600" />
                      <span className="text-sm font-medium text-amber-700">
                        Searches today: {limits.used_today}/{limits.daily_limit}
                      </span>
                    </>
                  ) : (
                    <>
                      <InfinityIcon className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-700">
                        Unlimited
                      </span>
                    </>
                  )}
                </div>
              )}

              {/* User menu */}
              <div className="flex items-center gap-3">
                <span className="hidden md:block text-sm text-gray-500">
                  {user?.email}
                </span>
                <button
                  onClick={signOut}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl transition-all text-gray-600 hover:bg-gray-100 hover:text-gray-800"
                  title="Sign out"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="hidden sm:inline text-sm font-medium">Sign out</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Find the Right Journal
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Paste your abstract below and we'll analyze it to find the most relevant academic journals for your research.
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-blue-100/50 p-8 mb-10">
          <form onSubmit={handleSearch} className="space-y-6">
            {error && (
              <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Title Field */}
            <div className="space-y-2">
              <label htmlFor="title" className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <FileText className="w-4 h-4 text-gray-400" />
                Article Title
                <span className="text-red-500">*</span>
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter your article title"
                className="w-full px-4 py-3.5 text-gray-800 bg-blue-50/50 border border-blue-100 rounded-xl transition-all duration-200 placeholder:text-gray-400 hover:border-blue-200 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100"
                required
              />
            </div>

            {/* Abstract Field */}
            <div className="space-y-2">
              <label htmlFor="abstract" className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Sparkles className="w-4 h-4 text-gray-400" />
                Abstract
                <span className="text-red-500">*</span>
              </label>
              <textarea
                id="abstract"
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                placeholder="Paste your article abstract here... We'll analyze it to find matching journals."
                rows={8}
                className="w-full px-4 py-3.5 text-gray-800 bg-blue-50/50 border border-blue-100 rounded-xl transition-all duration-200 placeholder:text-gray-400 hover:border-blue-200 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 resize-y"
                required
              />
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-400">
                  Minimum 50 characters required
                </p>
                <p className={`text-xs font-medium ${abstract.length >= 50 ? 'text-green-500' : 'text-gray-400'}`}>
                  {abstract.length} characters
                </p>
              </div>
            </div>

            {/* Keywords Field */}
            <div className="space-y-2">
              <label htmlFor="keywords" className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Tag className="w-4 h-4 text-gray-400" />
                Keywords
                <span className="text-xs font-normal text-gray-400">(optional, comma-separated)</span>
              </label>
              <input
                id="keywords"
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="machine learning, neural networks, deep learning"
                className="w-full px-4 py-3.5 text-gray-800 bg-blue-50/50 border border-blue-100 rounded-xl transition-all duration-200 placeholder:text-gray-400 hover:border-blue-200 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100"
              />
            </div>

            {/* Options Row */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-2">
              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={preferOA}
                    onChange={(e) => setPreferOA(e.target.checked)}
                    className="peer sr-only"
                  />
                  <div className="w-5 h-5 rounded-md border-2 border-gray-300 transition-all peer-checked:border-cyan-500 peer-checked:bg-cyan-500">
                    {preferOA && (
                      <svg className="w-full h-full text-white p-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </div>
                </div>
                <span className="text-sm text-gray-600">
                  Prefer Open Access journals
                </span>
              </label>

              {/* Buttons */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleClearForm}
                  className="flex items-center gap-2 px-4 py-3 text-gray-600 bg-white border border-gray-200 rounded-xl font-medium transition-all hover:border-gray-300 hover:bg-gray-50"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear
                </button>
                <button
                  type="submit"
                  disabled={loading || (limits?.can_search === false)}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-xl transition-all duration-200 hover:shadow-lg hover:shadow-blue-200 hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Searching...
                    </>
                  ) : (
                    <>
                      <SearchIcon className="w-5 h-5" />
                      Find Journals
                    </>
                  )}
                </button>
              </div>
            </div>

            {limits?.can_search === false && (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
                <p className="text-sm text-amber-700">
                  You've reached your daily search limit. Upgrade for unlimited searches!
                </p>
              </div>
            )}
          </form>
        </div>

        {/* Results */}
        {results && aiAnalysis && (
          <div className="max-w-5xl mx-auto">
            {/* AI Analysis Header */}
            <AIAnalysisHeader analysis={aiAnalysis} />

            {/* Filter Bar */}
            <FilterBar
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
            />

            {/* Export Actions */}
            {results.journals.length > 0 && (
              <div className="flex items-center justify-end gap-2 mb-6 no-print">
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
                  />
                ))}

                {/* Bottom CTA */}
                <div className="mt-12 bg-gradient-to-r from-blue-500 via-blue-600 to-cyan-500 rounded-3xl p-10 text-center shadow-xl shadow-blue-200/30">
                  <h3 className="text-2xl font-bold text-white mb-3">
                    Need Different Recommendations?
                  </h3>
                  <p className="text-blue-100 mb-6 max-w-xl mx-auto">
                    Try adjusting your abstract, adding more keywords, or specifying different criteria for better matches
                  </p>
                  <div className="flex justify-center gap-4">
                    <button
                      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                      className="px-8 py-3.5 bg-white text-blue-600 font-bold rounded-xl hover:shadow-lg transition-all"
                    >
                      Refine Search
                    </button>
                    <button
                      onClick={handleExportCSV}
                      className="px-8 py-3.5 bg-white/20 text-white font-bold rounded-xl hover:bg-white/30 transition-all border border-white/30"
                    >
                      Export Results
                    </button>
                  </div>
                </div>
              </>
            ) : results.journals.length > 0 ? (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-100/50 p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center bg-amber-100">
                  <SearchIcon className="w-8 h-8 text-amber-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  No journals match filters
                </h3>
                <p className="text-gray-500">
                  Try adjusting your filter settings to see more results.
                </p>
              </div>
            ) : (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-100/50 p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center bg-amber-100">
                  <SearchIcon className="w-8 h-8 text-amber-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  No journals found
                </h3>
                <p className="text-gray-500">
                  Try adjusting your keywords or abstract for better matches.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
