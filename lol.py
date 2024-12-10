import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar

# Окно регистрации
class RegistrationWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Регистрация")
        self.geometry("400x300")

        # Роль
        self.role_label = tk.Label(self, text="Выберите роль", font=("Arial", 12))
        self.role_label.pack(pady=10)
        
        self.role_var = tk.StringVar(value="Учитель")
        self.role_menu = ttk.Combobox(self, textvariable=self.role_var, state="readonly")
        self.role_menu['values'] = ["Учитель", "Ученик", "Родитель"]
        self.role_menu.pack(pady=5)
        
        # Логин
        self.login_label = tk.Label(self, text="Логин", font=("Arial", 12))
        self.login_label.pack(pady=10)
        self.login_entry = tk.Entry(self, width=30)
        self.login_entry.pack(pady=5)
        
        # Пароль
        self.password_label = tk.Label(self, text="Пароль", font=("Arial", 12))
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)
        
        # Кнопка входа
        self.register_button = tk.Button(self, text="Войти", command=self.login)
        self.register_button.pack(pady=20)
    
    def login(self):
        role = self.role_var.get()
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if role == "Учитель" and login and password:
            messagebox.showinfo("Успех", f"Добро пожаловать, {login}!")
            self.open_teacher_dashboard()
        else:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
    
    def open_teacher_dashboard(self):
        self.destroy()  # Закрыть окно регистрации
        TeacherDashboard()  # Открыть панель учителя


# Панель учителя
class TeacherDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Панель учителя")
        self.geometry("400x300")
        
        self.label = tk.Label(self, text="Выберите действие", font=("Arial", 14))
        self.label.pack(pady=20)

        # Кнопка для работы с календарём
        self.calendar_button = tk.Button(self, text="Календарь уроков", command=self.open_calendar)
        self.calendar_button.pack(pady=10)

        # Кнопка для выбора предмета
        self.subjects_button = tk.Button(self, text="Работа с предметами", command=self.open_subject_selection)
        self.subjects_button.pack(pady=10)
    
    def open_calendar(self):
        TeacherCalendarWindow(self)
    
    def open_subject_selection(self):
        SubjectSelectionWindow(self)


# Окно учителя с календарем
class TeacherCalendarWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Календарь уроков")
        self.geometry("900x600")

        # Заголовок
        self.label = tk.Label(self, text="Календарь уроков", font=("Arial", 16))
        self.label.pack(pady=10)

        self.calendar = Calendar(self, selectmode="day", year=2024, month=12, day=1)
        self.calendar.pack(pady=10, fill=tk.X)

        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=10)

        # Поля для добавления урока
        self.lesson_name_label = tk.Label(self.control_frame, text="Название урока:")
        self.lesson_name_label.grid(row=0, column=0, padx=5)
        self.lesson_name_entry = tk.Entry(self.control_frame)
        self.lesson_name_entry.grid(row=0, column=1, padx=5)

        self.time_label = tk.Label(self.control_frame, text="Время (часы:мин):")
        self.time_label.grid(row=1, column=0, padx=5)
        self.time_entry = tk.Entry(self.control_frame)
        self.time_entry.grid(row=1, column=1, padx=5)

        self.class_label = tk.Label(self.control_frame, text="Класс:")
        self.class_label.grid(row=2, column=0, padx=5)
        self.class_entry = tk.Entry(self.control_frame)
        self.class_entry.grid(row=2, column=1, padx=5)

        self.teacher_label = tk.Label(self.control_frame, text="Имя учителя:")
        self.teacher_label.grid(row=3, column=0, padx=5)
        self.teacher_entry = tk.Entry(self.control_frame)
        self.teacher_entry.grid(row=3, column=1, padx=5)

        # Кнопка добавления урока
        self.add_button = tk.Button(self.control_frame, text="Добавить урок", command=self.add_lesson)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Список уроков по дате
        self.lessons = {}

        # Кнопка для отображения уроков
        self.show_button = tk.Button(self, text="Показать уроки на выбранную дату", command=self.show_lessons)
        self.show_button.pack(pady=10)

        # Список уроков
        self.lesson_listbox = tk.Listbox(self, width=80, height=10)
        self.lesson_listbox.pack(pady=10)

    def add_lesson(self):
        """Добавить урок в календарь."""
        date = self.calendar.get_date()
        lesson_name = self.lesson_name_entry.get()
        time = self.time_entry.get()
        class_name = self.class_entry.get()
        teacher_name = self.teacher_entry.get()

        if not lesson_name or not time or not class_name or not teacher_name:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        lesson_info = {
            "Название": lesson_name,
            "Время": time,
            "Класс": class_name,
            "Учитель": teacher_name
        }

        if date not in self.lessons:
            self.lessons[date] = []

        self.lessons[date].append(lesson_info)
        messagebox.showinfo("Успех", f"Урок '{lesson_name}' добавлен на {date}.")
        self.clear_inputs()

    def clear_inputs(self):
        """Очистить поля ввода."""
        self.lesson_name_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.class_entry.delete(0, tk.END)
        self.teacher_entry.delete(0, tk.END)

    def show_lessons(self):
        """Отобразить уроки на выбранную дату."""
        date = self.calendar.get_date()
        self.lesson_listbox.delete(0, tk.END)

        if date not in self.lessons or not self.lessons[date]:
            self.lesson_listbox.insert(tk.END, "Уроков на выбранную дату нет.")
        else:
            for lesson in self.lessons[date]:
                lesson_text = (f"{lesson['Время']} - {lesson['Название']} | "
                               f"Класс: {lesson['Класс']} | Учитель: {lesson['Учитель']}")
                self.lesson_listbox.insert(tk.END, lesson_text)


# Окно выбора предметов
class SubjectSelectionWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Предметы")
        self.geometry("400x300")
        
        self.label = tk.Label(self, text="Выберите предмет", font=("Arial", 14))
        self.label.pack(pady=20)
        
        self.subjects = [
            "Алгебра", "Геометрия", "Русский язык", "Русская литература",
            "Химия", "Биология", "История Казахстана", "Всемирная история",
            "География", "Казахский язык", "Английский язык"
        ]
        
        for subject in self.subjects:
            button = tk.Button(self, text=subject, command=lambda s=subject: self.open_subject_window(s))
            button.pack(pady=5)
    
    def open_subject_window(self, subject):
        SubjectWindow(self, subject)


# Окно для работы с конкретным предметом
class SubjectWindow(tk.Toplevel):
    def __init__(self, parent, subject):
        super().__init__(parent)
        self.title(f"{subject} - Окно учителя")
        self.geometry("600x400")
        
        self.label = tk.Label(self, text=f"Учитель: {subject}", font=("Arial", 16))
        self.label.pack(pady=20)
        
        self.tree = ttk.Treeview(self, columns=("name", "grade", "comment"), show="headings")
        self.tree.heading("name", text="Имя ученика")
        self.tree.heading("grade", text="Оценка")
        self.tree.heading("comment", text="Комментарий")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.add_frame = tk.Frame(self)
        self.add_frame.pack(pady=10)
        
        self.name_entry = tk.Entry(self.add_frame)
        self.name_entry.grid(row=0, column=0, padx=5)
        self.name_entry.insert(0, "Имя ученика")
        
        self.grade_entry = tk.Entry(self.add_frame)
        self.grade_entry.grid(row=0, column=1, padx=5)
        self.grade_entry.insert(0, "Оценка")
        
        self.comment_entry = tk.Entry(self.add_frame)
        self.comment_entry.grid(row=0, column=2, padx=5)
        self.comment_entry.insert(0, "Комментарий")
        
        self.add_button = tk.Button(self.add_frame, text="Добавить", command=self.add_entry)
        self.add_button.grid(row=0, column=3, padx=5)

    def add_entry(self):
        name = self.name_entry.get()
        grade = self.grade_entry.get()
        comment = self.comment_entry.get()
        self.tree.insert("", "end", values=(name, grade, comment))
        self.name_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.comment_entry.delete(0, tk.END)


# Запуск приложения
if __name__ == "__main__":
    app = RegistrationWindow()
    app.mainloop()
