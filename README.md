# ІС Ідентифікації Діамантів (mntu_diplom_bachelors)

![Repo Status](https://img.shields.io/badge/status-active-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-05998b)
![MariaDB](https://img.shields.io/badge/MariaDB-Local-003545)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Render-336791)
![License](https://img.shields.io/badge/license-MIT-yellow)

**Кваліфікаційна робота бакалавра**
**Тема:** Розроблення інформаційної системи ідентифікації діамантів.
**Заклад:** МНТУ (MNTU)

## 📌 Опис проєкту

Система призначена для автоматизації роботи гемологів, проведення інтелектуального аналізу фізичних характеристик діамантів та прогнозування їхньої ринкової вартості на основі моделей машинного навчання.

## 🏗 Архітектура системи

Проєкт базується на каскадній обробці даних та розділенні на три логічні зони (БД):

- **OLTP (diamond_oltp)**: Зберігання транзакційних даних експертів та звітів.
- **Market (diamond_market)**: Довідники стандартів IDC та ринкові індекси.
- **Analytics (diamond_analytics)**: Результати роботи ML-моделей та кластеризації.

## 🧭 Структура репозиторію

```
mntu_diplom/
├── .venv/ # Віртуальне середовище Python
├── .gitignore # Файл для ігнорування системного сміття
├── .env # Налаштування підключення до БД (не потрапляє в Git)
├── requirements.txt # Залежності Python
├── data/
│ └── diamonds_dataset.csv
├── scripts/
│ └── seed_db.py # Скрипт наповнення бази
├── backend/ # FastAPI додаток (Python)
│ ├── main.py
│ ├── Dockerfile # Конфігурація для Docker (Render)
│ └── render.yaml # Опис сервісів для Render (Blueprint)
├── frontend/ # Фронтенд на Pug/SCSS
├── src/ # Вихідні коди
├── dist/ # Скомпільований результат (HTML/CSS/JS)
└── gulpfile.js # Налаштування збірки
```

## 🚀 Поточний стан реалізації

- [x] Розроблено концептуальну та логічну схему БД.
- [x] Створено скрипти ініціалізації MariaDB (XAMPP).
- [x] Реалізовано автоматизоване наповнення бази даних (1000 записів).
- [x] Налаштовано середовище розробки та Git-flow (гілка `local-dev`).

## 🛠 Технологічний стек

- **Backend**: Python (FastAPI), SQLAlchemy.
- **Frontend**: Gulp, Pug, SCSS, JavaScript.
- **Database**: MariaDB (Local Dev) / PostgreSQL (Cloud Prod).
- **DevOps**: Docker, Render.

## ▶️ Приклад роботи з `venv` (Windows PowerShell)

```bash
# Створюємо віртуальне середовище (один раз)
python -m venv .venv

# Активуємо віртуальне середовище
.venv\Scripts\activate

# Оновлюємо pip
python -m pip install --upgrade pip

# Встановлюємо залежності
pip install -r requirements.txt

# Наповнення бази даних (із кореня проєкту)
python scripts/seed_db.py

# Деактивуємо середовище
deactivate
```

> 💡 Якщо використовуємо Bash (наприклад, Git Bash або WSL), команда активації буде: `source .venv/bin/activate`
