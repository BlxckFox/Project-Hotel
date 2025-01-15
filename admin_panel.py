import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import sys
from main import get_database_path
from init_rooms_db import initialize_rooms_db
from edit_db import create_database

def init_databases():
    #Инициализация баз данных при первом запуске
    try:
        application_path = os.path.dirname(os.path.abspath(__file__))
        db_dir = os.path.join(application_path, 'database')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Инициализируем базы данных если их нет
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
            tables_to_check = ['client', 'administrators', 'services']
            for table in tables_to_check:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    create_database()
                    break
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при инициализации баз данных: {str(e)}")

class EditRecordWindow:
    def __init__(self, parent, record_id, record_data, callback):
        self.window = tk.Toplevel()
        self.window.title("Редактирование записи")
        self.window.geometry("600x800")
        self.callback = callback
        self.record_id = record_id
        
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill='both', expand=True)
        
        self.fields = {}
        row = 0
        for column, value in record_data.items():
            if column != 'id':
                ttk.Label(frame, text=f"{column}:").grid(row=row, column=0, pady=5, sticky='w')
                entry = ttk.Entry(frame, width=40)
                entry.insert(0, str(value))
                entry.grid(row=row, column=1, pady=5, sticky='w')
                self.fields[column] = entry
                row += 1
        
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_changes).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=self.window.destroy).pack(side='left', padx=5)
    
    def save_changes(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            # SQL запрос для обновления
            update_fields = []
            values = []
            for field, entry in self.fields.items():
                update_fields.append(f"{field} = ?")
                values.append(entry.get())
            
            values.append(self.record_id)
            
            sql = f"UPDATE client SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Изменения сохранены")
            self.callback()  # Апдейт основной таблицы
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

class AdminEditWindow:
    def __init__(self, parent, admin_id=None, admin_data=None, callback=None):
        self.window = tk.Toplevel()
        self.window.title("Редактирование администратора" if admin_id else "Новый администратор")
        self.window.geometry("400x400")
        self.callback = callback
        self.admin_id = admin_id
        
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill='both', expand=True)
        
        # Поля для редактирования
        ttk.Label(frame, text="ФИО:").grid(row=0, column=0, pady=5, sticky='w')
        self.name = ttk.Entry(frame, width=40)
        self.name.grid(row=0, column=1, pady=5, sticky='w')
        
        # Пол
        ttk.Label(frame, text="Пол:").grid(row=1, column=0, pady=5, sticky='w')
        gender_frame = ttk.Frame(frame)
        gender_frame.grid(row=1, column=1, pady=5, sticky='w')
        
        self.gender_var = tk.StringVar(value='м')
        self.male_cb = ttk.Checkbutton(
            gender_frame, 
            text="Мужской", 
            variable=self.gender_var, 
            onvalue='м', 
            offvalue='ж',
            command=lambda: self.female_cb.state(['!selected'] if 'selected' in self.male_cb.state() else ['selected'])
        )
        self.male_cb.pack(side='left', padx=(0, 10))
        
        self.female_cb = ttk.Checkbutton(
            gender_frame, 
            text="Женский", 
            variable=self.gender_var, 
            onvalue='ж', 
            offvalue='м',
            command=lambda: self.male_cb.state(['!selected'] if 'selected' in self.female_cb.state() else ['selected'])
        )
        self.female_cb.pack(side='left')
        
        ttk.Label(frame, text="Дата приема:").grid(row=2, column=0, pady=5, sticky='w')
        self.hire_date = ttk.Entry(frame, width=20)
        self.hire_date.grid(row=2, column=1, pady=5, sticky='w')
        
        ttk.Label(frame, text="Дата увольнения:").grid(row=3, column=0, pady=5, sticky='w')
        self.termination_date = ttk.Entry(frame, width=20)
        self.termination_date.grid(row=3, column=1, pady=5, sticky='w')
        
        ttk.Label(frame, text="Зарплата:").grid(row=4, column=0, pady=5, sticky='w')
        self.salary = ttk.Entry(frame, width=20)
        self.salary.grid(row=4, column=1, pady=5, sticky='w')
        
        if admin_data:
            self.name.insert(0, admin_data['name'])
            self.gender_var.set(admin_data['gender'])
            if admin_data['gender'] == 'м':
                self.male_cb.state(['selected'])
                self.female_cb.state(['!selected'])
            else:
                self.female_cb.state(['selected'])
                self.male_cb.state(['!selected'])
            self.hire_date.insert(0, admin_data['hire_date'])
            if admin_data['termination_date']:
                self.termination_date.insert(0, admin_data['termination_date'])
            self.salary.insert(0, str(admin_data['salary']))
        else:
            # Пол
            self.male_cb.state(['selected'])
            self.female_cb.state(['!selected'])
        
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_changes).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=self.window.destroy).pack(side='left', padx=5)
    
    def save_changes(self):
        try:
            # *
            if not all([self.name.get(), self.hire_date.get(), self.salary.get()]):
                raise ValueError("Заполните все обязательные поля")
            
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            values = [
                self.name.get(),
                self.gender_var.get(),
                self.hire_date.get(),
                self.termination_date.get() if self.termination_date.get() else None,
                int(self.salary.get())
            ]
            
            if self.admin_id:  # Обновление существующих админов в списке
                values.append(self.admin_id)
                cursor.execute('''
                    UPDATE administrators 
                    SET name=?, gender=?, hire_date=?, termination_date=?, salary=?
                    WHERE id=?
                ''', values)
            else:  # Добавление нового админина
                cursor.execute('''
                    INSERT INTO administrators (name, gender, hire_date, termination_date, salary)
                    VALUES (?, ?, ?, ?, ?)
                ''', values)
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Данные сохранены")
            if self.callback:
                self.callback()
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

class AdminPanel:
    def __init__(self):
        # Инициализция БД
        init_databases()
        
        self.root = tk.Tk()
        self.root.title("Панель администратора гостиницы «Каспий»")
        self.root.geometry("1200x800")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Клиентская таблица
        self.clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_frame, text="Клиенты")
        
        # Админ таблица
        self.admins_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.admins_frame, text="Администраторы")
        
        self.setup_clients_tab()
        self.setup_admins_tab()
    
    def setup_admins_tab(self):
        buttons_frame = ttk.Frame(self.admins_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            buttons_frame,
            text="Добавить администратора",
            command=self.add_administrator
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Редактировать",
            command=self.edit_administrator
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Удалить",
            command=self.delete_administrator
        ).pack(side='left', padx=5)
        
        # Таблица админиов
        self.admins_tree = ttk.Treeview(self.admins_frame)
        self.admins_tree.pack(expand=True, fill='both')
        
        vsb = ttk.Scrollbar(self.admins_frame, orient="vertical", command=self.admins_tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(self.admins_frame, orient="horizontal", command=self.admins_tree.xview)
        hsb.pack(side='bottom', fill='x')
        
        self.admins_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.admins_tree['columns'] = ('name', 'gender', 'hire_date', 'termination_date', 'salary')
        self.admins_tree.heading('name', text='ФИО')
        self.admins_tree.heading('gender', text='Пол')
        self.admins_tree.heading('hire_date', text='Дата приема')
        self.admins_tree.heading('termination_date', text='Дата увольнения')
        self.admins_tree.heading('salary', text='Зарплата')
        
        self.admins_tree['show'] = 'headings'
        self.load_administrators()
    
    def setup_clients_tab(self):
        # Фильтры
        filter_frame = ttk.LabelFrame(self.clients_frame, text="Фильтры", padding="10")
        filter_frame.pack(fill='x', pady=(0, 20))
        
        # Даты
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill='x', pady=5)
        
        ttk.Label(date_frame, text="Период с:").pack(side='left', padx=5)
        self.date_from = ttk.Entry(date_frame, width=15)
        self.date_from.pack(side='left', padx=5)
        self.date_from.insert(0, "2025-01-01")
        
        ttk.Label(date_frame, text="по:").pack(side='left', padx=5)
        self.date_to = ttk.Entry(date_frame, width=15)
        self.date_to.pack(side='left', padx=5)
        self.date_to.insert(0, "2025-12-31")
        
        # Дополнительные фильтры
        additional_frame = ttk.Frame(filter_frame)
        additional_frame.pack(fill='x', pady=5)
        
        # Услуга
        ttk.Label(additional_frame, text="Услуга:").pack(side='left', padx=5)
        self.service_entry = ttk.Entry(additional_frame, width=20)
        self.service_entry.pack(side='left', padx=5)
        
        # Тип номера
        ttk.Label(additional_frame, text="Тип номера:").pack(side='left', padx=5)
        self.room_type_var = tk.StringVar(value='люкс')
        room_type_combo = ttk.Combobox(additional_frame, textvariable=self.room_type_var, 
                                     values=['люкс', 'комфорт', 'эконом'], width=10)
        room_type_combo.pack(side='left', padx=5)
        
        # Даты заселения и выселения
        dates_frame = ttk.Frame(filter_frame)
        dates_frame.pack(fill='x', pady=5)
        
        ttk.Label(dates_frame, text="Дата заселения:").pack(side='left', padx=5)
        self.checkin_date = ttk.Entry(dates_frame, width=15)
        self.checkin_date.pack(side='left', padx=5)
        
        ttk.Label(dates_frame, text="Дата выселения:").pack(side='left', padx=5)
        self.checkout_date = ttk.Entry(dates_frame, width=15)
        self.checkout_date.pack(side='left', padx=5)

        # Количество дней переноса
        days_frame = ttk.Frame(filter_frame)
        days_frame.pack(fill='x', pady=5)
        
        ttk.Label(days_frame, text="Количество дней переноса:").pack(side='left', padx=5)
        self.days_changed = ttk.Entry(days_frame, width=10)
        self.days_changed.pack(side='left', padx=5)

        buttons_frame = ttk.Frame(self.clients_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            buttons_frame,
            text="Гости с безналичной оплатой и животными",
            command=self.show_guests_with_pets_and_cashless
        ).pack(pady=5, fill='x')
        
        ttk.Button(
            buttons_frame,
            text="Номера с перенесенной бронью",
            command=self.show_rescheduled_rooms
        ).pack(pady=5, fill='x')
        
        ttk.Button(
            buttons_frame,
            text="Популярные номера",
            command=self.show_popular_rooms
        ).pack(pady=5, fill='x')
        
        ttk.Button(
            buttons_frame,
            text="Статистика администраторов по гостям",
            command=self.show_admin_guests_stats
        ).pack(pady=5, fill='x')
        
        ttk.Button(
            buttons_frame,
            text="Гости по услугам",
            command=self.show_guests_by_service
        ).pack(pady=5, fill='x')
        
        ttk.Button(
            buttons_frame,
            text="Гости по дате выселения",
            command=self.show_guests_by_checkout
        ).pack(pady=5, fill='x')
        
        ttk.Button(
            buttons_frame,
            text="Гости по дате заселения",
            command=self.show_guests_by_checkin
        ).pack(pady=5, fill='x')
        
        ttk.Button(
            buttons_frame,
            text="Статистика по услугам",
            command=self.show_services_stats
        ).pack(pady=5, fill='x')

        # Управление записями
        edit_buttons_frame = ttk.Frame(self.clients_frame)
        edit_buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(edit_buttons_frame, text="Удалить выбранную запись", 
                  command=self.delete_selected_record).pack(side='left', padx=5)
        ttk.Button(edit_buttons_frame, text="Редактировать выбранную запись", 
                  command=self.edit_selected_record).pack(side='left', padx=5)
        
        # Результаты дерева
        self.tree = ttk.Treeview(self.clients_frame)
        self.tree.pack(expand=True, fill='both')
        
        vsb = ttk.Scrollbar(self.clients_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(self.clients_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected_record)
        self.context_menu.add_command(label="Удалить", command=self.delete_selected_record)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        self.show_all_records()
    
    def load_administrators(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            # Очистка
            for item in self.admins_tree.get_children():
                self.admins_tree.delete(item)
            
            cursor.execute("SELECT * FROM administrators ORDER BY name")
            
            for row in cursor.fetchall():
                values = list(row[1:])
                if values[3] is None:
                    values[3] = ""
                self.admins_tree.insert('', 'end', values=values, tags=(str(row[0]),))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def add_administrator(self):
        AdminEditWindow(self.root, callback=self.load_administrators)
    
    def edit_administrator(self):
        selected = self.admins_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите администратора для редактирования")
            return
        
        # Админ
        values = self.admins_tree.item(selected[0])['values']
        admin_id = self.admins_tree.item(selected[0])['tags'][0]
        
        admin_data = {
            'name': values[0],
            'gender': values[1],
            'hire_date': values[2],
            'termination_date': values[3],
            'salary': values[4]
        }
        
        AdminEditWindow(self.root, admin_id, admin_data, self.load_administrators)
    
    def delete_administrator(self):
        selected = self.admins_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите администратора для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого администратора?"):
            try:
                admin_id = self.admins_tree.item(selected[0])['tags'][0]
                
                conn = sqlite3.connect(get_database_path('clients.db'))
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM administrators WHERE id = ?", (admin_id,))
                conn.commit()
                conn.close()
                
                self.admins_tree.delete(selected[0])
                messagebox.showinfo("Успех", "Администратор удален")
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
    
    def search_records(self):
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.show_all_records()
            return
            
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            # Очистка дерева
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            cursor.execute("PRAGMA table_info(client)")
            columns = [info[1] for info in cursor.fetchall()]
            
            self.tree['columns'] = columns
            for col in columns:
                self.tree.heading(col, text=col)
            
            search_conditions = " OR ".join([f"LOWER({col}) LIKE ?" for col in columns])
            search_values = [f"%{search_term}%" for _ in columns]
            
            cursor.execute(f"SELECT * FROM client WHERE {search_conditions}", search_values)
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_all_records(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            # Очистка
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            cursor.execute("PRAGMA table_info(client)")
            columns = [info[1] for info in cursor.fetchall()]
            
            self.tree['columns'] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100) 
            
            cursor.execute("SELECT * FROM client ORDER BY check_in_time DESC")
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def delete_selected_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
            
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
            try:
                record_id = self.tree.item(selected_item)['values'][0]
                
                conn = sqlite3.connect(get_database_path('clients.db'))
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM client WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()
                
                self.tree.delete(selected_item)
                messagebox.showinfo("Успех", "Запись удалена")
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
    
    def edit_selected_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return
            
        try:
            # Данные выбранной записи
            values = self.tree.item(selected_item)['values']
            columns = self.tree['columns']
            
            record_data = dict(zip(columns, values))
            
            #Эдитор
            EditRecordWindow(self.root, values[0], record_data, self.show_all_records)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_context_menu(self, event):
        try:
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def show_guests_with_pets_and_cashless(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            # Очистка дерева
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tree['columns'] = ('name', 'room_type', 'cost', 'check_in', 'departure')
            self.tree.heading('name', text='ФИО')
            self.tree.heading('room_type', text='Тип номера')
            self.tree.heading('cost', text='Стоимость')
            self.tree.heading('check_in', text='Дата заезда')
            self.tree.heading('departure', text='Дата выезда')
            
            cursor.execute('''
                SELECT name, type, cost, check_in_time, departure_time
                FROM client
                WHERE animal_is_available = 'Да'
                AND payment_type = 'Безналичный расчет'
                AND check_in_time BETWEEN ? AND ?
                ORDER BY check_in_time
            ''', (self.date_from.get(), self.date_to.get()))
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_rescheduled_rooms(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tree['columns'] = ('room_number', 'room_type', 'days_changed', 'prepayment')
            self.tree.heading('room_number', text='Номер комнаты')
            self.tree.heading('room_type', text='Тип номера')
            self.tree.heading('days_changed', text='Дней перенесено')
            self.tree.heading('prepayment', text='Предоплата')
            
            days_filter = self.days_changed.get()
            days_condition = f"AND days_changed = {days_filter}" if days_filter else ""
            
            cursor.execute(f'''
                SELECT room_number, type, days_changed, cost * 0.2 as prepayment
                FROM client
                WHERE days_changed > 0 {days_condition}
                AND check_in_time BETWEEN ? AND ?
            ''', (self.date_from.get(), self.date_to.get()))
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
            
            total = len(self.tree.get_children())
            messagebox.showinfo("Статистика", f"Всего номеров с перенесенной бронью: {total}")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_popular_rooms(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tree['columns'] = ('room_number', 'room_type', 'bookings_count')
            self.tree.heading('room_number', text='Номер комнаты')
            self.tree.heading('room_type', text='Тип номера')
            self.tree.heading('bookings_count', text='Количество бронирований')
            
            cursor.execute('''
                SELECT room_number, type, COUNT(*) as bookings_count
                FROM client
                WHERE check_in_time BETWEEN ? AND ?
                GROUP BY room_number
                ORDER BY bookings_count DESC
            ''', (self.date_from.get(), self.date_to.get()))
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
            
            total_bookings = sum(int(self.tree.item(item)['values'][2]) for item in self.tree.get_children())
            messagebox.showinfo("Статистика", 
                f"Всего бронирований: {total_bookings}\n"
                f"Всего уникальных номеров: {len(self.tree.get_children())}")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_admin_guests_stats(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tree['columns'] = ('admin_name', 'guests_count', 'period_start', 'period_end')
            self.tree.heading('admin_name', text='ФИО Администратора')
            self.tree.heading('guests_count', text='Количество гостей')
            self.tree.heading('period_start', text='Начало периода')
            self.tree.heading('period_end', text='Конец периода')
            
            cursor.execute('''
                SELECT a.name, COUNT(c.id) as guests_count, MIN(c.check_in_time), MAX(c.check_in_time)
                FROM administrators a
                JOIN client c ON c.admin_id = a.id
                WHERE c.check_in_time BETWEEN ? AND ?
                AND c.type = 'эконом'
                GROUP BY a.id
                ORDER BY guests_count DESC
            ''', (self.date_from.get(), self.date_to.get()))
            
            results = cursor.fetchall()
            for row in results:
                self.tree.insert('', 'end', values=row)
            
            total = sum(row[1] for row in results)
            messagebox.showinfo("Статистика", f"Общее количество заселенных гостей: {total}")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_guests_by_service(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            # Очистка
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            self.tree['columns'] = ('guest_name', 'room_number', 'room_type', 'services', 'service_count')
            self.tree.heading('guest_name', text='ФИО Гостя')
            self.tree.heading('room_number', text='Номер комнаты')
            self.tree.heading('room_type', text='Тип номера')
            self.tree.heading('services', text='Список услуг')
            self.tree.heading('service_count', text='Количество услуг')
            
            # SQL запрос для получения клиентов с их доп. услугами
            cursor.execute('''
                SELECT 
                    name,
                    room_number,
                    type,
                    (
                        CASE WHEN animal_is_available = 'да' 
                             THEN 'Проживание с животными; ' 
                             ELSE '' 
                        END ||
                        CASE WHEN child = 'да' 
                             THEN 'Дети до 12 лет; ' 
                             ELSE '' 
                        END ||
                        CASE WHEN excursions = 'планирую посещать' 
                             THEN 'Экскурсионный тур; ' 
                             ELSE '' 
                        END ||
                        CASE WHEN parking_rent_days > 0 
                             THEN 'Парковка; ' 
                             ELSE '' 
                        END ||
                        CASE WHEN transport != 'не требуется' AND transport IS NOT NULL 
                             THEN transport || '; '
                             ELSE '' 
                        END
                    ) as services_list,
                    (
                        CASE WHEN animal_is_available = 'да' THEN 1 ELSE 0 END +
                        CASE WHEN child = 'да' THEN 1 ELSE 0 END +
                        CASE WHEN excursions = 'планирую посещать' THEN 1 ELSE 0 END +
                        CASE WHEN parking_rent_days > 0 THEN 1 ELSE 0 END +
                        CASE WHEN transport != 'не требуется' AND transport IS NOT NULL THEN 1 ELSE 0 END
                    ) as service_count
                FROM client
                GROUP BY name, room_number, type
                HAVING service_count > 0
                ORDER BY service_count DESC, name ASC
            ''')
            
            results = cursor.fetchall()
            
            # Результат
            for row in results:
                name, room, type_, services, count = row
                services = services.rstrip('; ')
                self.tree.insert('', 'end', values=(name, room, type_, services, count))
                
            # Отображение статистики
            total_guests = len(results)
            if total_guests > 0:
                cursor.execute('''
                    SELECT AVG(
                        CASE WHEN animal_is_available = 'да' THEN 1 ELSE 0 END +
                        CASE WHEN child = 'да' THEN 1 ELSE 0 END +
                        CASE WHEN excursions = 'планирую посещать' THEN 1 ELSE 0 END +
                        CASE WHEN parking_rent_days > 0 THEN 1 ELSE 0 END +
                        CASE WHEN transport != 'не требуется' AND transport IS NOT NULL THEN 1 ELSE 0 END
                    )
                    FROM client
                ''')
                avg_services = cursor.fetchone()[0]
                
                messagebox.showinfo("Статистика", 
                    f"Найдено гостей с услугами: {total_guests}\n"
                    f"Среднее количество услуг на гостя: {avg_services:.1f}"
                )
            else:
                messagebox.showinfo("Статистика", 
                    "Гостей с дополнительными услугами не найдено"
                )
                
            conn.close()
            
        except Exception as e:
            print(f"Ошибка при поиске по услугам: {e}")
            messagebox.showerror("Ошибка", str(e))

    def show_guests_by_checkout(self):
        try:
            print("Подключение к базе данных...")
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            print("Очистка дерева...")
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            checkout_date = self.checkout_date.get()
            print(f"Дата выселения для поиска: {checkout_date}")
            
            if not checkout_date:
                messagebox.showwarning("Предупреждение", "Введите дату выселения.")
                return
            
            cursor.execute('''
                SELECT name, room_number, type, departure_time
                FROM client
                LIMIT 1
            ''')
            debug_results = cursor.fetchall()
            print("Отладка - пример записи из базы:")
            for row in debug_results:
                print(f"Имя: {row[0]}, Номер: {row[1]}, Тип: {row[2]}, Дата выселения: {row[3]}")
            
            self.tree['columns'] = ('guest_name', 'room_number', 'room_type', 'checkout_date')
            self.tree.heading('guest_name', text='ФИО Гостя')
            self.tree.heading('room_number', text='Номер комнаты')
            self.tree.heading('room_type', text='Категория номера')
            self.tree.heading('checkout_date', text='Дата выселения')
            
            print("Выполнение SQL-запроса...")
            cursor.execute('''
                SELECT name, room_number, type, departure_time
                FROM client
                WHERE substr(departure_time, 1, 10) = ?
                ORDER BY room_number, name
            ''', (checkout_date,))
            
            results = cursor.fetchall()
            print(f"Найдено записей: {len(results)}")
            for row in results:
                self.tree.insert('', 'end', values=row)
                print(f"Добавлена запись: {row}")
            
            total = len(results)
            messagebox.showinfo("Статистика", f"Общее количество выселившихся гостей: {total}")
            
            conn.close()
            
        except Exception as e:
            print(f"Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))

    def show_guests_by_checkin(self): 
        try: 
            conn = sqlite3.connect(get_database_path('clients.db')) 
            cursor = conn.cursor() 
             
            for item in self.tree.get_children(): 
                self.tree.delete(item) 
             
            checkin_date = self.checkin_date.get() 
            print(f"Дата заселения для поиска: {checkin_date}")

            if not checkin_date:
                messagebox.showwarning("Предупреждение", "Введите дату заселения.")
                return
            
            self.tree['columns'] = ('guest_name', 'room_number', 'room_type', 'checkin_date')
            self.tree.heading('guest_name', text='ФИО Гостя')
            self.tree.heading('room_number', text='Номер комнаты')
            self.tree.heading('room_type', text='Категория номера')
            self.tree.heading('checkin_date', text='Дата заселения')
            
            cursor.execute('SELECT DISTINCT check_in_time FROM client')
            dates = cursor.fetchall()
            print("Существующие даты заселения в базе:")
            for date in dates:
                print(date[0])
            
            # Все записи по дате заселения
            cursor.execute('''
                SELECT name, room_number, type, check_in_time
                FROM client
                WHERE substr(check_in_time, 1, 10) = ?
                ORDER BY room_number, name
            ''', (checkin_date,))
            
            results = cursor.fetchall()
            print(f"Найдено записей: {len(results)}")
            for row in results:
                self.tree.insert('', 'end', values=row)
                print(f"Добавлена запись: {row}")
            
            total = len(results)
            messagebox.showinfo("Статистика", 
                f"Найдено гостей по дате заселения: {total}\n"
                f"Дата поиска: {checkin_date}"
            )
            
            conn.close() 
            
        except Exception as e: 
            print(f"Ошибка: {e}")  
            messagebox.showerror("Ошибка", str(e)) 


    def show_services_stats(self):
        try:
            conn = sqlite3.connect(get_database_path('clients.db'))
            cursor = conn.cursor()
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tree['columns'] = ('service_name', 'count', 'total_cost', 'avg_cost')
            self.tree.heading('service_name', text='Название услуги')
            self.tree.heading('count', text='Количество')
            self.tree.heading('total_cost', text='Общая стоимость')
            self.tree.heading('avg_cost', text='Средняя стоимость')
            
            cursor.execute('''
                SELECT 
                    service_name,
                    COUNT(*) as count,
                    SUM(cost) as total_cost,
                    AVG(cost) as avg_cost
                FROM services
                GROUP BY service_name
                ORDER BY count DESC
            ''')
            
            results = cursor.fetchall()
            for row in results:
                self.tree.insert('', 'end', values=row)
            
            total_services = sum(row[1] for row in results)
            total_cost = sum(row[2] for row in results)
            messagebox.showinfo("Статистика", 
                              f"Общее количество оказанных услуг: {total_services}\n"
                              f"Общая стоимость услуг: {total_cost:.2f}")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AdminPanel()
    app.run()
