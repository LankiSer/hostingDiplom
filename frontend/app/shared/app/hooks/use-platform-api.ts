import { useRuntimeConfig } from '#imports';
import { useSession } from './use-session';

export function usePlatformApi() {
  const config = useRuntimeConfig();
  const { session } = useSession();

  function createUrl(path: string) {
    return config.public.apiBaseUrl ? `${config.public.apiBaseUrl}${path}` : path;
  }

  async function get<T>(path: string) {
    return $fetch<T>(createUrl(path), { headers: authHeaders() });
  }

  async function post<T>(path: string, body: object) {
    return $fetch<T>(createUrl(path), {
      body,
      headers: authHeaders(),
      method: 'POST'
    });
  }

  async function put<T>(path: string, body: object) {
    return $fetch<T>(createUrl(path), {
      body,
      headers: authHeaders(),
      method: 'PUT'
    });
  }

  async function del(path: string) {
    return $fetch(createUrl(path), { headers: authHeaders(), method: 'DELETE' });
  }

  function authHeaders() {
    if (!session.value) return {};
    return {
      'x-platform-email': session.value.email,
      'x-platform-name': session.value.displayName,
      'x-platform-role': session.value.role,
    };
  }

  return {
    del,
    get,
    post,
    put
  };
}
