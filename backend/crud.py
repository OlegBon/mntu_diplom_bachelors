from sqlalchemy.orm import Session
from datetime import date

from . import models, schemas
from .security import get_password_hash

# Отримати користувача за логіном (для авторизації)
def get_user_by_username(db: Session, username: str):
    return db.query(models.Expert).filter(models.Expert.username == username).first()

# Отримати всіх користувачів (для адміна - /users/)
def get_all_users(db: Session):
    return db.query(models.Expert).all()

# Створення користувача
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.Expert(
        username=user.username,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Оновлення даних користувача (пароль або роль)
def update_user(db: Session, expert_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.Expert).filter(models.Expert.expert_id == expert_id).first()
    if not db_user:
        return None
    
    # Якщо прийшов новий пароль - хешуємо його
    if user_update.password:
        db_user.password_hash = get_password_hash(user_update.password)
    
    # Якщо прийшла нова роль - оновлюємо
    if user_update.role:
        db_user.role = user_update.role
        
    db.commit()
    db.refresh(db_user)
    return db_user

# Видалення користувача
def delete_user(db: Session, expert_id: int):
    db_user = db.query(models.Expert).filter(models.Expert.expert_id == expert_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# Отримати тільки гемологів (фільтр по ролі - /experts/)
def get_active_experts(db: Session):
    return db.query(models.Expert).filter(models.Expert.role != 'admin').all()

# Отримати звіт по ID
def get_diamond_report(db: Session, report_id: str):
    return db.query(models.DiamondReport).filter(models.DiamondReport.report_id == report_id).first()

# Функція для створення нового звіту
def create_diamond_report(db: Session, diamond: schemas.DiamondCreate, expert_id: int):
    # Генерація унікального ID (Format: DR-01001)
    # Рахуємо кількість записів. Це простий підхід. 
    # У складних системах використовують UUID або окремі лічильники.
    count = db.query(models.DiamondReport).count()
    new_id_num = count + 1
    new_report_id = f"DR-{new_id_num:05d}" # 5 цифр з нулями зліва

    # Створення об'єкта моделі
    db_diamond = models.DiamondReport(
        report_id=new_report_id,
        report_date=date.today(), # Дата сьогоднішня
        expert_id=expert_id, # ID того, хто залогінений
        
        # Розпаковка даних з форми (carat, color, clarity...)
        **diamond.dict(),
        
        # Значення за замовчуванням (поки немає ML, виправемо пізніше)
        evaluation_time_min=0,
        report_notes_length=0,
        report_sentiment=0,
        is_investment_grade=False,
        is_report_rejected=False,
        is_sold=False,
        days_on_market=0,
        sale_date=None
    )
    
    # Записуємо в БД
    db.add(db_diamond)
    db.commit()
    db.refresh(db_diamond)
    return db_diamond

# Функція для отримання список з пагінацією
def get_diamonds(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.DiamondReport).offset(skip).limit(limit).all()

# Функція для оновлення звіту
def update_diamond_report(db: Session, report_id: str, updates: schemas.DiamondUpdate):
    db_report = db.query(models.DiamondReport).filter(models.DiamondReport.report_id == report_id).first()
    if db_report:
        for key, value in updates.dict(exclude_unset=True).items():
            setattr(db_report, key, value)
        db.commit()
        db.refresh(db_report)
    return db_report

# Функція для видалення звіту
def delete_diamond_report(db: Session, report_id: str):
    db_report = db.query(models.DiamondReport).filter(models.DiamondReport.report_id == report_id).first()
    if db_report:
        db.delete(db_report)
        db.commit()
    return db_report

# Функція для отримання статистики гемологів (SQL GROUP BY)
from sqlalchemy import func
def get_expert_stats(db: Session):
    return db.query(
        models.Expert.username.label("expert_username"),
        func.count(models.DiamondReport.report_id).label("total_reports"),
        func.avg(models.DiamondReport.carat_weight).label("avg_carat")
    ).join(models.DiamondReport).group_by(models.Expert.username).all()