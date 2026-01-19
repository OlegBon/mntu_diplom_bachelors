from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from jose import JWTError, jwt

from . import models, schemas, database, crud, security

app = FastAPI(title="Diamond ID System API")

# Спеціальна схема, яка каже Swagger-у, де брати токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функція для отримання поточного користувача за токеном
# Ця функція буде використовуватися як Dependency в ендпоінтах, де потрібна авторизація
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Розшифровуємо токен
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Шукаємо користувача в БД
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Авторизація - отримання токена (логін)
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Шукаємо користувача в базі
    user = crud.get_user_by_username(db, username=form_data.username)
    
    # Перевіряємо чи юзер існує і чи правильний пароль
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Якщо все ОК - генеруємо токен
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Віддаємо токен клієнту
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def read_root():
    return {"message": "Diamond Identification System API is running"}

# Технічний ендпоінт (адмінський)
# Повертає список всіх користувачів
# Без токена доступ заборонено, current_user перевіряє токен
@app.get("/users/", response_model=List[schemas.ExpertBase])
def read_users(
    db: Session = Depends(get_db), 
    current_user: models.Expert = Depends(get_current_user)
):
    # Додаткова перевірка: чи це точно адмін?
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    users = crud.get_all_users(db)
    return users

# Бізнес-ендпоінт - тільки для гемологів (експертів)
# Повертає список всіх активних гемологів
# Доступ лише з валідним токеном
@app.get("/experts/", response_model=List[schemas.ExpertBase])
def read_experts(
    db: Session = Depends(get_db),
    current_user: models.Expert = Depends(get_current_user) # Перевірка токена
):
    experts = crud.get_active_experts(db)
    return 

# Ендпоінт "Я" (профіль поточного юзера)
@app.get("/users/me", response_model=schemas.ExpertBase)
def read_user_me(current_user: models.Expert = Depends(get_current_user)):
    return current_user

# Створення юзера (тільки для адміна)
@app.post("/users/", response_model=schemas.ExpertBase)
def create_user(
    user_data: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: models.Expert = Depends(get_current_user)
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    # Перевірка чи юзер вже існує
    db_user = crud.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    return crud.create_user(db=db, user=user_data)

# Оновлення юзера (тільки для адміна)
@app.put("/users/{expert_id}", response_model=schemas.ExpertBase)
def update_user(
    expert_id: int,
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.Expert = Depends(get_current_user)
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can update users")
    
    updated_user = crud.update_user(db, expert_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

# Видалення юзера (тільки для адміна)
@app.delete("/users/{expert_id}")
def delete_user(
    expert_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Expert = Depends(get_current_user)
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    deleted = crud.delete_user(db, expert_id=expert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {expert_id} deleted successfully"}

# Пошук звіту
@app.get("/diamonds/{report_id}", response_model=schemas.DiamondReportSchema)
def read_diamond(report_id: str, db: Session = Depends(get_db)):
    diamond = crud.get_diamond_report(db, report_id=report_id)
    if not diamond:
        raise HTTPException(status_code=404, detail="Diamond report not found")
    return diamond

# Створення нового звіту (тільки для авторизованих експертів)
@app.post("/diamonds/", response_model=schemas.DiamondReportSchema)
def create_report(
    diamond_data: schemas.DiamondCreate, # Pydantic перевірить типи даних
    db: Session = Depends(get_db),
    current_user: models.Expert = Depends(get_current_user) # Тільки авторизовані
):
    # Тут пізніше ми додамо виклик ML:
    # ml_results = ml_service.predict_price(diamond_data)
    # diamond_data.price = ml_results.price
    
    return crud.create_diamond_report(db=db, diamond=diamond_data, expert_id=current_user.expert_id)

# Список усіх діамантів (з пагінацією)
@app.get("/diamonds/", response_model=List[schemas.DiamondReportSchema])
def read_diamonds(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_diamonds(db, skip=skip, limit=limit)

# Оновлення звіту (доступно авторизованим)
@app.put("/diamonds/{report_id}", response_model=schemas.DiamondReportSchema)
def update_report(
    report_id: str, 
    update_data: schemas.DiamondUpdate, 
    db: Session = Depends(get_db),
    current_user: models.Expert = Depends(get_current_user)
):
    return crud.update_diamond_report(db, report_id, update_data)

# Видалення звіту (тільки для адміна)
@app.delete("/diamonds/{report_id}")
def delete_report(
    report_id: str, 
    db: Session = Depends(get_db),
    current_user: models.Expert = Depends(get_current_user)
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can delete reports")
    crud.delete_diamond_report(db, report_id)
    return {"message": "Report deleted"}

# Статистика експертів
@app.get("/statistics/expert-performance", response_model=List[schemas.ExpertStats])
def get_stats(db: Session = Depends(get_db)):
    return crud.get_expert_stats(db)