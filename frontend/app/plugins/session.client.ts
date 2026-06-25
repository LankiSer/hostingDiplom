import type { SessionEntity } from '~/common/auth/entities/session.entity';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import { useSession } from '~/shared/app/hooks/use-session';

export default defineNuxtPlugin(async () => {
  const { isAuthenticated, save, session } = useSession();

  if (!isAuthenticated.value || !session.value?.email) {
    return;
  }

  try {
    const { get } = usePlatformApi();
    const refreshed = await get<SessionEntity>('/api/v1/platform/session');
    save({
      ...session.value,
      ...refreshed,
    });
  } catch {
    // Сессия остаётся как есть — пользователь может перелогиниться вручную.
  }
});
