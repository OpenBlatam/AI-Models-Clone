import { router } from 'expo-router';
import { ROUTES } from '@/constants';

// Navigation Helpers
export function navigateTo(route: string, params?: Record<string, unknown>): void {
  if (params) {
    router.push({
      pathname: route as any,
      params,
    });
  } else {
    router.push(route as any);
  }
}

export function navigateBack(): void {
  if (router.canGoBack()) {
    router.back();
  }
}

export function navigateReplace(route: string, params?: Record<string, unknown>): void {
  if (params) {
    router.replace({
      pathname: route as any,
      params,
    });
  } else {
    router.replace(route as any);
  }
}

export function navigateToShipmentDetail(shipmentId: string): void {
  navigateTo(ROUTES.SHIPMENT_DETAIL(shipmentId));
}

export function navigateToQuoteCreate(): void {
  navigateTo(ROUTES.QUOTE_CREATE);
}

export function navigateToBookingCreate(): void {
  navigateTo(ROUTES.BOOKING_CREATE);
}

export function navigateToDashboard(): void {
  navigateReplace(ROUTES.DASHBOARD);
}

export function navigateToShipments(): void {
  navigateTo(ROUTES.SHIPMENTS);
}

export function navigateToTracking(): void {
  navigateTo(ROUTES.TRACKING);
}

export function navigateToAlerts(): void {
  navigateTo(ROUTES.ALERTS);
}

// Deep Link Helpers
export function buildDeepLink(path: string, params?: Record<string, string>): string {
  const baseUrl = 'logistics://';
  const url = new URL(path, baseUrl);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, value);
    });
  }
  
  return url.toString();
}

export function parseDeepLink(url: string): { path: string; params: Record<string, string> } {
  try {
    const parsed = new URL(url);
    const params: Record<string, string> = {};
    
    parsed.searchParams.forEach((value, key) => {
      params[key] = value;
    });
    
    return {
      path: parsed.pathname,
      params,
    };
  } catch {
    return { path: '', params: {} };
  }
}

