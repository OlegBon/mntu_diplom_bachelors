// Це модуль. Він експортує функцію.

export const checkAuth = () => {
  console.log("🔐 Перевірка авторизації...");
  const token = localStorage.getItem("token");

  if (token) {
    console.log("✅ Користувач авторизований");
    return true;
  } else {
    console.log("❌ Користувач не авторизований");
    return false;
  }
};

export const logout = () => {
  console.log("👋 Вихід із системи...");
  localStorage.removeItem("token");
  window.location.reload();
};
