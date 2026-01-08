import { Sparkles, Target, Heart, CheckCircle, Star, TrendingUp, Layers, FileText, Globe2, Cpu } from 'lucide-react'
import type { AIAnalysis } from '../../utils/searchResultsMapper'

interface AIAnalysisHeaderProps {
  analysis: AIAnalysis
}

export function AIAnalysisHeader({ analysis }: AIAnalysisHeaderProps) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden mb-10">
      {/* Header */}
      <div className="bg-slate-900 dark:bg-slate-900 px-8 py-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-white/10 rounded-2xl">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">AI Analysis Complete</h1>
            <p className="text-slate-300">Strategic journal recommendations for your manuscript</p>
          </div>
        </div>
      </div>

      {/* Analysis Content */}
      <div className="p-8">
        {/* Greeting & Paper Title */}
        <div className="mb-8">
          <p className="text-lg text-slate-700 dark:text-slate-300 leading-relaxed">
            <span className="font-semibold text-slate-800 dark:text-slate-200">{analysis.greeting}</span>
          </p>
          <h2 className="text-xl font-bold text-teal-600 dark:text-teal-400 mt-2 leading-relaxed">
            "{analysis.title}"
          </h2>
        </div>

        {/* Analysis Breakdown */}
        <div className="mb-8">
          <p className="text-slate-700 dark:text-slate-300 mb-5 text-lg">
            Based on the title, abstract, and keywords, I have analyzed your submission:
          </p>

          <div className="space-y-4 bg-slate-50 dark:bg-slate-700/50 rounded-2xl p-6 border border-slate-200 dark:border-slate-600">
            {/* Academic Domain (Universal Mode) */}
            {analysis.primaryDomain && (
              <div className="flex items-start gap-4">
                <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl shrink-0">
                  <Globe2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div className="flex-1">
                  <span className="text-slate-500 dark:text-slate-400 font-medium">Academic Domain:</span>
                  <div className="flex items-center gap-3 mt-1">
                    <p className="text-slate-800 dark:text-slate-200 font-semibold text-lg">
                      {analysis.primaryDomain}
                    </p>
                    {analysis.detectionMethod && (
                      <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300">
                        <Cpu className="w-3 h-3" />
                        {analysis.detectionMethod === 'openalex_ml' ? 'ML Detection' : 'Keyword'}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Primary Discipline with Confidence (Story 2.1) */}
            {analysis.primaryDiscipline && (
              <div className="flex items-start gap-4">
                <div className="p-2 bg-teal-50 dark:bg-teal-900/30 rounded-xl shrink-0">
                  <Target className="w-5 h-5 text-teal-600 dark:text-teal-400" />
                </div>
                <div className="flex-1">
                  <span className="text-slate-500 dark:text-slate-400 font-medium">Primary Discipline:</span>
                  <div className="flex items-center gap-3 mt-1">
                    <p className="text-slate-800 dark:text-slate-200 font-semibold text-lg">
                      {analysis.primaryDiscipline}
                    </p>
                    {analysis.disciplineConfidence !== undefined && analysis.disciplineConfidence > 0 && (
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        analysis.disciplineConfidence >= 0.7
                          ? 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300'
                          : analysis.disciplineConfidence >= 0.4
                          ? 'bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300'
                          : 'bg-slate-100 dark:bg-slate-600 text-slate-600 dark:text-slate-300'
                      }`}>
                        {Math.round(analysis.disciplineConfidence * 100)}% confidence
                      </span>
                    )}
                  </div>
                  {analysis.parentField && analysis.parentField !== analysis.primaryDiscipline && (
                    <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
                      Field: {analysis.parentField}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Secondary Disciplines (Multi-discipline detection) */}
            {analysis.secondaryDisciplines && analysis.secondaryDisciplines.length > 0 && (
              <div className="flex items-start gap-4">
                <div className="p-2 bg-purple-50 dark:bg-purple-900/30 rounded-xl shrink-0">
                  <Layers className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <span className="text-slate-500 dark:text-slate-400 font-medium">Related Disciplines:</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {analysis.secondaryDisciplines.map((disc, i) => (
                      <span
                        key={i}
                        className="px-3 py-1.5 bg-white dark:bg-slate-600 text-slate-700 dark:text-slate-200 text-sm font-medium rounded-full border border-purple-200 dark:border-purple-700 shadow-sm"
                      >
                        {disc.name}
                        <span className="ml-1.5 text-purple-600 dark:text-purple-400 text-xs">
                          {Math.round(disc.confidence * 100)}%
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Article Type */}
            {analysis.articleType && (
              <div className="flex items-start gap-4">
                <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-xl shrink-0">
                  <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1">
                  <span className="text-slate-500 dark:text-slate-400 font-medium">Article Type:</span>
                  <div className="flex items-center gap-3 mt-1">
                    <p className="text-slate-800 dark:text-slate-200 font-semibold">
                      {analysis.articleType.displayName}
                    </p>
                    {analysis.articleType.confidence > 0 && (
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        analysis.articleType.confidence >= 0.5
                          ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                          : 'bg-slate-100 dark:bg-slate-600 text-slate-600 dark:text-slate-300'
                      }`}>
                        {Math.round(analysis.articleType.confidence * 100)}% match
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Key Themes */}
            {analysis.keyThemes.length > 0 && (
              <div className="flex items-start gap-4">
                <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-xl shrink-0">
                  <Heart className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                  <span className="text-slate-500 dark:text-slate-400 font-medium">Key Themes:</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {analysis.keyThemes.map((theme, i) => (
                      <span
                        key={i}
                        className="px-3 py-1.5 bg-white dark:bg-slate-600 text-slate-700 dark:text-slate-200 text-sm font-medium rounded-full border border-slate-200 dark:border-slate-500 shadow-sm"
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
        <p className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-6">
          {analysis.closingStatement}
        </p>

        {/* Summary Stats */}
        <div className="pt-6 border-t border-slate-100 dark:border-slate-700">
          <div className="flex flex-wrap items-center gap-4 text-sm">
            <div className="flex items-center gap-2 bg-green-50 dark:bg-green-900/30 px-4 py-2 rounded-xl">
              <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400" />
              <span className="text-slate-700 dark:text-slate-300">
                <strong className="text-green-700 dark:text-green-400">{analysis.totalJournals}</strong> matching journals
              </span>
            </div>
            {analysis.topTierCount > 0 && (
              <div className="flex items-center gap-2 bg-amber-50 dark:bg-amber-900/30 px-4 py-2 rounded-xl">
                <Star className="w-5 h-5 text-amber-500 dark:text-amber-400" />
                <span className="text-slate-700 dark:text-slate-300">
                  <strong className="text-amber-700 dark:text-amber-400">{analysis.topTierCount}</strong> top-tier picks
                </span>
              </div>
            )}
            {/* TODO: [FUTURE_DATA] avgImpactFactor - Scimago API integration */}
            <div className="flex items-center gap-2 bg-purple-50 dark:bg-purple-900/30 px-4 py-2 rounded-xl">
              <TrendingUp className="w-5 h-5 text-purple-500 dark:text-purple-400" />
              <span className="text-slate-700 dark:text-slate-300">
                Best match: <strong className="text-purple-700 dark:text-purple-400">{analysis.bestMatch}%</strong>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
