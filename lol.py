import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        self.geometry("600x500")

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

    def add_lesson(self):
        selected_date = self.calendar.get_date()
        lesson_name = self.lesson_entry.get()
        if lesson_name:
            self.lessons_listbox.insert(tk.END, f"{selected_date}: {lesson_name}")
            self.lesson_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Введите название урока!")


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
