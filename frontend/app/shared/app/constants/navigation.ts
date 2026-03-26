import type { AppNavigationItem } from '../entities/navigation.entity';

export const APP_NAVIGATION_ITEMS: AppNavigationItem[] = [
  { label: 'Обзор', to: '/dashboard', group: 'hosting' },
  { label: 'Проекты', to: '/projects', group: 'hosting' },
  { label: 'Приложения', to: '/applications', group: 'hosting' },
  { label: 'Деплои', to: '/deployments', group: 'deploys' },
  { label: 'Домены', to: '/domains', group: 'deploys' },
  { label: 'Логи', to: '/logs', group: 'deploys' },
  { label: 'Биллинг', to: '/billing', group: 'finance' },
  { label: 'Документы', to: '/documents', group: 'finance' },
  { label: 'Команда', to: '/team', group: 'team' },
  { label: 'Доступы', to: '/access', group: 'team' },
  { label: 'Настройки', to: '/settings', group: 'team' },
];
