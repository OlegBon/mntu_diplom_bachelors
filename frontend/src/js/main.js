// Імпортуємо функцію з іншого файлу
// ВАЖЛИВО: Для нативних модулів у браузері треба писати розширення .js
import { checkAuth, logout } from "./modules/auth.js";

console.log("🚀 Головний скрипт запущено (ES Modules)");

// Використовуємо DOMContentLoaded, щоб переконатися, що HTML завантажився
document.addEventListener("DOMContentLoaded", () => {
  // Викликаємо функцію з модуля
  const isLogged = checkAuth();

  if (isLogged) {
    // Знаходимо кнопку виходу (якщо вона є на сторінці)
    const logoutBtn = document.querySelector("#logout-btn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        logout();
      });
    }
  }
});
