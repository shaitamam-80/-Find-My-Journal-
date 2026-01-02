/**
 * Logger utility that only logs in development mode.
 * In production, errors could be sent to a monitoring service.
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LoggerConfig {
  enabled: boolean
  minLevel: LogLevel
}

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
}

const config: LoggerConfig = {
  enabled: import.meta.env.DEV,
  minLevel: import.meta.env.DEV ? 'debug' : 'error',
}

function shouldLog(level: LogLevel): boolean {
  return config.enabled && LOG_LEVELS[level] >= LOG_LEVELS[config.minLevel]
}

export const logger = {
  debug: (...args: unknown[]): void => {
    if (shouldLog('debug')) {
      console.debug('[DEBUG]', ...args)
    }
  },

  info: (...args: unknown[]): void => {
    if (shouldLog('info')) {
      console.info('[INFO]', ...args)
    }
  },

  warn: (...args: unknown[]): void => {
    if (shouldLog('warn')) {
      console.warn('[WARN]', ...args)
    }
  },

  error: (message: string, error?: unknown, context?: Record<string, unknown>): void => {
    if (shouldLog('error')) {
      console.error('[ERROR]', message, error, context)
    }

    // TODO: In production, send to monitoring service
    // if (import.meta.env.PROD) {
    //   Sentry.captureException(error, { extra: { message, ...context } })
    // }
  },
}

export default logger
