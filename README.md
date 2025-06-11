# SciHlp - Data Analysis & Organization Tool

SciHlp is a desktop application that integrates several useful functionalities for data analysis and organization. The application provides a user-friendly interface for visualizing mathematical functions, fetching weather data, managing a to-do list, and handling user profiles with email notifications.

## Features

- **User Authentication**: Secure login and registration system
- **Function Plotting**: Visualize mathematical functions using matplotlib
- **Weather Data**: Fetch and display current weather data for any location
- **Todo List**: Add, mark as done, and remove tasks specific to your user account
- **User Profile**: Manage your login credentials and email preferences
- **Email Notifications**: Send reminders to your registered email

## Installation

1. Clone this repository or download the files
2. Make sure you have Python 3.7+ installed
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application by executing the main script:

```bash
python scihlp.py
```

### Initial Login

The application comes with a default admin account:
- Login: admin
- Password: admin
- Email: admin@admin.com

You can register a new account by clicking the "Register" button on the login screen.

### Function Plotting

1. Go to the "Plot Function" tab
2. Enter a mathematical function (e.g., sin(x), x**2, cos(x) + sin(x), etc.)
3. Click the "Plot" button to visualize the function

### Weather Data

1. Go to the "Weather" tab
2. Enter a location (e.g., city name)
3. Click "Fetch Weather" to get the current weather data

Note: This feature uses a placeholder for the actual API call. In a real-world scenario, you would need to replace "API-KEY" with your actual API key.

### Todo List

1. Go to the "To-Do List" tab
2. Enter a task in the input field
3. Click "Add Task" to add it to your list
4. Select a task and click "Mark as Done" to mark it as complete
5. Select a task and click "Remove Task" to delete it

### User Profile

1. Go to the "Profile" tab
2. Update your email and password
3. Click "Update Profile" to save changes
4. Use the email notification feature to send yourself reminders

## Customization

- **Weather API**: Replace the "API-KEY" placeholder in the code with your actual API key
- **Email Notifications**: Configure the SMTP settings with your actual email service provider details

## Data Storage

All user data, including login credentials and to-do lists, are stored in a local JSON file (`data.json`). The file is created automatically when the application is first run.

## Requirements

- Python 3.7+
- Tkinter (usually comes pre-installed with Python)
- Matplotlib
- NumPy
- Requests

## License

This project is open-source and available for personal and educational use.

## Contributors

- Wojtek Aszkiełowicz [353873]