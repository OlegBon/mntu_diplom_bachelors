import random

class MLService:
    @staticmethod
    def predict_price(carat: float, color: int, clarity: int, cut: int) -> float:
        """
        Емуляція ML-моделі регресії.
        """
        # Базова ціна Rapaport (умовна)
        base = 6000 
        
        # Фактори
        w_factor = carat ** 1.3  # Експоненціальний ріст від ваги
        
        # Color (0=D - найкращий, 10=N - гірший)
        c_factor = 1.0 - (color * 0.05) 
        
        # Clarity (0=IF - найкращий)
        cl_factor = 1.0 - (clarity * 0.07)
        
        # Cut (0=Ex - найкращий)
        cut_factor = 1.0 - (cut * 0.10)
        
        price = base * w_factor * c_factor * cl_factor * cut_factor
        
        # Додаємо трохи рандому ("шум ринку")
        price = price * random.uniform(0.90, 1.10)
        
        return round(max(price, 100), 2)