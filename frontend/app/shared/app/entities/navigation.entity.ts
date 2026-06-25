export type AppNavigationGroup = 'platform' | 'release' | 'billing' | 'account';

export type AppNavigationIcon =
  | 'dashboard'
  | 'projects'
  | 'apps'
  | 'deployments'
  | 'domains'
  | 'logs'
  | 'billing'
  | 'documents'
  | 'team'
  | 'settings';

export interface AppNavigationItem {
  group: AppNavigationGroup;
  icon: AppNavigationIcon;
  hint?: string;
  label: string;
  permission?: string;
  to: string;
}

export const NAV_GROUP_LABELS: Record<AppNavigationGroup, string> = {
  account: 'Аккаунт',
  billing: 'Бухгалтерия',
  platform: 'Хостинг',
  release: 'Релизы',
};
