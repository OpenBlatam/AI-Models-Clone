export function safeParseJSON<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json) as T
  } catch {
    return fallback
  }
}

export function safeStringify(obj: unknown, fallback = '{}'): string {
  try {
    return JSON.stringify(obj)
  } catch {
    return fallback
  }
}

export function safeParseInt(value: string | number, fallback = 0): number {
  const parsed = typeof value === 'string' ? parseInt(value, 10) : value
  return isNaN(parsed) ? fallback : parsed
}

export function safeParseFloat(value: string | number, fallback = 0): number {
  const parsed = typeof value === 'string' ? parseFloat(value) : value
  return isNaN(parsed) ? fallback : parsed
}


