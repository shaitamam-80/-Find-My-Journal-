import { useState } from 'react'
import {
  FileText,
  Sparkles,
  Tag,
  AlertCircle,
  Trash2,
  Search as SearchIcon,
} from 'lucide-react'

interface SearchFormProps {
  onSearch: (data: SearchFormData) => Promise<void>
  loading: boolean
  error: string
  canSearch: boolean
  onClearError: () => void
}

export interface SearchFormData {
  title: string
  abstract: string
  keywords: string[]
  preferOpenAccess: boolean
}

export function SearchForm({
  onSearch,
  loading,
  error,
  canSearch,
  onClearError,
}: SearchFormProps) {
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [keywords, setKeywords] = useState('')
  const [preferOA, setPreferOA] = useState(false)
  const [localError, setLocalError] = useState('')

  const handleClear = () => {
    setTitle('')
    setAbstract('')
    setKeywords('')
    setPreferOA(false)
    setLocalError('')
    onClearError()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError('')
    onClearError()

    if (title.length < 5) {
      setLocalError('Title must be at least 5 characters')
      return
    }

    if (abstract.length < 50) {
      setLocalError('Abstract must be at least 50 characters')
      return
    }

    const keywordList = keywords
      .split(',')
      .map((k) => k.trim())
      .filter((k) => k.length > 0)

    await onSearch({
      title,
      abstract,
      keywords: keywordList,
      preferOpenAccess: preferOA,
    })
  }

  const displayError = localError || error

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-10">
      <form onSubmit={handleSubmit} className="space-y-6">
        {displayError && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <p className="text-sm text-red-600">{displayError}</p>
          </div>
        )}

        {/* Title Field */}
        <div className="space-y-2">
          <label
            htmlFor="title"
            className="flex items-center gap-2 text-sm font-medium text-slate-700"
          >
            <FileText className="w-4 h-4 text-slate-400" />
            Article Title
            <span className="text-red-500">*</span>
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter your article title"
            className="w-full px-4 py-3.5 text-slate-900 bg-white border border-slate-200 rounded-xl transition-all duration-200 placeholder:text-slate-400 hover:border-slate-300 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100"
            required
          />
        </div>

        {/* Abstract Field */}
        <div className="space-y-2">
          <label
            htmlFor="abstract"
            className="flex items-center gap-2 text-sm font-medium text-slate-700"
          >
            <Sparkles className="w-4 h-4 text-slate-400" />
            Abstract
            <span className="text-red-500">*</span>
          </label>
          <textarea
            id="abstract"
            value={abstract}
            onChange={(e) => setAbstract(e.target.value)}
            placeholder="Paste your article abstract here... We'll analyze it to find matching journals."
            rows={8}
            className="w-full px-4 py-3.5 text-slate-900 bg-white border border-slate-200 rounded-xl transition-all duration-200 placeholder:text-slate-400 hover:border-slate-300 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100 resize-y"
            required
          />
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-400">Minimum 50 characters required</p>
            <p
              className={`text-xs font-medium ${
                abstract.length >= 50 ? 'text-green-500' : 'text-gray-400'
              }`}
            >
              {abstract.length} characters
            </p>
          </div>
        </div>

        {/* Keywords Field */}
        <div className="space-y-2">
          <label
            htmlFor="keywords"
            className="flex items-center gap-2 text-sm font-medium text-slate-700"
          >
            <Tag className="w-4 h-4 text-slate-400" />
            Keywords
            <span className="text-xs font-normal text-slate-400">
              (optional, comma-separated)
            </span>
          </label>
          <input
            id="keywords"
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="machine learning, neural networks, deep learning"
            className="w-full px-4 py-3.5 text-slate-900 bg-white border border-slate-200 rounded-xl transition-all duration-200 placeholder:text-slate-400 hover:border-slate-300 focus:outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100"
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
              <div className="w-5 h-5 rounded-md border-2 border-slate-300 transition-all peer-checked:border-teal-600 peer-checked:bg-teal-600">
                {preferOA && (
                  <svg
                    className="w-full h-full text-white p-0.5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                  >
                    <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
            </div>
            <span className="text-sm text-slate-600">Prefer Open Access journals</span>
          </label>

          {/* Buttons */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleClear}
              className="flex items-center gap-2 px-4 py-3 text-slate-600 bg-white border border-slate-200 rounded-xl font-medium transition-all hover:border-slate-300 hover:bg-slate-50"
            >
              <Trash2 className="w-4 h-4" />
              Clear
            </button>
            <button
              type="submit"
              disabled={loading || !canSearch}
              className="flex items-center gap-2 px-6 py-3 bg-slate-900 text-white font-semibold rounded-xl transition-all duration-200 hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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

        {!canSearch && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
            <p className="text-sm text-amber-700">
              You've reached your daily search limit. Upgrade for unlimited searches!
            </p>
          </div>
        )}
      </form>
    </div>
  )
}

// Export form data for reuse
export type { SearchFormData }
