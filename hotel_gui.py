import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import sys
import sqlite3

# Добавляем путь к текущей директории в sys.path
if getattr(sys, 'frozen', False):
    # Если приложение "заморожено" (exe)
    application_path = os.path.dirname(sys.executable)
else:
    # Если запущено как .py
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

from main import Rental, get_database_path, DateValidationError
from init_rooms_db import initialize_rooms_db
from edit_db import create_database

def init_databases():
    #Инициализация баз данных при первом запуске
    try:
        db_dir = os.path.join(application_path, 'database')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        rooms_db = get_database_path('rooms.db')
        clients_db = get_database_path('clients.db')
        
        if not os.path.exists(rooms_db):
            initialize_rooms_db()
        if not os.path.exists(clients_db):
            create_database()
            
        # Проверка таблиц
        with sqlite3.connect(rooms_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rooms'")
            if not cursor.fetchone():
                initialize_rooms_db()
                
        with sqlite3.connect(clients_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='client'")
            if not cursor.fetchone():
                create_database()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при инициализации баз данных: {str(e)}")
        sys.exit(1)

class WelcomeWindow:
    def __init__(self):
        # Инициализируем базы данных
        init_databases()
        
        self.rental = Rental()
        self.root = tk.Tk()
        self.root.title("Гостиница «Каспий»")
        self.root.geometry("800x600")
        
        # Styles
        style = ttk.Style()
        style.configure('Large.TButton', font=('Helvetica', 14))
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        welcome_text = """Добро пожаловать в гостиницу «Каспий»!
        
Мы рады приветствовать вас в нашей гостиице."""
        
        welcome_label = ttk.Label(main_frame, text=welcome_text, font=('Helvetica', 16))
        welcome_label.pack(pady=50)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=30)
        
        continue_button = ttk.Button(
            buttons_frame, 
            text="Новое бронирование", 
            style='Large.TButton',
            command=self.open_booking_window
        )
        continue_button.pack(pady=10)
        
        change_dates_button = ttk.Button(
            buttons_frame, 
            text="Изменить даты бронирования", 
            style='Large.TButton',
            command=self.open_change_dates_window
        )
        change_dates_button.pack(pady=10)

        # Кнопка управления услугами
        services_button = ttk.Button(
            self.root,
            text="Управление услугами",
            command=self.open_services_tab
        )
        services_button.pack(side='right', padx=10, pady=10)

    def open_booking_window(self):
        self.root.withdraw()
        BookingWindow(self)
        
    def open_change_dates_window(self):
        ChangeDatesWindow()
        
    def open_services_tab(self):
        self.root.withdraw()
        booking_window = BookingWindow(self)
        # Переключаемся на вкладку услуг
        booking_window.notebook.select(1)  # Индекс 1 - вкладка доп. услуг

    def show(self):
        self.root.mainloop()

class ChangeDatesWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Изменить даты бронирования")
        self.window.geometry("400x300")
        
        self.rental = Rental()
        
        frame = ttk.Frame(self.window, padding="10")
        frame.pack(fill='both', expand=True)
        
        # Реаренда
        ttk.Label(frame, text="Номер бронирования:").grid(row=0, column=0, pady=5, sticky='w')
        self.booking_id = ttk.Entry(frame, width=40)
        self.booking_id.grid(row=0, column=1, pady=5, sticky='w')
        
        # Новая дата заезда
        ttk.Label(frame, text="Новая дата заезда (ГГГГ-ММ-ДД):").grid(row=1, column=0, pady=5, sticky='w')
        self.new_check_in = ttk.Entry(frame, width=40)
        self.new_check_in.grid(row=1, column=1, pady=5, sticky='w')
        
        # Новое количество дней
        ttk.Label(frame, text="Количество дней:").grid(row=2, column=0, pady=5, sticky='w')
        self.new_days = ttk.Entry(frame, width=40)
        self.new_days.grid(row=2, column=1, pady=5, sticky='w')
        
        # Кнопка изменения дат
        ttk.Button(frame, text="Изменить даты", command=self.update_dates).grid(row=3, column=0, columnspan=2, pady=20)

    def update_dates(self):
        try:
            booking_id = int(self.booking_id.get())
            new_check_in = self.new_check_in.get()
            new_days = int(self.new_days.get())
            
            # Даты
            try:
                datetime.strptime(new_check_in, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте формат ГГГГ-ММ-ДД")
                return
            
            if self.rental.update_booking_dates(booking_id, new_check_in, new_days):
                messagebox.showinfo("Успех", "Даты бронирования успешно изменены!")
                self.window.destroy()
            else:
                messagebox.showerror("Ошибка", "Бронирование с указанным номером не найдено")
        except DateValidationError as e:
            messagebox.showerror("Ошибка", str(e))
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, проверьте правильность введенных данных")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

class PaymentForm:
    def __init__(self, parent, total_cost):
        self.window = tk.Toplevel()
        self.window.title("Оплата по карте")
        self.window.geometry("400x500")
        
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill='both', expand=True)
        
        # Заголовок с суммой
        ttk.Label(frame, text=f"Сумма к оплате: {total_cost} руб.", font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        # Номер карты
        ttk.Label(frame, text="Номер карты:").pack(pady=5)
        self.card_number = ttk.Entry(frame, width=30)
        self.card_number.pack(pady=5)
        
        # Срок действия
        ttk.Label(frame, text="Срок действия (ММ/ГГ):").pack(pady=5)
        self.expiry = ttk.Entry(frame, width=10)
        self.expiry.pack(pady=5)
        
        # CVV
        ttk.Label(frame, text="CVV:").pack(pady=5)
        self.cvv = ttk.Entry(frame, width=5, show="*")
        self.cvv.pack(pady=5)
        
        # Имя держателя
        ttk.Label(frame, text="Имя держателя карты:").pack(pady=5)
        self.card_holder = ttk.Entry(frame, width=30)
        self.card_holder.pack(pady=5)
        
        # Кнопка оплаты
        ttk.Button(frame, text="Оплатить", command=self.process_payment).pack(pady=20)
        
    def process_payment(self):
        # Имитация обработки платежа
        messagebox.showinfo("Успех", "Оплата прошла успешно!")
        self.window.destroy()

class BookingWindow:
    def __init__(self, welcome_window):
        self.welcome_window = welcome_window
        self.rental = Rental()
        
        self.window = tk.Toplevel()
        self.window.title("Бронирование номера")
        self.window.geometry("1000x800")
        
        # Основной контейнер
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both', pady=10)
        
        # Вкладка основной информации
        main_info_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(main_info_frame, text="Основная информация")
        
        # Вкладка дополнительных услуг
        services_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(services_frame, text="Дополнительные услуги")
        
        # Основная информация
        self.create_main_info_fields(main_info_frame)
        
        # Дополнительные услуги
        self.create_services_fields(services_frame)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(buttons_frame, text="Забронировать", command=self.book_room).pack(side='right', padx=5)
        ttk.Button(buttons_frame, text="Назад", command=self.go_back).pack(side='right', padx=5)

    def create_main_info_fields(self, frame):
        # Тип номера
        ttk.Label(frame, text="Тип номера:").grid(row=0, column=0, pady=5, sticky='w')
        self.room_type = ttk.Combobox(frame, values=[
            f"Эконом ({self.rental.ECONOM_PRICE} руб/сутки)", 
            f"Комфорт ({self.rental.COMFORT_PRICE} руб/сутки)", 
            f"Люкс ({self.rental.LUX_PRICE} руб/сутки)"
        ])
        self.room_type.grid(row=0, column=1, pady=5, sticky='w')
        
        # Тип оплаты
        ttk.Label(frame, text="Тип оплаты:").grid(row=1, column=0, pady=5, sticky='w')
        self.payment_type = ttk.Combobox(frame, values=["Оплата по карте", "Безналичный расчет"])
        self.payment_type.grid(row=1, column=1, pady=5, sticky='w')
        self.payment_type.set("Оплата по карте")
        
        # Личные данные
        ttk.Label(frame, text="ФИО:").grid(row=2, column=0, pady=5, sticky='w')
        self.name = ttk.Entry(frame, width=40)
        self.name.grid(row=2, column=1, pady=5, sticky='w')
        
        ttk.Label(frame, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=3, column=0, pady=5, sticky='w')
        self.birth_date = ttk.Entry(frame, width=40)
        self.birth_date.grid(row=3, column=1, pady=5, sticky='w')
        
        # Паспортные данные
        ttk.Label(frame, text="Серия паспорта:").grid(row=4, column=0, pady=5, sticky='w')
        self.passport_series = ttk.Entry(frame, width=40)
        self.passport_series.grid(row=4, column=1, pady=5, sticky='w')
        
        ttk.Label(frame, text="Номер паспорта:").grid(row=5, column=0, pady=5, sticky='w')
        self.passport_number = ttk.Entry(frame, width=40)
        self.passport_number.grid(row=5, column=1, pady=5, sticky='w')
        
        # Дополнительная информация
        ttk.Label(frame, text="Национальность:").grid(row=6, column=0, pady=5, sticky='w')
        self.nationality = ttk.Entry(frame, width=40)
        self.nationality.grid(row=6, column=1, pady=5, sticky='w')
        
        ttk.Label(frame, text="Страна рождения:").grid(row=7, column=0, pady=5, sticky='w')
        self.residence = ttk.Entry(frame, width=40)
        self.residence.grid(row=7, column=1, pady=5, sticky='w')
        
        ttk.Label(frame, text="Количество дней:").grid(row=8, column=0, pady=5, sticky='w')
        self.rental_days = ttk.Entry(frame, width=40)
        self.rental_days.grid(row=8, column=1, pady=5, sticky='w')

    def create_services_fields(self, frame):
        # Животные
        ttk.Label(frame, text="Проживание с животными:").grid(row=0, column=0, pady=5, sticky='w')
        self.pet_pass = ttk.Combobox(frame, values=["да", "нет"])
        self.pet_pass.grid(row=0, column=1, pady=5, sticky='w')
        self.pet_pass.set("нет")

        # Дети
        ttk.Label(frame, text="Имеются у вас дети до 12 лет?:").grid(row=0, column=2, pady=5, sticky='w')
        self.children = ttk.Combobox(frame, values=["да", "нет"])
        self.children.grid(row=0, column=3, pady=5, sticky='w')
        self.children.set("нет")
        
        # Экскурсии
        ttk.Label(frame, text="Экскурсионный тур:").grid(row=1, column=0, pady=5, sticky='w')
        self.excursions = ttk.Combobox(frame, values=["планирую посещать", "не планирую посещать"])
        self.excursions.grid(row=1, column=1, pady=5, sticky='w')
        self.excursions.set("не планирую посещать")
        
        ttk.Label(frame, text="Парковка:").grid(row=2, column=0, pady=5, sticky='w')
        self.parking = ttk.Combobox(frame, values=["да", "нет"])
        self.parking.grid(row=2, column=1, pady=5, sticky='w')
        self.parking.set("нет")

        # Транспорт
        ttk.Label(frame, text="Транспорт:").grid(row=3, column=0, pady=5, sticky='w')
        transport_frame = ttk.Frame(frame)
        transport_frame.grid(row=3, column=1, columnspan=3, pady=5, sticky='w')
        
        self.transport_listbox = tk.Listbox(transport_frame, selectmode=tk.MULTIPLE, width=50, height=5)
        self.transport_listbox.pack(side='left', fill='both')
        
        # Скролбар
        scrollbar = ttk.Scrollbar(transport_frame, orient="vertical", command=self.transport_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.transport_listbox.configure(yscrollcommand=scrollbar.set)
        
        transport_options = [
            "не требуется",
            "Каршеринг (1200 руб/сутки)",
            "Каршеринг VIP (3200 руб/сутки)",
            "Водный скутер \"Морион\" (850 руб/сутки)",
            "Абонемент на общественный транспорт (850 руб на весь срок)"
        ]
        
        for option in transport_options:
            self.transport_listbox.insert(tk.END, option)
            
        # Не требуется по умолч.
        self.transport_listbox.select_set(0)

    def get_selected_transport(self):
        selected_indices = self.transport_listbox.curselection()
        selected_transport = [self.transport_listbox.get(i) for i in selected_indices]
        if "не требуется" in selected_transport and len(selected_transport) > 1:
            selected_transport.remove("не требуется")
        return selected_transport if selected_transport else ["не требуется"]

    def book_room(self):
        try:
            rental_days = int(self.rental_days.get())
            
            self.rental.booking(
                room_type=self.room_type.get(),
                name=self.name.get(),
                date_of_birth=self.birth_date.get(),
                passport_series=self.passport_series.get(),
                passport_number=self.passport_number.get(),
                nationality=self.nationality.get(),
                residence=self.residence.get(),
                check_in_time=datetime.utcnow().strftime("%Y-%m-%d"),
                rental_days=rental_days,
                child=self.children.get(),
                pet_pass=self.pet_pass.get(),
                excursions=self.excursions.get(),
                parking_form=self.parking.get(),
                transport=self.get_selected_transport(),
                payment_type=self.payment_type.get(),
                additional_services=1
            )
            
            if self.payment_type.get() == "Оплата по карте":
                payment_form = PaymentForm(self, self.rental.cost)
                payment_form.window.wait_window()
            
            message = f"""Бронирование успешно!

Номер бронирования: {self.rental.booking_id}
Номер комнаты: {self.rental.room_number}
Дата отъезда: {self.rental.departure_time}
Стоимость: {self.rental.cost} руб."""

            if self.payment_type.get() == "Безналичный расчет":
                message += f"\n\n{self.name.get()}, для оплаты подойдите к стойке администрирования заранее"

            messagebox.showinfo("Успех", message)
            
            self.window.destroy()
            self.welcome_window.root.deiconify()
            
        except DateValidationError as e:
            messagebox.showerror("Ошибка", str(e))
        except ValueError as e:
            messagebox.showerror("Ошибка", "Пожалуйста, проверьте правильность введенных данных")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def go_back(self):
        self.window.destroy()
        self.welcome_window.root.deiconify()

if __name__ == "__main__":
    app = WelcomeWindow()
    app.show()
