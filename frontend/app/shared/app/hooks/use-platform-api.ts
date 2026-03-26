import { useRuntimeConfig } from '#imports';

export function usePlatformApi() {
  const config = useRuntimeConfig();

  function createUrl(path: string) {
    return config.public.apiBaseUrl ? `${config.public.apiBaseUrl}${path}` : path;
  }

  async function get<T>(path: string) {
    return $fetch<T>(createUrl(path));
  }

  async function post<T>(path: string, body: object) {
    return $fetch<T>(createUrl(path), {
      body,
      method: 'POST'
    });
  }

  async function put<T>(path: string, body: object) {
    return $fetch<T>(createUrl(path), {
      body,
      method: 'PUT'
    });
  }

  async function del(path: string) {
    return $fetch(createUrl(path), { method: 'DELETE' });
  }

  return {
    del,
    get,
    post,
    put
  };
}
