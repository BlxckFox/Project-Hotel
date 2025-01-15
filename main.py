from datetime import datetime, timedelta
import sqlite3
import os
import sys

def get_database_path(filename):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    database_dir = os.path.join(application_path, 'database')
    if not os.path.exists(database_dir):
        os.makedirs(database_dir)
    
    return os.path.join(database_dir, filename)

class DateValidationError(Exception):
    pass

def validate_birth_date(date_str):
    try:
        birth_date = datetime.strptime(date_str, "%Y-%m-%d")
        min_date = datetime(1935, 1, 1)
        if birth_date < min_date:  
            raise DateValidationError("Ошибка! Некорректная дата рождения")
    except ValueError:
        raise DateValidationError("Ошибка! Неверный формат даты рождения")

def validate_booking_date(check_in_date_str):
    try:
        check_in_date = datetime.strptime(check_in_date_str, "%Y-%m-%d")
        today = datetime.now()
        max_date = today + timedelta(days=60)  

        if check_in_date.date() < today.date():
            raise DateValidationError("Ошибка! Некорректная дата брони")
        if check_in_date > max_date:
            raise DateValidationError("Ошибка! Невозможно выполнить бронь. Выберите более ранние сроки")
    except ValueError:
        raise DateValidationError("Ошибка! Неверный формат даты бронирования")

def format_date_of_birth(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%b-%d")
    except ValueError:
        raise DateValidationError("Ошибка! Неверный формат даты рождения")

class Rental:
    ECONOM_PRICE = 2000
    COMFORT_PRICE = 3500
    LUX_PRICE = 5000

    def __init__(self):
        self.room_type = ''
        self.room_number = ''
        self.name = ''
        self.date_of_birth = ''
        self.passport = ''
        self.nationality = ''
        self.residence = ''
        self.check_in_time = ''
        self.departure_time = ''
        self.cost = 0
        self.child = ''
        self.pet_pass = ''
        self.excursions = ''
        self.parking_rent_days = 0
        self.additional_services = 0
        self.booking_id = 0
        self.room_cost = 0
        self.transport = ''
        self.payment_type = ''

    def get_available_room(self, room_type, has_children, has_pets):
        db = sqlite3.connect(get_database_path('rooms.db'))
        cursor = db.cursor()
        
        needs_child_room = "Да" if has_children.lower() == "да" else "Нет"
        needs_pet_room = "Да" if has_pets.lower() == "да" else "Нет"
        
        room_type = room_type.split(" (")[0]
        
        cursor.execute(
            "SELECT room_number FROM rooms WHERE quality = ? AND status = 'Свободен' LIMIT 1",
            (room_type,)
        )
        
        result = cursor.fetchone()
        
        if not result:
            db.close()
            raise Exception(f"Нет свободных номеров типа {room_type}")
            
        room_number = result[0]
        
        cursor.execute(
            """UPDATE rooms 
               SET status = 'Забронирован',
                   childs = ?,
                   animals_is_available = ?
               WHERE room_number = ?""",
            (needs_child_room, needs_pet_room, room_number)
        )
        
        db.commit()
        db.close()
        return room_number

    def update_room_status(self, room_number, status):
        db = sqlite3.connect(get_database_path('rooms.db'))
        cursor = db.cursor()
        
        cursor.execute(
            "UPDATE rooms SET status = ? WHERE room_number = ?",
            (status, room_number)
        )
        
        db.commit()
        db.close()

    def departure(self, check_in_time, rental_days):
        check_in_date = datetime.strptime(check_in_time, "%Y-%m-%d")
        departure_date = check_in_date + timedelta(days=rental_days)
        return departure_date.strftime("%Y-%m-%d")

    def booking(self, room_type, name, date_of_birth, passport_series, passport_number, nationality, residence, check_in_time, rental_days, child, pet_pass, excursions, parking_form, transport, payment_type, additional_services):
        validate_birth_date(date_of_birth)
        validate_booking_date(check_in_time)

        self.room_number = self.get_available_room(room_type, child, pet_pass)

        db = sqlite3.connect(get_database_path('clients.db'))
        cursor = db.cursor()

        self.room_type = room_type
        self.name = name
        self.date_of_birth = format_date_of_birth(date_of_birth)
        self.passport = f"{passport_series}/{passport_number}"
        self.nationality = nationality
        self.residence = residence
        self.check_in_time = check_in_time
        self.child = 'Да' if child.lower() == "да" else 'Нет'
        self.pet_pass = 'Да' if pet_pass.lower() == "да" else 'Нет'
        self.payment_type = payment_type

        self.departure_time = self.departure(check_in_time, rental_days)

        room_type_clean = room_type.split(" (")[0].lower()
        
        if room_type_clean == "эконом":
            self.cost = self.ECONOM_PRICE * rental_days
            self.room_cost = self.ECONOM_PRICE
        elif room_type_clean == "комфорт":
            self.cost = self.COMFORT_PRICE * rental_days
            self.room_cost = self.COMFORT_PRICE
        elif room_type_clean == "люкс":
            self.cost = self.LUX_PRICE * rental_days
            self.room_cost = self.LUX_PRICE

        pet_cost = 0
        if pet_pass.lower() == "да":
            pet_cost = 3000 * rental_days
            self.cost += pet_cost

        if excursions.lower() == "планирую посещать":
            excursion_cost = 780 * rental_days
            self.cost += excursion_cost

        parking_cost = 0
        if parking_form == 'да':
            parking_cost = 500 * rental_days
            self.cost += parking_cost

        transport_cost = 0
        if isinstance(transport, str):
            transport = [transport]
        
        for transport_option in transport:
            if transport_option != "не требуется":
                if "Каршеринг (1200" in transport_option:
                    transport_cost += 1200 * rental_days
                elif "Каршеринг VIP (3200" in transport_option:
                    transport_cost += 3200 * rental_days
                elif "Водный скутер" in transport_option:
                    transport_cost += 850 * rental_days
                elif "Абонемент на общественный транспорт" in transport_option:
                    transport_cost += 850  
        self.cost += transport_cost

        self.cost += self.additional_services

        self.excursions = excursions
        self.parking_rent_days = rental_days if parking_form == 'да' else 0
        self.additional_services = additional_services
        self.transport = ", ".join(transport) if isinstance(transport, list) else transport

        cursor.execute(
            """INSERT INTO client (type, room_number, name, date_of_birth, passport_series_and_number, nationality, 
                                   address_place_of_residence, check_in_time, departure_time, 
                                   cost, excursions, child, animal_is_available, parking_rent_days, additional_services, transport,
                                   payment_type, days_changed) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.room_type, self.room_number, self.name, self.date_of_birth, self.passport, self.nationality,
             self.residence, self.check_in_time, self.departure_time,
             self.cost, self.excursions, self.child, self.pet_pass, self.parking_rent_days, self.additional_services, self.transport,
             self.payment_type, 0)
        )

        self.booking_id = cursor.lastrowid

        db.commit()
        db.close()

    def update_booking_dates(self, booking_id, new_check_in_time, new_rental_days):
        try:
            validate_booking_date(new_check_in_time)

            db = sqlite3.connect(get_database_path('clients.db'))
            cursor = db.cursor()

            cursor.execute("""
                SELECT type, cost, parking_rent_days, excursions, passport_series_and_number, room_number
                FROM client 
                WHERE id = ?""", (booking_id,))
            booking_data = cursor.fetchone()

            if not booking_data:
                return False

            room_type, old_cost, parking_days, excursions, passport, room_number = booking_data
            
            new_departure_time = self.departure(new_check_in_time, new_rental_days)

            new_cost = 0
            if room_type.lower() == "эконом":
                new_cost = self.ECONOM_PRICE * new_rental_days
            elif room_type.lower() == "комфорт":
                new_cost = self.COMFORT_PRICE * new_rental_days
            elif room_type.lower() == "люкс":
                new_cost = self.LUX_PRICE * new_rental_days

            if parking_days > 0:
                new_cost += 500 * new_rental_days


            if excursions.lower() == "планирую посещать":
                new_cost += 780 * new_rental_days

            cursor.execute("""
                DELETE FROM client 
                WHERE passport_series_and_number = ? AND id != ?""", 
                (passport, booking_id))

            cursor.execute("""
                UPDATE client 
                SET check_in_time = ?, 
                    departure_time = ?, 
                    cost = ?,
                    parking_rent_days = ?
                WHERE id = ?""", 
                (new_check_in_time, new_departure_time, new_cost, 
                 new_rental_days if parking_days > 0 else 0, booking_id))

            db.commit()
            db.close()
            return True
        except DateValidationError as e:
            raise e
        except Exception as e:
            print(f"Ошибка при обновлении дат: {e}")
            return False


if __name__ == "__main__":
    rental = Rental()
    try:
        rental.booking(
            room_type="Эконом",
            name="Иванов Иван Иванович",
            date_of_birth="1990-01-01",
            passport_series="1234",
            passport_number="567890",
            nationality="Русский",
            residence="г. Москва",
            check_in_time="2025-01-15",
            rental_days=5,
            child="Нет",
            pet_pass="Нет",
            excursions="Не планирую",
            parking_form="Нет",
            transport="не требуется",
            payment_type="Наличными",
            additional_services=0
        )
    except DateValidationError as e:
        print(f"Ошибка: {e}")
