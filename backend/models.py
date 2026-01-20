from sqlalchemy import Column, Integer, String, DECIMAL, Date, ForeignKey, Enum, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from .database import Base

class Expert(Base):
    __tablename__ = "experts"
    __table_args__ = {"schema": "diamond_oltp"} # Явно вказуємо базу

    expert_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'gemologist'), default='gemologist')
    created_at = Column(TIMESTAMP, server_default=func.now())

class DiamondReport(Base):
    __tablename__ = "diamond_reports"
    __table_args__ = {"schema": "diamond_oltp"}

    report_id = Column(String(20), primary_key=True, index=True)
    report_date = Column(Date, nullable=False)
    
    # Фізичні виміри
    table_percent = Column(DECIMAL(5,2), nullable=True)
    depth_percent = Column(DECIMAL(5,2), nullable=True)
    crown_angle = Column(DECIMAL(5,2), nullable=True)
    pavilion_angle = Column(DECIMAL(5,2), nullable=True)

    # Основні характеристики
    carat_weight = Column(DECIMAL(10,2))
    color_grade = Column(Integer)
    clarity_grade = Column(Integer)
    
    # Оцінки (Grades)
    cut_grade = Column(Integer)
    polish_grade = Column(Integer)
    proportions_grade = Column(Integer)
    symmetry_grade = Column(Integer)
    
    fluorescence_grade = Column(Integer)
    stone_origin = Column(Integer)
    
    # Мета-дані та продажі
    expert_id = Column(Integer, ForeignKey("diamond_oltp.experts.expert_id"))
    evaluation_time_min = Column(Integer)
    report_notes_length = Column(Integer)
    report_sentiment = Column(Integer)
    
    price = Column(DECIMAL(12,2))
    is_investment_grade = Column(Boolean, default=False)
    is_report_rejected = Column(Boolean, default=False)
    is_sold = Column(Boolean, default=False)
    days_on_market = Column(Integer, nullable=True)
    sale_date = Column(Date, nullable=True)