export function buildPlatformWsUrl(path: string, params: Record<string, string> = {}) {
  const config = useRuntimeConfig();
  const query = new URLSearchParams(params).toString();
  const pathWithQuery = query ? `${path}?${query}` : path;

  if (import.meta.client) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    if (config.public.apiBaseUrl) {
      const base = new URL(config.public.apiBaseUrl);
      return `${protocol}//${base.host}${pathWithQuery}`;
    }
    return `${protocol}//${window.location.host}${pathWithQuery}`;
  }

  return `ws://localhost:8009${pathWithQuery}`;
}
