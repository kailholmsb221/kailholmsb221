import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import re

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Образовательная Система")
        self.geometry("800x600")

        # Контейнер для всех фреймов
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Словарь для хранения фреймов
        self.frames = {}

        # Текущий пользователь
        self.current_user = None  # Будет хранить словарь с информацией о пользователе

        # Инициализация всех фреймов
        for F in (LoginFrame, RegistrationFrame, DashboardFrame, CalendarFrame, SubjectSelectionFrame, SubjectFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Показать начальный фрейм
        self.show_frame(LoginFrame)

    def show_frame(self, cont, **kwargs):
        frame = self.frames[cont]
        if cont == SubjectFrame and 'subject' in kwargs:
            frame.set_subject(kwargs['subject'])
        elif cont == DashboardFrame:
            frame.update_buttons()  # Обновить кнопки в зависимости от роли
        frame.tkraise()

class PhoneEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar()
        self.var.trace_add("write", self.format_phone)
        self.configure(textvariable=self.var)
        self.max_length = 16  # Максимальная длина форматированного номера

    def format_phone(self, *args):
        # Удаляем все нецифровые символы
        value = re.sub(r"\D", "", self.var.get())
        formatted = "+7 "

        # Форматируем номер по шаблону
        if len(value) > 1:
            formatted += value[1:4] + " "  # Код оператора
        if len(value) > 4:
            formatted += value[4:7] + " "  # Первые три цифры номера
        if len(value) > 7:
            formatted += value[7:9] + " "  # Следующие две цифры номера
        if len(value) > 9:
            formatted += value[9:11]       # Последние две цифры номера

        # Обрезаем лишние символы
        if len(formatted) > self.max_length:
            formatted = formatted[:self.max_length]

        # Обновляем поле ввода
        self.var.set(formatted)

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=20, pady=20)

        self.title_label = tk.Label(self, text="Вход", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Логин (почта, ИИН или номер телефона)
        self.login_label = tk.Label(self, text="Введите почту, ИИН или номер телефона", font=("Arial", 12))
        self.login_label.pack(pady=5)
        self.login_entry = tk.Entry(self, width=30)
        self.login_entry.pack(pady=5)

        # Пароль
        self.password_label = tk.Label(self, text="Пароль", font=("Arial", 12))
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Кнопка входа
        self.login_button = tk.Button(self, text="Войти", command=self.login)
        self.login_button.pack(pady=20)

        # Ссылка на регистрацию
        self.register_label = tk.Label(self, text="Регистрация", font=("Arial", 10), fg="blue", cursor="hand2")
        self.register_label.pack()
        self.register_label.bind("<Button-1>", lambda e: controller.show_frame(RegistrationFrame))

    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get()

        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
            return

        # Проверка данных (упрощенно, здесь можно добавить логику проверки с базой данных)
        if self.controller.current_user and (
            login == self.controller.current_user.get("email") or
            login == self.controller.current_user.get("iin") or
            login == self.controller.current_user.get("phone")
        ) and password == self.controller.current_user.get("password"):
            messagebox.showinfo("Успех", f"Добро пожаловать, {self.controller.current_user['fio']}!")
            self.controller.show_frame(DashboardFrame)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

class RegistrationFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=20, pady=20)

        self.title_label = tk.Label(self, text="Регистрация", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # ФИО
        self.fio_label = tk.Label(self, text="ФИО", font=("Arial", 12))
        self.fio_label.pack(pady=5)
        self.fio_entry = tk.Entry(self, width=30)
        self.fio_entry.pack(pady=5)

        # ИИН
        self.iin_label = tk.Label(self, text="ИИН", font=("Arial", 12))
        self.iin_label.pack(pady=5)
        self.iin_entry = tk.Entry(self, width=30)
        self.iin_entry.pack(pady=5)

        # Номер телефона
        self.phone_label = tk.Label(self, text="Номер телефона", font=("Arial", 12))
        self.phone_label.pack(pady=5)
        self.phone_entry = PhoneEntry(self, font=("Arial", 14), width=20)
        self.phone_entry.pack(pady=5)

        # Почта
        self.email_label = tk.Label(self, text="Электронная почта", font=("Arial", 12))
        self.email_label.pack(pady=5)
        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.pack(pady=5)

        # Пароль
        self.password_label = tk.Label(self, text="Пароль", font=("Arial", 12))
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Роль
        self.role_label = tk.Label(self, text="Выберите роль", font=("Arial", 12))
        self.role_label.pack(pady=5)

        self.role_var = tk.StringVar(value="Учитель")
        self.role_menu = ttk.Combobox(self, textvariable=self.role_var, state="readonly")
        self.role_menu['values'] = ["Учитель", "Ученик", "Родитель"]
        self.role_menu.pack(pady=5)

        # Кнопка регистрации
        self.register_button = tk.Button(self, text="Зарегистрироваться", command=self.register)
        self.register_button.pack(pady=20)

    def register(self):
        fio = self.fio_entry.get().strip()
        iin = self.iin_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_var.get()

        # Валидация ФИО
        if not fio:
            messagebox.showerror("Ошибка", "Введите ФИО!")
            return

        # Валидация ИИН
        if not iin.isdigit() or len(iin) != 12:
            messagebox.showerror("Ошибка", "ИИН должен состоять из 12 цифр!")
            return

        # Валидация номера телефона
        phone_pattern = r'^\+7 \d{3} \d{3} \d{2} \d{2}$'
        if not re.match(phone_pattern, phone):
            messagebox.showerror("Ошибка", "Номер телефона должен быть в формате +7 XXX XXX XX XX!")
            return

        # Валидация почты
        if '@' not in email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Ошибка", "Введите корректную электронную почту!")
            return

        # Валидация пароля
        if len(password) < 8:
            messagebox.showerror("Ошибка", "Пароль должен быть не менее 8 символов!")
            return

        # Если все проверки пройдены, сохраняем пользователя
        user_info = {
            "fio": fio,
            "iin": iin,
            "phone": phone,
            "email": email,
            "password": password,  # В реальном приложении не храните пароли в открытом виде!
            "role": role
        }
        self.controller.current_user = user_info
        messagebox.showinfo("Успех", f"Добро пожаловать, {fio}!")
        self.controller.show_frame(LoginFrame)

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=20, pady=20)

        self.label = tk.Label(self, text="Панель пользователя", font=("Arial", 16))
        self.label.pack(pady=10)

        # Кнопка для работы с календарём
        self.calendar_button = tk.Button(self, text="Календарь уроков", command=lambda: controller.show_frame(CalendarFrame))
        self.calendar_button.pack(pady=10)

        # Кнопка для выбора предмета
        self.subjects_button = tk.Button(self, text="Работа с предметами", command=lambda: controller.show_frame(SubjectSelectionFrame))
        self.subjects_button.pack(pady=10)

        # Кнопка выхода
        self.logout_button = tk.Button(self, text="Выйти", command=self.logout)
        self.logout_button.pack(pady=10)

    def update_buttons(self):
        user = self.controller.current_user
        if user and user.get("role") == "Учитель":
            self.calendar_button.config(state="normal")
        else:
            self.calendar_button.config(state="disabled")

    def logout(self):
        self.controller.current_user = None
        messagebox.showinfo("Вышли", "Вы успешно вышли из системы.")
        self.controller.show_frame(LoginFrame)

class CalendarFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=20, pady=20)

        self.label = tk.Label(self, text="Календарь уроков", font=("Arial", 16))
        self.label.pack(pady=10)

        self.calendar = Calendar(self, selectmode="day", year=2024, month=1, day=1)
        self.calendar.pack(pady=20)

        self.lesson_label = tk.Label(self, text="Введите название урока", font=("Arial", 12))
        self.lesson_label.pack(pady=5)

        self.lesson_entry = tk.Entry(self, width=30)
        self.lesson_entry.pack(pady=5)

        self.add_lesson_button = tk.Button(self, text="Добавить урок", command=self.add_lesson)
        self.add_lesson_button.pack(pady=10)

        self.lessons_listbox = tk.Listbox(self, width=50, height=10)
        self.lessons_listbox.pack(pady=10)

        # Кнопка назад
        self.back_button = tk.Button(self, text="Назад", command=lambda: controller.show_frame(DashboardFrame))
        self.back_button.pack(pady=10)

    def add_lesson(self):
        selected_date = self.calendar.get_date()
        lesson_name = self.lesson_entry.get().strip()
        if lesson_name:
            self.lessons_listbox.insert(tk.END, f"{selected_date}: {lesson_name}")
            self.lesson_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Введите название урока!")

class SubjectSelectionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=20, pady=20)

        self.label = tk.Label(self, text="Выберите предмет", font=("Arial", 16))
        self.label.pack(pady=10)

        self.subjects = [
            "Алгебра", "Геометрия", "Русский язык", "Русская литература",
            "Химия", "Биология", "История Казахстана", "Всемирная история",
            "География", "Казахский язык", "Английский язык"
        ]

        # Создание кнопок для каждого предмета
        for subject in self.subjects:
            button = tk.Button(self, text=subject, width=30, command=lambda s=subject: controller.show_frame(SubjectFrame, subject=s))
            button.pack(pady=5)

        # Кнопка назад
        self.back_button = tk.Button(self, text="Назад", command=lambda: controller.show_frame(DashboardFrame))
        self.back_button.pack(pady=10)

class SubjectFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.subject = ""
        self.configure(padx=20, pady=20)

        self.label = tk.Label(self, text="", font=("Arial", 16))
        self.label.pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("name", "grade", "comment"), show="headings")
        self.tree.heading("name", text="Имя ученика")
        self.tree.heading("grade", text="Оценка")
        self.tree.heading("comment", text="Комментарий")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.add_frame = tk.Frame(self)
        self.add_frame.pack(pady=10)

        self.name_entry = tk.Entry(self.add_frame, width=20)
        self.name_entry.grid(row=0, column=0, padx=5)
        self.name_entry.insert(0, "Имя ученика")

        self.grade_entry = tk.Entry(self.add_frame, width=10)
        self.grade_entry.grid(row=0, column=1, padx=5)
        self.grade_entry.insert(0, "Оценка")

        self.comment_entry = tk.Entry(self.add_frame, width=20)
        self.comment_entry.grid(row=0, column=2, padx=5)
        self.comment_entry.insert(0, "Комментарий")

        self.add_button = tk.Button(self.add_frame, text="Добавить", command=self.add_entry)
        self.add_button.grid(row=0, column=3, padx=5)

        # Кнопка назад
        self.back_button = tk.Button(self, text="Назад", command=lambda: controller.show_frame(SubjectSelectionFrame))
        self.back_button.pack(pady=10)

    def set_subject(self, subject):
        self.subject = subject
        self.label.config(text=f"Предмет: {self.subject}")
        # Очистка текущих данных в дереве при смене предмета
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Можно добавить загрузку данных из базы данных или другого источника здесь

    def add_entry(self):
        name = self.name_entry.get().strip()
        grade = self.grade_entry.get().strip()
        comment = self.comment_entry.get().strip()
        if name and grade:
            self.tree.insert("", "end", values=(name, grade, comment))
            self.name_entry.delete(0, tk.END)
            self.grade_entry.delete(0, tk.END)
            self.comment_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Введите имя ученика и оценку!")

# Запуск приложения
if __name__ == "__main__":
    app = Application()
    app.mainloop()  