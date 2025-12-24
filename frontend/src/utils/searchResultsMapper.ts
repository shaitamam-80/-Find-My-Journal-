import type { Journal, SearchResponse } from '../types'

// UI category keys for the 4 sections
export type JournalCategoryKey = 'topTier' | 'niche' | 'methodology' | 'broad'

// Filter types for the filter bar
export type FilterType = 'all' | 'openAccess' | 'highHIndex'

// AI Analysis data structure
export interface AIAnalysis {
  greeting: string
  title: string
  primaryDiscipline: string | null
  parentField: string | null // Story 2.1: Parent field (e.g., "Medicine")
  disciplineConfidence: number // Story 2.1: Confidence score 0-1
  // TODO: [FUTURE_DATA] secondaryDiscipline - Enhanced discipline detection
  keyThemes: string[]
  // TODO: [FUTURE_DATA] strategicSummary - AI-generated summary
  totalJournals: number
  topTierCount: number
  // TODO: [FUTURE_DATA] avgImpactFactor - Scimago API integration
  bestMatch: number
  closingStatement: string
}

// Map API category to UI category key
export function mapCategoryToKey(category: string | null): JournalCategoryKey {
  switch (category) {
    case 'top_tier':
      return 'topTier'
    case 'niche':
      return 'niche'
    case 'emerging':
      return 'methodology' // Best fit mapping
    case 'broad_audience':
      return 'broad'
    default:
      return 'broad' // Fallback
  }
}

// Generate acronym from journal name (e.g., "Child Development" -> "CD")
export function generateAcronym(name: string): string {
  const acronym = name
    .split(/\s+/)
    .filter((word) => word.length > 2 && word[0] === word[0].toUpperCase())
    .map((word) => word[0])
    .join('')
    .slice(0, 4)

  return acronym || name.slice(0, 2).toUpperCase()
}

// Group journals by category
export function groupJournalsByCategory(
  journals: Journal[]
): Record<JournalCategoryKey, Journal[]> {
  const groups: Record<JournalCategoryKey, Journal[]> = {
    topTier: [],
    niche: [],
    methodology: [],
    broad: [],
  }

  journals.forEach((journal) => {
    const key = mapCategoryToKey(journal.category)
    groups[key].push(journal)
  })

  return groups
}

// Convert relevance_score (0-1) to match percentage (0-100)
export function toMatchPercentage(relevanceScore: number): number {
  return Math.round(relevanceScore * 100)
}

// Format discipline string for display (e.g., "developmental_psychology" -> "Developmental Psychology")
export function formatDiscipline(discipline: string | null): string | null {
  if (!discipline) return null
  return discipline
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Build AI Analysis data from search request and response
export function buildAIAnalysis(
  request: { title: string; keywords: string[] },
  response: SearchResponse
): AIAnalysis {
  const topTierCount = response.journals.filter(
    (j) => j.category === 'top_tier'
  ).length

  const bestMatch =
    response.journals.length > 0
      ? Math.max(
          ...response.journals.map((j) => toMatchPercentage(j.relevance_score))
        )
      : 0

  // Story 2.1: Extract discipline detection with confidence
  const disciplineDetection = response.discipline_detection
  const parentField = disciplineDetection?.field ?? null
  const disciplineConfidence = disciplineDetection?.confidence ?? 0

  return {
    greeting: 'Hello! I have analyzed your manuscript,',
    title: request.title,
    primaryDiscipline: formatDiscipline(response.discipline),
    parentField, // Story 2.1
    disciplineConfidence, // Story 2.1
    keyThemes: request.keywords,
    totalJournals: response.total_found,
    topTierCount,
    bestMatch,
    closingStatement: 'Here are my recommendations for publication:',
  }
}

// Apply filter to journals
export function filterJournals(
  journals: Journal[],
  filter: FilterType
): Journal[] {
  switch (filter) {
    case 'openAccess':
      return journals.filter((j) => j.is_oa)
    case 'highHIndex':
      return journals.filter((j) => (j.metrics.h_index ?? 0) >= 50)
    case 'all':
    default:
      return journals
  }
}

// Category configuration for display
export const categoryConfig = {
  topTier: {
    title: 'Top-Tier Journals',
    subtitle: 'Highest impact, most competitive',
    gradient: 'from-amber-500 to-orange-500',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
  },
  niche: {
    title: 'Niche Specialists',
    subtitle: 'Field-specific, targeted audience',
    gradient: 'from-teal-600 to-teal-700',
    bg: 'bg-teal-50',
    border: 'border-teal-200',
    text: 'text-teal-700',
  },
  methodology: {
    title: 'Methodology-Focused',
    subtitle: 'Emerging and specialized venues',
    gradient: 'from-purple-500 to-pink-500',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    text: 'text-purple-700',
  },
  broad: {
    title: 'Broad Scope',
    subtitle: 'Wide reach, interdisciplinary',
    gradient: 'from-green-500 to-teal-500',
    bg: 'bg-green-50',
    border: 'border-green-200',
    text: 'text-green-700',
  },
} as const
