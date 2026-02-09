// URL Utilities

export function buildQueryString(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      if (Array.isArray(value)) {
        value.forEach((item) => {
          searchParams.append(key, String(item));
        });
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  
  return searchParams.toString();
}

export function parseQueryString(queryString: string): Record<string, string> {
  const params: Record<string, string> = {};
  const searchParams = new URLSearchParams(queryString);
  
  searchParams.forEach((value, key) => {
    params[key] = value;
  });
  
  return params;
}

export function appendQueryParams(url: string, params: Record<string, unknown>): string {
  const separator = url.includes('?') ? '&' : '?';
  const queryString = buildQueryString(params);
  return queryString ? `${url}${separator}${queryString}` : url;
}

export function getUrlParams(url: string): Record<string, string> {
  try {
    const urlObj = new URL(url);
    return parseQueryString(urlObj.search);
  } catch {
    return {};
  }
}

export function isValidUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

export function getDomain(url: string): string | null {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return null;
  }
}

export function getPath(url: string): string | null {
  try {
    const urlObj = new URL(url);
    return urlObj.pathname;
  } catch {
    return null;
  }
}

