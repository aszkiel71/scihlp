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

# Constants
DATA_FILE = "data.json"


class UserManager:
    """Handles user authentication and profile management"""

    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None
        self.current_user = None
        self.load_data()

    def load_data(self):
        """Load user data from file"""
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
        """Save user data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def login(self, username, password):
        """Authenticate user"""
        for user in self.data["users"]:
            if user["login"] == username and user["password"] == password:
                self.current_user = user
                return True
        return False

    def register(self, username, password, email):
        """Register new user"""
        # Check if username exists
        for user in self.data["users"]:
            if user["login"] == username:
                return False, "Login already exists"

        # Create new user
        new_user = {
            "login": username,
            "password": password,
            "email": email,
            "tasks": []
        }

        self.data["users"].append(new_user)
        self.save_data()
        return True, "Registration successful"

    def update_profile(self, email, password):
        """Update user profile"""
        self.current_user["email"] = email
        self.current_user["password"] = password

        # Update in data
        for i, user in enumerate(self.data["users"]):
            if user["login"] == self.current_user["login"]:
                self.data["users"][i] = self.current_user
                break

        self.save_data()

    def logout(self):
        """Logout current user"""
        self.current_user = None


class Plotter:
    """Handles function plotting functionality"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.plot_frame = None
        self.canvas = None
        self.function_entry = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the plotting UI"""
        frame = tk.Frame(self.parent_frame, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Input for function
        input_frame = tk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="Enter function (e.g., sin(x), x**2):").pack(side=tk.LEFT, padx=5)
        self.function_entry = tk.Entry(input_frame, width=30)
        self.function_entry.pack(side=tk.LEFT, padx=5)

        plot_button = tk.Button(input_frame, text="Plot", command=self.plot_function)
        plot_button.pack(side=tk.LEFT, padx=5)

        # Frame for the plot
        self.plot_frame = tk.Frame(frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Default plot
        self.create_default_plot()

    def create_default_plot(self):
        """Create a default sine wave plot"""
        figure = Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)

        x = np.linspace(-10, 10, 1000)
        y = np.sin(x)

        ax.plot(x, y)
        ax.set_title("Default Plot: sin(x)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)

        self._draw_plot(figure)

    def plot_function(self):
        """Plot the user-entered function"""
        function_str = self.function_entry.get()

        if not function_str:
            messagebox.showerror("Error", "Please enter a function")
            return

        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        try:
            # Create figure
            figure = Figure(figsize=(6, 4), dpi=100)
            ax = figure.add_subplot(111)

            # Generate x values
            x = np.linspace(-10, 10, 1000)

            # Replace common functions with np. prefix
            function_str = function_str.replace("sin", "np.sin")
            function_str = function_str.replace("cos", "np.cos")
            function_str = function_str.replace("tan", "np.tan")
            function_str = function_str.replace("exp", "np.exp")
            function_str = function_str.replace("log", "np.log")
            function_str = function_str.replace("sqrt", "np.sqrt")

            # Evaluate the function
            y = eval(function_str)

            # Plot
            ax.plot(x, y)
            ax.set_title(f"Plot of {self.function_entry.get()}")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True)

            self._draw_plot(figure)

        except Exception as e:
            messagebox.showerror("Error", f"Error plotting function: {str(e)}")

    def _draw_plot(self, figure):
        """Helper method to draw the plot on canvas"""
        self.canvas = FigureCanvasTkAgg(figure, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


class WeatherFetcher:
    """Handles weather data fetching and display"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.weather_data_frame = None
        self.location_entry = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the weather UI"""
        frame = tk.Frame(self.parent_frame, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Input for location
        input_frame = tk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="Enter location:").pack(side=tk.LEFT, padx=5)
        self.location_entry = tk.Entry(input_frame, width=30)
        self.location_entry.pack(side=tk.LEFT, padx=5)

        fetch_button = tk.Button(input_frame, text="Fetch Weather", command=self.fetch_weather)
        fetch_button.pack(side=tk.LEFT, padx=5)

        # Frame for weather data display
        self.weather_data_frame = tk.Frame(frame)
        self.weather_data_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Default message
        tk.Label(self.weather_data_frame, text="Enter a location and click 'Fetch Weather' to see the weather data.",
                 font=("Arial", 12)).pack(pady=20)

    def fetch_weather(self):
        """Fetch and display weather data"""
        location = self.location_entry.get()

        if not location:
            messagebox.showerror("Error", "Please enter a location")
            return

        # Clear previous weather data
        for widget in self.weather_data_frame.winfo_children():
            widget.destroy()

        try:
            # Simulated API call
            data = self._simulate_weather_api_call(location)

            # Display weather data
            self._display_weather_data(data)

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching weather data: {str(e)}")

    def _simulate_weather_api_call(self, location):
        """Simulate weather API response (replace with real API call)"""
        return {
            "main": {
                "temp": 22.5,
                "humidity": 65,
                "pressure": 1012
            },
            "wind": {
                "speed": 5.2
            },
            "weather": [
                {
                    "description": "scattered clouds"
                }
            ],
            "name": location
        }

    def _display_weather_data(self, data):
        """Display weather data in the UI"""
        weather_frame = tk.Frame(self.weather_data_frame)
        weather_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        location_label = tk.Label(weather_frame, text=f"Weather for {data['name']}", font=("Arial", 16, "bold"))
        location_label.pack(pady=10)

        temp_label = tk.Label(weather_frame, text=f"Temperature: {data['main']['temp']}°C", font=("Arial", 12))
        temp_label.pack(pady=5)

        desc_label = tk.Label(weather_frame, text=f"Description: {data['weather'][0]['description']}",
                              font=("Arial", 12))
        desc_label.pack(pady=5)

        humidity_label = tk.Label(weather_frame, text=f"Humidity: {data['main']['humidity']}%", font=("Arial", 12))
        humidity_label.pack(pady=5)

        wind_label = tk.Label(weather_frame, text=f"Wind Speed: {data['wind']['speed']} m/s", font=("Arial", 12))
        wind_label.pack(pady=5)

        pressure_label = tk.Label(weather_frame, text=f"Pressure: {data['main']['pressure']} hPa", font=("Arial", 12))
        pressure_label.pack(pady=5)

        time_label = tk.Label(weather_frame, text=f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                              font=("Arial", 10))
        time_label.pack(pady=5)


class TaskManager:
    """Handles to-do list functionality"""

    def __init__(self, parent_frame, user_manager):
        self.parent_frame = parent_frame
        self.user_manager = user_manager
        self.task_entry = None
        self.tasks_listbox = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the to-do list UI"""
        frame = tk.Frame(self.parent_frame, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Input for new task
        input_frame = tk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="New task:").pack(side=tk.LEFT, padx=5)
        self.task_entry = tk.Entry(input_frame, width=40)
        self.task_entry.pack(side=tk.LEFT, padx=5)

        add_button = tk.Button(input_frame, text="Add Task", command=self.add_task)
        add_button.pack(side=tk.LEFT, padx=5)

        # Frame for tasks
        tasks_frame = tk.Frame(frame)
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create a listbox with scrollbar
        self.tasks_listbox = tk.Listbox(tasks_frame, height=15, width=50)
        self.tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(tasks_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tasks_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tasks_listbox.yview)

        # Buttons for task management
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        mark_done_button = tk.Button(button_frame, text="Mark as Done", command=self.mark_task_done)
        mark_done_button.pack(side=tk.LEFT, padx=5)

        remove_button = tk.Button(button_frame, text="Remove Task", command=self.remove_task)
        remove_button.pack(side=tk.LEFT, padx=5)

        # Populate tasks
        self.populate_tasks()

    def populate_tasks(self):
        """Populate the tasks listbox with current user's tasks"""
        self.tasks_listbox.delete(0, tk.END)
        for task in self.user_manager.current_user["tasks"]:
            self.tasks_listbox.insert(tk.END, task)

    def add_task(self):
        """Add a new task"""
        task = self.task_entry.get()

        if not task:
            messagebox.showerror("Error", "Please enter a task")
            return

        self.user_manager.current_user["tasks"].append(task)
        self.user_manager.save_data()
        self.populate_tasks()
        self.task_entry.delete(0, tk.END)

    def mark_task_done(self):
        """Mark a task as done"""
        selection = self.tasks_listbox.curselection()

        if not selection:
            messagebox.showerror("Error", "Please select a task")
            return

        index = selection[0]
        task = self.user_manager.current_user["tasks"][index]

        if not task.startswith("[DONE] "):
            self.user_manager.current_user["tasks"][index] = f"[DONE] {task}"
            self.user_manager.save_data()
            self.populate_tasks()

    def remove_task(self):
        """Remove a task"""
        selection = self.tasks_listbox.curselection()

        if not selection:
            messagebox.showerror("Error", "Please select a task")
            return

        index = selection[0]

        if messagebox.askyesno("Confirm", "Are you sure you want to remove this task?"):
            del self.user_manager.current_user["tasks"][index]
            self.user_manager.save_data()
            self.populate_tasks()


class ProfileManager:
    """Handles user profile and notifications"""

    def __init__(self, parent_frame, user_manager):
        self.parent_frame = parent_frame
        self.user_manager = user_manager
        self.email_var = None
        self.password_var = None
        self.notification_entry = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the profile UI"""
        frame = tk.Frame(self.parent_frame, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Profile information
        profile_frame = tk.Frame(frame)
        profile_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(profile_frame, text="User Profile", font=("Arial", 16, "bold")).pack(pady=10)

        info_frame = tk.Frame(profile_frame)
        info_frame.pack(fill=tk.X, pady=10)

        # Login
        tk.Label(info_frame, text="Login:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        login_label = tk.Label(info_frame, text=self.user_manager.current_user["login"])
        login_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Email
        tk.Label(info_frame, text="Email:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_var = tk.StringVar(value=self.user_manager.current_user["email"])
        email_entry = tk.Entry(info_frame, textvariable=self.email_var, width=30)
        email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Password
        tk.Label(info_frame, text="Password:", width=15, anchor="e").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.password_var = tk.StringVar(value=self.user_manager.current_user["password"])
        password_entry = tk.Entry(info_frame, textvariable=self.password_var, width=30, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Update button
        update_button = tk.Button(info_frame, text="Update Profile", command=self.update_profile)
        update_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Email notification
        notification_frame = tk.Frame(profile_frame)
        notification_frame.pack(fill=tk.X, pady=20)

        tk.Label(notification_frame, text="Email Notification", font=("Arial", 14, "bold")).pack(pady=10)

        input_frame = tk.Frame(notification_frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="Message:").pack(side=tk.LEFT, padx=5)
        self.notification_entry = tk.Entry(input_frame, width=40)
        self.notification_entry.pack(side=tk.LEFT, padx=5)

        send_button = tk.Button(input_frame, text="Send Notification", command=self.send_notification)
        send_button.pack(side=tk.LEFT, padx=5)

    def update_profile(self):
        """Update user profile information"""
        new_email = self.email_var.get()
        new_password = self.password_var.get()

        if not new_email or not new_password:
            messagebox.showerror("Error", "Email and password cannot be empty")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
            messagebox.showerror("Error", "Invalid email format")
            return

        self.user_manager.current_user["email"] = new_email
        self.user_manager.current_user["password"] = new_password
        self.user_manager.save_data()
        messagebox.showinfo("Success", "Profile updated successfully")

    def send_notification(self):
        """Send email notification"""
        message = self.notification_entry.get()

        if not message:
            messagebox.showerror("Error", "Please enter a message")
            return

        try:
            # In a real app, implement actual email sending
            messagebox.showinfo("Success", f"Notification sent to {self.user_manager.current_user['email']}")
            self.notification_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error sending notification: {str(e)}")


class AuthUI:
    """Handles authentication UI (login and registration)"""

    def __init__(self, root, user_manager, on_login_success):
        self.root = root
        self.user_manager = user_manager
        self.on_login_success = on_login_success
        self.login_entry = None
        self.password_entry = None
        self.reg_login_entry = None
        self.reg_password_entry = None
        self.reg_confirm_entry = None
        self.reg_email_entry = None

    def show_login_screen(self):
        """Show the login screen"""
        self._clear_screen()

        frame = tk.Frame(self.root, padx=20, pady=20)
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

        login_button = tk.Button(button_frame, text="Login", command=self._login, width=10)
        login_button.pack(side=tk.LEFT, padx=5)

        register_button = tk.Button(button_frame, text="Register", command=self.show_register_screen, width=10)
        register_button.pack(side=tk.LEFT, padx=5)

    def show_register_screen(self):
        """Show the registration screen"""
        self._clear_screen()

        frame = tk.Frame(self.root, padx=20, pady=20)
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

        register_button = tk.Button(button_frame, text="Register", command=self._register, width=10)
        register_button.pack(side=tk.LEFT, padx=5)

        back_button = tk.Button(button_frame, text="Back", command=self.show_login_screen, width=10)
        back_button.pack(side=tk.LEFT, padx=5)

    def _login(self):
        """Handle login attempt"""
        username = self.login_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter login and password")
            return

        if self.user_manager.login(username, password):
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Invalid login or password")

    def _register(self):
        """Handle registration attempt"""
        username = self.reg_login_entry.get()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        email = self.reg_email_entry.get()

        if not username or not password or not confirm or not email:
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email format")
            return

        success, message = self.user_manager.register(username, password, email)
        if success:
            messagebox.showinfo("Success", message)
            self.show_login_screen()
        else:
            messagebox.showerror("Error", message)

    def _clear_screen(self):
        """Clear all widgets from the root window"""
        for widget in self.root.winfo_children():
            widget.destroy()


class MainUI:
    """Handles the main application UI after login"""

    def __init__(self, root, user_manager, on_logout):
        self.root = root
        self.user_manager = user_manager
        self.on_logout = on_logout
        self.notebook = None
        self.plotter = None
        self.weather_fetcher = None
        self.task_manager = None
        self.profile_manager = None

    def show_main_screen(self):
        """Show the main application screen with tabs"""
        self._clear_screen()

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        plot_tab = ttk.Frame(self.notebook)
        weather_tab = ttk.Frame(self.notebook)
        todo_tab = ttk.Frame(self.notebook)
        profile_tab = ttk.Frame(self.notebook)

        self.notebook.add(plot_tab, text="Plot Function")
        self.notebook.add(weather_tab, text="Weather")
        self.notebook.add(todo_tab, text="To-Do List")
        self.notebook.add(profile_tab, text="Profile")

        # Initialize tab components
        self.plotter = Plotter(plot_tab)
        self.weather_fetcher = WeatherFetcher(weather_tab)
        self.task_manager = TaskManager(todo_tab, self.user_manager)
        self.profile_manager = ProfileManager(profile_tab, self.user_manager)

        # Logout button
        logout_button = tk.Button(self.root, text="Logout", command=self._logout)
        logout_button.pack(pady=10)

    def _logout(self):
        """Handle logout"""
        self.user_manager.logout()
        self.on_logout()

    def _clear_screen(self):
        """Clear all widgets from the root window"""
        for widget in self.root.winfo_children():
            widget.destroy()


class SciHlp:
    """Main application class"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SciHlp - Data Analysis & Organization Tool")
        self.root.geometry("900x600")
        self.root.minsize(800, 600)

        # Initialize user manager
        self.user_manager = UserManager(DATA_FILE)

        # Initialize UI components
        self.auth_ui = AuthUI(self.root, self.user_manager, self._on_login_success)
        self.main_ui = MainUI(self.root, self.user_manager, self._on_logout)

        # Start with login screen
        self.auth_ui.show_login_screen()

        self.root.mainloop()

    def _on_login_success(self):
        """Callback for successful login"""
        self.main_ui.show_main_screen()

    def _on_logout(self):
        """Callback for logout"""
        self.auth_ui.show_login_screen()


if __name__ == "__main__":
    app = SciHlp()
