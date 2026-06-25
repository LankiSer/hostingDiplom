import { computed } from 'vue';
import { useRequestURL } from '#app';
import type { SessionEntity } from '../../../common/auth/entities/session.entity';
import { SESSION_COOKIE_KEY, SESSION_COOKIE_MAX_AGE_SEC } from '../constants/cookies';

export function useSession() {
  const requestUrl = useRequestURL();
  const session = useCookie<SessionEntity | null>(SESSION_COOKIE_KEY, {
    default: () => null,
    maxAge: SESSION_COOKIE_MAX_AGE_SEC,
    sameSite: 'lax',
    secure: requestUrl.protocol === 'https:',
  });

  const isAuthenticated = computed(() => Boolean(session.value?.email));

  function clear() {
    session.value = null;
  }

  function save(value: SessionEntity) {
    session.value = value;
  }

  return {
    clear,
    isAuthenticated,
    save,
    session
  };
}
