# Al Alanda Project Setup Guide

This guide will help you set up and run the Al Alanda project on Windows or Mac machines without any prior Python installation.

## Prerequisites

### For Windows Users

Before you begin, you'll need to install the following software:

1. **Python**: Download and install Python from the official website
   - Go to [Python Downloads](https://www.python.org/downloads/)
   - Download the latest Python 3.11+ version for Windows
   - During installation, make sure to check "Add Python to PATH"

2. **Redis**: This project uses Redis for caching and session management
   - Download Redis for Windows from [GitHub](https://github.com/tporadowski/redis/releases)
   - Install Redis and ensure it's running (you can install it as a Windows service)

### For Mac Users

1. **Python**: Install Python using Homebrew or the official installer
   - Option 1: Using Homebrew (recommended)
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     brew install python@3.11
     ```
   - Option 2: Download from [Python Downloads](https://www.python.org/downloads/)
     - Download the latest Python 3.11+ version for macOS

2. **Redis**: Install Redis using Homebrew
   ```
   brew install redis
   brew services start redis
   ```



## Setup Steps

### For Windows Users

1. **Extract the project files**
   - Extract the project zip file to a location of your choice (e.g., `C:\Projects\al-alanda`)

2. **Open Command Prompt**
   - Press `Win + R`, type `cmd`, and press Enter
   - Navigate to the project folder:
     ```
     cd C:\path\to\al-alanda
     ```

3. **Create a virtual environment**
   - Run the following command:
     ```
     python -m venv venv
     ```
   - Activate the virtual environment:
     ```
     venv\Scripts\activate
     ```

### For Mac Users

1. **Extract the project files**
   - Extract the project zip file to a location of your choice (e.g., `~/Projects/al-alanda`)

2. **Open Terminal**
   - Open Terminal from Applications > Utilities > Terminal
   - Navigate to the project folder:
     ```
     cd ~/path/to/al-alanda
     ```

3. **Create a virtual environment**
   - Run the following command:
     ```
     python3 -m venv venv
     ```
   - Activate the virtual environment:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**
   - Install all required packages:
     ```
     pip install -r requirements.txt
     ```

5. **Initialize the database**
   - Run the following commands:
     ```
     python manage.py migrate
     python manage.py createsuperuser
     ```
   - Follow the prompts to create an admin user

6. **Collect static files**
   - Run:
     ```
     python manage.py collectstatic
     ```

7. **Run the development server**
   - Start the server:
     ```
     python manage.py runserver
     ```
   - Open your browser and go to: http://127.0.0.1:8000/

## Project Structure

- `core`: Core functionality and shared components
- `products`: Product management app
- `orders`: Order processing and cart functionality
- `templates`: HTML templates for the website
- `static`: Static files (CSS, JS, images)
- `media`: User-uploaded files
- `locale`: Translation files (English and Arabic)

## Admin Access

- Access the admin panel at: http://127.0.0.1:8000/admin/
- Log in with the superuser credentials you created earlier

## Troubleshooting

### Redis Connection Issues
If you encounter Redis connection errors:
1. Make sure Redis is running
   - Windows: Check Redis service in Task Manager or Services
   - Mac: Run `brew services list` to check if Redis is running
2. Open `project/settings.py`
3. Find the `CACHES` setting and ensure the Redis location is correct

### Database Issues
If you have database issues:
1. Delete the `db.sqlite3` file
2. Run `python manage.py migrate` again
3. Create a new superuser with `python manage.py createsuperuser`

### Static Files Not Loading
If static files aren't loading:
1. Make sure you've run `python manage.py collectstatic`
2. Check that `DEBUG = True` in settings.py

### Mac-Specific Issues

#### Permission Denied Errors
If you encounter permission errors on Mac:
1. Make sure you have proper permissions for the project directory
2. Run `chmod -R 755 ~/path/to/al-alanda` to set appropriate permissions

#### Python Version Issues
If you have multiple Python versions installed:
1. Use `python3` instead of `python` in all commands
2. Verify your Python version with `python3 --version`

## Support

If you encounter any issues during setup or have questions about the project, please contact the development team.
