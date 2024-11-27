import tkinter as tk
from tkinter import messagebox

# Пример данных студентов (имена и оценки)
students_data = [
    {'name': 'Иван Иванов', 'grade': 85},
    {'name': 'Петр Петров', 'grade': 92},
    {'name': 'Светлана Светлова', 'grade': 78},
    {'name': 'Анна Кузнецова', 'grade': 89},
    {'name': 'Дмитрий Сидоров', 'grade': 95},
    {'name': 'Ольга Орлова', 'grade': 70}
]

class StudentPerformanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ и прогнозирование успеваемости студентов")
        self.root.geometry("400x300")

        # Кнопка для вычисления средней оценки группы
        self.avg_button = tk.Button(root, text="Средняя оценка группы", command=self.calculate_average)
        self.avg_button.pack(pady=10)

        # Кнопка для вывода самых успешных студентов
        self.top_students_button = tk.Button(root, text="Самые успешные студенты", command=self.show_top_students)
        self.top_students_button.pack(pady=10)

        # Поле для вывода результата
        self.result_text = tk.Text(root, height=10, width=40)
        self.result_text.pack(pady=10)

    def calculate_average(self):
        """Вычислить и показать среднюю оценку группы"""
        if not students_data:
            messagebox.showerror("Ошибка", "Нет данных о студентах")
            return

        total_grade = sum(student['grade'] for student in students_data)
        average_grade = total_grade / len(students_data)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Средняя оценка группы: {average_grade:.2f}\n")

    def show_top_students(self):
        """Показать студентов с оценкой выше 85"""
        top_students = [student for student in students_data if student['grade'] > 85]
        self.result_text.delete(1.0, tk.END)
        if top_students:
            self.result_text.insert(tk.END, "Самые успешные студенты:\n")
            for student in top_students:
                self.result_text.insert(tk.END, f"{student['name']} - {student['grade']}\n")
        else:
            self.result_text.insert(tk.END, "Нет студентов с оценкой выше 85\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentPerformanceApp(root)
    root.mainloop()
