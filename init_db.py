import os
import sqlite3
import pymysql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'wellness_db')

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    total_points INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wellness_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    record_date DATE NOT NULL,
    sleep_hours REAL NULL,
    sleep_quality INTEGER NULL,
    water_glasses INTEGER NULL,
    exercise_type TEXT NULL,
    exercise_duration INTEGER NULL,
    exercise_intensity TEXT NULL,
    mood INTEGER NULL,
    stress_level INTEGER NULL,
    study_hours REAL NULL,
    study_sessions INTEGER NULL,
    study_subject TEXT NULL,
    wellness_score INTEGER NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, record_date),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    entry_date DATE NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS wellness_tips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    challenge_type TEXT NOT NULL DEFAULT 'daily',
    points INTEGER NOT NULL DEFAULT 20,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS challenge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    completion_date DATE NULL,
    is_completed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    badge_icon TEXT NOT NULL,
    criteria_type TEXT NOT NULL,
    criteria_value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    earned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements (id) ON DELETE CASCADE
);
"""

ACHIEVEMENTS_SEED = [
    ('3-Day Streak', 'Logged daily wellness activities for 3 consecutive days.', 'fire', 'streak', 3),
    ('7-Day Streak', 'Maintained consistency for 7 consecutive days!', 'flame-fill', 'streak', 7),
    ('30-Day Streak', 'Exceptional habit consistency for 30 days!', 'trophy-fill', 'streak', 30),
    ('Hydration Hero', 'Met daily hydration targets for 7 consecutive days.', 'droplet-fill', 'hydration_streak', 7),
    ('Early Sleeper', 'Recorded 7+ hours of restful sleep for 5 days.', 'moon-stars-fill', 'sleep_count', 5),
    ('Active Student', 'Completed exercise sessions 7 times in a month.', 'activity', 'exercise_count', 7),
    ('Gratitude Starter', 'Written 5 reflective gratitude journal entries.', 'journal-bookmark-fill', 'journal_count', 5),
    ('Gratitude Champion', 'Written 30 reflective gratitude journal entries.', 'book-half', 'journal_count', 30),
    ('Challenge Conqueror', 'Successfully completed 10 wellness challenges.', 'award-fill', 'challenges_completed', 10),
    ('Wellness Explorer', 'Logged all 6 wellness categories in a single day.', 'compass-fill', 'all_categories_day', 1)
]

TIPS_SEED = [
    ('Sleep', 'Aim for 7–9 hours of sleep each night. Establish a calming pre-bedtime routine and turn off blue-light screens 30 minutes before sleep.', 1),
    ('Sleep', 'Maintain a consistent sleep schedule even on weekends to reinforce your natural circadian rhythm.', 1),
    ('Hydration', 'Drink at least 8 glasses (approx. 2 liters) of water daily. Keep a reusable water bottle at your study desk.', 1),
    ('Hydration', 'Hydrate first thing in the morning to kickstart your metabolism and boost alertness.', 1),
    ('Exercise', 'Take a 15-minute brisk walk between long study sessions. Regular physical movement improves focus and reduces stress.', 1),
    ('Exercise', 'Incorporate gentle stretching or yoga during study breaks to relieve muscle tension in your neck and back.', 1),
    ('Stress', 'Try the 4-7-8 breathing technique during stressful moments: inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds.', 1),
    ('Stress', 'Break large academic tasks into smaller 25-minute Pomodoro study intervals with short breaks to prevent burnout.', 1),
    ('Study', 'Create a dedicated, clutter-free study environment to mentally separate work time from relaxation.', 1),
    ('Study', 'Review complex notes right before sleep to enhance memory consolidation during deep sleep cycles.', 1),
    ('General', 'Take time every evening to reflect on three positive events or moments of gratitude from your day.', 1)
]

CHALLENGES_SEED = [
    ('Hydration Boost', 'Drink at least 8 glasses of water throughout the day.', 'daily', 20, 1),
    ('Study Break Stretches', 'Take a 10-minute stretching break during your study sessions today.', 'daily', 20, 1),
    ('8-Hour Sleep Night', 'Get 8 hours of restorative sleep tonight.', 'daily', 20, 1),
    ('Gratitude Reflection', 'Write down three things you are grateful for today in your gratitude journal.', 'daily', 20, 1),
    ('Screen-Free Bedtime', 'Avoid using phones or computers 30 minutes before going to bed.', 'daily', 20, 1),
    ('Weekly Exercise Master', 'Complete at least 3 exercise sessions this week (minimum 20 mins each).', 'weekly', 50, 1),
    ('Consistent Habit Tracker', 'Log your wellness data every day this week.', 'weekly', 50, 1)
]

def init_sqlite():
    """Initializes SQLite database wellness.db."""
    db_path = os.path.join(os.path.dirname(__file__), 'wellness.db')
    print(f"Initializing SQLite database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript(SQLITE_SCHEMA)
    
    # Seed achievements
    for ach in ACHIEVEMENTS_SEED:
        cursor.execute("SELECT id FROM achievements WHERE name = ?", (ach[0],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO achievements (name, description, badge_icon, criteria_type, criteria_value) VALUES (?, ?, ?, ?, ?)", ach)
            
    # Seed tips
    for tip in TIPS_SEED:
        cursor.execute("SELECT id FROM wellness_tips WHERE content = ?", (tip[1],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO wellness_tips (category, content, is_active) VALUES (?, ?, ?)", tip)

    # Seed challenges
    for ch in CHALLENGES_SEED:
        cursor.execute("SELECT id FROM challenges WHERE title = ?", (ch[0],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO challenges (title, description, challenge_type, points, is_active) VALUES (?, ?, ?, ?, ?)", ch)

    # Seed Admin account
    admin_email = "admin@wellvia.edu"
    admin_username = "admin"
    admin_hash = generate_password_hash("Admin@123")
    
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (admin_email, admin_username))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, total_points, is_active) VALUES (?, ?, ?, 'admin', 0, 1)",
            (admin_username, admin_email, admin_hash)
        )
        print("Default admin user created: admin@wellvia.edu / Admin@123")

    conn.commit()
    conn.close()
    print("SQLite database initialized successfully!")

def init_mysql():
    """Attempts MySQL database initialization."""
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        connect_timeout=3,
        autocommit=True
    )
    
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database `{MYSQL_DB}` verified/created.")
    conn.close()

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )
    
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_statements = f.read()
            for statement in sql_statements.split(';'):
                stmt = statement.strip()
                if stmt:
                    with conn.cursor() as cursor:
                        cursor.execute(stmt)

    seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
    if os.path.exists(seed_path):
        with open(seed_path, 'r', encoding='utf-8') as f:
            sql_statements = f.read()
            for statement in sql_statements.split(';'):
                stmt = statement.strip()
                if stmt:
                    with conn.cursor() as cursor:
                        try:
                            cursor.execute(stmt)
                        except Exception:
                            pass

    admin_email = "admin@wellvia.edu"
    admin_username = "admin"
    admin_hash = generate_password_hash("Admin@123")
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (admin_email, admin_username))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role, total_points, is_active) VALUES (%s, %s, %s, 'admin', 0, 1)",
                (admin_username, admin_email, admin_hash)
            )

    conn.close()
    print("MySQL database initialized successfully!")

def init_database():
    print(f"Initializing Wellvia Database...")
    engine = os.environ.get('DB_ENGINE', 'auto').lower()
    
    if engine == 'mysql':
        try:
            init_mysql()
        except Exception as e:
            print(f"MySQL initialization failed: {e}")
            print("Falling back to SQLite database...")
            init_sqlite()
    elif engine == 'sqlite':
        init_sqlite()
    else: # auto
        try:
            init_mysql()
        except Exception as e:
            print(f"MySQL connection unavailable/access denied ({e}).")
            print("Auto-initializing SQLite fallback database ('wellness.db')...")
            init_sqlite()

if __name__ == '__main__':
    init_database()
