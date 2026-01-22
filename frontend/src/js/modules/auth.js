// Перевірка авторизації користувача
export const checkAuth = () => {
  const token = localStorage.getItem("token");
  return !!token;
};

// Вихід із системи
export const logout = () => {
  localStorage.clear();
  window.location.href = "/";
};
