from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Налаштування безпеки (в реальному проді це має бути складний ключ)
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_for_mntu_diplom_bachelors")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Контекст для хешування паролів (використовуємо bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функція перевірки пароля (чи співпадає введений з тим, що в базі)
def verify_password(plain_password, hashed_password):
    # ПРИМІТКА: Оскільки в seed_db.py зараз записані паролі як звичайний текст ('admin_pass'),
    # а не хеш, то для першого тесту поки що порівняємо напряму.
    # Для фінальної версії це змінимо на правильне хешування.
    
    # Тимчасово:
    if plain_password == hashed_password:
        return True
    
    # Правильно (розкоментуємо, коли оновимо базу хешами):
    # return pwd_context.verify(plain_password, hashed_password)
    return False

# Функція для створення хешу (для реєстрації)
def get_password_hash(password):
    return pwd_context.hash(password)

# Функція створення токена доступу (JWT)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # if expires_delta:
    #     expire = datetime.utcnow() + expires_delta
    # else:
    #     expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Використовуємо datetime.now(timezone.utc) замість utcnow()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Додаємо час "смерті" токена
    to_encode.update({"exp": expire})
    
    # Кодуємо в рядок
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt