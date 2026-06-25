import { computed } from 'vue';
import { useSession } from './use-session';

export const ROLE_PERMISSIONS: Record<string, string[]> = {
  owner: [
    'projects:read',
    'projects:write',
    'deploys:read',
    'deploys:write',
    'domains:read',
    'domains:write',
    'logs:read',
    'billing:read',
    'billing:write',
    'documents:read',
    'settings:read',
    'settings:write',
    'team:read',
    'team:write',
    'audit:read',
    'calls:read',
    'calls:write',
  ],
  ops: ['projects:read', 'projects:write', 'deploys:read', 'deploys:write', 'domains:read', 'domains:write', 'logs:read', 'team:read', 'audit:read', 'calls:read', 'calls:write'],
  finance: ['billing:read', 'billing:write', 'documents:read', 'team:read', 'audit:read', 'calls:read', 'calls:write'],
  viewer: ['projects:read', 'deploys:read', 'domains:read', 'logs:read', 'billing:read', 'documents:read', 'team:read', 'audit:read', 'calls:read', 'calls:write'],
};

export function usePermissions() {
  const { session } = useSession();
  const permissions = computed(() => session.value?.permissions?.length ? session.value.permissions : ROLE_PERMISSIONS[session.value?.role ?? 'viewer'] ?? []);

  function can(permission: string) {
    return permissions.value.includes(permission);
  }

  return {
    can,
    permissions,
    role: computed(() => session.value?.role ?? 'viewer'),
  };
}
