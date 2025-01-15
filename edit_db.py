import sqlite3
import os
from utils import get_database_path

def create_database():
    db_path = get_database_path('clients.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS client (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        passport_series TEXT NOT NULL,
        passport_number TEXT NOT NULL,
        nationality TEXT NOT NULL,
        residence TEXT NOT NULL,
        room_number TEXT NOT NULL,
        type TEXT NOT NULL,
        check_in_time TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        rental_days INTEGER NOT NULL,
        child TEXT NOT NULL,
        animal_is_available TEXT NOT NULL,
        excursions TEXT NOT NULL,
        parking_form TEXT NOT NULL,
        transport TEXT,
        payment_type TEXT NOT NULL,
        additional_services INTEGER NOT NULL,
        cost REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS administrator (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        hire_date TEXT NOT NULL,
        termination_date TEXT,
        salary REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        service_name TEXT NOT NULL,
        service_date TEXT NOT NULL,
        cost REAL NOT NULL,
        FOREIGN KEY (client_id) REFERENCES client (id)
    )
    ''')

    cursor.execute('''
    INSERT INTO client (
        name, date_of_birth, passport_series, passport_number,
        nationality, residence, room_number, type,
        check_in_time, departure_time, rental_days,
        child, animal_is_available, excursions,
        parking_form, transport, payment_type, additional_services, cost
    )
    VALUES (
        'Иванов Иван Иванович', '1990-01-01', '1234', '567890',
        'РФ', 'Москва', '101', 'люкс',
        '2024-01-01', '2024-01-05', 4,
        'Да', 'Нет', 'планирую посещать',
        'Да', 'Каршеринг (1200 руб/сутки)', 'Оплата по карте', 2, 32000
    )
    ''')

    cursor.execute('''
    INSERT INTO administrator (name, gender, hire_date, salary)
    VALUES ('Петров Петр Петрович', 'М', '2023-01-01', 50000)
    ''')

    cursor.execute('''
    INSERT INTO client (
        name, date_of_birth, passport_series, passport_number,
        nationality, residence, room_number, type,
        check_in_time, departure_time, rental_days,
        child, animal_is_available, excursions,
        parking_form, transport, payment_type, additional_services, cost
    )
    VALUES (
        'Сидоров Сидор Сидорович', '1985-05-15', '5678', '123456',
        'РФ', 'Санкт-Петербург', '102', 'комфорт',
        '2024-02-01', '2024-02-05', 4,
        'Да', 'Да', 'планирую посещать',
        'Да', 'Каршеринг VIP (3200 руб/сутки)', 'Безналичный расчет', 2, 16000
    )
    ''')

    conn.commit()
    conn.close()
