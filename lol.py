import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Программа")
        self.geometry("800x600")
        self.current_user = {"role": None, "subject": None}

        # Создание вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Вкладка для регистрации
        self.registration_frame = tk.Frame(self.notebook)
        self.create_registration_frame()
        self.notebook.add(self.registration_frame, text="Регистрация")

        # Вкладка для панели учителя
        self.teacher_frame = tk.Frame(self.notebook)
        self.create_teacher_dashboard()
        self.notebook.add(self.teacher_frame, text="Панель учителя")

        # Вкладка для календаря
        self.calendar_frame = tk.Frame(self.notebook)
        self.create_shared_calendar()
        self.notebook.add(self.calendar_frame, text="Общий календарь")

        # Установка начальной вкладки
        self.notebook.select(self.registration_frame)

        # Уроки по пользователям
        self.lessons = {}

    def create_registration_frame(self):
        role_label = tk.Label(self.registration_frame, text="Выберите роль", font=("Arial", 12))
        role_label.pack(pady=10)

        self.role_var = tk.StringVar(value="Учитель")
        role_menu = ttk.Combobox(self.registration_frame, textvariable=self.role_var, state="readonly")
        role_menu['values'] = ["Учитель", "Ученик", "Родитель"]
        role_menu.pack(pady=5)

        login_label = tk.Label(self.registration_frame, text="Логин", font=("Arial", 12))
        login_label.pack(pady=10)
        self.login_entry = tk.Entry(self.registration_frame, width=30)
        self.login_entry.pack(pady=5)

        password_label = tk.Label(self.registration_frame, text="Пароль", font=("Arial", 12))
        password_label.pack(pady=10)
        self.password_entry = tk.Entry(self.registration_frame, width=30, show="*")
        self.password_entry.pack(pady=5)

        subject_label = tk.Label(self.registration_frame, text="Предмет (только для учителей)", font=("Arial", 12))
        subject_label.pack(pady=10)
        self.subject_entry = tk.Entry(self.registration_frame, width=30)
        self.subject_entry.pack(pady=5)

        register_button = tk.Button(self.registration_frame, text="Войти", command=self.login)
        register_button.pack(pady=20)

    def login(self):
        role = self.role_var.get()
        login = self.login_entry.get()
        password = self.password_entry.get()
        subject = self.subject_entry.get()

        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
            return

        self.current_user["role"] = role
        self.current_user["subject"] = subject if role == "Учитель" else None

        messagebox.showinfo("Успех", f"Добро пожаловать, {login}!")
        self.notebook.hide(self.registration_frame)
        self.notebook.select(self.teacher_frame if role == "Учитель" else self.calendar_frame)

    def create_teacher_dashboard(self):
        label = tk.Label(self.teacher_frame, text="Панель учителя", font=("Arial", 14))
        label.pack(pady=20)

        # Кнопки
        my_lessons_button = tk.Button(self.teacher_frame, text="Мои уроки", command=self.show_my_lessons)
        my_lessons_button.pack(pady=10)

        calendar_button = tk.Button(self.teacher_frame, text="Общий календарь", command=lambda: self.notebook.select(self.calendar_frame))
        calendar_button.pack(pady=10)

        self.my_lessons_listbox = tk.Listbox(self.teacher_frame, width=80, height=10)
        self.my_lessons_listbox.pack(pady=10)

        # Оценка и комментарий
        control_frame = tk.Frame(self.teacher_frame)
        control_frame.pack(pady=10)

        self.comment_entry = tk.Entry(control_frame, width=40)
        self.comment_entry.grid(row=0, column=0, padx=5)
        self.comment_entry.insert(0, "Комментарий")

        self.grade_entry = tk.Entry(control_frame, width=10)
        self.grade_entry.grid(row=0, column=1, padx=5)
        self.grade_entry.insert(0, "Оценка")

        self.add_comment_button = tk.Button(control_frame, text="Добавить", command=self.add_comment)
        self.add_comment_button.grid(row=0, column=2, padx=5)

    def show_my_lessons(self):
        """Показать уроки текущего учителя."""
        subject = self.current_user.get("subject")
        if not subject:
            messagebox.showerror("Ошибка", "Вы не учитель!")
            return

        self.my_lessons_listbox.delete(0, tk.END)
        if subject in self.lessons:
            for lesson in self.lessons[subject]:
                self.my_lessons_listbox.insert(tk.END, f"{lesson['Дата']} - {lesson['Время']} - {lesson['Название']}")
        else:
            self.my_lessons_listbox.insert(tk.END, "Нет уроков.")

    def add_comment(self):
        """Добавить комментарий и оценку к уроку."""
        selected = self.my_lessons_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите урок!")
            return

        comment = self.comment_entry.get()
        grade = self.grade_entry.get()

        if not comment or not grade:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        messagebox.showinfo("Успех", f"Комментарий: {comment}, Оценка: {grade}")

    def create_shared_calendar(self):
        label = tk.Label(self.calendar_frame, text="Общий календарь уроков", font=("Arial", 14))
        label.pack(pady=20)

        self.calendar = Calendar(self.calendar_frame, selectmode="day", year=2024, month=12, day=1)
        self.calendar.pack(pady=10)

        self.lesson_listbox = tk.Listbox(self.calendar_frame, width=80, height=10)
        self.lesson_listbox.pack(pady=10)

        show_button = tk.Button(self.calendar_frame, text="Показать уроки на дату", command=self.show_lessons)
        show_button.pack(pady=10)

    def show_lessons(self):
        """Показать уроки на выбранную дату."""
        date = self.calendar.get_date()
        self.lesson_listbox.delete(0, tk.END)

        found = False
        for subject, lessons in self.lessons.items():
            for lesson in lessons:
                if lesson["Дата"] == date:
                    found = True
                    self.lesson_listbox.insert(tk.END, f"{lesson['Время']} - {lesson['Название']} ({subject})")

        if not found:
            self.lesson_listbox.insert(tk.END, "Уроков на эту дату нет.")

    def add_lesson(self, date, time, name, subject):
        """Добавить урок в календарь."""
        if subject not in self.lessons:
            self.lessons[subject] = []

        self.lessons[subject].append({"Дата": date, "Время": time, "Название": name})


if __name__ == "__main__":
    app = MainApplication()
    # Пример добавления уроков
    app.add_lesson("2024-12-01", "10:00", "Биология 101", "Биология")
    app.add_lesson("2024-12-01", "12:00", "Химия 202", "Химия")
    app.mainloop()
