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

  // --- Create Report Wizard Logic ---
  const wizardForm = document.getElementById("wizard-form");
  if (wizardForm) {
    // 1. Ініціалізація дати та таймера
    const dateInput = document.getElementById("input-date");
    if (dateInput) {
      dateInput.valueAsDate = new Date(); // Сьогоднішня дата
    }

    // Фіксуємо час початку (для статистики)
    const startTimeInput = document.getElementById("start-time");
    if (startTimeInput) {
      startTimeInput.value = Date.now();
    }

    // 2. Логіка перемикання кроків
    const tabs = document.querySelectorAll(".stepper-tabs .tab");
    const steps = document.querySelectorAll(".step-content");
    const nextBtn = document.getElementById("next-btn");
    const prevBtn = document.getElementById("prev-btn");
    const saveBtn = document.getElementById("save-btn");

    let currentStep = 1;
    const totalSteps = steps.length;

    function updateUI() {
      // Перемикаємо контент
      steps.forEach((step) => {
        step.classList.remove("active");
        if (parseInt(step.dataset.step) === currentStep)
          step.classList.add("active");
      });

      // Перемикаємо таби
      tabs.forEach((tab) => {
        const stepNum = parseInt(tab.dataset.step);
        tab.classList.toggle("active", stepNum === currentStep);
      });

      // Кнопки
      prevBtn.disabled = currentStep === 1;
      if (currentStep === totalSteps) {
        nextBtn.style.display = "none";
        saveBtn.style.display = "inline-block";
      } else {
        nextBtn.style.display = "inline-block";
        saveBtn.style.display = "none";
      }
    }

    nextBtn.addEventListener("click", () => {
      if (currentStep < totalSteps) {
        // Можна додати валідацію тут: if(!validateStep(currentStep)) return;
        currentStep++;
        updateUI();
        // Скрол вгору форми
        window.scrollTo({ top: 100, behavior: "smooth" });
      }
    });

    prevBtn.addEventListener("click", () => {
      if (currentStep > 1) {
        currentStep--;
        updateUI();
      }
    });

    // Клік по табах (опціонально, якщо хочемо дозволити стрибати)
    /*
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                currentStep = parseInt(tab.dataset.step);
                updateUI();
            });
        });
        */

    // --- Авто-скрол до активного табу ---
    // Знаходимо активний таб
    const activeTab = document.querySelector(".stepper-tabs .tab.active");
    if (activeTab) {
      // Прокрути так, щоб елемент став по центру (для браузерів, що підтримують smooth scroll)
      activeTab.scrollIntoView({
        behavior: "smooth",
        inline: "center",
        block: "nearest",
      });
    }

    // Обробка форми (Submit)
    wizardForm.addEventListener("submit", (e) => {
      e.preventDefault();
      alert(
        "Функціонал збереження в базу буде підключено на наступному етапі (API Integration).",
      );
      // Тут буде fetch('/api/reports', ...)
    });
  }

  // --- Live Calculator Logic (IDC & Price Mock) ---
  // Слухаємо зміни у всій формі, щоб ловити і Step 2, і Step 3
  const calcInputs = document.querySelectorAll(
    "#wizard-form input, #wizard-form select",
  );

  // Елементи результату (Права колонка)
  const resProp = document.getElementById("res-prop");
  const resPol = document.getElementById("res-pol"); // НОВЕ
  const resSym = document.getElementById("res-sym");
  const resFinal = document.getElementById("res-final");
  const resPrice = document.getElementById("res-price");

  // Приховані поля (для збереження в БД)
  const hiddenCut = document.getElementById("calc-cut-grade");
  const hiddenProp = document.getElementById("calc-proportions-grade");
  const hiddenPrice = document.getElementById("calc-price");

  if (calcInputs.length > 0) {
    calcInputs.forEach((input) => {
      // Використовуємо і input, і change для надійності (особливо для select)
      input.addEventListener("input", updateCalculator);
      input.addEventListener("change", updateCalculator);
    });

    // Запускаємо один раз при старті, щоб заповнити нулями/дефолтами
    updateCalculator();
  }

  function updateCalculator() {
    // --- 1. Збір даних ---
    // Step 2: Dimensions & Angles
    const table =
      parseFloat(
        document.querySelector('input[name="table_percent"]')?.value,
      ) || 0;
    const depth =
      parseFloat(
        document.querySelector('input[name="depth_percent"]')?.value,
      ) || 0;
    const crown =
      parseFloat(document.querySelector('input[name="crown_angle"]')?.value) ||
      0;
    const pav =
      parseFloat(
        document.querySelector('input[name="pavilion_angle"]')?.value,
      ) || 0;
    const carat =
      parseFloat(document.querySelector('input[name="carat_weight"]')?.value) ||
      0;

    // Step 3: Finish (Polish / Symmetry)
    // value="0" -> Excellent, "1" -> VG...
    const polInput = document.querySelector('select[name="polish_grade"]');
    const symInput = document.querySelector('select[name="symmetry_grade"]');

    const polVal = polInput ? parseInt(polInput.value) : 0;
    const symVal = symInput ? parseInt(symInput.value) : 0;

    // --- 2. Логіка Proportions (Більш точна імітація IDC) ---
    // 0=Ex, 1=VG, 2=G, 3=Fair
    let propScore = 3; // За замовчуванням Fair (поки не введеш нормальні дані)

    // Перевіряємо, чи взагалі введені дані
    if (table > 0 && depth > 0 && crown > 0 && pav > 0) {
      // Excellent range (Приблизний стандарт Round Brilliant)
      const isEx =
        table >= 56 &&
        table <= 61 &&
        depth >= 59 &&
        depth <= 62.5 &&
        crown >= 34.0 &&
        crown <= 35.0 &&
        pav >= 40.6 &&
        pav <= 41.0;

      // Very Good range
      const isVG =
        table >= 53 &&
        table <= 63 &&
        depth >= 58 &&
        depth <= 63.5 &&
        crown >= 32.5 &&
        crown <= 36.0 &&
        pav >= 40.2 &&
        pav <= 41.8;

      // Good range
      const isGood = table >= 51 && table <= 66 && depth >= 56 && depth <= 65;

      if (isEx) propScore = 0;
      else if (isVG) propScore = 1;
      else if (isGood) propScore = 2;
      else propScore = 3; // Fair/Poor
    } else {
      // Якщо дані не введені або неповні - ставимо прочерк в логіці
      propScore = -1;
    }

    // --- 3. Відображення (Properties, Polish, Symmetry) ---
    const grades = ["Excellent", "Very Good", "Good", "Fair"];

    // Helper для тексту
    const getLabel = (score) =>
      score >= 0 && score < grades.length ? grades[score] : "--";

    if (resProp) {
      resProp.textContent = getLabel(propScore);
      // Якщо score = -1 (дані не введені), показуємо сірий "--"
      resProp.classList.toggle("placeholder", propScore === -1);
    }

    if (resPol) resPol.textContent = getLabel(polVal);
    if (resSym) resSym.textContent = getLabel(symVal);

    // --- 4. Final Cut Grade (Rule: Worst Grade Wins) ---
    // Тобто MAX з чисел (бо 3 це гірше ніж 0)

    let finalScore = 3; // Default Fair

    if (propScore !== -1) {
      // Якщо пропорції пораховані, беремо максимум серед трьох
      finalScore = Math.max(propScore, polVal, symVal);
    } else {
      // Якщо пропорції ще не введені, фінальна оцінка недоступна
      finalScore = -1;
    }

    if (resFinal) {
      resFinal.textContent = getLabel(finalScore);
      resFinal.className = "calc-value"; // Скидаємо класи
      if (finalScore === 0) resFinal.classList.add("price"); // Зелений якщо Ex
      if (finalScore === -1) resFinal.classList.add("placeholder");

      // Запис в hidden inputs для БД
      if (hiddenCut) hiddenCut.value = finalScore === -1 ? 3 : finalScore;
      if (hiddenProp) hiddenProp.value = propScore === -1 ? 3 : propScore;
    }

    // --- 5. Marcet Valution ---
    // Рахуємо ціну, якщо є хоча б вага (Carat)
    if (carat > 0) {
      let basePrice = 6000; // Це число ми потім візьмемо з бази (API)
      let multiplier = 1.0; // Базовий множник

      // Якщо Cut Grade вже відомий - застосовуємо уточнення
      if (finalScore !== -1) {
        if (finalScore === 0)
          multiplier = 1.15; // Ex +15%
        else if (finalScore === 1)
          multiplier = 1.05; // VG +5%
        else if (finalScore === 2)
          multiplier = 0.9; // G -10%
        else multiplier = 0.8; // Fair -20%
      } else {
        // Якщо оцінки ще немає, припускаємо, що це "Good" (середній камінь)
        // щоб ціна не стрибала від 0 до мільйона
        multiplier = 0.95;
      }

      // В майбутньому тут будуть множники для Color/Clarity з API

      const finalPrice = Math.round(carat * basePrice * multiplier);

      const priceFormatted = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(finalPrice);

      if (resPrice) {
        resPrice.textContent = priceFormatted;
        resPrice.classList.remove("placeholder");
      }
      // Записуємо в приховане поле, щоб відправити на сервер
      if (hiddenPrice) hiddenPrice.value = finalPrice;
    } else {
      // Якщо ваги немає - показуємо прочерки
      if (resPrice) {
        resPrice.textContent = "$ --,--";
        resPrice.classList.add("placeholder");
      }
    }
  }
});
