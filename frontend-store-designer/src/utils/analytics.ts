export interface AnalyticsEvent {
  action: string
  category: string
  label?: string
  value?: number
}

export function trackEvent(event: AnalyticsEvent): void {
  if (typeof window === 'undefined') return

  if (window.gtag) {
    window.gtag('event', event.action, {
      event_category: event.category,
      event_label: event.label,
      value: event.value,
    })
  }

  if (process.env.NODE_ENV === 'development') {
    console.log('[Analytics]', event)
  }
}

export function trackPageView(path: string): void {
  if (typeof window === 'undefined') return

  if (window.gtag) {
    window.gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: path,
    })
  }
}

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void
  }
}


