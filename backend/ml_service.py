from sqlalchemy.orm import Session
from . import models, database

import random

class MLService:
    @staticmethod
    def get_market_base_price():
        """Отримує актуальну базову ціну з БД Market"""
        db = database.SessionLocal()
        try:
            # Беремо останній запис
            record = db.query(models.MarketPriceRef).order_by(models.MarketPriceRef.id.desc()).first()
            if record:
                return float(record.price_index_value)
            return 6000.0 # Fallback, якщо база порожня
        finally:
            db.close()

    @staticmethod
    def predict_price(carat: float, color: int, clarity: int, cut: int) -> float:
        # Отримуємо ціну з бази
        base = MLService.get_market_base_price()
        
        w_factor = carat ** 1.3
        c_factor = 1.0 - (color * 0.05)
        cl_factor = 1.0 - (clarity * 0.07)
        cut_factor = 1.0 - (cut * 0.10)
        
        price = base * w_factor * c_factor * cl_factor * cut_factor
        
        price = price * random.uniform(0.90, 1.10)
        
        return round(max(price, 100), 2)