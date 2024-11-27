import tkinter as tk
from tkinter import messagebox
import psycopg2
from psycopg2 import sql

# Подключение к базе данных PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="mydatabase",
            user="your_user",    # Замените на ваше имя пользователя
            password="your_password",  # Замените на ваш пароль
            host="localhost",    # Замените на адрес вашего хоста, если это не локальный сервер
            port="5432"          # Обычно порт по умолчанию - 5432
        )
        return conn
    except Exception as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return None

# Функция для добавления пользователя в базу данных
def add_user():
    name = name_entry.get()
    age = age_entry.get()

    if name and age:
        try:
            age = int(age)
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                insert_query = sql.SQL("INSERT INTO users (name, age) VALUES (%s, %s)")
                cursor.execute(insert_query, (name, age))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Успех", "Пользователь добавлен")
                name_entry.delete(0, tk.END)
                age_entry.delete(0, tk.END)
                show_users()
        except ValueError:
            messagebox.showerror("Ошибка", "Возраст должен быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {e}")
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")

# Функция для отображения пользователей
def show_users():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            user_list.delete(0, tk.END)
            for row in rows:
                user_list.insert(tk.END, f"ID: {row[0]}, Имя: {row[1]}, Возраст: {row[2]}")
            cursor.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")
        finally:
            conn.close()

# Функция для удаления выбранного пользователя
def delete_user():
    selected_item = user_list.curselection()
    if selected_item:
        user_data = user_list.get(selected_item)
        user_id = int(user_data.split(",")[0].split(":")[1].strip())

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                delete_query = sql.SQL("DELETE FROM users WHERE id = %s")
                cursor.execute(delete_query, (user_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Пользователь удален")
                show_users()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя: {e}")
            finally:
                cursor.close()
                conn.close()
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите пользователя для удаления")

# Инициализация окна приложения
root = tk.Tk()
root.title("Управление пользователями (PostgreSQL)")

# Метки и поля для ввода данных
name_label = tk.Label(root, text="Имя:")
name_label.grid(row=0, column=0, padx=10, pady=10)

name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=10, pady=10)

age_label = tk.Label(root, text="Возраст:")
age_label.grid(row=1, column=0, padx=10, pady=10)

age_entry = tk.Entry(root)
age_entry.grid(row=1, column=1, padx=10, pady=10)

# Кнопки для добавления, удаления и просмотра пользователей
add_button = tk.Button(root, text="Добавить пользователя", command=add_user)
add_button.grid(row=2, column=0, columnspan=2, pady=10)

delete_button = tk.Button(root, text="Удалить пользователя", command=delete_user)
delete_button.grid(row=3, column=0, columnspan=2, pady=10)

show_button = tk.Button(root, text="Показать пользователей", command=show_users)
show_button.grid(row=4, column=0, columnspan=2, pady=10)

# Список для отображения пользователей
user_list = tk.Listbox(root, width=50)
user_list.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Запуск главного цикла
root.mainloop()
