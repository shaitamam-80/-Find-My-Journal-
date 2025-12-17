import { cn } from '../../lib/utils'

interface MatchScoreBadgeProps {
  score: number
  className?: string
}

function getScoreLevel(score: number): 'high' | 'medium' | 'low' {
  if (score >= 85) return 'high'
  if (score >= 50) return 'medium'
  return 'low'
}

const scoreStyles = {
  high: 'bg-emerald-600 text-white',
  medium: 'bg-amber-500 text-white',
  low: 'bg-slate-400 text-white',
}

export function MatchScoreBadge({ score, className }: MatchScoreBadgeProps) {
  const level = getScoreLevel(score)

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-lg px-3 py-2 min-w-[60px]',
        scoreStyles[level],
        className
      )}
    >
      <span className="text-lg font-bold">{score}%</span>
      <span className="text-xs opacity-90">Match</span>
    </div>
  )
}
