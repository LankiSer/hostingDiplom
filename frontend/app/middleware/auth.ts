export default defineNuxtRouteMiddleware((to) => {
  const session = useCookie('platform_session');

  if (!session.value) {
    return navigateTo(`/login?redirect=${encodeURIComponent(to.fullPath)}`);
  }
});
