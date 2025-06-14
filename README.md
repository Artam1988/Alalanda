# Al Alanda Project Setup Guide

This guide will help you set up and run the Al Alanda project on a Mac machine after cloning it from GitHub.

## Prerequisites

1. **Python**: Install Python using Homebrew or the official installer
   - Option 1: Using Homebrew (recommended)
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     brew install python@3.11
     ```
   - Option 2: Download from [Python Downloads](https://www.python.org/downloads/)
     - Download the latest Python 3.11+ version for macOS


## Setup Steps

1. **Clone the project from GitHub**
   - Open Terminal and run:

     git clone https://github.com/Artam1988/Alalanda.git
     cd al-alanda

2. **Create a virtual environment**
   - Run the following commands:
     
     python3 -m venv venv
     source venv/bin/activate


3. **Install dependencies**
     pip install -r requirements.txt


4. **Initialize the database**
   - Run the following command:
     python manage.py migrate


5. **Collect static files**
   - Run:
     python manage.py collectstatic


6. **Run the development server**
   - Run:
     python manage.py runserver

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