from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# Схема для створення юзера (з паролем)
class UserCreate(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    role: Optional[str] = "gemologist"

# Схема для оновлення юзера (пароль необов'язковий)
class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None

# Схема для експерта (дані, що ми віддаємо на фронт)
class ExpertBase(BaseModel):
    expert_id: int
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    role: str

    class Config:
        from_attributes = True

# Схема для створення нового звіту (те, що вводить експерт)
class DiamondCreate(BaseModel):
    # Фізичні виміри (обов'язкові)
    carat_weight: float
    table_percent: float
    depth_percent: float
    crown_angle: float
    pavilion_angle: float
    
    # Експертні оцінки (те, що бачить око)
    color_grade: int
    clarity_grade: int
    polish_grade: int
    symmetry_grade: int
    fluorescence_grade: int
    stone_origin: int

    # Поля, які ми або порахуємо, або візьмемо введені (необов'язкові)
    cut_grade: Optional[int] = None
    proportions_grade: Optional[int] = None
    
    # Ціна (якщо 0 - викличемо ML)
    price: Optional[float] = 0.0

# Схема для оновлення звіту (всі поля необов'язкові)
class DiamondUpdate(BaseModel):
    is_sold: Optional[bool] = None
    price: Optional[float] = None

# Схема для статистики (для аналізу експертів)
class ExpertStats(BaseModel):
    expert_username: str
    total_reports: int
    avg_carat: float

# Схема для діаманта (базові поля)
class DiamondReportSchema(BaseModel):
    report_id: str
    report_date: date
    carat_weight: float
    color_grade: int
    clarity_grade: int
    price: float
    is_sold: bool

    class Config:
        from_attributes = True

# Схема для токена (JWT)
class Token(BaseModel):
    access_token: str
    token_type: str

class GradeMappingSchema(BaseModel):
    """
    Схема для передачі довідкових даних (метаданих) на клієнт.
    Використовується для заповнення Select-елементів у формах.
    """
    category: str      # Назва категорії (напр. 'color', 'cut')
    grade_value: int   # Числове значення в БД (напр. 2)
    grade_label: str   # Текстова назва для людини (напр. 'F')

    class Config:
        from_attributes = True

class MarketPriceCreate(BaseModel):
    """Схема для встановлення нової ринкової ціни (Admin input)"""
    price_index_value: float
    notes: Optional[str] = None

class MarketPriceResponse(BaseModel):
    """Схема для відображення поточної ціни"""
    id: int
    price_index_value: float
    updated_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True