import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Підключення до MariaDB
def get_connection(db_name=None):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=db_name
    )

def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    print(" -> Створення облікових записів...")
    # 1. Заповнення експертів (Admin + 5 Гемологів)
    # password_hash тут для прикладу, у реальному бекенді будемо хешувати
    experts_data = [
        (0, 'admin', 'admin_pass', 'admin'),
        (1, 'expert_1', 'pass_1', 'gemologist'),
        (2, 'expert_2', 'pass_2', 'gemologist'),
        (3, 'expert_3', 'pass_3', 'gemologist'),
        (4, 'expert_4', 'pass_4', 'gemologist'),
        (5, 'expert_5', 'pass_5', 'gemologist')
    ]
    
    cursor.execute("USE diamond_oltp")
    cursor.executemany(
        "INSERT IGNORE INTO experts (expert_id, username, password_hash, role) VALUES (%s, %s, %s, %s)",
        experts_data
    )

    print(" -> Завантаження датасету...")
    # 2. Завантаження основного датасету
    # df = pd.read_csv('../data/diamonds_dataset.csv')

    # Визначаємо шлях до поточної папки скрипта
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Формуємо шлях до файлу відносно кореня проєкту
    DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'diamonds_dataset.csv')

    print(f" -> Читання файлу: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    # Заміна NaN у sale_date на None для SQL
    df['sale_date'] = df['sale_date'].where(pd.notnull(df['sale_date']), None)

    for _, row in df.iterrows():
        sql = """INSERT IGNORE INTO diamond_reports 
                 (report_id, report_date, carat_weight, color_grade, clarity_grade, cut_grade, 
                  polish_grade, proportions_grade, symmetry_grade, fluorescence_grade, stone_origin, 
                  expert_id, evaluation_time_min, report_notes_length, report_sentiment, price, 
                  is_investment_grade, is_report_rejected, is_sold, days_on_market, sale_date) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, tuple(row))

    print(" -> Заповнення мапінгів...")
    # 3. Заповнення довідників у diamond_market (Приклад для Origin)
    cursor.execute("USE diamond_market")
    mappings = [
        ('origin', 1, 'Natural'), ('origin', 2, 'Treated'), 
        ('origin', 3, 'Synthetic'), ('origin', 0, 'Simulant')
    ]
    cursor.executemany("INSERT IGNORE INTO grade_mappings (category, grade_value, grade_label) VALUES (%s, %s, %s)", mappings)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Бази успішно наповнені!")

if __name__ == "__main__":
    seed_data()