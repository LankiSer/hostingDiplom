import type { AppNavigationItem } from '../entities/navigation.entity';

export const APP_NAVIGATION_ITEMS: AppNavigationItem[] = [
  { label: 'Обзор', to: '/dashboard', group: 'platform', icon: 'dashboard', hint: 'Проекты и деплои', permission: 'projects:read' },
  { label: 'Проекты', to: '/projects', group: 'platform', icon: 'projects', hint: 'Git и окружения', permission: 'projects:read' },
  { label: 'Приложения', to: '/applications', group: 'platform', icon: 'apps', hint: 'Запущенные сервисы', permission: 'projects:read' },
  { label: 'Деплои', to: '/deployments', group: 'release', icon: 'deployments', hint: 'История сборок', permission: 'deploys:read' },
  { label: 'Домены', to: '/domains', group: 'release', icon: 'domains', hint: 'Маршруты и адреса', permission: 'domains:read' },
  { label: 'Логи', to: '/logs', group: 'release', icon: 'logs', hint: 'События деплоев', permission: 'logs:read' },
  { label: 'Биллинг', to: '/billing', group: 'billing', icon: 'billing', hint: 'Счета и 1С', permission: 'billing:read' },
  { label: 'Документы', to: '/documents', group: 'billing', icon: 'documents', hint: 'Счета для юрлиц', permission: 'documents:read' },
  { label: 'Команда', to: '/team', group: 'account', icon: 'team', hint: 'Участники и роли', permission: 'team:read' },
  { label: 'Настройки', to: '/settings', group: 'account', icon: 'settings', hint: 'Профиль и домены', permission: 'settings:read' },
];
