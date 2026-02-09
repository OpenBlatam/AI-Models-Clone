import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { trackPageView, trackEvent, type AnalyticsEvent } from '@/utils/analytics'

export function usePageTracking() {
  const pathname = usePathname()

  useEffect(() => {
    trackPageView(pathname)
  }, [pathname])
}

export function useAnalytics() {
  return {
    track: trackEvent,
  }
}


