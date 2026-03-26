export type AppNavigationGroup = 'hosting' | 'deploys' | 'finance' | 'team';

export interface AppNavigationItem {
  group: AppNavigationGroup;
  label: string;
  to: string;
}

export const NAV_GROUP_LABELS: Record<AppNavigationGroup, string> = {
  deploys: 'Деплои',
  finance: 'Финансы',
  hosting: 'Хостинг',
  team: 'Управление',
};
