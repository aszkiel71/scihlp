import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import requests
import smtplib
from email.mime.text import MIMEText
import re
from datetime import datetime

DATA_FILE = "data.json"



class UserModel:


    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None
        self.current_user = None
        self.load_data()

    def load_data(self):

        if not os.path.exists(self.data_file):
            self.data = {
                "users": [
                    {
                        "login": "admin",
                        "password": "admin",
                        "email": "admin@admin.com",
                        "tasks": ["Task 1", "Task 2"]
                    }
                ]
            }
            self.save_data()
        else:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)

    def save_data(self):

        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def authenticate_user(self, username, password):

        for user in self.data["users"]:
            if user["login"] == username and user["password"] == password:
                self.current_user = user
                return True
        return False

    def register_new_user(self, username, password, email):
        """Rejestruje nowego usera"""

        for user in self.data["users"]:
            if user["login"] == username:
                return False, "Login already exists"


        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email format"


        new_user = {
            "login": username,
            "password": password,
            "email": email,
            "tasks": []
        }

        self.data["users"].append(new_user)
        self.save_data()
        return True, "Registration successful"

    def update_current_user_profile(self, email, password):

        if not self.current_user:
            return False, "No user logged in"

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email format"

        self.current_user["email"] = email
        self.current_user["password"] = password


        for i, user in enumerate(self.data["users"]):
            if user["login"] == self.current_user["login"]:
                self.data["users"][i] = self.current_user
                break

        self.save_data()
        return True, "Profile updated successfully"

    def logout_user(self):

        self.current_user = None

    def get_current_user_data(self):

        return self.current_user


class TaskModel:


    def __init__(self, user_model):
        self.user_model = user_model

    def add_new_task(self, task_text):

        if not self.user_model.current_user:
            return False

        if not task_text.strip():
            return False

        self.user_model.current_user["tasks"].append(task_text)
        self.user_model.save_data()
        return True

    def get_all_tasks(self):

        if not self.user_model.current_user:
            return []
        return self.user_model.current_user["tasks"]

    def mark_task_as_done(self, task_index):

        if not self.user_model.current_user:
            return False

        tasks = self.user_model.current_user["tasks"]
        if 0 <= task_index < len(tasks):
            task = tasks[task_index]
            if not task.startswith("[DONE] "):
                tasks[task_index] = f"[DONE] {task}"
                self.user_model.save_data()
                return True
        return False

    def remove_task_by_index(self, task_index):

        if not self.user_model.current_user:
            return False

        tasks = self.user_model.current_user["tasks"]
        if 0 <= task_index < len(tasks):
            del tasks[task_index]
            self.user_model.save_data()
            return True
        return False


class PlotModel:
    """Model odpowiedzialny za logikę rysowania wykresów"""

    def __init__(self):
        self.x_min = -10
        self.x_max = 10
        self.num_points = 1000

    def generate_function_data(self, function_string):
        """Generuje dane dla podanej funkcji"""
        if not function_string.strip():
            return None, None, "Empty function"

        try:

            x = np.linspace(self.x_min, self.x_max, self.num_points)


            safe_function = self.prepare_safe_function(function_string)


            y = eval(safe_function)

            return x, y, None
        except Exception as e:
            return None, None, str(e)

    def prepare_safe_function(self, function_str):
        safe_function = function_str
        safe_function = safe_function.replace("sin", "np.sin")
        safe_function = safe_function.replace("cos", "np.cos")
        safe_function = safe_function.replace("tan", "np.tan")
        safe_function = safe_function.replace("exp", "np.exp")
        safe_function = safe_function.replace("log", "np.log")
        safe_function = safe_function.replace("sqrt", "np.sqrt")
        return safe_function

    def get_default_data(self):
        x = np.linspace(self.x_min, self.x_max, self.num_points)
        y = np.sin(x)
        return x, y


class WeatherModel:


    def __init__(self):
        self.api_key = None  # place holder

    def fetch_weather_for_location(self, location):

        if not location.strip():
            return None

        try:
            return self.simulate_weather_response(location)
        except Exception:
            return None

    def simulate_weather_response(self, location):

        import random

        return {
            "main": {
                "temp": round(random.uniform(15, 30), 1),
                "humidity": random.randint(40, 90),
                "pressure": random.randint(1000, 1020)
            },
            "wind": {
                "speed": round(random.uniform(0, 15), 1)
            },
            "weather": [
                {
                    "description": random.choice([
                        "clear sky", "few clouds", "scattered clouds",
                        "broken clouds", "shower rain", "rain"
                    ])
                }
            ],
            "name": location
        }


class NotificationModel:


    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email_notification(self, email, message):

        if not email or not message:
            return False, "Email and message cannot be empty"

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email format"

        try:

            print(f"[SIMULATED] Email sent to {email}: {message}")
            return True, f"Notification sent to {email}"
        except Exception as e:
            return False, f"Error sending notification: {str(e)}"



class AuthView:

    def __init__(self, parent):
        self.parent = parent
        self.controller = None

        # Pola logowania
        self.login_entry = None
        self.password_entry = None

        # Pola rejestracji
        self.reg_login_entry = None
        self.reg_password_entry = None
        self.reg_confirm_entry = None
        self.reg_email_entry = None

    def set_controller(self, controller):

        self.controller = controller

    def show_login_screen(self):

        self.clear_parent()

        frame = tk.Frame(self.parent, padx=20, pady=20)
        frame.pack(expand=True)

        title = tk.Label(frame, text="SciHlp", font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(frame, text="Login:").grid(row=1, column=0, sticky="e", pady=5)
        self.login_entry = tk.Entry(frame, width=30)
        self.login_entry.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        self.password_entry = tk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky="w", pady=5)

        button_frame = tk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        login_button = tk.Button(button_frame, text="Login", command=self.handle_login_click, width=10)
        login_button.pack(side=tk.LEFT, padx=5)

        register_button = tk.Button(button_frame, text="Register", command=self.handle_register_click, width=10)
        register_button.pack(side=tk.LEFT, padx=5)

    def show_register_screen(self):

        self.clear_parent()

        frame = tk.Frame(self.parent, padx=20, pady=20)
        frame.pack(expand=True)

        title = tk.Label(frame, text="Registration", font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(frame, text="Login:").grid(row=1, column=0, sticky="e", pady=5)
        self.reg_login_entry = tk.Entry(frame, width=30)
        self.reg_login_entry.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        self.reg_password_entry = tk.Entry(frame, width=30, show="*")
        self.reg_password_entry.grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Confirm Password:").grid(row=3, column=0, sticky="e", pady=5)
        self.reg_confirm_entry = tk.Entry(frame, width=30, show="*")
        self.reg_confirm_entry.grid(row=3, column=1, sticky="w", pady=5)

        tk.Label(frame, text="Email:").grid(row=4, column=0, sticky="e", pady=5)
        self.reg_email_entry = tk.Entry(frame, width=30)
        self.reg_email_entry.grid(row=4, column=1, sticky="w", pady=5)

        button_frame = tk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        register_button = tk.Button(button_frame, text="Register", command=self.handle_register_submit, width=10)
        register_button.pack(side=tk.LEFT, padx=5)

        back_button = tk.Button(button_frame, text="Back", command=self.handle_back_click, width=10)
        back_button.pack(side=tk.LEFT, padx=5)

    def get_login_data(self):

        return self.login_entry.get(), self.password_entry.get()

    def get_register_data(self):

        return (
            self.reg_login_entry.get(),
            self.reg_password_entry.get(),
            self.reg_confirm_entry.get(),
            self.reg_email_entry.get()
        )

    def clear_parent(self):

        for widget in self.parent.winfo_children():
            widget.destroy()

    def handle_login_click(self):

        if self.controller:
            self.controller.process_login()

    def handle_register_click(self):

        if self.controller:
            self.controller.show_register_form()

    def handle_register_submit(self):

        if self.controller:
            self.controller.process_registration()

    def handle_back_click(self):

        if self.controller:
            self.controller.show_login_form()


class PlotView:
    """odpowiedzialny za interfejs rysowania wykresów"""

    def __init__(self, parent):
        self.parent = parent
        self.controller = None
        self.function_entry = None
        self.plot_frame = None
        self.canvas = None
        self.setup_ui()

    def set_controller(self, controller):

        self.controller = controller

    def setup_ui(self):

        frame = tk.Frame(self.parent, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)


        input_frame = tk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="Enter function (e.g., sin(x), x**2):").pack(side=tk.LEFT, padx=5)
        self.function_entry = tk.Entry(input_frame, width=30)
        self.function_entry.pack(side=tk.LEFT, padx=5)

        plot_button = tk.Button(input_frame, text="Plot", command=self.handle_plot_click)
        plot_button.pack(side=tk.LEFT, padx=5)


        self.plot_frame = tk.Frame(frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def get_function_input(self):

        return self.function_entry.get()

    def display_plot(self, x_data, y_data, title):

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        figure = Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)

        ax.plot(x_data, y_data)
        ax.set_title(title)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)

        self.canvas = FigureCanvasTkAgg(figure, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def handle_plot_click(self):

        if self.controller:
            self.controller.create_plot()


class WeatherView:


    def __init__(self, parent):
        self.parent = parent
        self.controller = None
        self.location_entry = None
        self.weather_data_frame = None
        self.setup_ui()

    def set_controller(self, controller):

        self.controller = controller

    def setup_ui(self):

        frame = tk.Frame(self.parent, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)


        input_frame = tk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="Enter location:").pack(side=tk.LEFT, padx=5)
        self.location_entry = tk.Entry(input_frame, width=30)
        self.location_entry.pack(side=tk.LEFT, padx=5)

        fetch_button = tk.Button(input_frame, text="Fetch Weather", command=self.handle_fetch_click)
        fetch_button.pack(side=tk.LEFT, padx=5)


        self.weather_data_frame = tk.Frame(frame)
        self.weather_data_frame.pack(fill=tk.BOTH, expand=True, pady=10)


        tk.Label(self.weather_data_frame, text="Enter a location and click 'Fetch Weather' to see the weather data.",
                 font=("Arial", 12)).pack(pady=20)

    def get_location_input(self):
        """Pobiera wprowadzona lokalizacje"""
        return self.location_entry.get()

    def display_weather_data(self, weather_data):
        for widget in self.weather_data_frame.winfo_children():
            widget.destroy()

        weather_frame = tk.Frame(self.weather_data_frame)
        weather_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        location_label = tk.Label(weather_frame, text=f"Weather for {weather_data['name']}",
                                  font=("Arial", 16, "bold"))
        location_label.pack(pady=10)

        temp_label = tk.Label(weather_frame, text=f"Temperature: {weather_data['main']['temp']}°C",
                              font=("Arial", 12))
        temp_label.pack(pady=5)

        desc_label = tk.Label(weather_frame, text=f"Description: {weather_data['weather'][0]['description']}",
                              font=("Arial", 12))
        desc_label.pack(pady=5)

        humidity_label = tk.Label(weather_frame, text=f"Humidity: {weather_data['main']['humidity']}%",
                                  font=("Arial", 12))
        humidity_label.pack(pady=5)

        wind_label = tk.Label(weather_frame, text=f"Wind Speed: {weather_data['wind']['speed']} m/s",
                              font=("Arial", 12))
        wind_label.pack(pady=5)

        pressure_label = tk.Label(weather_frame, text=f"Pressure: {weather_data['main']['pressure']} hPa",
                                  font=("Arial", 12))
        pressure_label.pack(pady=5)

        time_label = tk.Label(weather_frame, text=f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                              font=("Arial", 10))
        time_label.pack(pady=5)

    def handle_fetch_click(self):

        if self.controller:
            self.controller.fetch_weather_data()


class TaskView:


    def __init__(self, parent):
        self.parent = parent
        self.controller = None
        self.task_entry = None
        self.tasks_listbox = None
        self.setup_ui()

    def set_controller(self, controller):

        self.controller = controller

    def setup_ui(self):

        frame = tk.Frame(self.parent, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)


        input_frame = tk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="New task:").pack(side=tk.LEFT, padx=5)
        self.task_entry = tk.Entry(input_frame, width=40)
        self.task_entry.pack(side=tk.LEFT, padx=5)

        add_button = tk.Button(input_frame, text="Add Task", command=self.handle_add_click)
        add_button.pack(side=tk.LEFT, padx=5)


        tasks_frame = tk.Frame(frame)
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # todolista paskiem przewijania
        self.tasks_listbox = tk.Listbox(tasks_frame, height=15, width=50)
        self.tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(tasks_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tasks_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tasks_listbox.yview)


        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        mark_done_button = tk.Button(button_frame, text="Mark as Done", command=self.handle_mark_done_click)
        mark_done_button.pack(side=tk.LEFT, padx=5)

        remove_button = tk.Button(button_frame, text="Remove Task", command=self.handle_remove_click)
        remove_button.pack(side=tk.LEFT, padx=5)

    def get_task_input(self):

        return self.task_entry.get()

    def clear_task_input(self):

        self.task_entry.delete(0, tk.END)

    def get_selected_task_index(self):

        selection = self.tasks_listbox.curselection()
        return selection[0] if selection else None

    def update_tasks_display(self, tasks):

        self.tasks_listbox.delete(0, tk.END)
        for task in tasks:
            self.tasks_listbox.insert(tk.END, task)

    def handle_add_click(self):

        if self.controller:
            self.controller.add_task()

    def handle_mark_done_click(self):

        if self.controller:
            self.controller.mark_task_done()

    def handle_remove_click(self):

        if self.controller:
            self.controller.remove_task()


class ProfileView:
    """Widok odpowiedzialny za interfejs profilu użytkownika"""

    def __init__(self, parent):
        self.parent = parent
        self.controller = None
        self.email_var = None
        self.password_var = None
        self.notification_entry = None
        self.login_label = None
        self.setup_ui()

    def set_controller(self, controller):
        self.controller = controller

    def setup_ui(self):
        """Konfiguruje interfejs użytkownika"""
        frame = tk.Frame(self.parent, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Informacje o profilu
        profile_frame = tk.Frame(frame)
        profile_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(profile_frame, text="User Profile", font=("Arial", 16, "bold")).pack(pady=10)

        info_frame = tk.Frame(profile_frame)
        info_frame.pack(fill=tk.X, pady=10)

        # Zmienne dla formularza
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Login
        tk.Label(info_frame, text="Login:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.login_label = tk.Label(info_frame, text="")
        self.login_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Email
        tk.Label(info_frame, text="Email:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        email_entry = tk.Entry(info_frame, textvariable=self.email_var, width=30)
        email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Haslo
        tk.Label(info_frame, text="Password:", width=15, anchor="e").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        password_entry = tk.Entry(info_frame, textvariable=self.password_var, width=30, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Przycisk aktualizacji
        update_button = tk.Button(info_frame, text="Update Profile", command=self.handle_update_click)
        update_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Powiadomienia email
        notification_frame = tk.Frame(profile_frame)
        notification_frame.pack(fill=tk.X, pady=20)

        tk.Label(notification_frame, text="Email Notification", font=("Arial", 14, "bold")).pack(pady=10)

        input_frame = tk.Frame(notification_frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="Message:").pack(side=tk.LEFT, padx=5)
        self.notification_entry = tk.Entry(input_frame, width=40)
        self.notification_entry.pack(side=tk.LEFT, padx=5)

        send_button = tk.Button(input_frame, text="Send Notification", command=self.handle_send_click)
        send_button.pack(side=tk.LEFT, padx=5)

    def set_user_data(self, login, email, password):

        self.login_label.config(text=login)
        self.email_var.set(email)
        self.password_var.set(password)

    def get_profile_data(self):

        return self.email_var.get(), self.password_var.get()

    def get_notification_message(self):

        return self.notification_entry.get()

    def clear_notification_input(self):

        self.notification_entry.delete(0, tk.END)

    def handle_update_click(self):

        if self.controller:
            self.controller.update_profile()

    def handle_send_click(self):

        if self.controller:
            self.controller.send_notification()


class MainView:


    def __init__(self, parent):
        self.parent = parent
        self.controller = None
        self.notebook = None

        # Sub-widoki
        self.plot_view = None
        self.weather_view = None
        self.task_view = None
        self.profile_view = None

    def set_controller(self, controller):

        self.controller = controller

    def setup_main_interface(self):

        self.clear_parent()

        # Tworzenie notebook dla zakładek
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        plot_tab = ttk.Frame(self.notebook)
        weather_tab = ttk.Frame(self.notebook)
        todo_tab = ttk.Frame(self.notebook)
        profile_tab = ttk.Frame(self.notebook)

        self.notebook.add(plot_tab, text="Plot Function")
        self.notebook.add(weather_tab, text="Weather")
        self.notebook.add(todo_tab, text="To-Do List")
        self.notebook.add(profile_tab, text="Profile")


        self.plot_view = PlotView(plot_tab)
        self.weather_view = WeatherView(weather_tab)
        self.task_view = TaskView(todo_tab)
        self.profile_view = ProfileView(profile_tab)


        logout_button = tk.Button(self.parent, text="Logout", command=self.handle_logout_click)
        logout_button.pack(pady=10)

    def clear_parent(self):

        for widget in self.parent.winfo_children():
            widget.destroy()

    def handle_logout_click(self):

        if self.controller:
            self.controller.logout_user()




class AuthController:

    def __init__(self, user_model, auth_view):
        self.user_model = user_model
        self.auth_view = auth_view
        self.main_controller = None


        self.auth_view.set_controller(self)

    def set_main_controller(self, main_controller):
        self.main_controller = main_controller

    def process_login(self):
        username, password = self.auth_view.get_login_data()

        if not username or not password:
            messagebox.showerror("Error", "Please enter login and password")
            return

        if self.user_model.authenticate_user(username, password):
            if self.main_controller:
                self.main_controller.show_main_application()
        else:
            messagebox.showerror("Error", "Invalid login or password")

    def process_registration(self):
        username, password, confirm, email = self.auth_view.get_register_data()

        if not username or not password or not confirm or not email:
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        success, message = self.user_model.register_new_user(username, password, email)
        if success:
            messagebox.showinfo("Success", message)
            self.show_login_form()
        else:
            messagebox.showerror("Error", message)

    def show_login_form(self):
        self.auth_view.show_login_screen()

    def show_register_form(self):
        self.auth_view.show_register_screen()


class PlotController:

    def __init__(self, plot_model, plot_view):
        self.plot_model = plot_model
        self.plot_view = plot_view

        self.plot_view.set_controller(self)

        # pokaz domyslny wykres
        self.show_default_plot()

    def show_default_plot(self):
        x, y = self.plot_model.get_default_data()
        self.plot_view.display_plot(x, y, "Default Plot: sin(x)")

    def create_plot(self):
        function_str = self.plot_view.get_function_input()

        if not function_str:
            messagebox.showerror("Error", "Please enter a function")
            return

        x, y, error = self.plot_model.generate_function_data(function_str)

        if error:
            messagebox.showerror("Error", f"Error plotting function: {error}")
            return

        title = f"Plot of {function_str}"
        self.plot_view.display_plot(x, y, title)


class WeatherController:

    def __init__(self, weather_model, weather_view):
        self.weather_model = weather_model
        self.weather_view = weather_view


        self.weather_view.set_controller(self)

    def fetch_weather_data(self):
        """Pobiera dane pogodowe"""
        location = self.weather_view.get_location_input()

        if not location:
            messagebox.showerror("Error", "Please enter a location")
            return

        weather_data = self.weather_model.fetch_weather_for_location(location)

        if weather_data:
            self.weather_view.display_weather_data(weather_data)
        else:
            messagebox.showerror("Error", "Error fetching weather data")


class TaskController:

    def __init__(self, task_model, task_view):
        self.task_model = task_model
        self.task_view = task_view


        self.task_view.set_controller(self)


        self.refresh_tasks_display()

    def refresh_tasks_display(self):
        tasks = self.task_model.get_all_tasks()
        self.task_view.update_tasks_display(tasks)

    def add_task(self):
        task = self.task_view.get_task_input()

        if not task:
            messagebox.showerror("Error", "Please enter a task")
            return

        if self.task_model.add_new_task(task):
            self.task_view.clear_task_input()
            self.refresh_tasks_display()
        else:
            messagebox.showerror("Error", "Failed to add task")

    def mark_task_done(self):
        index = self.task_view.get_selected_task_index()

        if index is None:
            messagebox.showerror("Error", "Please select a task")
            return

        if self.task_model.mark_task_as_done(index):
            self.refresh_tasks_display()
        else:
            messagebox.showerror("Error", "Failed to mark task as done")

    def remove_task(self):
        index = self.task_view.get_selected_task_index()

        if index is None:
            messagebox.showerror("Error", "Please select a task")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove this task?"):
            if self.task_model.remove_task_by_index(index):
                self.refresh_tasks_display()
            else:
                messagebox.showerror("Error", "Failed to remove task")


class ProfileController:

    def __init__(self, user_model, notification_model, profile_view):
        self.user_model = user_model
        self.notification_model = notification_model
        self.profile_view = profile_view


        self.profile_view.set_controller(self)


        self.refresh_profile_data()

    def refresh_profile_data(self):
        user = self.user_model.get_current_user_data()
        if user:
            self.profile_view.set_user_data(user["login"], user["email"], user["password"])

    def update_profile(self):
        email, password = self.profile_view.get_profile_data()

        if not email or not password:
            messagebox.showerror("Error", "Email and password cannot be empty")
            return

        success, message = self.user_model.update_current_user_profile(email, password)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def send_notification(self):
        message = self.profile_view.get_notification_message()
        user = self.user_model.get_current_user_data()

        if not message:
            messagebox.showerror("Error", "Please enter a message")
            return

        if not user:
            messagebox.showerror("Error", "No user logged in")
            return

        success, result_message = self.notification_model.send_email_notification(user["email"], message)

        if success:
            messagebox.showinfo("Success", result_message)
            self.profile_view.clear_notification_input()
        else:
            messagebox.showerror("Error", result_message)


class MainController:
    """Glowny kontroler aplikacji"""

    def __init__(self, root):
        self.root = root

        # Inicjalizacja modeli itp...


        self.user_model = UserModel(DATA_FILE)
        self.task_model = TaskModel(self.user_model)
        self.weather_model = WeatherModel()
        self.plot_model = PlotModel()
        self.notification_model = NotificationModel()


        self.auth_view = AuthView(self.root)
        self.main_view = MainView(self.root)


        self.auth_controller = AuthController(self.user_model, self.auth_view)
        self.auth_controller.set_main_controller(self)

        # Sub-kontrolery (beda inicjalizowane w dalszej czesci kodu)
        self.plot_controller = None
        self.weather_controller = None
        self.task_controller = None
        self.profile_controller = None


        self.main_view.set_controller(self)

        # rozpocznij od ekranu logowania
        self.auth_controller.show_login_form()

    def show_main_application(self):
        self.main_view.setup_main_interface()

        # Inicjalizacja sub-kontrolerów
        self.plot_controller = PlotController(self.plot_model, self.main_view.plot_view)
        self.weather_controller = WeatherController(self.weather_model, self.main_view.weather_view)
        self.task_controller = TaskController(self.task_model, self.main_view.task_view)
        self.profile_controller = ProfileController(self.user_model, self.notification_model,
                                                    self.main_view.profile_view)

    def logout_user(self):
        """Wylogowuje użytkownika"""
        self.user_model.logout_user()
        self.auth_controller.show_login_form()



class SciHlpApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SciHlp")
        self.root.geometry("900x600")
        self.root.minsize(800, 600)

        self.main_controller = MainController(self.root)

    def run(self):
        self.root.mainloop()




if __name__ == "__main__":

    app = SciHlpApp()
    app.run()