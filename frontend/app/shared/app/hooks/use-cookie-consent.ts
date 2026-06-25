import { computed } from 'vue';
import {
  COOKIE_CONSENT_KEY,
  COOKIE_CONSENT_VERSION,
  SESSION_COOKIE_MAX_AGE_SEC,
} from '../constants/cookies';
import type { CookieConsentEntity } from '../entities/cookie-consent.entity';

export function useCookieConsent() {
  const consent = useCookie<CookieConsentEntity | null>(COOKIE_CONSENT_KEY, {
    default: () => null,
    sameSite: 'lax',
    maxAge: SESSION_COOKIE_MAX_AGE_SEC,
  });

  const isResolved = computed(() => Boolean(consent.value?.acceptedAt));

  function acceptAll() {
    consent.value = {
      version: COOKIE_CONSENT_VERSION,
      necessary: true,
      analytics: true,
      acceptedAt: new Date().toISOString(),
    };
  }

  function acceptNecessaryOnly() {
    consent.value = {
      version: COOKIE_CONSENT_VERSION,
      necessary: true,
      analytics: false,
      acceptedAt: new Date().toISOString(),
    };
  }

  function revoke() {
    consent.value = null;
  }

  return {
    acceptAll,
    acceptNecessaryOnly,
    consent,
    isResolved,
    revoke,
  };
}
