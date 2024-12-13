import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar

# В этом примере происходит объединение предыдущего функционала:
# - Отображение дня, недели, месяца (из предыдущего кода)
# - Расширенный дневной вид до 23:00 с получасовой разметкой
# - Возможность вертикального скроллинга в дневном режиме
# - Прокрутка колесом мыши в дневном режиме
#
# Данный код демонстрационный, и в реальном приложении могут потребоваться
# дополнительные улучшения и интеграция с базой данных или логикой событий.

events = [
    {
        'id': 1,
        'title': 'Математика',
        'start_time': datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
        'end_time': datetime.now().replace(hour=11, minute=0, second=0, microsecond=0),
        'subject': 'Математика',
        'instructor': 'Иванов',
        'comments': 'Подготовить домашнее задание',
        'status': 'planned'
    },
    {
        'id': 2,
        'title': 'Английский язык',
        'start_time': (datetime.now() + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0),
        'end_time': (datetime.now() + timedelta(days=1)).replace(hour=20, minute=0, second=0, microsecond=0),
        'subject': 'Английский',
        'instructor': 'Петров',
        'comments': 'Контрольная работа',
        'status': 'planned'
    },
    {
        'id': 3,
        'title': 'История',
        'start_time': (datetime.now() + timedelta(days=10)).replace(hour=9, minute=0, second=0, microsecond=0),
        'end_time': (datetime.now() + timedelta(days=10)).replace(hour=10, minute=0, second=0, microsecond=0),
        'subject': 'История',
        'instructor': 'Сидоров',
        'comments': 'Лекция об античности',
        'status': 'planned'
    },
    {
        'id': 4,
        'title': 'Физика',
        'start_time': (datetime.now() - timedelta(days=2)).replace(hour=16, minute=0, second=0, microsecond=0),
        'end_time': (datetime.now() - timedelta(days=2)).replace(hour=17, minute=0, second=0, microsecond=0),
        'subject': 'Физика',
        'instructor': 'Кузнецов',
        'comments': 'Прошедшее занятие. Проверка понимания',
        'status': 'completed'
    },
]

class EventDetailWindow(tk.Toplevel):
    def __init__(self, master, event):
        super().__init__(master)
        self.title("Детали события")
        self.event = event
        
        tk.Label(self, text="Название:").grid(row=0, column=0, sticky='e')
        tk.Label(self, text=self.event['title']).grid(row=0, column=1, sticky='w')
        
        tk.Label(self, text="Предмет:").grid(row=1, column=0, sticky='e')
        tk.Label(self, text=self.event['subject']).grid(row=1, column=1, sticky='w')

        tk.Label(self, text="Преподаватель:").grid(row=2, column=0, sticky='e')
        tk.Label(self, text=self.event['instructor']).grid(row=2, column=1, sticky='w')

        tk.Label(self, text="Начало:").grid(row=3, column=0, sticky='e')
        tk.Label(self, text=self.event['start_time'].strftime("%Y-%m-%d %H:%M")).grid(row=3, column=1, sticky='w')

        tk.Label(self, text="Окончание:").grid(row=4, column=0, sticky='e')
        tk.Label(self, text=self.event['end_time'].strftime("%Y-%m-%d %H:%M")).grid(row=4, column=1, sticky='w')

        tk.Label(self, text="Статус:").grid(row=5, column=0, sticky='e')
        tk.Label(self, text=self.event['status']).grid(row=5, column=1, sticky='w')

        tk.Label(self, text="Комментарии:").grid(row=6, column=0, sticky='ne')
        comments_text = tk.Text(self, width=40, height=5)
        comments_text.grid(row=6, column=1, sticky='w')
        comments_text.insert('1.0', self.event['comments'])
        
        tk.Button(self, text="Закрыть", command=self.destroy).grid(row=7, column=1, pady=10, sticky='e')


class CalendarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Календарь")
        self.geometry("1100x700")

        # Новые параметры для дневного вида
        self.start_hour = 8
        self.end_hour = 23
        self.row_height = 25  # 30 мин = 25px
        self.current_view = "month"
        self.current_date = datetime.now()

        # Верхняя панель (кнопка Сегодня + переключатели)
        self.topbar = tk.Frame(self)
        self.topbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_today = tk.Button(self.topbar, text="Сегодня", command=self.go_today)
        self.btn_today.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопки переключения видов
        self.btn_month = tk.Button(self.topbar, text="Месяц", command=lambda: self.switch_view("month"))
        self.btn_month.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn_week = tk.Button(self.topbar, text="Неделя", command=lambda: self.switch_view("week"))
        self.btn_week.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn_day = tk.Button(self.topbar, text="День", command=lambda: self.switch_view("day"))
        self.btn_day.pack(side=tk.RIGHT, padx=5, pady=5)

        # Заголовок с датой и стрелками
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

        # Область для календаря со скроллом
        self.scroll_frame = tk.Frame(self)
        self.scroll_frame.pack(expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.scroll_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_y = tk.Scrollbar(self.scroll_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # Фрейм контента внутри canvas
        self.content_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", self.on_frame_configure)

        # Привязка колеса мыши для прокрутки
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self.day_boxes = []
        self.draw_view()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-event.delta/120), "units")

    def switch_view(self, view):
        self.current_view = view
        self.draw_view()

    def go_today(self):
        self.current_date = datetime.now()
        self.draw_view()

    def prev_period(self):
        if self.current_view == "day":
            self.current_date -= timedelta(days=1)
        elif self.current_view == "week":
            self.current_date -= timedelta(weeks=1)
        elif self.current_view == "month":
            year = self.current_date.year
            month = self.current_date.month
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            day = min(self.current_date.day, calendar.monthrange(year, month)[1])
            self.current_date = self.current_date.replace(year=year, month=month, day=day)
        self.draw_view()

    def next_period(self):
        if self.current_view == "day":
            self.current_date += timedelta(days=1)
        elif self.current_view == "week":
            self.current_date += timedelta(weeks=1)
        elif self.current_view == "month":
            year = self.current_date.year
            month = self.current_date.month
            month += 1
            if month > 12:
                month = 1
                year += 1
            day = min(self.current_date.day, calendar.monthrange(year, month)[1])
            self.current_date = self.current_date.replace(year=year, month=month, day=day)
        self.draw_view()

    def update_header(self):
        if self.current_view == "day":
            date_str = self.current_date.strftime("%d %B %Y г.")
            self.header_label.config(text=date_str)
        elif self.current_view == "week":
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            date_str = f"Неделя: {start_of_week.strftime('%d %B %Y')} - {end_of_week.strftime('%d %B %Y')}"
            self.header_label.config(text=date_str)
        elif self.current_view == "month":
            date_str = self.current_date.strftime("%B %Y г.")
            self.header_label.config(text=date_str)
        else:
            self.header_label.config(text="")

    def update_view_buttons(self):
        default_bg = self.btn_day.cget("bg")
        default_fg = self.btn_day.cget("fg")
        self.btn_day.config(bg=default_bg, fg=default_fg)
        self.btn_week.config(bg=default_bg, fg=default_fg)
        self.btn_month.config(bg=default_bg, fg=default_fg)

        if self.current_view == "day":
            self.btn_day.config(bg="green", fg="white")
        elif self.current_view == "week":
            self.btn_week.config(bg="green", fg="white")
        elif self.current_view == "month":
            self.btn_month.config(bg="green", fg="white")

    def draw_view(self):
        # Очистим content_frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.day_boxes.clear()
        self.update_header()
        self.update_view_buttons()

        if self.current_view == "day":
            self.draw_day_view()
            self.place_day_events()
        elif self.current_view == "week":
            self.draw_week_view()
            self.place_week_events()
        elif self.current_view == "month":
            self.draw_month_view()
            self.place_month_events()
        else:
            self.canvas.create_text(200, 100, text="Вид не поддерживается", font=("Arial", 14))

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ------------------- День -------------------
    def draw_day_view(self):
        # Дневной вид с 8:00 до 23:00
        left_margin = 80
        top_margin = 20
        timeline_canvas = tk.Canvas(self.content_frame, bg="white", highlightthickness=0)
        timeline_canvas.pack(fill=tk.BOTH, expand=True)

        total_hours = self.end_hour - self.start_hour + 1
        total_height = total_hours * self.row_height * 2 + top_margin * 2
        timeline_canvas.config(height=total_height, width=1000)

        # Подсветка сегодняшнего дня
        if self.current_date.date() == datetime.now().date():
            timeline_canvas.create_rectangle(0,0,2000,2000,fill="#fffacd",outline="")

        for hour in range(self.start_hour, self.end_hour + 1):
            y = top_margin + (hour - self.start_hour)*self.row_height*2
            timeline_canvas.create_line(left_margin, y, 2000, y, width=2, fill="black")
            time_str = f"{hour}:00"
            timeline_canvas.create_text(left_margin - 10, y, text=time_str, anchor='e', font=("Arial", 10))

            if hour < self.end_hour:
                half_y = y + self.row_height
                timeline_canvas.create_line(left_margin, half_y, 2000, half_y, fill="gray", dash=(2,2))
                half_str = f"{hour}:30"
                timeline_canvas.create_text(left_margin - 10, half_y, text=half_str, anchor='e', font=("Arial", 8))

    def place_day_events(self):
        day_events = [e for e in events if e['start_time'].date() == self.current_date.date()]
        day_events.sort(key=lambda ev: ev['start_time'])
        if not day_events:
            return

        # Найдём Canvas (он единственный в дневном режиме)
        timeline_canvas = self.content_frame.winfo_children()[0]

        left_margin = 80
        top_margin = 20

        for event in day_events:
            start_hour = event['start_time'].hour
            start_minute = event['start_time'].minute
            end_hour = event['end_time'].hour
            end_minute = event['end_time'].minute

            start_y = top_margin + (start_hour - self.start_hour)*self.row_height*2 + (self.row_height if start_minute>=30 else 0)
            end_y = top_margin + (end_hour - self.start_hour)*self.row_height*2 + (self.row_height if end_minute>=30 else 0)

            x1 = left_margin + 10
            x2 = x1 + 200
            y1 = start_y + 5
            y2 = max(y1+20, end_y - 5)
            fill_color = "lightgreen" if event['status'] == 'planned' else "#d3d3d3"

            rect = timeline_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
            event_text = f"{event['title']}\n{event['start_time'].strftime('%H:%M')}-{event['end_time'].strftime('%H:%M')}"
            txt = timeline_canvas.create_text(x1+5, (y1+y2)/2, text=event_text, anchor='w', font=("Arial", 10), width=190)

            def on_event_click(e, ev=event):
                EventDetailWindow(self, ev)

            timeline_canvas.tag_bind(rect, "<Button-1>", on_event_click)
            timeline_canvas.tag_bind(txt, "<Button-1>", on_event_click)

    # ------------------- Неделя -------------------
    def draw_week_view(self):
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        week_canvas = tk.Canvas(self.content_frame, bg="white", highlightthickness=0)
        week_canvas.pack(fill=tk.BOTH, expand=True)

        col_width = 120
        row_height = self.row_height
        left_margin = 50
        top_margin = 20

        current_day_of_week = self.current_date.weekday()
        start_of_week = self.current_date - timedelta(days=current_day_of_week)
        total_hours = self.end_hour - self.start_hour
        canvas_height = (total_hours * row_height) + (row_height) + top_margin + 200
        week_canvas.config(height=canvas_height, width=1000)

        for i, day_name in enumerate(days_of_week):
            x = left_margin + i * col_width
            y = top_margin
            day_date = start_of_week + timedelta(days=i)
            if day_date.date() == datetime.now().date():
                week_canvas.create_rectangle(x, y, x+col_width, y+row_height, fill="#fffacd", outline="black")
                week_canvas.create_text(x+col_width/2, y+row_height/2, text=day_name, font=("Arial", 10, "bold"))
            else:
                week_canvas.create_rectangle(x, y, x+col_width, y+row_height, fill="#f0f0f0", outline="black")
                week_canvas.create_text(x+col_width/2, y+row_height/2, text=day_name, font=("Arial", 10))

        start_y = top_margin + row_height
        for hour in range(self.start_hour, self.end_hour+1):
            y = start_y + (hour - self.start_hour) * row_height
            week_canvas.create_line(left_margin, y, left_margin + col_width*7, y, fill="gray")
            time_str = f"{hour}:00"
            week_canvas.create_text(left_margin - 30, y, text=time_str, anchor='e')

        for i in range(8):
            x = left_margin + i * col_width
            week_canvas.create_line(x, top_margin + row_height, x, top_margin + row_height + total_hours*row_height, fill="gray")

    def place_week_events(self):
        left_margin = 50
        top_margin = 20
        col_width = 120
        row_height = self.row_height

        current_day_of_week = self.current_date.weekday()
        start_of_week = self.current_date - timedelta(days=current_day_of_week)
        end_of_week = start_of_week + timedelta(days=6)
        week_events = [e for e in events if start_of_week.date() <= e['start_time'].date() <= end_of_week.date()]
        week_events.sort(key=lambda ev: ev['start_time'])

        week_canvas = self.content_frame.winfo_children()[0]

        base_y = top_margin + self.row_height
        for event in week_events:
            day_index = (event['start_time'].date() - start_of_week.date()).days
            start_hour = event['start_time'].hour
            end_hour = event['end_time'].hour
            start_minute = event['start_time'].minute
            end_minute = event['end_time'].minute

            start_y = base_y + (start_hour - self.start_hour)*row_height
            # Можно добавить учёт минут, если нужно
            # Но для упрощения оставим без интервалов минут, или добавить (start_minute/60)*row_height
            y1 = start_y + 5
            # Аналогично для end_y
            end_y = base_y + (end_hour - self.start_hour)*row_height
            y2 = max(y1+20, end_y - 5)

            x = left_margin + day_index * col_width
            fill_color = "lightgreen" if event['status'] == 'planned' else "#d3d3d3"
            rect = week_canvas.create_rectangle(x+2, y1, x+col_width-2, y2, fill=fill_color, outline="black")
            event_text = f"{event['title']} ({event['start_time'].strftime('%H:%M')}-{event['end_time'].strftime('%H:%M')})"
            txt = week_canvas.create_text(x+col_width/2, (y1+y2)/2, text=event_text, font=("Arial", 9), width=col_width-10)

            def on_event_click(e, ev=event):
                EventDetailWindow(self, ev)
            
            week_canvas.tag_bind(rect, "<Button-1>", on_event_click)
            week_canvas.tag_bind(txt, "<Button-1>", on_event_click)

    # ------------------- Месяц -------------------
    def draw_month_view(self):
        self.day_boxes = []
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        year = self.current_date.year
        month = self.current_date.month
        first_day_weekday, num_days = calendar.monthrange(year, month)

        month_canvas = tk.Canvas(self.content_frame, bg="white", highlightthickness=0)
        month_canvas.pack(fill=tk.BOTH, expand=True)
        cell_width = 150
        cell_height = 100
        top_margin = 40
        left_margin = 50

        # Шапка дней недели
        for i, d in enumerate(days_of_week):
            x = left_margin + i * cell_width
            y = top_margin
            month_canvas.create_rectangle(x, y, x+cell_width, y+(cell_height*0.5), fill="#e0e0e0", outline="black")
            month_canvas.create_text(x+cell_width/2, y+(cell_height*0.5)/2, text=d, font=("Arial", 10, "bold"))

        start_date = datetime(year, month, 1)
        start_weekday = first_day_weekday
        calendar_start_date = start_date - timedelta(days=start_weekday)

        for week in range(6):
            for wday in range(7):
                day_date = calendar_start_date + timedelta(days=week*7+wday)
                x = left_margin + wday * cell_width
                y = top_margin + cell_height*0.5 + week * cell_height
                month_canvas.create_rectangle(x, y, x+cell_width, y+cell_height, fill="white", outline="black")

                if day_date.month == month:
                    text_color = "black"
                else:
                    text_color = "gray"

                if day_date.date() == datetime.now().date() and day_date.month == month:
                    month_canvas.create_rectangle(x, y, x+cell_width, y+cell_height, fill="#fffacd", outline="black")

                month_canvas.create_text(x+5, y+10, text=str(day_date.day), anchor='nw', fill=text_color, font=("Arial", 10))
                self.day_boxes.append((day_date, x, y, cell_width, cell_height))

    def place_month_events(self):
        if not self.day_boxes:
            return

        min_date = self.day_boxes[0][0].date()
        max_date = self.day_boxes[-1][0].date()
        month_events = [e for e in events if min_date <= e['start_time'].date() <= max_date]
        events_by_day = {}
        for e in month_events:
            d = e['start_time'].date()
            events_by_day.setdefault(d, []).append(e)

        month_canvas = self.content_frame.winfo_children()[0]

        for day_date, x, y, w, h in self.day_boxes:
            day_events = events_by_day.get(day_date.date(), [])
            day_events.sort(key=lambda ev: ev['start_time'])
            displayed_events = day_events[:2]
            extra_count = len(day_events) - 2 if len(day_events) > 2 else 0

            event_y = y + 25
            for ev in displayed_events:
                start_str = ev['start_time'].strftime("%H:%M")
                end_str = ev['end_time'].strftime("%H:%M")
                event_str = f"{start_str}-{end_str} {ev['title']}"
                fill_color = "lightgreen" if ev['status'] == 'planned' else "#d3d3d3"
                rect = month_canvas.create_rectangle(x+5, event_y, x+w-5, event_y+20, fill=fill_color, outline="black")
                txt = month_canvas.create_text(x+10, event_y+10, text=event_str, anchor='w', font=("Arial", 9))

                def on_event_click(e, ev=ev):
                    EventDetailWindow(self, ev)

                month_canvas.tag_bind(rect, "<Button-1>", on_event_click)
                month_canvas.tag_bind(txt, "<Button-1>", on_event_click)
                event_y += 25

            # При клике на ячейку или "ещё..." переходим в дневной вид
            def on_day_click_empty(e, d=day_date):
                self.current_date = datetime(d.year, d.month, d.day)
                self.switch_view("day")

            transparent_rect = month_canvas.create_rectangle(x+1, y+1, x+w-1, y+h-1, outline="", fill="", width=0)
            month_canvas.tag_bind(transparent_rect, "<Button-1>", on_day_click_empty)

            if extra_count > 0:
                more_str = f"ещё {extra_count}..."
                more_txt = month_canvas.create_text(x+10, event_y+10, text=more_str, anchor='w', font=("Arial", 9, "underline"), fill="blue")
                # При клике на "ещё..." также переходим в дневной вид
                month_canvas.tag_bind(more_txt, "<Button-1>", on_day_click_empty)


if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()
