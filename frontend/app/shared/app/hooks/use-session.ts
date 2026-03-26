import { computed } from 'vue';
import type { SessionEntity } from '../../../common/auth/entities/session.entity';

const SESSION_COOKIE_KEY = 'platform_session';

export function useSession() {
  const session = useCookie<SessionEntity | null>(SESSION_COOKIE_KEY, {
    default: () => null,
    sameSite: 'lax'
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
