import { checkAuth, logout } from "./modules/auth.js";
import { loginUser } from "./modules/api.js";

// --- Redirect from /index.html to / ---
if (window.location.pathname.endsWith("/index.html")) {
  window.history.replaceState({}, "", "/");
}

// --- Оновлення Хедера (UI) ---
function updateHeaderUI(isAuthenticated) {
  const authBlock = document.getElementById("auth-block");
  const navList = document.getElementById("nav-list");

  if (!authBlock) return;

  if (isAuthenticated) {
    const username = localStorage.getItem("username") || "User";

    // Mapping
    let displayName = username;
    let roleClass = "text-expert";

    if (username === "admin") {
      displayName = "Admin";
      roleClass = "text-admin";
    } else if (username === "expert_1") {
      displayName = "Bondarenko O.";
    }

    // HTML для Dropdown
    authBlock.innerHTML = `
            <div class="user-trigger" id="user-trigger">
                <span class="user-name ${roleClass}">${displayName}</span>
                <span class="arrow-icon">▼</span>
            </div>
            
            <div class="user-dropdown-menu" id="user-dropdown">
                <a href="/profile.html">👤 Мій профіль</a>
                <div class="divider"></div>
                <button id="logout-btn" class="logout-btn">🚪 Вихід</button>
            </div>
        `;

    // Логіка Dropdown (JS)
    const trigger = document.getElementById("user-trigger");
    const dropdown = document.getElementById("user-dropdown");
    const logoutBtn = document.getElementById("logout-btn");

    // Toggle меню
    trigger.addEventListener("click", (e) => {
      e.stopPropagation(); // Щоб клік не пішов далі на document
      dropdown.classList.toggle("is-visible");
      trigger.classList.toggle("is-active");
    });

    // Logout
    logoutBtn.addEventListener("click", logout);

    // Закриття при кліку поза межами
    document.addEventListener("click", (e) => {
      if (!authBlock.contains(e.target)) {
        dropdown.classList.remove("is-visible");
        trigger.classList.remove("is-active");
      }
    });

    // Меню Експерта (Навігація)
    if (navList && !document.getElementById("nav-dashboard")) {
      navList.innerHTML = `
                <li id="nav-dashboard"><a href="/dashboard.html">Звіти</a></li>
                <li id="nav-create"><a href="/create-report.html">Новий звіт</a></li>
                <li id="nav-analytics"><a href="/ml-analysis.html">Аналітика</a></li>
             `;
    }
  } else {
    // Гість
    authBlock.innerHTML = `
            <a class="btn btn-sm btn-primary" href="/login.html">Вхід</a>
        `;

    if (navList) {
      navList.innerHTML = `
                <li><a href="/">Головна</a></li>
             `;
    }
  }
}

// --- Оновлення року у футері ---
function updateFooterYear() {
  const yearSpan = document.getElementById("copyright-year");
  if (yearSpan) {
    const startYear = 2026;
    const currentYear = new Date().getFullYear();
    yearSpan.textContent =
      currentYear > startYear ? `${startYear}-${currentYear}` : `${startYear}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const isAuthenticated = checkAuth();
  updateHeaderUI(isAuthenticated);

  // Мобільне меню (Burger)
  const burgerBtn = document.getElementById("burger-btn");
  const mainNav = document.getElementById("main-nav");

  if (burgerBtn && mainNav) {
    burgerBtn.addEventListener("click", () => {
      burgerBtn.classList.toggle("is-active");
      mainNav.classList.toggle("is-active");
    });

    // Закривати меню при кліку на посилання (UX)
    mainNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        burgerBtn.classList.remove("is-active");
        mainNav.classList.remove("is-active");
      });
    });
  }

  // --- Логіка для сторінки логіну ---
  if (window.location.pathname.includes("login.html")) {
    // Якщо вже авторизовані -> на Головну (root)
    if (isAuthenticated) {
      window.location.href = "/";
    }

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
      loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = loginForm.username.value;
        const password = loginForm.password.value;
        const errorMsg = document.getElementById("error-msg");

        try {
          const token = await loginUser(username, password);

          localStorage.setItem("token", token);
          localStorage.setItem("username", username);

          // Редірект на корінь
          window.location.href = "/";
        } catch (err) {
          errorMsg.textContent = "Помилка: " + err.message;
          errorMsg.style.display = "block";
        }
      });
    }
  }

  // Логіка пошуку на Головній
  const searchForm = document.getElementById("public-search-form");
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const query = document.getElementById("search-input").value.trim();

      if (query) {
        // Перенаправляємо на сторінку перегляду (з параметром ?id=...)
        // Поки що сторінки view-report.html немає, але посилання буде правильним
        window.location.href = `/view-report.html?id=${encodeURIComponent(query)}`;
      }
    });
  }

  // --- Advanced Filters Toggle ---
  const toggleFiltersBtn = document.getElementById("toggle-filters");
  const advancedFiltersPanel = document.getElementById("advanced-filters");

  if (toggleFiltersBtn && advancedFiltersPanel) {
    toggleFiltersBtn.addEventListener("click", () => {
      // Перемикаємо клас видимості
      advancedFiltersPanel.classList.toggle("is-visible");

      // Змінюємо стиль кнопки (активна/неактивна)
      toggleFiltersBtn.classList.toggle("btn-primary");
      toggleFiltersBtn.classList.toggle("btn-outline");
    });
  }

  // --- Dashboard Search (натискання Enter) ---
  // Шукаємо інпут всередині .search-group на сторінці дашборду
  const dashboardSearchInput = document.querySelector(
    ".filters-bar .search-group input",
  );

  if (dashboardSearchInput) {
    dashboardSearchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault(); // Щоб форма не сабмітилась, якщо вона є
        const query = dashboardSearchInput.value.trim();

        if (query) {
          console.log(`🔎 Шукаємо звіт: ${query}`);
          // Тут пізніше буде виклик API: fetchReports({ search: query })
          alert(`Виконання пошуку для: ${query}`); // Тимчасова заглушка
        }
      }
    });
  }
});
