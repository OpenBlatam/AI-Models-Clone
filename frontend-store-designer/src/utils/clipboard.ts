export async function copyToClipboard(text: string): Promise<boolean> {
  if (!navigator.clipboard) {
    return fallbackCopyToClipboard(text)
  }

  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    return fallbackCopyToClipboard(text)
  }
}

function fallbackCopyToClipboard(text: string): boolean {
  const textArea = document.createElement('textarea')
  textArea.value = text
  textArea.style.position = 'fixed'
  textArea.style.left = '-999999px'
  textArea.style.top = '-999999px'
  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()

  try {
    const successful = document.execCommand('copy')
    document.body.removeChild(textArea)
    return successful
  } catch {
    document.body.removeChild(textArea)
    return false
  }
}

export async function readFromClipboard(): Promise<string> {
  if (!navigator.clipboard) {
    throw new Error('Clipboard API not available')
  }

  try {
    return await navigator.clipboard.readText()
  } catch {
    throw new Error('Failed to read from clipboard')
  }
}


