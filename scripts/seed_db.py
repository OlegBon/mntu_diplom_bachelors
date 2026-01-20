import mysql.connector
import pandas as pd
import os
import random
import sys
from dotenv import load_dotenv

# Додаємо кореневу папку проєкту в sys.path, щоб бачити папку backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models, database  # Імпортуємо наші моделі та налаштування БД

load_dotenv()

# Підключення до MariaDB (для "сирих" запитів)
def get_connection(db_name=None):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=db_name
    )

def generate_measurements(proportions_grade):
    """
    Reverse Engineering: Генерує правдоподібні розміри на основі оцінки.
    """
    if proportions_grade == 0: # EXCELLENT
        table = round(random.uniform(56.0, 61.0), 1)
        depth = round(random.uniform(59.0, 62.5), 1)
        crown = round(random.uniform(34.0, 35.0), 1)
        pavilion = round(random.uniform(40.6, 40.9), 1)
    
    elif proportions_grade == 1: # VERY GOOD
        table = round(random.uniform(53.0, 63.0), 1)
        depth = round(random.uniform(58.0, 63.5), 1)
        crown = round(random.uniform(32.5, 36.0), 1)
        pavilion = round(random.uniform(40.4, 41.2), 1)
        
    else: # GOOD / FAIR
        table = round(random.uniform(64.0, 68.0), 1)
        depth = round(random.uniform(64.0, 66.0), 1)
        crown = round(random.uniform(36.0, 40.0), 1)
        pavilion = round(random.uniform(42.0, 44.0), 1)

    return table, depth, crown, pavilion

def seed_data():
    # Створення баз даних (через raw connection, бо SQLAlchemy не вміє CREATE DATABASE)
    raw_conn = get_connection()
    raw_cursor = raw_conn.cursor()
    
    print(" -> Перевірка/Створення баз даних...")
    raw_cursor.execute("CREATE DATABASE IF NOT EXISTS diamond_oltp")
    raw_cursor.execute("CREATE DATABASE IF NOT EXISTS diamond_market")
    raw_cursor.execute("CREATE DATABASE IF NOT EXISTS diamond_analytics")

    print(" -> Видалення застарілих таблиць Market (щоб оновити структуру)...")
    raw_cursor.execute("DROP TABLE IF EXISTS diamond_market.grade_mappings")
    raw_cursor.execute("DROP TABLE IF EXISTS diamond_market.market_price_reference")

    raw_conn.commit()
    raw_cursor.close()
    raw_conn.close()

    # Створення таблиць (через SQLAlchemy models) 
    print(" -> Створення таблиць згідно з models.py...")
    # Ця магічна команда дивиться в models.py і створює таблиці, якщо їх немає
    models.Base.metadata.create_all(bind=database.engine)

    # Наповнення довідників (Market)
    conn_market = get_connection("diamond_market")
    cursor_market = conn_market.cursor()
    
    print(" -> Наповнення довідників (Mappings)...")
    
    # Очистка старих мапінгів
    cursor_market.execute("TRUNCATE TABLE grade_mappings")
    
    mappings = []
    
    # Color: 0=D, 1=E, 2=F ...
    colors = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N-Z']
    for i, label in enumerate(colors):
        mappings.append(('color', i, label))
        
    # Clarity: 0=FL, 1=IF ...
    clarities = ['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1', 'I2', 'I3']
    for i, label in enumerate(clarities):
        mappings.append(('clarity', i, label))
        
    # Cut / Polish / Symmetry: 0=Excellent ...
    cuts = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
    for i, label in enumerate(cuts):
        mappings.append(('cut', i, label))
        mappings.append(('polish', i, label))
        mappings.append(('symmetry', i, label))
        mappings.append(('proportions', i, label)) # Додаємо і це

    # Fluorescence
    fluorescences = ['None', 'Faint', 'Medium', 'Strong', 'Very Strong']
    for i, label in enumerate(fluorescences):
        mappings.append(('fluorescence', i, label))
        
    # Origin
    origins = ['Natural', 'Lab-Grown']
    for i, label in enumerate(origins):
        mappings.append(('origin', i, label))

    cursor_market.executemany(
        "INSERT INTO grade_mappings (category, grade_value, grade_label) VALUES (%s, %s, %s)",
        mappings
    )
    
    # Додаємо початкову ринкову ціну (Базовий індекс)
    cursor_market.execute("TRUNCATE TABLE market_price_reference")
    cursor_market.execute(
        "INSERT INTO market_price_reference (price_index_value, updated_by, notes) VALUES (6000.00, 0, 'Initial Base Price')"
    )
    
    conn_market.commit()
    cursor_market.close()
    conn_market.close()

    # Наповнення даними
    conn = get_connection("diamond_oltp") # Підключаємося вже до конкретної бази
    cursor = conn.cursor()

    # Експерти
    print(" -> Додавання експертів...")
    experts_data = [
        (0, 'admin', 'admin_pass', 'admin'),
        (1, 'expert_1', 'pass_1', 'gemologist'),
        (2, 'expert_2', 'pass_2', 'gemologist'),
        (3, 'expert_3', 'pass_3', 'gemologist'),
        (4, 'expert_4', 'pass_4', 'gemologist'),
        (5, 'expert_5', 'pass_5', 'gemologist')
    ]
    cursor.executemany(
        "INSERT IGNORE INTO experts (expert_id, username, password_hash, role) VALUES (%s, %s, %s, %s)", 
        experts_data
    )
    conn.commit()

    # Звіти (Діаманти)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'diamonds_dataset.csv')

    print(f" -> Читання CSV та генерація вимірів: {DATA_PATH}")
    
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"ПОМИЛКА: Не знайдено файл {DATA_PATH}")
        return

    # Очистка для SQL
    df['sale_date'] = df['sale_date'].where(pd.notnull(df['sale_date']), None)

    count = 0
    print(" -> Інсерт даних (це може зайняти кілька секунд)...")
    
    for _, row in df.iterrows():
        # Генерація фейкових вимірів
        p_grade = row['proportions_grade']
        table, depth, crown, pav = generate_measurements(p_grade)
        
        sql = """INSERT IGNORE INTO diamond_reports 
                 (report_id, report_date, 
                  table_percent, depth_percent, crown_angle, pavilion_angle,
                  carat_weight, color_grade, clarity_grade, cut_grade, 
                  polish_grade, proportions_grade, symmetry_grade, fluorescence_grade, stone_origin, 
                  expert_id, evaluation_time_min, report_notes_length, report_sentiment, price, 
                  is_investment_grade, is_report_rejected, is_sold, days_on_market, sale_date) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        values = (
            row['report_id'], row['report_date'],
            table, depth, crown, pav,
            row['carat_weight'], row['color_grade'], row['clarity_grade'], row['cut_grade'],
            row['polish_grade'], row['proportions_grade'], row['symmetry_grade'], 
            row['fluorescence_grade'], row['stone_origin'], row['expert_id'], 
            row['evaluation_time_min'], row['report_notes_length'], row['report_sentiment'], 
            row['price'], row['is_investment_grade'], row['is_report_rejected'], 
            row['is_sold'], row['days_on_market'], row['sale_date']
        )
        cursor.execute(sql, values)
        count += 1

    conn.commit()
    print(f" -> ✅ Успішно! Завантажено {count} діамантів.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed_data()