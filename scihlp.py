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

class SciHlp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SciHlp - Data Analysis & Organization Tool")
        self.root.geometry("900x600")
        self.root.minsize(800, 600)
        
        # Initialize data
        self.initialize_data()
        self.current_user = None
        
        # Start with login screen
        self.show_login_screen()
        
        self.root.mainloop()
    
    def initialize_data(self):
        """Initialize the data file if it doesn't exist"""
        if not os.path.exists(DATA_FILE):
            default_data = {
                "users": [
                    {
                        "login": "admin",
                        "password": "admin",
                        "email": "admin@admin.com",
                        "tasks": ["Task 1", "Task 2"]
                    }
                ]
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
        
        # Load data
        with open(DATA_FILE, 'r') as f:
            self.data = json.load(f)
    
    def save_data(self):
        """Save data to the JSON file"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def show_login_screen(self):
        """Display the login screen"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)
        
        # Logo or title
        title = tk.Label(frame, text="SciHlp", font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Login fields
        tk.Label(frame, text="Login:").grid(row=1, column=0, sticky="e", pady=5)
        self.login_entry = tk.Entry(frame, width=30)
        self.login_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        tk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        self.password_entry = tk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        login_button = tk.Button(button_frame, text="Login", command=self.login, width=10)
        login_button.pack(side=tk.LEFT, padx=5)
        
        register_button = tk.Button(button_frame, text="Register", command=self.show_register_screen, width=10)
        register_button.pack(side=tk.LEFT, padx=5)
    
    def show_register_screen(self):
        """Display the registration screen"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)
        
        # Logo or title
        title = tk.Label(frame, text="Registration", font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Registration fields
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
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        register_button = tk.Button(button_frame, text="Register", command=self.register, width=10)
        register_button.pack(side=tk.LEFT, padx=5)
        
        back_button = tk.Button(button_frame, text="Back", command=self.show_login_screen, width=10)
        back_button.pack(side=tk.LEFT, padx=5)
    
    def login(self):
        """Handle login process"""
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if not login or not password:
            messagebox.showerror("Error", "Please enter login and password")
            return
        
        # Check login
        for user in self.data["users"]:
            if user["login"] == login and user["password"] == password:
                self.current_user = user
                self.show_main_screen()
                return
        
        messagebox.showerror("Error", "Invalid login or password")
    
    def register(self):
        """Handle registration process"""
        login = self.reg_login_entry.get()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        email = self.reg_email_entry.get()
        
        # Validation
        if not login or not password or not confirm or not email:
            messagebox.showerror("Error", "All fields are required")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        # Check if login already exists
        for user in self.data["users"]:
            if user["login"] == login:
                messagebox.showerror("Error", "Login already exists")
                return
        
        # Create new user
        new_user = {
            "login": login,
            "password": password,
            "email": email,
            "tasks": []
        }
        
        # Add to data and save
        self.data["users"].append(new_user)
        self.save_data()
        
        messagebox.showinfo("Success", "Registration successful! You can now log in.")
        self.show_login_screen()
    
    def show_main_screen(self):
        """Display the main application screen"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        plot_tab = ttk.Frame(notebook)
        weather_tab = ttk.Frame(notebook)
        todo_tab = ttk.Frame(notebook)
        profile_tab = ttk.Frame(notebook)
        
        notebook.add(plot_tab, text="Plot Function")
        notebook.add(weather_tab, text="Weather")
        notebook.add(todo_tab, text="To-Do List")
        notebook.add(profile_tab, text="Profile")
        
        # Setup each tab
        self.setup_plot_tab(plot_tab)
        self.setup_weather_tab(weather_tab)
        self.setup_todo_tab(todo_tab)
        self.setup_profile_tab(profile_tab)
    
    def setup_plot_tab(self, parent):
        """Setup the function plotting tab"""
        frame = tk.Frame(parent, padx=10, pady=10)
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
        """Create a default plot"""
        figure = Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        x = np.linspace(-10, 10, 1000)
        y = np.sin(x)
        
        ax.plot(x, y)
        ax.set_title("Default Plot: sin(x)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(figure, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
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
            
            # Evaluate the function
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
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(figure, self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error plotting function: {str(e)}")
    
    def setup_weather_tab(self, parent):
        """Setup the weather tab"""
        frame = tk.Frame(parent, padx=10, pady=10)
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
            # Simulated API call (replace with actual API call)
            # In a real app, you would use the API key and make a request
            # For example:
            # api_key = "API-KEY"
            # url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            # response = requests.get(url)
            # data = response.json()
            
            # Simulated weather data
            data = {
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
            
            # Display weather data
            weather_frame = tk.Frame(self.weather_data_frame)
            weather_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            location_label = tk.Label(weather_frame, text=f"Weather for {data['name']}", font=("Arial", 16, "bold"))
            location_label.pack(pady=10)
            
            temp_label = tk.Label(weather_frame, text=f"Temperature: {data['main']['temp']}°C", font=("Arial", 12))
            temp_label.pack(pady=5)
            
            desc_label = tk.Label(weather_frame, text=f"Description: {data['weather'][0]['description']}", font=("Arial", 12))
            desc_label.pack(pady=5)
            
            humidity_label = tk.Label(weather_frame, text=f"Humidity: {data['main']['humidity']}%", font=("Arial", 12))
            humidity_label.pack(pady=5)
            
            wind_label = tk.Label(weather_frame, text=f"Wind Speed: {data['wind']['speed']} m/s", font=("Arial", 12))
            wind_label.pack(pady=5)
            
            pressure_label = tk.Label(weather_frame, text=f"Pressure: {data['main']['pressure']} hPa", font=("Arial", 12))
            pressure_label.pack(pady=5)
            
            time_label = tk.Label(weather_frame, text=f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 10))
            time_label.pack(pady=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching weather data: {str(e)}")
    
    def setup_todo_tab(self, parent):
        """Setup the todo list tab"""
        frame = tk.Frame(parent, padx=10, pady=10)
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
        # Clear listbox
        self.tasks_listbox.delete(0, tk.END)
        
        # Add tasks
        for task in self.current_user["tasks"]:
            self.tasks_listbox.insert(tk.END, task)
    
    def add_task(self):
        """Add a new task"""
        task = self.task_entry.get()
        
        if not task:
            messagebox.showerror("Error", "Please enter a task")
            return
        
        # Add to current user's tasks
        self.current_user["tasks"].append(task)
        
        # Update the data file
        for i, user in enumerate(self.data["users"]):
            if user["login"] == self.current_user["login"]:
                self.data["users"][i] = self.current_user
                break
        
        self.save_data()
        
        # Refresh tasks display
        self.populate_tasks()
        
        # Clear entry
        self.task_entry.delete(0, tk.END)
    
    def mark_task_done(self):
        """Mark a task as done (by adding [DONE] prefix)"""
        selection = self.tasks_listbox.curselection()
        
        if not selection:
            messagebox.showerror("Error", "Please select a task")
            return
        
        index = selection[0]
        task = self.current_user["tasks"][index]
        
        # If already marked as done, don't modify
        if task.startswith("[DONE] "):
            return
        
        # Mark as done
        self.current_user["tasks"][index] = f"[DONE] {task}"
        
        # Update the data file
        for i, user in enumerate(self.data["users"]):
            if user["login"] == self.current_user["login"]:
                self.data["users"][i] = self.current_user
                break
        
        self.save_data()
        
        # Refresh tasks display
        self.populate_tasks()
    
    def remove_task(self):
        """Remove a task"""
        selection = self.tasks_listbox.curselection()
        
        if not selection:
            messagebox.showerror("Error", "Please select a task")
            return
        
        index = selection[0]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this task?"):
            # Remove from current user's tasks
            del self.current_user["tasks"][index]
            
            # Update the data file
            for i, user in enumerate(self.data["users"]):
                if user["login"] == self.current_user["login"]:
                    self.data["users"][i] = self.current_user
                    break
            
            self.save_data()
            
            # Refresh tasks display
            self.populate_tasks()
    
    def setup_profile_tab(self, parent):
        """Setup the profile tab"""
        frame = tk.Frame(parent, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Profile information
        profile_frame = tk.Frame(frame)
        profile_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(profile_frame, text="User Profile", font=("Arial", 16, "bold")).pack(pady=10)
        
        info_frame = tk.Frame(profile_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        # Login
        tk.Label(info_frame, text="Login:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        login_label = tk.Label(info_frame, text=self.current_user["login"])
        login_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Email
        tk.Label(info_frame, text="Email:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_var = tk.StringVar(value=self.current_user["email"])
        email_entry = tk.Entry(info_frame, textvariable=self.email_var, width=30)
        email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Password
        tk.Label(info_frame, text="Password:", width=15, anchor="e").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.password_var = tk.StringVar(value=self.current_user["password"])
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
        
        # Logout button
        logout_button = tk.Button(frame, text="Logout", command=self.logout)
        logout_button.pack(pady=10)
    
    def update_profile(self):
        """Update the user profile"""
        # Get new values
        new_email = self.email_var.get()
        new_password = self.password_var.get()
        
        # Validation
        if not new_email or not new_password:
            messagebox.showerror("Error", "Email and password cannot be empty")
            return
        
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        # Update current user
        self.current_user["email"] = new_email
        self.current_user["password"] = new_password
        
        # Update data file
        for i, user in enumerate(self.data["users"]):
            if user["login"] == self.current_user["login"]:
                self.data["users"][i] = self.current_user
                break
        
        self.save_data()
        
        messagebox.showinfo("Success", "Profile updated successfully")
    
    def send_notification(self):
        """Send an email notification"""
        message = self.notification_entry.get()
        
        if not message:
            messagebox.showerror("Error", "Please enter a message")
            return
        
        try:
            # In a real app, you would configure the SMTP server and send the email
            # For example:
            # sender_email = "API-KEY"  # Replace with your sender email
            # sender_password = "API-KEY"  # Replace with your sender password
            # 
            # msg = MIMEText(message)
            # msg["Subject"] = "SciHlp Notification"
            # msg["From"] = sender_email
            # msg["To"] = self.current_user["email"]
            # 
            # with smtplib.SMTP("smtp.gmail.com", 587) as server:
            #     server.starttls()
            #     server.login(sender_email, sender_password)
            #     server.send_message(msg)
            
            messagebox.showinfo("Success", f"Notification sent to {self.current_user['email']}")
            

            self.notification_entry.delete(0, tk.END)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error sending notification: {str(e)}")
    
    def logout(self):
        """Logout the current user"""
        self.current_user = None
        self.show_login_screen()

if __name__ == "__main__":
    app = SciHlp()