/**
 * Centralized validation rules and messages.
 */

export const VALIDATION_RULES = {
  TITLE_MIN_LENGTH: 5,
  TITLE_MAX_LENGTH: 500,
  ABSTRACT_MIN_LENGTH: 50,
  ABSTRACT_MAX_LENGTH: 10000,
  PASSWORD_MIN_LENGTH: 6,
  KEYWORDS_MAX_COUNT: 20,
} as const

export const VALIDATION_MESSAGES = {
  TITLE_TOO_SHORT: `Title must be at least ${VALIDATION_RULES.TITLE_MIN_LENGTH} characters`,
  TITLE_TOO_LONG: `Title must be less than ${VALIDATION_RULES.TITLE_MAX_LENGTH} characters`,
  ABSTRACT_TOO_SHORT: `Abstract must be at least ${VALIDATION_RULES.ABSTRACT_MIN_LENGTH} characters`,
  ABSTRACT_TOO_LONG: `Abstract must be less than ${VALIDATION_RULES.ABSTRACT_MAX_LENGTH} characters`,
  PASSWORD_TOO_SHORT: `Password must be at least ${VALIDATION_RULES.PASSWORD_MIN_LENGTH} characters`,
  PASSWORDS_NO_MATCH: 'Passwords do not match',
  LOGIN_REQUIRED: 'Please log in to continue',
  SEARCH_LIMIT_REACHED: 'Daily search limit reached. Please upgrade or try again tomorrow.',
  EXPLANATION_LIMIT_REACHED: 'Daily explanation limit reached. Upgrade for unlimited AI insights.',
} as const

/**
 * Validate search form data
 */
export function validateSearchForm(data: {
  title: string
  abstract: string
}): { isValid: boolean; error?: string } {
  if (data.title.length < VALIDATION_RULES.TITLE_MIN_LENGTH) {
    return { isValid: false, error: VALIDATION_MESSAGES.TITLE_TOO_SHORT }
  }

  if (data.title.length > VALIDATION_RULES.TITLE_MAX_LENGTH) {
    return { isValid: false, error: VALIDATION_MESSAGES.TITLE_TOO_LONG }
  }

  if (data.abstract.length < VALIDATION_RULES.ABSTRACT_MIN_LENGTH) {
    return { isValid: false, error: VALIDATION_MESSAGES.ABSTRACT_TOO_SHORT }
  }

  if (data.abstract.length > VALIDATION_RULES.ABSTRACT_MAX_LENGTH) {
    return { isValid: false, error: VALIDATION_MESSAGES.ABSTRACT_TOO_LONG }
  }

  return { isValid: true }
}

/**
 * Validate signup form data
 */
export function validateSignupForm(data: {
  password: string
  confirmPassword: string
}): { isValid: boolean; error?: string } {
  if (data.password.length < VALIDATION_RULES.PASSWORD_MIN_LENGTH) {
    return { isValid: false, error: VALIDATION_MESSAGES.PASSWORD_TOO_SHORT }
  }

  if (data.password !== data.confirmPassword) {
    return { isValid: false, error: VALIDATION_MESSAGES.PASSWORDS_NO_MATCH }
  }

  return { isValid: true }
}
