import { computed } from 'vue';
import { APP_NAVIGATION_ITEMS } from '../constants/navigation';
import { NAV_GROUP_LABELS, type AppNavigationGroup } from '../entities/navigation.entity';

export function useNavigation() {
  const grouped = computed(() => {
    const order: AppNavigationGroup[] = ['hosting', 'deploys', 'finance', 'team'];
    return order.map((group) => ({
      group,
      label: NAV_GROUP_LABELS[group],
      items: APP_NAVIGATION_ITEMS.filter((i) => i.group === group),
    }));
  });

  return { grouped, items: APP_NAVIGATION_ITEMS };
}
