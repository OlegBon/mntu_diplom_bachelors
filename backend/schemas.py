from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# Схема для експерта (дані, що ми віддаємо на фронт)
class ExpertBase(BaseModel):
    expert_id: int
    username: str
    role: str

    class Config:
        from_attributes = True

# Схема для створення нового звіту (те, що вводить експерт)
class DiamondCreate(BaseModel):
    # Фізичні характеристики (обов'язкові)
    carat_weight: float
    color_grade: int
    clarity_grade: int
    cut_grade: int
    polish_grade: int
    proportions_grade: int
    symmetry_grade: int
    fluorescence_grade: int
    stone_origin: int
    
    # Можна дозволити вводити ціну вручну, або залишити 0 (бо ML поки немає, виправимо пізніше)
    price: Optional[float] = 0.0

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