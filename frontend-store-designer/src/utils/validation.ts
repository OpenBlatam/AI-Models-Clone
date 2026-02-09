export function validateEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

export function validateRequired(value: unknown): boolean {
  if (typeof value === 'string') {
    return value.trim().length > 0
  }
  return value !== null && value !== undefined
}

export function validateMinLength(value: string, min: number): boolean {
  return value.length >= min
}

export function validateMaxLength(value: string, max: number): boolean {
  return value.length <= max
}

export function validateUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

export function validateNumber(
  value: string | number,
  min?: number,
  max?: number
): boolean {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return false
  if (min !== undefined && num < min) return false
  if (max !== undefined && num > max) return false
  return true
}

export function validatePattern(value: string, pattern: RegExp): boolean {
  return pattern.test(value)
}
