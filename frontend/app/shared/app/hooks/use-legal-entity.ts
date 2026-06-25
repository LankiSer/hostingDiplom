import { computed } from 'vue';
import { useRuntimeConfig } from '#imports';
import { LEGAL_ENTITY_DEFAULTS } from '../constants/legal-entity';
import type { LegalEntity } from '../entities/legal-entity.entity';

function pick(value: unknown, fallback: string): string {
  const text = typeof value === 'string' ? value.trim() : '';
  return text || fallback;
}

export function useLegalEntity() {
  const config = useRuntimeConfig().public as Record<string, string | undefined>;

  const entity = computed<LegalEntity>(() => ({
    companyName: pick(config.legalCompanyName, LEGAL_ENTITY_DEFAULTS.companyName),
    inn: pick(config.legalInn, LEGAL_ENTITY_DEFAULTS.inn),
    ogrn: pick(config.legalOgrn, LEGAL_ENTITY_DEFAULTS.ogrn),
    kpp: pick(config.legalKpp, LEGAL_ENTITY_DEFAULTS.kpp),
    legalAddress: pick(config.legalAddress, LEGAL_ENTITY_DEFAULTS.legalAddress),
    email: pick(config.legalEmail, LEGAL_ENTITY_DEFAULTS.email),
    phone: pick(config.legalPhone, LEGAL_ENTITY_DEFAULTS.phone),
  }));

  const requisitesLine = computed(() => {
    const parts = [
      entity.value.companyName,
      entity.value.inn ? `ИНН ${entity.value.inn}` : '',
      entity.value.ogrn ? `ОГРН ${entity.value.ogrn}` : '',
      entity.value.kpp ? `КПП ${entity.value.kpp}` : '',
    ].filter(Boolean);
    return parts.join(' · ');
  });

  return { entity, requisitesLine };
}
