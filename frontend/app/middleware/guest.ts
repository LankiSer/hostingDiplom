export default defineNuxtRouteMiddleware(() => {
  const session = useCookie('platform_session');

  if (session.value) {
    return navigateTo('/dashboard');
  }
});
