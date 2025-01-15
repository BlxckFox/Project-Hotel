from init_rooms_db import initialize_rooms_db
from edit_db import create_database

def init_all_databases():
    print("Initializing rooms database...")
    initialize_rooms_db()
    print("Initializing clients database...")
    create_database()
    print("Database initialization complete!")

if __name__ == "__main__":
    init_all_databases()
