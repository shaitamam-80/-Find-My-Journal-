import { useState } from 'react'
import { CheckCircle, AlertTriangle, XCircle, HelpCircle, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { cn } from '../../lib/utils'
import type { VerificationStatus, BadgeColor } from '../../types'

interface VerificationBadgeProps {
  verification: VerificationStatus
  showDetails?: boolean
  className?: string
}

/**
 * Badge configuration for each verification status.
 * Uses factual, non-defamatory language.
 */
const badgeConfig: Record<BadgeColor, {
  bgColor: string
  textColor: string
  borderColor: string
  Icon: typeof CheckCircle
  iconColor: string
}> = {
  verified: {
    bgColor: 'bg-teal-50',
    textColor: 'text-teal-700',
    borderColor: 'border-teal-200',
    Icon: CheckCircle,
    iconColor: 'text-teal-600',
  },
  caution: {
    bgColor: 'bg-amber-50',
    textColor: 'text-amber-700',
    borderColor: 'border-amber-200',
    Icon: AlertTriangle,
    iconColor: 'text-amber-600',
  },
  high_risk: {
    bgColor: 'bg-red-50',
    textColor: 'text-red-700',
    borderColor: 'border-red-200',
    Icon: XCircle,
    iconColor: 'text-red-600',
  },
  unverified: {
    bgColor: 'bg-slate-50',
    textColor: 'text-slate-500',
    borderColor: 'border-slate-200',
    Icon: HelpCircle,
    iconColor: 'text-slate-400',
  },
}

/**
 * Source labels for display
 */
const sourceLabels: Record<string, string> = {
  medline: 'MEDLINE',
  doaj: 'DOAJ',
  cope: 'COPE',
  oaspa: 'OASPA',
  pmc: 'PMC',
  blacklist: 'Watchlist',
  heuristic: 'Analysis',
}

export function VerificationBadge({
  verification,
  showDetails = false,
  className,
}: VerificationBadgeProps) {
  const [isExpanded, setIsExpanded] = useState(showDetails)

  const config = badgeConfig[verification.badge_color]
  const { Icon } = config

  return (
    <div className={cn('relative', className)}>
      {/* Main Badge */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn(
          'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border transition-all',
          'hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-1',
          config.bgColor,
          config.textColor,
          config.borderColor,
          verification.badge_color === 'verified' && 'focus:ring-teal-300',
          verification.badge_color === 'caution' && 'focus:ring-amber-300',
          verification.badge_color === 'high_risk' && 'focus:ring-red-300',
          verification.badge_color === 'unverified' && 'focus:ring-slate-300',
        )}
        title={verification.reasons?.join('. ') || verification.status_text}
      >
        <Icon className={cn('w-3.5 h-3.5', config.iconColor)} />
        <span>{verification.status_text}</span>
        {verification.subtitle && (
          <span className="opacity-75">({verification.subtitle})</span>
        )}
        {isExpanded ? (
          <ChevronUp className="w-3 h-3 opacity-60" />
        ) : (
          <ChevronDown className="w-3 h-3 opacity-60" />
        )}
      </button>

      {/* Expanded Details Panel */}
      {isExpanded && (
        <div
          className={cn(
            'absolute top-full start-0 mt-2 w-80 p-4 rounded-xl border shadow-lg z-50',
            'bg-white',
            config.borderColor,
          )}
        >
          {/* Header */}
          <div className="flex items-center gap-2 mb-3 pb-3 border-b border-slate-100">
            <Icon className={cn('w-5 h-5', config.iconColor)} />
            <div>
              <p className={cn('font-semibold', config.textColor)}>
                {verification.status_text}
              </p>
              {verification.subtitle && (
                <p className="text-xs text-slate-500">
                  Verified by: {verification.subtitle}
                </p>
              )}
            </div>
          </div>

          {/* Reasons */}
          {verification.reasons && verification.reasons.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-slate-600 mb-1.5">Details:</p>
              <ul className="space-y-1">
                {verification.reasons.map((reason, i) => (
                  <li key={i} className="text-sm text-slate-600 flex items-start gap-1.5">
                    <span className="text-slate-400 mt-0.5">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Sources Checked */}
          {verification.sources_checked && verification.sources_checked.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-slate-600 mb-1.5">Sources checked:</p>
              <div className="flex flex-wrap gap-1">
                {verification.sources_checked.map((source) => (
                  <span
                    key={source}
                    className={cn(
                      'px-2 py-0.5 rounded-full text-xs',
                      source === verification.verified_by
                        ? 'bg-teal-100 text-teal-700 font-medium'
                        : 'bg-slate-100 text-slate-500',
                    )}
                  >
                    {sourceLabels[source] || source}
                    {source === verification.verified_by && ' ✓'}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Warning for caution/high_risk */}
          {(verification.badge_color === 'caution' || verification.badge_color === 'high_risk') && (
            <div className={cn(
              'p-2.5 rounded-lg text-xs',
              verification.badge_color === 'high_risk'
                ? 'bg-red-50 text-red-700'
                : 'bg-amber-50 text-amber-700',
            )}>
              <p className="font-medium mb-1">
                {verification.badge_color === 'high_risk'
                  ? '⚠️ Proceed with caution'
                  : '⚠️ Review carefully'}
              </p>
              <p className="opacity-80">
                {verification.badge_color === 'high_risk'
                  ? 'This journal has multiple risk indicators. Consider alternative options.'
                  : 'This journal has limited verification. Conduct additional research before submitting.'}
              </p>
            </div>
          )}

          {/* Methodology link */}
          <div className="mt-3 pt-3 border-t border-slate-100">
            <a
              href="#methodology"
              className="text-xs text-teal-600 hover:text-teal-700 flex items-center gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              Learn about our methodology
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Compact version of the badge for tight spaces.
 * Shows only the icon with a tooltip.
 */
export function VerificationIcon({
  verification,
  className,
}: {
  verification: VerificationStatus
  className?: string
}) {
  const config = badgeConfig[verification.badge_color]
  const { Icon } = config

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center w-6 h-6 rounded-full',
        config.bgColor,
        className,
      )}
      title={`${verification.status_text}${verification.subtitle ? ` (${verification.subtitle})` : ''}: ${verification.reasons?.join('. ')}`}
    >
      <Icon className={cn('w-3.5 h-3.5', config.iconColor)} />
    </div>
  )
}
