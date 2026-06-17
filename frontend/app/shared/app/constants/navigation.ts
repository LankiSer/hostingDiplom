import type { AppNavigationItem } from '../entities/navigation.entity';

export const APP_NAVIGATION_ITEMS: AppNavigationItem[] = [
  { label: 'Обзор', to: '/dashboard', group: 'platform', icon: 'dashboard' },
  { label: 'Проекты', to: '/projects', group: 'platform', icon: 'projects' },
  { label: 'Приложения', to: '/applications', group: 'platform', icon: 'apps' },
  { label: 'Деплои', to: '/deployments', group: 'release', icon: 'deployments' },
  { label: 'Домены', to: '/domains', group: 'release', icon: 'domains' },
  { label: 'Логи', to: '/logs', group: 'release', icon: 'logs' },
  { label: 'Биллинг', to: '/billing', group: 'billing', icon: 'billing' },
  { label: 'Документы', to: '/documents', group: 'billing', icon: 'documents' },
  { label: 'Команда', to: '/team', group: 'account', icon: 'team' },
  { label: 'Настройки', to: '/settings', group: 'account', icon: 'settings' },
];
