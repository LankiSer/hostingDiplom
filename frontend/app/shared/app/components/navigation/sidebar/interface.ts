import type { AppNavigationItem } from '../../../entities/navigation.entity';

export interface AppSidebarItemProps {
  isActive: boolean;
  item: AppNavigationItem;
}
