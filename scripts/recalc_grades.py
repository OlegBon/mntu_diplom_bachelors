import sys
import os
from sqlalchemy.orm import Session

# Додаємо шлях до кореня проєкту, щоб бачити папку backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models, database
from backend.calculator import DiamondCalculator

def recalculate_all_diamonds():
    # Створюємо сесію
    db = database.SessionLocal()
    
    print(" -> Отримання всіх діамантів з бази...")
    diamonds = db.query(models.DiamondReport).all()
    total = len(diamonds)
    print(f" -> Знайдено {total} звітів. Починаємо перерахунок...")

    updated_count = 0
    
    for i, diamond in enumerate(diamonds):
        # Пропускаємо, якщо немає фізичних даних (хоча після seed_db вони мають бути)
        if diamond.table_percent is None:
            continue

        # Викликаємо  Калькулятор для Пропорцій
        # Перетворюємо Decimal у float для розрахунків
        new_proportions = DiamondCalculator.evaluate_proportions(
            float(diamond.table_percent),
            float(diamond.depth_percent),
            float(diamond.crown_angle),
            float(diamond.pavilion_angle)
        )
        
        # Перераховуємо фінальний Cut Grade
        # Беремо існуючі polish/symmetry з бази
        new_cut = DiamondCalculator.calculate_final_cut(
            new_proportions,
            diamond.polish_grade,
            diamond.symmetry_grade
        )

        # Записуємо нові значення
        # (Перезаписуємо їх, навіть якщо вони не змінилися, щоб гарантувати цілісність)
        if diamond.cut_grade != new_cut or diamond.proportions_grade != new_proportions:
            diamond.proportions_grade = new_proportions
            diamond.cut_grade = new_cut
            updated_count += 1
        
        # Вивід прогресу кожні 100 записів
        if (i + 1) % 100 == 0:
            print(f"   ...оброблено {i + 1}/{total}")

    # Зберігаємо зміни
    db.commit()
    print(f" -> ✅ Готово! Оновлено оцінки для {updated_count} діамантів.")
    db.close()

if __name__ == "__main__":
    recalculate_all_diamonds()