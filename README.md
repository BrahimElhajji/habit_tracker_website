# 🌟 Habit Tracker

**Habit Tracker** is a web application designed to help users build and maintain daily habits, track progress, and stay consistent. Featuring a user-friendly dashboard, habit streak tracking, detailed analytics, and gamification elements, it empowers users to reach their goals!

![Habit Tracker Dashboard](https://raw.githubusercontent.com/BrahimElhajji/habit_tracker_website/refs/heads/master/app/static/images/habittracker.png)

## 🚀 Features

- **👤 User Authentication**
  - Secure registration and login (JWT-based).
  - Password hashing for security.
  - Profile management (update username, email, and password).
  
- **📋 Habit Management**
  - Create, edit, and delete habits.
  - Track daily habit completions.
  - View completion history on a calendar.

- **🔥 Streak Tracking**
  - Automatically tracks habit streaks for consistency.
  - Visual feedback on streaks to keep users motivated.

- **📊 Analytics & Statistics**
  - Progress bars for habit completion percentages.
  - Insights into daily and weekly completions.
  - Calendar view to track when habits are completed.

- **🏷️ Habit Categories**
  - Organize habits into categories for better management.

- **🎮 Gamification**
  - Unlock badges and rewards for milestones and consistency.
  - Track overall progress and habit completions.

- **🌙 Dark Mode**
  - Toggle between light and dark themes for a personalized experience.

## 🛠️ Tech Stack

- **Backend**: Flask, Flask-JWT-Extended, SQLAlchemy
- **Frontend**: Bootstrap 5, FullCalendar.js
- **Database**: SQLite (easily replaceable with other SQL-based databases)
- **Authentication**: JWT-based authentication

## 🎯 Quick Start

### 1️⃣ Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/BrahimElhajji/habit_tracker_website.git
    cd habit_tracker
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up the database**:

    ```bash
    flask db upgrade
    ```

4. **Run the application**:

    ```bash
    flask run
    ```

5. **Access the app**:  
   The application will be available at `http://localhost:5000`.

### 2️⃣ Configuration

- Update the `config.py` file to customize settings (e.g., database URI, secret keys).

### 3️⃣ API Documentation

The application provides a RESTful API for managing users, habits, and completions.

| Endpoint                  | Method | Description                           |
|---------------------------|--------|---------------------------------------|
| `/api/auth/register`       | POST   | Register a new user                   |
| `/api/auth/login`          | POST   | Login and receive a JWT               |
| `/api/habits/`             | GET    | Retrieve all user habits              |
| `/api/habits/`             | POST   | Create a new habit                    |
| `/api/habits/<habit_id>`   | GET    | Get a specific habit by ID            |
| `/api/habits/<habit_id>`   | PUT    | Update a specific habit               |
| `/api/habits/<habit_id>`   | DELETE | Delete a habit                        |
| `/api/completions/`        | GET    | Get all habit completions             |
| `/api/completions/`        | POST   | Mark a habit as completed             |


## 📂 Project Structure
```
habit_tracker/
├── app/
│   ├── __init__.py             # Initialize the app
│   ├── models.py               # Database models (User, Habit, Completion)
│   ├── api/                    # API routes
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── habits.py           # Habit CRUD endpoints
│   │   └── completions.py      # Habit completion 
│   │   └── ...
endpoints
│   ├── web/                    # Web UI routes and forms
│   ├── templates/              # HTML templates for the web interface
│   └── static/                 # Static assets (CSS, JS, images)
├── config.py                   # App configuration (e.g., database URI)
├── requirements.txt            # List of Python dependencies
├── run.py                      # Run the app
└── migrations/                 # Database migrations
```
## 👨‍💻 Contributing

Contributions are welcome! Feel free to fork this repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you'd like to change.

## 📜 License

This project is licensed under the MIT License.

---

