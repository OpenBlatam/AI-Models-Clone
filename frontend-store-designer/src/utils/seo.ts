export interface SEOData {
  title: string
  description: string
  keywords?: string[]
  ogImage?: string
  ogType?: string
}

export function generateSEOTags(data: SEOData): string {
  const tags = [
    `<title>${data.title}</title>`,
    `<meta name="description" content="${data.description}" />`,
  ]

  if (data.keywords) {
    tags.push(`<meta name="keywords" content="${data.keywords.join(', ')}" />`)
  }

  tags.push(
    `<meta property="og:title" content="${data.title}" />`,
    `<meta property="og:description" content="${data.description}" />`,
    `<meta property="og:type" content="${data.ogType || 'website'}" />`
  )

  if (data.ogImage) {
    tags.push(`<meta property="og:image" content="${data.ogImage}" />`)
  }

  return tags.join('\n')
}


