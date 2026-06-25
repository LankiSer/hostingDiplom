import { computed } from 'vue';
import { APP_NAVIGATION_ITEMS } from '../constants/navigation';
import { NAV_GROUP_LABELS, type AppNavigationGroup } from '../entities/navigation.entity';
import { usePermissions } from './use-permissions';

export function useNavigation() {
  const { can } = usePermissions();
  const visibleItems = computed(() => APP_NAVIGATION_ITEMS.filter((item) => !item.permission || can(item.permission)));

  const grouped = computed(() => {
    const order: AppNavigationGroup[] = ['platform', 'release', 'billing', 'account'];
    return order
      .map((group) => ({
        group,
        label: NAV_GROUP_LABELS[group],
        items: visibleItems.value.filter((i) => i.group === group),
      }))
      .filter((group) => group.items.length);
  });

  return { grouped, items: visibleItems };
}
