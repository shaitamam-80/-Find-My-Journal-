import { Sparkles, Target, Heart, CheckCircle, Star, TrendingUp } from 'lucide-react'
import type { AIAnalysis } from '../../utils/searchResultsMapper'

interface AIAnalysisHeaderProps {
  analysis: AIAnalysis
}

export function AIAnalysisHeader({ analysis }: AIAnalysisHeaderProps) {
  return (
    <div className="bg-white rounded-3xl border border-gray-200 shadow-xl shadow-blue-100/30 overflow-hidden mb-10">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 via-blue-600 to-cyan-500 px-8 py-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-white/20 backdrop-blur-sm rounded-2xl">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">AI Analysis Complete</h1>
            <p className="text-blue-100">Strategic journal recommendations for your manuscript</p>
          </div>
        </div>
      </div>

      {/* Analysis Content */}
      <div className="p-8">
        {/* Greeting & Paper Title */}
        <div className="mb-8">
          <p className="text-lg text-gray-700 leading-relaxed">
            <span className="font-semibold text-gray-800">{analysis.greeting}</span>
          </p>
          <h2 className="text-xl font-bold text-blue-600 mt-2 leading-relaxed">
            "{analysis.title}"
          </h2>
        </div>

        {/* Analysis Breakdown */}
        <div className="mb-8">
          <p className="text-gray-700 mb-5 text-lg">
            Based on the title, abstract, and keywords, I have analyzed your submission:
          </p>

          <div className="space-y-4 bg-gray-50 rounded-2xl p-6 border border-gray-100">
            {/* Primary Discipline */}
            {analysis.primaryDiscipline && (
              <div className="flex items-start gap-4">
                <div className="p-2 bg-blue-100 rounded-xl flex-shrink-0">
                  <Target className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <span className="text-gray-500 font-medium">Primary Discipline:</span>
                  <p className="text-gray-800 font-semibold text-lg">
                    {analysis.primaryDiscipline}
                  </p>
                </div>
              </div>
            )}

            {/* TODO: [FUTURE_DATA] secondaryDiscipline - Enhanced discipline detection */}

            {/* Key Themes */}
            {analysis.keyThemes.length > 0 && (
              <div className="flex items-start gap-4">
                <div className="p-2 bg-amber-100 rounded-xl flex-shrink-0">
                  <Heart className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <span className="text-gray-500 font-medium">Key Themes:</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {analysis.keyThemes.map((theme, i) => (
                      <span
                        key={i}
                        className="px-3 py-1.5 bg-white text-gray-700 text-sm font-medium rounded-full border border-gray-200 shadow-sm"
                      >
                        {theme}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* TODO: [FUTURE_DATA] strategicSummary - AI-generated strategic advice section */}

        {/* Closing Statement */}
        <p className="text-lg font-semibold text-gray-800 mb-6">
          {analysis.closingStatement}
        </p>

        {/* Summary Stats */}
        <div className="pt-6 border-t border-gray-100">
          <div className="flex flex-wrap items-center gap-4 text-sm">
            <div className="flex items-center gap-2 bg-green-50 px-4 py-2 rounded-xl">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-gray-700">
                <strong className="text-green-700">{analysis.totalJournals}</strong> matching journals
              </span>
            </div>
            {analysis.topTierCount > 0 && (
              <div className="flex items-center gap-2 bg-amber-50 px-4 py-2 rounded-xl">
                <Star className="w-5 h-5 text-amber-500" />
                <span className="text-gray-700">
                  <strong className="text-amber-700">{analysis.topTierCount}</strong> top-tier picks
                </span>
              </div>
            )}
            {/* TODO: [FUTURE_DATA] avgImpactFactor - Scimago API integration */}
            <div className="flex items-center gap-2 bg-purple-50 px-4 py-2 rounded-xl">
              <TrendingUp className="w-5 h-5 text-purple-500" />
              <span className="text-gray-700">
                Best match: <strong className="text-purple-700">{analysis.bestMatch}%</strong>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
