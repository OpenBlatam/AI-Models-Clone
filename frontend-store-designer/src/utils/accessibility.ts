export function generateId(prefix = 'id'): string {
  return `${prefix}-${Math.random().toString(36).substring(2, 9)}`
}

export function getAriaLabel(
  action: string,
  item?: string
): string {
  return item ? `${action} ${item}` : action
}

export function formatForScreenReader(text: string): string {
  return text.replace(/\s+/g, ' ').trim()
}


