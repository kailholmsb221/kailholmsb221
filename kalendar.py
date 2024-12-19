import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime, timedelta
import sqlite3
import os
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Инициализация базы данных ---
def initialize_db():
    conn = sqlite3.connect('class_journal.db')
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            contact_phone TEXT,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            birth_date TEXT,
            gender TEXT,
            class TEXT,
            contact_phone TEXT,
            address TEXT,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES parents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS school (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            director TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            date TEXT,
            grade INTEGER,
            comment TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            comments TEXT,
            reference_id INTEGER,
            event_type TEXT
        )
    """)

    # Заполнение начальными данными, если таблицы пусты
    cursor.execute("SELECT COUNT(*) FROM school")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO school (name, address, contact_phone, contact_email, director)
            VALUES (?, ?, ?, ?, ?)
        """, ("Школа №1", "г. Москва, ул. Ленина, д.1", "1234567890", "school1@example.com", "Иванов Иван Иванович"))

    cursor.execute("SELECT COUNT(*) FROM parents")
    if cursor.fetchone()[0] == 0:
        parents = [
            ("Петрова Мария Сергеевна", "0987654321", "г. Москва, ул. Пушкина, д.2"),
            ("Сидоров Алексей Николаевич", "1122334455", "г. Москва, ул. Чехова, д.3")
        ]
        cursor.executemany("""
            INSERT INTO parents (full_name, contact_phone, address)
            VALUES (?, ?, ?)
        """, parents)

    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        students = [
            ("Иванов Иван Иванович", "15.04.2010", "М", "7А", "5551234567", "г. Москва, ул. Ленина, д.1", 1),
            ("Смирнова Анна Петровна", "22.08.2010", "Ж", "7Б", "5559876543", "г. Москва, ул. Ленина, д.1", 2)
        ]
        cursor.executemany("""
            INSERT INTO students (full_name, birth_date, gender, class, contact_phone, address, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, students)

    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] == 0:
        subjects = [
            ("Математика", "Сидоров Сергей Петрович"),
            ("Русский язык", "Кузнецова Светлана Владимировна"),
            ("Английский язык", "Иванова Наталья Юрьевна"),
            ("Физика", "Павлов Дмитрий Александрович"),
            ("Химия", "Васильев Алексей Иванович"),
            ("История", "Лебедева Мария Сергеевна")
        ]
        cursor.executemany("""
            INSERT INTO subjects (name, teacher)
            VALUES (?, ?)
        """, subjects)

    conn.commit()
    conn.close()

initialize_db()

# --- Главное Окно Приложения ---
class MainApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Меню
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Разделы меню
        profile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Профиль", menu=profile_menu)
        profile_menu.add_command(label="Профиль ученика", command=self.open_student_profile)
        profile_menu.add_command(label="Профиль родителя", command=self.open_parent_profile)

        education_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Место обучения", menu=education_menu)
        education_menu.add_command(label="Информация об учебном заведении", command=self.open_school_info)

        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Анализ успеваемости", menu=analysis_menu)
        analysis_menu.add_command(label="Анализ академической успеваемости", command=self.open_performance_analysis)

        menubar.add_command(label="Календарь", command=self.open_calendar)
        menubar.add_command(label="Выход", command=self.master.quit)

    def open_student_profile(self):
        StudentProfileWindow(self.master)

    def open_parent_profile(self):
        ParentProfileWindow(self.master)

    def open_school_info(self):
        SchoolInfoWindow(self.master)

    def open_performance_analysis(self):
        PerformanceAnalysisWindow(self.master)

    def open_calendar(self):
        CalendarAppWindow(self.master)

# --- Профиль ученика ---
class StudentProfileWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Профиль ученика")
        self.geometry("900x700")
        self.resizable(False, False)
        self.create_widgets()
        self.load_student_data()

    def create_widgets(self):
        # Шапка профиля
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        # Аватарка
        self.avatar_size = (150, 150)
        self.avatar_path = "default_avatar.png"  # Путь к дефолтной аватарке
        self.load_avatar(self.avatar_path)
        self.avatar_label = tk.Label(header_frame, image=self.avatar_image, bd=2, relief=tk.RIDGE)
        self.avatar_label.pack()

        # ФИО и класс
        self.full_name_var = tk.StringVar()
        self.class_var = tk.StringVar()
        tk.Label(header_frame, textvariable=self.full_name_var, font=("Arial", 18, "bold")).pack(pady=5)
        tk.Label(header_frame, textvariable=self.class_var, font=("Arial", 14)).pack()

        # Основная информация
        info_frame = tk.Frame(self)
        info_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Личная информация
        personal_info_frame = tk.LabelFrame(info_frame, text="Личная информация", padx=10, pady=10)
        personal_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Дата рождения
        tk.Label(personal_info_frame, text="Дата рождения:").grid(row=0, column=0, sticky='e', pady=5)
        self.birth_date_var = tk.StringVar()
        tk.Label(personal_info_frame, textvariable=self.birth_date_var).grid(row=0, column=1, sticky='w', pady=5)

        # Контактный телефон
        tk.Label(personal_info_frame, text="Контактный телефон:").grid(row=1, column=0, sticky='e', pady=5)
        self.contact_phone_var = tk.StringVar()
        tk.Label(personal_info_frame, textvariable=self.contact_phone_var).grid(row=1, column=1, sticky='w', pady=5)

        # Адрес
        tk.Label(personal_info_frame, text="Адрес:").grid(row=2, column=0, sticky='e', pady=5)
        self.address_var = tk.StringVar()
        tk.Label(personal_info_frame, textvariable=self.address_var).grid(row=2, column=1, sticky='w', pady=5)

        # Кнопка редактирования
        self.edit_button = tk.Button(personal_info_frame, text="Редактировать", bg="orange", width=15, command=self.edit_personal_info)
        self.edit_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Учебная информация
        academic_info_frame = tk.LabelFrame(info_frame, text="Учебная информация", padx=10, pady=10)
        academic_info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Таблица предметов
        columns = ("Предмет", "Преподаватель", "Последняя оценка", "Действие")
        self.subjects_tree = ttk.Treeview(academic_info_frame, columns=columns, show='headings')
        for col in columns:
            self.subjects_tree.heading(col, text=col)
            self.subjects_tree.column(col, width=150)
        self.subjects_tree.pack(fill=tk.BOTH, expand=True)

        # Добавление кнопки "Посмотреть журнал" в таблицу
        self.subjects_tree.bind("<Double-1>", self.on_subject_double_click)

        # Нижняя часть профиля
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(pady=20)

        # Кнопка анализа успеваемости
        self.analysis_button = tk.Button(bottom_frame, text="Анализ академической успеваемости", bg="blue", fg="white", width=30, height=2, command=self.open_performance_analysis)
        self.analysis_button.pack(pady=10)

        # Кнопка "Назад в главное меню"
        self.back_button = tk.Button(bottom_frame, text="Назад в главное меню", bg="gray", fg="white", width=20, height=2, command=self.destroy)
        self.back_button.pack(pady=10)

    def load_avatar(self, path):
        try:
            image = Image.open(path).resize(self.avatar_size, Image.ANTIALIAS)
            # Создание круглой маски
            mask = Image.new('L', self.avatar_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + self.avatar_size, fill=255)
            image.putalpha(mask)
            self.avatar_image = ImageTk.PhotoImage(image)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить аватарку: {e}")
            # Создание дефолтной аватарки
            image = Image.new('RGB', self.avatar_size, color='gray')
            mask = Image.new('L', self.avatar_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + self.avatar_size, fill=255)
            image.putalpha(mask)
            self.avatar_image = ImageTk.PhotoImage(image)

    def load_student_data(self):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        # Предположим, что мы загружаем первого ученика из базы
        cursor.execute("""
            SELECT students.full_name, students.class, students.birth_date, students.contact_phone, students.address
            FROM students
            LIMIT 1
        """)
        student = cursor.fetchone()
        if student:
            self.full_name_var.set(student[0])
            self.class_var.set(f"Класс: {student[1]}")
            self.birth_date_var.set(student[2])
            self.contact_phone_var.set(student[3])
            self.address_var.set(student[4])
        else:
            messagebox.showinfo("Информация", "В базе данных нет учеников.")
        conn.close()

        # Загрузка таблицы предметов и последних оценок
        self.load_subjects()

    def load_subjects(self):
        for row in self.subjects_tree.get_children():
            self.subjects_tree.delete(row)
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT subjects.id, subjects.name, subjects.teacher, MAX(grades.grade)
            FROM subjects
            LEFT JOIN grades ON subjects.id = grades.subject_id
            GROUP BY subjects.id
        """)
        subjects = cursor.fetchall()
        for subj in subjects:
            last_grade = subj[3] if subj[3] is not None else "Нет оценок"
            self.subjects_tree.insert("", tk.END, values=(subj[1], subj[2], last_grade, "Посмотреть журнал"))
        conn.close()

    def edit_personal_info(self):
        EditPersonalInfoWindow(self)

    def open_performance_analysis(self):
        PerformanceAnalysisWindow(self)

    def on_subject_double_click(self, event):
        selected_item = self.subjects_tree.focus()
        if not selected_item:
            return
        subject_name = self.subjects_tree.item(selected_item)['values'][0]
        JournalWindow(self, subject_name)

# --- Форма Редактирования Личной Информации Ученика ---
class EditPersonalInfoWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Редактировать личную информацию")
        self.geometry("400x400")
        self.parent = parent
        self.create_widgets()
        self.load_current_data()

    def create_widgets(self):
        # ФИО
        tk.Label(self, text="ФИО:").pack(pady=5)
        self.full_name_var = tk.StringVar()
        self.full_name_entry = tk.Entry(self, textvariable=self.full_name_var)
        self.full_name_entry.pack(fill=tk.X, padx=20)

        # Дата рождения
        tk.Label(self, text="Дата рождения (ДД.ММ.ГГГГ):").pack(pady=5)
        self.birth_date_var = tk.StringVar()
        self.birth_date_entry = tk.Entry(self, textvariable=self.birth_date_var)
        self.birth_date_entry.pack(fill=tk.X, padx=20)

        # Контактный телефон
        tk.Label(self, text="Контактный телефон:").pack(pady=5)
        self.contact_phone_var = tk.StringVar()
        self.contact_phone_entry = tk.Entry(self, textvariable=self.contact_phone_var)
        self.contact_phone_entry.pack(fill=tk.X, padx=20)

        # Адрес
        tk.Label(self, text="Адрес:").pack(pady=5)
        self.address_var = tk.StringVar()
        self.address_entry = tk.Entry(self, textvariable=self.address_var)
        self.address_entry.pack(fill=tk.X, padx=20)

        # Кнопка сохранения
        tk.Button(self, text="Сохранить", bg="green", fg="white", command=self.save_changes).pack(pady=20)

    def load_current_data(self):
        self.full_name_var.set(self.parent.full_name_var.get())
        self.birth_date_var.set(self.parent.birth_date_var.get())
        self.contact_phone_var.set(self.parent.contact_phone_var.get())
        self.address_var.set(self.parent.address_var.get())

    def save_changes(self):
        full_name = self.full_name_var.get().strip()
        birth_date = self.birth_date_var.get().strip()
        contact_phone = self.contact_phone_var.get().strip()
        address = self.address_var.get().strip()

        if not all([full_name, birth_date, contact_phone, address]):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Валидация даты рождения
        try:
            datetime.strptime(birth_date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты рождения.")
            return

        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        # Предположим, что мы редактируем первого ученика
        cursor.execute("""
            UPDATE students
            SET full_name=?, birth_date=?, contact_phone=?, address=?
            WHERE id=?
        """, (full_name, birth_date, contact_phone, address, 1))
        conn.commit()
        conn.close()

        # Обновление данных в основном окне
        self.parent.full_name_var.set(full_name)
        self.parent.birth_date_var.set(birth_date)
        self.parent.contact_phone_var.set(contact_phone)
        self.parent.address_var.set(address)
        messagebox.showinfo("Успех", "Данные успешно обновлены.")
        self.destroy()

# --- Журнал по Предмету ---
class JournalWindow(tk.Toplevel):
    def __init__(self, master, subject_name):
        super().__init__(master)
        self.title(f"Журнал по предмету: {subject_name}")
        self.geometry("700x500")
        self.subject_name = subject_name
        self.create_widgets()
        self.load_journal_data()

    def create_widgets(self):
        columns = ("Дата", "Оценка", "Комментарий")
        self.journal_tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.journal_tree.heading(col, text=col)
            self.journal_tree.column(col, width=150)
        self.journal_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить запись", bg="green", fg="white", command=self.add_journal_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Редактировать запись", bg="orange", command=self.edit_journal_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Удалить запись", bg="red", fg="white", command=self.delete_journal_entry).pack(side=tk.LEFT, padx=5)

    def load_journal_data(self):
        for row in self.journal_tree.get_children():
            self.journal_tree.delete(row)
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT grades.id, grades.date, grades.grade, grades.comment
            FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE subjects.name=?
            ORDER BY grades.date
        """, (self.subject_name,))
        entries = cursor.fetchall()
        conn.close()
        for entry in entries:
            self.journal_tree.insert("", tk.END, values=(entry[1], entry[2], entry[3]), tags=(entry[0],))

    def add_journal_entry(self):
        JournalEntryForm(self, self.subject_name, self.load_journal_data)

    def edit_journal_entry(self):
        selected = self.journal_tree.focus()
        if not selected:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для редактирования.")
            return
        entry_id = self.journal_tree.item(selected, 'tags')[0]
        JournalEntryForm(self, self.subject_name, self.load_journal_data, entry_id=entry_id)

    def delete_journal_entry(self):
        selected = self.journal_tree.focus()
        if not selected:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для удаления.")
            return
        entry_id = self.journal_tree.item(selected, 'tags')[0]
        values = self.journal_tree.item(selected, 'values')
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить запись от {values[0]}?")
        if confirm:
            conn = sqlite3.connect('class_journal.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM grades WHERE id=?", (entry_id,))
            conn.commit()
            conn.close()
            self.load_journal_data()
            messagebox.showinfo("Успех", "Запись удалена успешно.")

# --- Форма Добавления/Редактирования Записи в Журнале Ученика ---
class JournalEntryForm(tk.Toplevel):
    def __init__(self, parent, subject_name, refresh_callback, entry_id=None):
        super().__init__(parent)
        self.title("Добавить запись" if not entry_id else "Редактировать запись")
        self.geometry("400x400")
        self.subject_name = subject_name
        self.refresh_callback = refresh_callback
        self.entry_id = entry_id
        self.create_widgets()
        if self.entry_id:
            self.load_entry_data()

    def create_widgets(self):
        # Дата
        tk.Label(self, text="Дата (ДД.ММ.ГГГГ):").pack(pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(self, textvariable=self.date_var)
        self.date_entry.pack(fill=tk.X, padx=20)

        # Оценка
        tk.Label(self, text="Оценка (1-10):").pack(pady=5)
        self.grade_var = tk.StringVar()
        self.grade_entry = tk.Entry(self, textvariable=self.grade_var)
        self.grade_entry.pack(fill=tk.X, padx=20)

        # Комментарий
        tk.Label(self, text="Комментарий:").pack(pady=5)
        self.comment_text = tk.Text(self, height=4)
        self.comment_text.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # Кнопка сохранения
        tk.Button(self, text="Сохранить", bg="green", fg="white", command=self.save_entry).pack(pady=20)

    def load_entry_data(self):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, grade, comment
            FROM grades
            WHERE id=?
        """, (self.entry_id,))
        entry = cursor.fetchone()
        conn.close()
        if entry:
            self.date_var.set(entry[0])
            self.grade_var.set(str(entry[1]))
            self.comment_text.insert(tk.END, entry[2])

    def save_entry(self):
        date = self.date_var.get().strip()
        grade = self.grade_var.get().strip()
        comment = self.comment_text.get("1.0", tk.END).strip()

        if not all([date, grade]):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните обязательные поля.")
            return

        # Валидация даты
        try:
            datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты.")
            return

        # Валидация оценки
        if not grade.isdigit() or not (1 <= int(grade) <= 10):
            messagebox.showerror("Ошибка", "Оценка должна быть числом от 1 до 10.")
            return

        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()

        # Получение ID предмета
        cursor.execute("""
            SELECT id FROM subjects WHERE name=?
        """, (self.subject_name,))
        subject = cursor.fetchone()
        if not subject:
            messagebox.showerror("Ошибка", "Предмет не найден.")
            conn.close()
            return
        subject_id = subject[0]

        if self.entry_id:
            # Редактирование записи
            cursor.execute("""
                UPDATE grades
                SET date=?, grade=?, comment=?
                WHERE id=?
            """, (date, int(grade), comment, self.entry_id))
        else:
            # Добавление новой записи
            # Предположим, что мы редактируем первого ученика
            cursor.execute("""
                SELECT id FROM students LIMIT 1
            """)
            student = cursor.fetchone()
            if not student:
                messagebox.showerror("Ошибка", "В базе данных нет учеников.")
                conn.close()
                return
            student_id = student[0]

            cursor.execute("""
                INSERT INTO grades (student_id, subject_id, date, grade, comment)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, subject_id, date, int(grade), comment))
        conn.commit()
        conn.close()

        # Обновление данных в журнале
        self.refresh_callback()
        messagebox.showinfo("Успех", "Запись успешно сохранена.")
        self.destroy()

# --- Профиль родителя ---
class ParentProfileWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Профиль родителя")
        self.geometry("900x700")
        self.resizable(False, False)
        self.create_widgets()
        self.load_parent_data()

    def create_widgets(self):
        # Шапка профиля
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        # Аватарка родителя
        self.avatar_size = (150, 150)
        self.avatar_path = "default_avatar_parent.png"  # Путь к дефолтной аватарке
        self.load_avatar(self.avatar_path)
        self.avatar_label = tk.Label(header_frame, image=self.avatar_image, bd=2, relief=tk.RIDGE)
        self.avatar_label.pack()

        # ФИО
        self.full_name_var = tk.StringVar()
        tk.Label(header_frame, textvariable=self.full_name_var, font=("Arial", 18, "bold")).pack(pady=5)

        # Личная информация
        personal_info_frame = tk.LabelFrame(self, text="Личная информация", padx=10, pady=10)
        personal_info_frame.pack(pady=20, padx=20, fill=tk.X)

        # Контактный телефон
        tk.Label(personal_info_frame, text="Контактный телефон:").grid(row=0, column=0, sticky='e', pady=5)
        self.contact_phone_var = tk.StringVar()
        tk.Label(personal_info_frame, textvariable=self.contact_phone_var).grid(row=0, column=1, sticky='w', pady=5)

        # Адрес
        tk.Label(personal_info_frame, text="Адрес:").grid(row=1, column=0, sticky='e', pady=5)
        self.address_var = tk.StringVar()
        tk.Label(personal_info_frame, textvariable=self.address_var).grid(row=1, column=1, sticky='w', pady=5)

        # Кнопка редактирования
        self.edit_button = tk.Button(personal_info_frame, text="Редактировать", bg="orange", width=15, command=self.edit_personal_info)
        self.edit_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Список детей
        children_frame = tk.LabelFrame(self, text="Список детей", padx=10, pady=10)
        children_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        columns = ("ФИО ребенка", "Класс", "Действие")
        self.children_tree = ttk.Treeview(children_frame, columns=columns, show='headings')
        for col in columns:
            self.children_tree.heading(col, text=col)
            self.children_tree.column(col, width=200)
        self.children_tree.pack(fill=tk.BOTH, expand=True)

        # Добавление кнопки "Посмотреть успеваемость" в таблицу
        self.children_tree.bind("<Double-1>", self.on_child_double_click)

        # Обратная связь
        feedback_frame = tk.LabelFrame(self, text="Обратная связь", padx=10, pady=10)
        feedback_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(feedback_frame, text="Сообщение учителю:").pack(pady=5)
        self.message_text = tk.Text(feedback_frame, height=5)
        self.message_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        tk.Button(feedback_frame, text="Отправить сообщение", bg="green", fg="white", command=self.send_message).pack(pady=5)

        # Кнопка "Назад в главное меню"
        self.back_button = tk.Button(self, text="Назад в главное меню", bg="gray", fg="white", width=20, command=self.destroy)
        self.back_button.pack(pady=10)

    def load_avatar(self, path):
        try:
            image = Image.open(path).resize(self.avatar_size, Image.ANTIALIAS)
            # Создание круглой маски
            mask = Image.new('L', self.avatar_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + self.avatar_size, fill=255)
            image.putalpha(mask)
            self.avatar_image = ImageTk.PhotoImage(image)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить аватарку: {e}")
            # Создание дефолтной аватарки
            image = Image.new('RGB', self.avatar_size, color='gray')
            mask = Image.new('L', self.avatar_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + self.avatar_size, fill=255)
            image.putalpha(mask)
            self.avatar_image = ImageTk.PhotoImage(image)

    def load_parent_data(self):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        # Предположим, что мы загружаем первого родителя из базы
        cursor.execute("""
            SELECT full_name, contact_phone, address
            FROM parents
            LIMIT 1
        """)
        parent = cursor.fetchone()
        if parent:
            self.full_name_var.set(parent[0])
            self.contact_phone_var.set(parent[1])
            self.address_var.set(parent[2])
        else:
            messagebox.showinfo("Информация", "В базе данных нет родителей.")
        conn.close()

        # Загрузка списка детей
        self.load_children()

    def load_children(self):
        for row in self.children_tree.get_children():
            self.children_tree.delete(row)
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        # Предположим, что мы загружаем детей родителя с id=1
        cursor.execute("""
            SELECT full_name, class, id FROM students
            WHERE parent_id=?
        """, (1,))
        children = cursor.fetchall()
        for child in children:
            self.children_tree.insert("", tk.END, values=(child[0], child[1], "Посмотреть успеваемость"), tags=(child[2],))
        conn.close()

    def edit_personal_info(self):
        EditParentInfoWindow(self)

    def on_child_double_click(self, event):
        selected_item = self.children_tree.focus()
        if not selected_item:
            return
        child_id = self.children_tree.item(selected_item, 'tags')[0]
        child_name = self.children_tree.item(selected_item)['values'][0]
        PerformanceAnalysisWindow(self, child_id, child_name)

    def send_message(self):
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Ошибка", "Пожалуйста, введите сообщение.")
            return
        # Здесь можно добавить функциональность для отправки сообщения учителю
        # Например, сохранять сообщение в базу данных или отправлять по email
        messagebox.showinfo("Успех", "Сообщение отправлено учителю.")
        self.message_text.delete("1.0", tk.END)

# --- Форма Редактирования Личной Информации Родителя ---
class EditParentInfoWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Редактировать личную информацию родителя")
        self.geometry("400x300")
        self.parent = parent
        self.create_widgets()
        self.load_current_data()

    def create_widgets(self):
        # ФИО
        tk.Label(self, text="ФИО:").pack(pady=5)
        self.full_name_var = tk.StringVar()
        self.full_name_entry = tk.Entry(self, textvariable=self.full_name_var)
        self.full_name_entry.pack(fill=tk.X, padx=20)

        # Контактный телефон
        tk.Label(self, text="Контактный телефон:").pack(pady=5)
        self.contact_phone_var = tk.StringVar()
        self.contact_phone_entry = tk.Entry(self, textvariable=self.contact_phone_var)
        self.contact_phone_entry.pack(fill=tk.X, padx=20)

        # Адрес
        tk.Label(self, text="Адрес:").pack(pady=5)
        self.address_var = tk.StringVar()
        self.address_entry = tk.Entry(self, textvariable=self.address_var)
        self.address_entry.pack(fill=tk.X, padx=20)

        # Кнопка сохранения
        tk.Button(self, text="Сохранить", bg="green", fg="white", command=self.save_changes).pack(pady=20)

    def load_current_data(self):
        self.full_name_var.set(self.parent.full_name_var.get())
        self.contact_phone_var.set(self.parent.contact_phone_var.get())
        self.address_var.set(self.parent.address_var.get())

    def save_changes(self):
        full_name = self.full_name_var.get().strip()
        contact_phone = self.contact_phone_var.get().strip()
        address = self.address_var.get().strip()

        if not all([full_name, contact_phone, address]):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        # Предположим, что мы редактируем первого родителя
        cursor.execute("""
            UPDATE parents
            SET full_name=?, contact_phone=?, address=?
            WHERE id=?
        """, (full_name, contact_phone, address, 1))
        conn.commit()
        conn.close()

        # Обновление данных в основном окне
        self.parent.full_name_var.set(full_name)
        self.parent.contact_phone_var.set(contact_phone)
        self.parent.address_var.set(address)
        messagebox.showinfo("Успех", "Данные успешно обновлены.")
        self.destroy()

# --- Анализ академической успеваемости ---
class PerformanceAnalysisWindow(tk.Toplevel):
    def __init__(self, master, student_id=None, student_name=None):
        super().__init__(master)
        self.title("Анализ академической успеваемости")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.student_id = student_id
        self.student_name = student_name
        self.create_widgets()
        self.load_performance_data()

    def create_widgets(self):
        # Шапка анализа
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        self.analysis_title_var = tk.StringVar()
        tk.Label(header_frame, textvariable=self.analysis_title_var, font=("Arial", 16, "bold")).pack()

        # Кнопка "Назад в профиль"
        self.back_button = tk.Button(header_frame, text="Назад в профиль", bg="gray", fg="white", command=self.destroy)
        self.back_button.pack(pady=5)

        # Графики
        graphs_frame = tk.Frame(self)
        graphs_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Линейный график среднего балла
        self.fig1, self.ax1 = plt.subplots(figsize=(5,4))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=graphs_frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Гистограмма распределения оценок
        self.fig2, self.ax2 = plt.subplots(figsize=(5,4))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=graphs_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Динамика успеваемости (таблица)
        table_frame = tk.Frame(self)
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        columns = ("Дата", "Предмет", "Оценка")
        self.performance_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.performance_tree.heading(col, text=col)
            self.performance_tree.column(col, width=200)
        self.performance_tree.pack(fill=tk.BOTH, expand=True)

        # Выводы
        conclusions_frame = tk.LabelFrame(self, text="Выводы", padx=10, pady=10)
        conclusions_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.conclusions_text = tk.Text(conclusions_frame, height=4, wrap=tk.WORD)
        self.conclusions_text.pack(fill=tk.BOTH, expand=True)

    def load_performance_data(self):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()

        if self.student_id:
            cursor.execute("""
                SELECT full_name FROM students WHERE id=?
            """, (self.student_id,))
            student = cursor.fetchone()
            if student:
                student_name = student[0]
        else:
            # Предположим, что мы загружаем первого ученика из базы
            cursor.execute("""
                SELECT full_name, id FROM students LIMIT 1
            """)
            student = cursor.fetchone()
            if student:
                student_name = student[0]
                self.student_id = student[1]
            else:
                messagebox.showinfo("Информация", "В базе данных нет учеников.")
                conn.close()
                return

        self.analysis_title_var.set(f"Анализ академической успеваемости: {student_name}")

        # Получение оценок
        cursor.execute("""
            SELECT subjects.name, grades.date, grades.grade
            FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE grades.student_id=?
            ORDER BY grades.date
        """, (self.student_id,))
        grades = cursor.fetchall()
        conn.close()

        if not grades:
            messagebox.showinfo("Информация", "У этого ученика нет оценок.")
            return

        # Обновление таблицы
        for row in self.performance_tree.get_children():
            self.performance_tree.delete(row)
        for subj, date, grade in grades:
            self.performance_tree.insert("", tk.END, values=(date, subj, grade))

        # Подготовка данных для графиков
        dates = []
        avg_grades = []
        subjects = {}
        for subj, date, grade in grades:
            try:
                date_obj = datetime.strptime(date, "%d.%m.%Y")
            except ValueError:
                continue  # Пропуск неверных дат
            dates.append(date_obj)
            if date_obj.date() not in subjects:
                subjects[date_obj.date()] = []
            subjects[date_obj.date()].append(grade)
        sorted_dates = sorted(subjects.keys())
        cumulative_grades = []
        for date in sorted_dates:
            avg = sum(subjects[date])/len(subjects[date])
            cumulative_grades.append(avg)

        # Линейный график среднего балла
        self.ax1.clear()
        self.ax1.plot(sorted_dates, cumulative_grades, marker='o', linestyle='-', color='b')
        self.ax1.set_title("Средний балл по датам")
        self.ax1.set_xlabel("Дата")
        self.ax1.set_ylabel("Средний балл")
        self.ax1.grid(True)
        self.fig1.autofmt_xdate()
        self.canvas1.draw()

        # Гистограмма распределения оценок
        all_grades = [grade for _, _, grade in grades]
        self.ax2.clear()
        self.ax2.hist(all_grades, bins=range(1, 12), color='g', edgecolor='black')
        self.ax2.set_title("Распределение оценок")
        self.ax2.set_xlabel("Оценка")
        self.ax2.set_ylabel("Количество")
        self.ax2.set_xticks(range(1, 11))
        self.canvas2.draw()

        # Выводы
        average_grade = sum(all_grades)/len(all_grades)
        if average_grade >= 9:
            conclusion = f"Средний балл: {average_grade:.2f} - Отличная успеваемость."
        elif average_grade >= 7.5:
            conclusion = f"Средний балл: {average_grade:.2f} - Хорошая успеваемость."
        elif average_grade >= 6:
            conclusion = f"Средний балл: {average_grade:.2f} - Удовлетворительная успеваемость."
        else:
            conclusion = f"Средний балл: {average_grade:.2f} - Требуется улучшение успеваемости."
        self.conclusions_text.delete("1.0", tk.END)
        self.conclusions_text.insert(tk.END, conclusion)

# --- Календарь ---
class CalendarAppWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Календарь")
        self.geometry("1200x800")
        self.resizable(True, True)

        # Параметры внешнего вида
        self.cell_width = 160  # Ширина ячейки
        self.cell_height = 100  # Высота ячейки
        self.top_margin = 50   # Верхний отступ для шапки дней недели
        self.left_margin = 20  # Левый отступ

        self.current_view = "month"
        self.current_date = datetime.now()

        # Верхняя панель (Сегодня + переключатели видов)
        self.topbar = tk.Frame(self)
        self.topbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_today = tk.Button(self.topbar, text="Сегодня", command=self.go_today)
        self.btn_today.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_month = tk.Button(self.topbar, text="Месяц", command=lambda: self.switch_view("month"))
        self.btn_month.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn_week = tk.Button(self.topbar, text="Неделя", command=lambda: self.switch_view("week"))
        self.btn_week.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn_day = tk.Button(self.topbar, text="День", command=lambda: self.switch_view("day"))
        self.btn_day.pack(side=tk.RIGHT, padx=5, pady=5)

        # Заголовок с датой и навигационными стрелками
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.nav_frame = tk.Frame(self.header_frame)
        self.nav_frame.pack(side=tk.TOP, pady=10)

        self.btn_prev = tk.Button(self.nav_frame, text="←", command=self.prev_period)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.header_label = tk.Label(self.nav_frame, font=("Arial", 16, "bold"))
        self.header_label.pack(side=tk.LEFT, padx=10)

        self.btn_next = tk.Button(self.nav_frame, text="→", command=self.next_period)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        # Область для календаря
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Добавление полосы прокрутки
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # Связь события прокрутки с канвасом
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Для Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Для Linux

        self.update_calendar()

    def _on_mousewheel(self, event):
        # Для Windows и MacOS
        if event.delta:
            self.canvas.yview_scroll(int(-event.delta/120), "units")
        # Для Linux
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def update_calendar(self):
        self.canvas.delete("all")
        self.update_header()
        if self.current_view == "day":
            self.draw_day_view()
        elif self.current_view == "week":
            self.draw_week_view()
        elif self.current_view == "month":
            self.draw_month_view()

    def update_header(self):
        if self.current_view == "day":
            self.header_label.config(text=self.current_date.strftime("%d %B %Y г."))
        elif self.current_view == "week":
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            self.header_label.config(text=f"Неделя: {start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}")
        elif self.current_view == "month":
            self.header_label.config(text=self.current_date.strftime("%B %Y г."))

    def prev_period(self):
        if self.current_view == "day":
            self.current_date -= timedelta(days=1)
        elif self.current_view == "week":
            self.current_date -= timedelta(weeks=1)
        elif self.current_view == "month":
            year = self.current_date.year
            month = self.current_date.month - 1
            if month < 1:
                month = 12
                year -= 1
            try:
                self.current_date = self.current_date.replace(year=year, month=month, day=1)
            except ValueError:
                self.current_date = self.current_date.replace(year=year, month=month, day=28)
        self.update_calendar()

    def next_period(self):
        if self.current_view == "day":
            self.current_date += timedelta(days=1)
        elif self.current_view == "week":
            self.current_date += timedelta(weeks=1)
        elif self.current_view == "month":
            year = self.current_date.year
            month = self.current_date.month + 1
            if month > 12:
                month = 1
                year += 1
            try:
                self.current_date = self.current_date.replace(year=year, month=month, day=1)
            except ValueError:
                self.current_date = self.current_date.replace(year=year, month=month, day=28)
        self.update_calendar()

    def go_today(self):
        self.current_date = datetime.now()
        self.update_calendar()

    def switch_view(self, view):
        self.current_view = view
        self.update_calendar()

    def draw_day_view(self):
        # Отображение одного дня
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day
        day_of_week = self.current_date.weekday()

        # Шапка дней недели
        for i, dow in enumerate(days_of_week):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin
            self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height, fill="#f0f0f0", outline="black")
            self.canvas.create_text(
                x + self.cell_width / 2, 
                y + self.cell_height / 2, 
                text=dow, 
                font=("Arial", 12, "bold")
            )

        # Ячейка для выбранного дня
        x = self.left_margin + day_of_week * self.cell_width
        y = self.top_margin + self.cell_height

        # Определяем цвет ячейки
        today = datetime.now().date()
        current_date = self.current_date.date()
        fill_color = "#ffffcc" if current_date == today else "white"

        self.canvas.create_rectangle(
            x, y, x + self.cell_width, y + self.cell_height, 
            fill=fill_color, outline="black"
        )

        # Выводим номер дня
        self.canvas.create_text(
            x + 10, y + 10, 
            text=str(day), 
            anchor="nw", 
            font=("Arial", 10)
        )

        # Добавляем события
        self.add_events_to_cell(x, y, current_date)

    def draw_week_view(self):
        # Отображение недели
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        year = self.current_date.year
        month = self.current_date.month
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        dates = [start_of_week + timedelta(days=i) for i in range(7)]

        # Шапка дней недели
        for i, dow in enumerate(days_of_week):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin
            self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height, fill="#f0f0f0", outline="black")
            self.canvas.create_text(
                x + self.cell_width / 2, 
                y + self.cell_height / 2, 
                text=dow, 
                font=("Arial", 12, "bold")
            )

        # Отображение каждого дня недели
        today = datetime.now().date()
        for i, date in enumerate(dates):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin + self.cell_height

            fill_color = "#ffffcc" if date.date() == today else "white"

            self.canvas.create_rectangle(
                x, y, x + self.cell_width, y + self.cell_height, 
                fill=fill_color, outline="black"
            )

            # Выводим номер дня
            self.canvas.create_text(
                x + 10, y + 10, 
                text=str(date.day), 
                anchor="nw", 
                font=("Arial", 10)
            )

            # Добавляем события
            self.add_events_to_cell(x, y, date.date())

    def draw_month_view(self):
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        year = self.current_date.year
        month = self.current_date.month
        first_day_weekday, num_days = calendar.monthrange(year, month)

        # Создаем список дней с учетом отступов
        days = [""] * first_day_weekday + [str(day) for day in range(1, num_days + 1)]

        # Дополняем список до полного количества недель (6 недель)
        while len(days) % 7 != 0:
            days.append("")

        weeks = [days[i:i + 7] for i in range(0, len(days), 7)]

        # Шапка дней недели
        for i, day in enumerate(days_of_week):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin
            # Рисуем прямоугольник с светлым фоном
            self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height, fill="#f0f0f0", outline="black")
            # Рисуем текст по центру ячейки
            self.canvas.create_text(
                x + self.cell_width / 2, 
                y + self.cell_height / 2, 
                text=day, 
                font=("Arial", 12, "bold")
            )

        # Текущий день для выделения
        today = datetime.now().date()

        # Получение событий из базы данных для текущего месяца
        month_events = self.fetch_events_for_month(year, month)

        # Рисуем дни месяца
        for week_num, week in enumerate(weeks):
            for day_num, day in enumerate(week):
                x = self.left_margin + day_num * self.cell_width
                y = self.top_margin + self.cell_height + week_num * self.cell_height

                if day:
                    day_int = int(day)
                    try:
                        current_day = datetime(year, month, day_int)
                        current_date = current_day.date()
                    except ValueError:
                        continue  # Пропуск неверных дат

                    # Определяем цвет ячейки
                    fill_color = "#ffffcc" if current_date == today else "white"

                    # Рисуем ячейку
                    self.canvas.create_rectangle(
                        x, y, x + self.cell_width, y + self.cell_height, 
                        fill=fill_color, outline="black"
                    )

                    # Выводим номер дня с отступом
                    self.canvas.create_text(
                        x + 10, y + 10, 
                        text=str(day_int), 
                        anchor="nw", 
                        font=("Arial", 10)
                    )

                    # Добавляем события в ячейку
                    day_events = [event for event in month_events if event['start_time'].date() == current_date]
                    if day_events:
                        event_y_offset = y + 30  # Начальная позиция для событий
                        for event in day_events:
                            if event_y_offset + 15 > y + self.cell_height - 5:
                                # Если места нет, показываем ссылку "ещё..."
                                self.canvas.create_text(
                                    x + 10, y + self.cell_height - 15, 
                                    text="ещё...", 
                                    anchor="nw", 
                                    font=("Arial", 9, "underline"), 
                                    fill="blue"
                                )
                                break
                            # Создаем текст события
                            text_id = self.canvas.create_text(
                                x + 10, event_y_offset, 
                                text=event['title'], 
                                anchor="nw", 
                                font=("Arial", 9), 
                                fill="blue"
                            )
                            # Привязываем к тексту событие для обработки кликов
                            self.canvas.tag_bind(text_id, "<Button-1>", lambda e, ev=event: self.open_event_detail(ev))
                            event_y_offset += 15  # Отступ между событиями
                else:
                    # Пустые ячейки для других месяцев
                    self.canvas.create_rectangle(
                        x, y, x + self.cell_width, y + self.cell_height, 
                        fill="#e0e0e0", outline="black"
                    )

    def fetch_events_for_month(self, year, month):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        # Получение событий, относящихся к текущему месяцу
        cursor.execute("""
            SELECT id, title, description, start_time, end_time, status, comments, reference_id, event_type
            FROM events
            WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ?
            ORDER BY start_time
        """, (str(year), f"{month:02d}"))
        raw_events = cursor.fetchall()
        conn.close()
        # Преобразование в удобный формат
        formatted_events = []
        for event in raw_events:
            try:
                formatted_events.append({
                    'id': event[0],
                    'title': event[1],
                    'description': event[2],
                    'start_time': datetime.strptime(event[3], "%Y-%m-%d %H:%M"),
                    'end_time': datetime.strptime(event[4], "%Y-%m-%d %H:%M"),
                    'status': event[5],
                    'comments': event[6],
                    'reference_id': event[7],
                    'event_type': event[8]
                })
            except ValueError:
                continue  # Пропуск событий с неверными датами
        return formatted_events

    def add_events_to_cell(self, x, y, current_date):
        # Получение событий из базы данных
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, description, start_time, end_time, status, comments, id, event_type
            FROM events
            WHERE DATE(start_time) = ?
        """, (current_date.strftime("%Y-%m-%d"),))
        events = cursor.fetchall()
        conn.close()

        if not events:
            return

        event_y_offset = y + 30
        for event in events:
            if event_y_offset + 15 > y + self.cell_height - 5:
                # Если места нет, показываем ссылку "ещё..."
                self.canvas.create_text(
                    x + 10, y + self.cell_height - 15, 
                    text="ещё...", 
                    anchor="nw", 
                    font=("Arial", 9, "underline"), 
                    fill="blue"
                )
                break
            # Создаем текст события
            text_id = self.canvas.create_text(
                x + 10, event_y_offset, 
                text=event[0], 
                anchor="nw", 
                font=("Arial", 9), 
                fill="blue"
            )
            # Привязываем к тексту событие для обработки кликов
            self.canvas.tag_bind(text_id, "<Button-1>", lambda e, ev=event: self.open_event_detail(ev))
            event_y_offset += 15  # Отступ между событиями

    def open_event_detail(self, event):
        EventDetailWindow(self, event)

# --- Детали события ---
class EventDetailWindow(tk.Toplevel):
    def __init__(self, master, event):
        super().__init__(master)
        self.title("Детали события")
        self.geometry("500x400")
        self.event = event
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text=f"Название: {self.event['title']}", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self, text=f"Описание: {self.event['description']}").pack(pady=5)
        tk.Label(self, text=f"Начало: {self.event['start_time'].strftime('%d.%m.%Y %H:%M')}").pack(pady=5)
        tk.Label(self, text=f"Окончание: {self.event['end_time'].strftime('%d.%m.%Y %H:%M')}").pack(pady=5)
        tk.Label(self, text=f"Статус: {self.event['status']}").pack(pady=5)
        tk.Label(self, text=f"Комментарии: {self.event['comments']}").pack(pady=5)

        # Кнопки для редактирования и удаления события
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Редактировать", bg="orange", command=self.edit_event).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Удалить", bg="red", fg="white", command=self.delete_event).pack(side=tk.LEFT, padx=5)

    def edit_event(self):
        EditEventWindow(self, self.event)
        self.destroy()

    def delete_event(self):
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это событие?")
        if confirm:
            conn = sqlite3.connect('class_journal.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id=?", (self.event['id'],))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Событие удалено успешно.")
            self.master.update_calendar()
            self.destroy()

# --- Форма Редактирования События ---
class EditEventWindow(tk.Toplevel):
    def __init__(self, parent, event):
        super().__init__(parent)
        self.title("Редактировать событие")
        self.geometry("400x500")
        self.parent = parent
        self.event = event
        self.create_widgets()

    def create_widgets(self):
        # Название
        tk.Label(self, text="Название:").pack(pady=5)
        self.title_var = tk.StringVar(value=self.event['title'])
        self.title_entry = tk.Entry(self, textvariable=self.title_var)
        self.title_entry.pack(fill=tk.X, padx=20)

        # Описание
        tk.Label(self, text="Описание:").pack(pady=5)
        self.description_text = tk.Text(self, height=5)
        self.description_text.insert(tk.END, self.event['description'])
        self.description_text.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # Начало
        tk.Label(self, text="Начало (ДД.ММ.ГГГГ ЧЧ:ММ):").pack(pady=5)
        self.start_time_var = tk.StringVar(value=self.event['start_time'].strftime("%d.%m.%Y %H:%M"))
        self.start_time_entry = tk.Entry(self, textvariable=self.start_time_var)
        self.start_time_entry.pack(fill=tk.X, padx=20)

        # Окончание
        tk.Label(self, text="Окончание (ДД.ММ.ГГГГ ЧЧ:ММ):").pack(pady=5)
        self.end_time_var = tk.StringVar(value=self.event['end_time'].strftime("%d.%m.%Y %H:%M"))
        self.end_time_entry = tk.Entry(self, textvariable=self.end_time_var)
        self.end_time_entry.pack(fill=tk.X, padx=20)

        # Статус
        tk.Label(self, text="Статус:").pack(pady=5)
        self.status_var = tk.StringVar(value=self.event['status'])
        self.status_combo = ttk.Combobox(self, textvariable=self.status_var, values=["planned", "completed", "cancelled"], state="readonly")
        self.status_combo.pack(fill=tk.X, padx=20)

        # Комментарии
        tk.Label(self, text="Комментарии:").pack(pady=5)
        self.comments_text = tk.Text(self, height=3)
        self.comments_text.insert(tk.END, self.event['comments'])
        self.comments_text.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # Кнопка сохранения
        tk.Button(self, text="Сохранить", bg="green", fg="white", command=self.save_changes).pack(pady=10)

    def save_changes(self):
        title = self.title_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        status = self.status_var.get().strip()
        comments = self.comments_text.get("1.0", tk.END).strip()

        if not all([title, start_time, end_time, status]):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        # Валидация дат и времени
        try:
            start_dt = datetime.strptime(start_time, "%d.%m.%Y %H:%M")
            end_dt = datetime.strptime(end_time, "%d.%m.%Y %H:%M")
            if end_dt <= start_dt:
                messagebox.showerror("Ошибка", "Время окончания должно быть позже времени начала.")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты и времени.")
            return

        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE events
            SET title=?, description=?, start_time=?, end_time=?, status=?, comments=?
            WHERE id=?
        """, (title, description, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"), status, comments, self.event['id']))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Событие успешно обновлено.")
        self.parent.update_calendar()
        self.destroy()

# --- Раздел «Место обучения» ---
class SchoolInfoWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Информация об учебном заведении")
        self.geometry("900x700")
        self.resizable(False, False)
        self.create_widgets()
        self.load_school_data()

    def create_widgets(self):
        # Шапка раздела
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        self.school_name_var = tk.StringVar()
        tk.Label(header_frame, textvariable=self.school_name_var, font=("Arial", 24, "bold")).pack()

        # Логотип или изображение
        self.logo_size = (200, 150)
        self.logo_path = "school_logo.png"  # Путь к логотипу
        self.logo_label = tk.Label(header_frame, text="Нет логотипа", width=30, height=10, bg="#f0f0f0")
        self.logo_label.pack(pady=10)
        self.load_logo(self.logo_path)

        # Основной блок информации
        info_frame = tk.Frame(self)
        info_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Название
        tk.Label(info_frame, text="Название:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky='e', pady=5)
        self.name_var = tk.StringVar()
        tk.Label(info_frame, textvariable=self.name_var).grid(row=0, column=1, sticky='w', pady=5)

        # Адрес
        tk.Label(info_frame, text="Адрес:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky='e', pady=5)
        self.address_var = tk.StringVar()
        tk.Label(info_frame, textvariable=self.address_var).grid(row=1, column=1, sticky='w', pady=5)

        # Контактный телефон и email
        tk.Label(info_frame, text="Контактный телефон:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky='e', pady=5)
        self.contact_phone_var = tk.StringVar()
        tk.Label(info_frame, textvariable=self.contact_phone_var).grid(row=2, column=1, sticky='w', pady=5)

        tk.Label(info_frame, text="Email:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky='e', pady=5)
        self.contact_email_var = tk.StringVar()
        tk.Label(info_frame, textvariable=self.contact_email_var).grid(row=3, column=1, sticky='w', pady=5)

        # Руководитель
        tk.Label(info_frame, text="Руководитель:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky='e', pady=5)
        self.director_var = tk.StringVar()
        tk.Label(info_frame, textvariable=self.director_var).grid(row=4, column=1, sticky='w', pady=5)

        # Список классов
        classes_frame = tk.LabelFrame(info_frame, text="Список классов", padx=10, pady=10)
        classes_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')

        columns = ("Класс", "Куратор", "Кол-во учеников")
        self.classes_tree = ttk.Treeview(classes_frame, columns=columns, show='headings')
        for col in columns:
            self.classes_tree.heading(col, text=col)
            self.classes_tree.column(col, width=150)
        self.classes_tree.pack(fill=tk.BOTH, expand=True)

        # Мероприятия
        events_frame = tk.LabelFrame(self, text="Мероприятия", padx=10, pady=10)
        events_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.events_canvas = tk.Canvas(events_frame)
        self.events_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(events_frame, orient="vertical", command=self.events_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.events_canvas.configure(yscrollcommand=scrollbar.set)
        self.events_canvas.bind('<Configure>', lambda e: self.events_canvas.configure(scrollregion=self.events_canvas.bbox("all")))

        self.events_inner_frame = tk.Frame(self.events_canvas)
        self.events_canvas.create_window((0,0), window=self.events_inner_frame, anchor='nw')

    def load_logo(self, path):
        if os.path.exists(path):
            try:
                image = Image.open(path).resize(self.logo_size, Image.ANTIALIAS)
                self.logo_image = ImageTk.PhotoImage(image)
                self.logo_label.config(image=self.logo_image, text="")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить логотип: {e}")
        else:
            self.logo_label.config(text="Нет логотипа")

    def load_school_data(self):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, address, contact_phone, contact_email, director
            FROM school
            LIMIT 1
        """)
        school = cursor.fetchone()
        if school:
            self.name_var.set(school[0])
            self.address_var.set(school[1])
            self.contact_phone_var.set(school[2])
            self.contact_email_var.set(school[3])
            self.director_var.set(school[4])
        conn.close()

        # Загрузка списка классов
        self.load_classes()

        # Загрузка мероприятий
        self.load_events()

    def load_classes(self):
        for row in self.classes_tree.get_children():
            self.classes_tree.delete(row)
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT class, teacher, COUNT(students.id)
            FROM students
            GROUP BY class
        """)
        classes = cursor.fetchall()
        for cls in classes:
            self.classes_tree.insert("", tk.END, values=cls)
        conn.close()

    def load_events(self):
        # Очистка предыдущих мероприятий
        for widget in self.events_inner_frame.winfo_children():
            widget.destroy()
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, date, location
            FROM events
            WHERE event_type='school_event'
            ORDER BY date
        """)
        events = cursor.fetchall()
        conn.close()
        for event in events:
            event_card = tk.Frame(self.events_inner_frame, bd=1, relief=tk.RIDGE, padx=10, pady=10)
            event_card.pack(pady=5, fill=tk.X, expand=True)

            tk.Label(event_card, text=event[0], font=("Arial", 14, "bold")).pack(anchor='w')
            tk.Label(event_card, text=f"Дата: {event[1]}", font=("Arial", 12)).pack(anchor='w')
            tk.Label(event_card, text=f"Место проведения: {event[2]}", font=("Arial", 12)).pack(anchor='w')

# --- Анализ академической успеваемости ---
class PerformanceAnalysisWindow(tk.Toplevel):
    def __init__(self, master, student_id=None, student_name=None):
        super().__init__(master)
        self.title("Анализ академической успеваемости")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.student_id = student_id
        self.student_name = student_name
        self.create_widgets()
        self.load_performance_data()

    def create_widgets(self):
        # Шапка анализа
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        self.analysis_title_var = tk.StringVar()
        tk.Label(header_frame, textvariable=self.analysis_title_var, font=("Arial", 16, "bold")).pack()

        # Кнопка "Назад в профиль"
        self.back_button = tk.Button(header_frame, text="Назад в профиль", bg="gray", fg="white", command=self.destroy)
        self.back_button.pack(pady=5)

        # Графики
        graphs_frame = tk.Frame(self)
        graphs_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Линейный график среднего балла
        self.fig1, self.ax1 = plt.subplots(figsize=(5,4))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=graphs_frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Гистограмма распределения оценок
        self.fig2, self.ax2 = plt.subplots(figsize=(5,4))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=graphs_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Динамика успеваемости (таблица)
        table_frame = tk.Frame(self)
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        columns = ("Дата", "Предмет", "Оценка")
        self.performance_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.performance_tree.heading(col, text=col)
            self.performance_tree.column(col, width=200)
        self.performance_tree.pack(fill=tk.BOTH, expand=True)

        # Выводы
        conclusions_frame = tk.LabelFrame(self, text="Выводы", padx=10, pady=10)
        conclusions_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.conclusions_text = tk.Text(conclusions_frame, height=4, wrap=tk.WORD)
        self.conclusions_text.pack(fill=tk.BOTH, expand=True)

    def load_performance_data(self):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()

        if self.student_id:
            cursor.execute("""
                SELECT full_name FROM students WHERE id=?
            """, (self.student_id,))
            student = cursor.fetchone()
            if student:
                student_name = student[0]
        else:
            # Предположим, что мы загружаем первого ученика из базы
            cursor.execute("""
                SELECT full_name, id FROM students LIMIT 1
            """)
            student = cursor.fetchone()
            if student:
                student_name = student[0]
                self.student_id = student[1]
            else:
                messagebox.showinfo("Информация", "В базе данных нет учеников.")
                conn.close()
                return

        self.analysis_title_var.set(f"Анализ академической успеваемости: {student_name}")

        # Получение оценок
        cursor.execute("""
            SELECT subjects.name, grades.date, grades.grade
            FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE grades.student_id=?
            ORDER BY grades.date
        """, (self.student_id,))
        grades = cursor.fetchall()
        conn.close()

        if not grades:
            messagebox.showinfo("Информация", "У этого ученика нет оценок.")
            return

        # Обновление таблицы
        for row in self.performance_tree.get_children():
            self.performance_tree.delete(row)
        for subj, date, grade in grades:
            self.performance_tree.insert("", tk.END, values=(date, subj, grade))

        # Подготовка данных для графиков
        dates = []
        avg_grades = []
        subjects = {}
        for subj, date, grade in grades:
            try:
                date_obj = datetime.strptime(date, "%d.%m.%Y")
            except ValueError:
                continue  # Пропуск неверных дат
            dates.append(date_obj)
            if date_obj.date() not in subjects:
                subjects[date_obj.date()] = []
            subjects[date_obj.date()].append(grade)
        sorted_dates = sorted(subjects.keys())
        cumulative_grades = []
        for date in sorted_dates:
            avg = sum(subjects[date])/len(subjects[date])
            cumulative_grades.append(avg)

        # Линейный график среднего балла
        self.ax1.clear()
        self.ax1.plot(sorted_dates, cumulative_grades, marker='o', linestyle='-', color='b')
        self.ax1.set_title("Средний балл по датам")
        self.ax1.set_xlabel("Дата")
        self.ax1.set_ylabel("Средний балл")
        self.ax1.grid(True)
        self.fig1.autofmt_xdate()
        self.canvas1.draw()

        # Гистограмма распределения оценок
        all_grades = [grade for _, _, grade in grades]
        self.ax2.clear()
        self.ax2.hist(all_grades, bins=range(1, 12), color='g', edgecolor='black')
        self.ax2.set_title("Распределение оценок")
        self.ax2.set_xlabel("Оценка")
        self.ax2.set_ylabel("Количество")
        self.ax2.set_xticks(range(1, 11))
        self.canvas2.draw()

        # Выводы
        average_grade = sum(all_grades)/len(all_grades)
        if average_grade >= 9:
            conclusion = f"Средний балл: {average_grade:.2f} - Отличная успеваемость."
        elif average_grade >= 7.5:
            conclusion = f"Средний балл: {average_grade:.2f} - Хорошая успеваемость."
        elif average_grade >= 6:
            conclusion = f"Средний балл: {average_grade:.2f} - Удовлетворительная успеваемость."
        else:
            conclusion = f"Средний балл: {average_grade:.2f} - Требуется улучшение успеваемости."
        self.conclusions_text.delete("1.0", tk.END)
        self.conclusions_text.insert(tk.END, conclusion)

# --- Календарь ---
class CalendarAppWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Календарь")
        self.geometry("1200x800")
        self.resizable(True, True)

        # Параметры внешнего вида
        self.cell_width = 160  # Ширина ячейки
        self.cell_height = 100  # Высота ячейки
        self.top_margin = 50   # Верхний отступ для шапки дней недели
        self.left_margin = 20  # Левый отступ

        self.current_view = "month"
        self.current_date = datetime.now()

        # Верхняя панель (Сегодня + переключатели видов)
        self.topbar = tk.Frame(self)
        self.topbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_today = tk.Button(self.topbar, text="Сегодня", command=self.go_today)
        self.btn_today.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_month = tk.Button(self.topbar, text="Месяц", command=lambda: self.switch_view("month"))
        self.btn_month.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn_week = tk.Button(self.topbar, text="Неделя", command=lambda: self.switch_view("week"))
        self.btn_week.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn_day = tk.Button(self.topbar, text="День", command=lambda: self.switch_view("day"))
        self.btn_day.pack(side=tk.RIGHT, padx=5, pady=5)

        # Заголовок с датой и навигационными стрелками
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.nav_frame = tk.Frame(self.header_frame)
        self.nav_frame.pack(side=tk.TOP, pady=10)

        self.btn_prev = tk.Button(self.nav_frame, text="←", command=self.prev_period)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.header_label = tk.Label(self.nav_frame, font=("Arial", 16, "bold"))
        self.header_label.pack(side=tk.LEFT, padx=10)

        self.btn_next = tk.Button(self.nav_frame, text="→", command=self.next_period)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        # Область для календаря
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Добавление полосы прокрутки
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # Связь события прокрутки с канвасом
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Для Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Для Linux

        self.update_calendar()

    def _on_mousewheel(self, event):
        # Для Windows и MacOS
        if event.delta:
            self.canvas.yview_scroll(int(-event.delta/120), "units")
        # Для Linux
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def update_calendar(self):
        self.canvas.delete("all")
        self.update_header()
        if self.current_view == "day":
            self.draw_day_view()
        elif self.current_view == "week":
            self.draw_week_view()
        elif self.current_view == "month":
            self.draw_month_view()

    def update_header(self):
        if self.current_view == "day":
            self.header_label.config(text=self.current_date.strftime("%d %B %Y г."))
        elif self.current_view == "week":
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            self.header_label.config(text=f"Неделя: {start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}")
        elif self.current_view == "month":
            self.header_label.config(text=self.current_date.strftime("%B %Y г."))

    def prev_period(self):
        if self.current_view == "day":
            self.current_date -= timedelta(days=1)
        elif self.current_view == "week":
            self.current_date -= timedelta(weeks=1)
        elif self.current_view == "month":
            year = self.current_date.year
            month = self.current_date.month - 1
            if month < 1:
                month = 12
                year -= 1
            try:
                self.current_date = self.current_date.replace(year=year, month=month, day=1)
            except ValueError:
                self.current_date = self.current_date.replace(year=year, month=month, day=28)
        self.update_calendar()

    def next_period(self):
        if self.current_view == "day":
            self.current_date += timedelta(days=1)
        elif self.current_view == "week":
            self.current_date += timedelta(weeks=1)
        elif self.current_view == "month":
            year = self.current_date.year
            month = self.current_date.month + 1
            if month > 12:
                month = 1
                year += 1
            try:
                self.current_date = self.current_date.replace(year=year, month=month, day=1)
            except ValueError:
                self.current_date = self.current_date.replace(year=year, month=month, day=28)
        self.update_calendar()

    def go_today(self):
        self.current_date = datetime.now()
        self.update_calendar()

    def switch_view(self, view):
        self.current_view = view
        self.update_calendar()

    def draw_day_view(self):
        # Отображение одного дня
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day
        day_of_week = self.current_date.weekday()

        # Шапка дней недели
        for i, dow in enumerate(days_of_week):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin
            self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height, fill="#f0f0f0", outline="black")
            self.canvas.create_text(
                x + self.cell_width / 2, 
                y + self.cell_height / 2, 
                text=dow, 
                font=("Arial", 12, "bold")
            )

        # Ячейка для выбранного дня
        x = self.left_margin + day_of_week * self.cell_width
        y = self.top_margin + self.cell_height

        # Определяем цвет ячейки
        today = datetime.now().date()
        current_date = self.current_date.date()
        fill_color = "#ffffcc" if current_date == today else "white"

        self.canvas.create_rectangle(
            x, y, x + self.cell_width, y + self.cell_height, 
            fill=fill_color, outline="black"
        )

        # Выводим номер дня
        self.canvas.create_text(
            x + 10, y + 10, 
            text=str(day), 
            anchor="nw", 
            font=("Arial", 10)
        )

        # Добавляем события
        self.add_events_to_cell(x, y, current_date)

    def draw_week_view(self):
        # Отображение недели
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        year = self.current_date.year
        month = self.current_date.month
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        dates = [start_of_week + timedelta(days=i) for i in range(7)]

        # Шапка дней недели
        for i, dow in enumerate(days_of_week):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin
            self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height, fill="#f0f0f0", outline="black")
            self.canvas.create_text(
                x + self.cell_width / 2, 
                y + self.cell_height / 2, 
                text=dow, 
                font=("Arial", 12, "bold")
            )

        # Отображение каждого дня недели
        today = datetime.now().date()
        for i, date in enumerate(dates):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin + self.cell_height

            fill_color = "#ffffcc" if date.date() == today else "white"

            self.canvas.create_rectangle(
                x, y, x + self.cell_width, y + self.cell_height, 
                fill=fill_color, outline="black"
            )

            # Выводим номер дня
            self.canvas.create_text(
                x + 10, y + 10, 
                text=str(date.day), 
                anchor="nw", 
                font=("Arial", 10)
            )

            # Добавляем события
            self.add_events_to_cell(x, y, date.date())

    def draw_month_view(self):
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        year = self.current_date.year
        month = self.current_date.month
        first_day_weekday, num_days = calendar.monthrange(year, month)

        # Создаем список дней с учетом отступов
        days = [""] * first_day_weekday + [str(day) for day in range(1, num_days + 1)]

        # Дополняем список до полного количества недель (6 недель)
        while len(days) % 7 != 0:
            days.append("")

        weeks = [days[i:i + 7] for i in range(0, len(days), 7)]

        # Шапка дней недели
        for i, day in enumerate(days_of_week):
            x = self.left_margin + i * self.cell_width
            y = self.top_margin
            # Рисуем прямоугольник с светлым фоном
            self.canvas.create_rectangle(x, y, x + self.cell_width, y + self.cell_height, fill="#f0f0f0", outline="black")
            # Рисуем текст по центру ячейки
            self.canvas.create_text(
                x + self.cell_width / 2, 
                y + self.cell_height / 2, 
                text=day, 
                font=("Arial", 12, "bold")
            )

        # Текущий день для выделения
        today = datetime.now().date()

        # Получение событий из базы данных для текущего месяца
        month_events = self.fetch_events_for_month(year, month)

        # Рисуем дни месяца
        for week_num, week in enumerate(weeks):
            for day_num, day in enumerate(week):
                x = self.left_margin + day_num * self.cell_width
                y = self.top_margin + self.cell_height + week_num * self.cell_height

                if day:
                    day_int = int(day)
                    try:
                        current_day = datetime(year, month, day_int)
                        current_date = current_day.date()
                    except ValueError:
                        continue  # Пропуск неверных дат

                    # Определяем цвет ячейки
                    fill_color = "#ffffcc" if current_date == today else "white"

                    # Рисуем ячейку
                    self.canvas.create_rectangle(
                        x, y, x + self.cell_width, y + self.cell_height, 
                        fill=fill_color, outline="black"
                    )

                    # Выводим номер дня с отступом
                    self.canvas.create_text(
                        x + 10, y + 10, 
                        text=str(day_int), 
                        anchor="nw", 
                        font=("Arial", 10)
                    )

                    # Добавляем события в ячейку
                    day_events = [event for event in month_events if event['start_time'].date() == current_date]
                    if day_events:
                        event_y_offset = y + 30  # Начальная позиция для событий
                        for event in day_events:
                            if event_y_offset + 15 > y + self.cell_height - 5:
                                # Если места нет, показываем ссылку "ещё..."
                                self.canvas.create_text(
                                    x + 10, y + self.cell_height - 15, 
                                    text="ещё...", 
                                    anchor="nw", 
                                    font=("Arial", 9, "underline"), 
                                    fill="blue"
                                )
                                break
                            # Создаем текст события
                            text_id = self.canvas.create_text(
                                x + 10, event_y_offset, 
                                text=event['title'], 
                                anchor="nw", 
                                font=("Arial", 9), 
                                fill="blue"
                            )
                            # Привязываем к тексту событие для обработки кликов
                            self.canvas.tag_bind(text_id, "<Button-1>", lambda e, ev=event: self.open_event_detail(ev))
                            event_y_offset += 15  # Отступ между событиями
                else:
                    # Пустые ячейки для других месяцев
                    self.canvas.create_rectangle(
                        x, y, x + self.cell_width, y + self.cell_height, 
                        fill="#e0e0e0", outline="black"
                    )

    def fetch_events_for_month(self, year, month):
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        # Получение событий, относящихся к текущему месяцу
        cursor.execute("""
            SELECT id, title, description, start_time, end_time, status, comments, reference_id, event_type
            FROM events
            WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ?
            ORDER BY start_time
        """, (str(year), f"{month:02d}"))
        raw_events = cursor.fetchall()
        conn.close()
        # Преобразование в удобный формат
        formatted_events = []
        for event in raw_events:
            try:
                formatted_events.append({
                    'id': event[0],
                    'title': event[1],
                    'description': event[2],
                    'start_time': datetime.strptime(event[3], "%Y-%m-%d %H:%M"),
                    'end_time': datetime.strptime(event[4], "%Y-%m-%d %H:%M"),
                    'status': event[5],
                    'comments': event[6],
                    'reference_id': event[7],
                    'event_type': event[8]
                })
            except ValueError:
                continue  # Пропуск событий с неверными датами
        return formatted_events

    def add_events_to_cell(self, x, y, current_date):
        # Получение событий из базы данных
        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, description, start_time, end_time, status, comments, id, event_type
            FROM events
            WHERE DATE(start_time) = ?
        """, (current_date.strftime("%Y-%m-%d"),))
        events = cursor.fetchall()
        conn.close()

        if not events:
            return

        event_y_offset = y + 30
        for event in events:
            if event_y_offset + 15 > y + self.cell_height - 5:
                # Если места нет, показываем ссылку "ещё..."
                self.canvas.create_text(
                    x + 10, y + self.cell_height - 15, 
                    text="ещё...", 
                    anchor="nw", 
                    font=("Arial", 9, "underline"), 
                    fill="blue"
                )
                break
            # Создаем текст события
            text_id = self.canvas.create_text(
                x + 10, event_y_offset, 
                text=event[0], 
                anchor="nw", 
                font=("Arial", 9), 
                fill="blue"
            )
            # Привязываем к тексту событие для обработки кликов
            self.canvas.tag_bind(text_id, "<Button-1>", lambda e, ev=event: self.open_event_detail(ev))
            event_y_offset += 15  # Отступ между событиями

    def open_event_detail(self, event):
        EventDetailWindow(self, event)

# --- Детали события ---
class EventDetailWindow(tk.Toplevel):
    def __init__(self, master, event):
        super().__init__(master)
        self.title("Детали события")
        self.geometry("500x400")
        self.event = event
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text=f"Название: {self.event['title']}", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self, text=f"Описание: {self.event['description']}").pack(pady=5)
        tk.Label(self, text=f"Начало: {self.event['start_time'].strftime('%d.%m.%Y %H:%M')}").pack(pady=5)
        tk.Label(self, text=f"Окончание: {self.event['end_time'].strftime('%d.%m.%Y %H:%M')}").pack(pady=5)
        tk.Label(self, text=f"Статус: {self.event['status']}").pack(pady=5)
        tk.Label(self, text=f"Комментарии: {self.event['comments']}").pack(pady=5)

        # Кнопки для редактирования и удаления события
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Редактировать", bg="orange", command=self.edit_event).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Удалить", bg="red", fg="white", command=self.delete_event).pack(side=tk.LEFT, padx=5)

    def edit_event(self):
        EditEventWindow(self, self.event)
        self.destroy()

    def delete_event(self):
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это событие?")
        if confirm:
            conn = sqlite3.connect('class_journal.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id=?", (self.event['id'],))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Событие удалено успешно.")
            self.master.update_calendar()
            self.destroy()

# --- Форма Редактирования События ---
class EditEventWindow(tk.Toplevel):
    def __init__(self, parent, event):
        super().__init__(parent)
        self.title("Редактировать событие")
        self.geometry("400x500")
        self.parent = parent
        self.event = event
        self.create_widgets()

    def create_widgets(self):
        # Название
        tk.Label(self, text="Название:").pack(pady=5)
        self.title_var = tk.StringVar(value=self.event['title'])
        self.title_entry = tk.Entry(self, textvariable=self.title_var)
        self.title_entry.pack(fill=tk.X, padx=20)

        # Описание
        tk.Label(self, text="Описание:").pack(pady=5)
        self.description_text = tk.Text(self, height=5)
        self.description_text.insert(tk.END, self.event['description'])
        self.description_text.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # Начало
        tk.Label(self, text="Начало (ДД.ММ.ГГГГ ЧЧ:ММ):").pack(pady=5)
        self.start_time_var = tk.StringVar(value=self.event['start_time'].strftime("%d.%m.%Y %H:%M"))
        self.start_time_entry = tk.Entry(self, textvariable=self.start_time_var)
        self.start_time_entry.pack(fill=tk.X, padx=20)

        # Окончание
        tk.Label(self, text="Окончание (ДД.ММ.ГГГГ ЧЧ:ММ):").pack(pady=5)
        self.end_time_var = tk.StringVar(value=self.event['end_time'].strftime("%d.%m.%Y %H:%M"))
        self.end_time_entry = tk.Entry(self, textvariable=self.end_time_var)
        self.end_time_entry.pack(fill=tk.X, padx=20)

        # Статус
        tk.Label(self, text="Статус:").pack(pady=5)
        self.status_var = tk.StringVar(value=self.event['status'])
        self.status_combo = ttk.Combobox(self, textvariable=self.status_var, values=["planned", "completed", "cancelled"], state="readonly")
        self.status_combo.pack(fill=tk.X, padx=20)

        # Комментарии
        tk.Label(self, text="Комментарии:").pack(pady=5)
        self.comments_text = tk.Text(self, height=3)
        self.comments_text.insert(tk.END, self.event['comments'])
        self.comments_text.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # Кнопка сохранения
        tk.Button(self, text="Сохранить", bg="green", fg="white", command=self.save_changes).pack(pady=10)

    def save_changes(self):
        title = self.title_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        status = self.status_var.get().strip()
        comments = self.comments_text.get("1.0", tk.END).strip()

        if not all([title, start_time, end_time, status]):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        # Валидация дат и времени
        try:
            start_dt = datetime.strptime(start_time, "%d.%m.%Y %H:%M")
            end_dt = datetime.strptime(end_time, "%d.%m.%Y %H:%M")
            if end_dt <= start_dt:
                messagebox.showerror("Ошибка", "Время окончания должно быть позже времени начала.")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты и времени.")
            return

        conn = sqlite3.connect('class_journal.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE events
            SET title=?, description=?, start_time=?, end_time=?, status=?, comments=?
            WHERE id=?
        """, (title, description, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"), status, comments, self.event['id']))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Событие успешно обновлено.")
        self.parent.update_calendar()
        self.destroy()

# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Электронный Классный Журнал")
    root.geometry("1000x800")
    app = MainApp(root)
    app.mainloop()
