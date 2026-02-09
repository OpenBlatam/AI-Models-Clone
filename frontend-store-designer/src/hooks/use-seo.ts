import { useEffect } from 'react'
import type { SEOData } from '@/utils/seo'

export function useSEO(data: SEOData) {
  useEffect(() => {
    document.title = data.title

    const updateMeta = (name: string, content: string) => {
      let element = document.querySelector(`meta[name="${name}"]`)
      if (!element) {
        element = document.createElement('meta')
        element.setAttribute('name', name)
        document.head.appendChild(element)
      }
      element.setAttribute('content', content)
    }

    updateMeta('description', data.description)

    if (data.keywords) {
      updateMeta('keywords', data.keywords.join(', '))
    }
  }, [data])
}


