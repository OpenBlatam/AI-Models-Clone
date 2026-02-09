export function downloadFile(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

export function getExportFilename(
  storeId: string,
  format: 'json' | 'markdown' | 'html'
): string {
  const extensions = {
    json: 'json',
    markdown: 'md',
    html: 'html',
  }
  return `design-${storeId}.${extensions[format]}`
}


