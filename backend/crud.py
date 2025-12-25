from sqlalchemy.orm import Session
from datetime import date

from . import models, schemas

# Отримати користувача за логіном (для авторизації)
def get_user_by_username(db: Session, username: str):
    return db.query(models.Expert).filter(models.Expert.username == username).first()

# Отримати всіх користувачів (для адміна - /users/)
def get_all_users(db: Session):
    return db.query(models.Expert).all()

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