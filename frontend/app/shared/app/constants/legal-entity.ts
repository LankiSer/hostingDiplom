import type { LegalEntity } from '../entities/legal-entity.entity';

/** Значения по умолчанию; переопределяются через NUXT_PUBLIC_LEGAL_* в production. */
export const LEGAL_ENTITY_DEFAULTS: LegalEntity = {
  companyName: 'ООО «Джиклауд»',
  inn: '7700000000',
  ogrn: '1234567890123',
  kpp: '770001001',
  legalAddress: '119021, г. Москва',
  email: 'legal@gcloude.ru',
  phone: '',
};

export const LEGAL_DOCUMENTS = [
  {
    to: '/legal/terms',
    title: 'Пользовательское соглашение',
    description: 'Условия доступа к платформе, деплою и доменам.',
  },
  {
    to: '/legal/privacy',
    title: 'Политика конфиденциальности',
    description: 'Какие данные собираются и как они защищаются.',
  },
  {
    to: '/legal/personal-data',
    title: 'Обработка персональных данных',
    description: 'Согласие при регистрации и порядок отзыва.',
  },
  {
    to: '/legal/cookies',
    title: 'Политика cookie',
    description: 'Обязательные и аналитические cookie платформы.',
  },
] as const;
