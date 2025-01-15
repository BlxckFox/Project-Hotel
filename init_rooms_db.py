import sqlite3
import random
from main import get_database_path

def initialize_rooms_db():
    db = sqlite3.connect(get_database_path('rooms.db'))
    cursor = db.cursor()
    
    cursor.execute('''DROP TABLE IF EXISTS rooms''')

    cursor.execute('''
    CREATE TABLE rooms (
        room_id INTEGER PRIMARY KEY,
        room_number TEXT NOT NULL,
        quality TEXT NOT NULL,
        status TEXT NOT NULL,
        childs TEXT,
        animals_is_available TEXT
    )
    ''')

    # Распределение номеров по этажам
    total_rooms = 108
    economy_rooms = 52
    comfort_rooms = 28
    luxury_rooms = total_rooms - economy_rooms - comfort_rooms  # 28

    # Список всех номеров
    all_rooms = []
    for floor in range(1, 10):
        for room in range(1, 13):
            room_number = f"{floor}{room:02d}" 
            all_rooms.append(room_number)

    random.shuffle(all_rooms)

    rooms_data = []
    
    for i in range(economy_rooms):
        rooms_data.append((all_rooms[i], 'Эконом', 'Свободен', '', ''))
    
    for i in range(economy_rooms, economy_rooms + comfort_rooms):
        rooms_data.append((all_rooms[i], 'Комфорт', 'Свободен', '', ''))
    
    for i in range(economy_rooms + comfort_rooms, total_rooms):
        rooms_data.append((all_rooms[i], 'Люкс', 'Свободен', '', ''))

    cursor.executemany(
        'INSERT INTO rooms (room_number, quality, status, childs, animals_is_available) VALUES (?, ?, ?, ?, ?)',
        rooms_data
    )

    db.commit()
    db.close()

if __name__ == "__main__":
    initialize_rooms_db()
