# 🌿 Wellvia — Student Physical & Mental Health Companion

Wellvia is an intelligent, full-stack holistic wellness web application designed specifically for college students. It empowers students to track, reflect on, and improve their physical, mental, and academic well-being through daily habit logging, interactive analytics, gamification, and an AI-powered wellness companion tailored to their real-time dashboard data.

---

## 🌟 Key Features

### 1. 📊 Interactive Student Dashboard
- **Daily Wellness Score**: Rule-based 0–100 composite score balancing sleep (20%), hydration (20%), exercise (15%), mood (15%), stress (15%), and study habits (15%).
- **Body Metrics & ML Health**: Real-time BMI calculation, World Health Organization weight categorization, Machine Learning Health Status classifier, and ML Lifestyle Risk assessment.
- **Today's Habits Quickview**: Clear visual cards for sleep duration & quality, water intake, workout duration & intensity, and study hours.
- **Daily Rotating Wellness Tip**: Curated actionable guidance for academic and lifestyle balance.
- **Active Challenges & Streaks**: Daily habit challenges and consistency streak tracker with achievement points.

### 2. 🤖 AI Wellness Companion (Google Gemini & Offline Fallback)
- **Dashboard-Aware Personalization**: Ingests the student's real-time dashboard metrics (height, weight, BMI, today's sleep, hydration, workouts, study hours, streak, points). When students ask questions like *"am I overweight?"* or *"how did I sleep today?"*, the companion answers directly using their actual recorded data.
- **Dual-Engine Resilience**: Powered by Google GenAI SDK (`gemini-2.5-flash` / `gemini-3.5-flash`) with automatic multi-model failover and a local offline contextual assistant (`wellvia_local_assistant`).
- **Immediate Crisis Safety Intervention**: Detects self-harm or acute crisis language and instantly returns emergency support resources (988 Lifeline, Crisis Text Line 741741, campus health center).

### 3. 📈 Redesigned Progress & Analytics
- **Wellness Overview**: High-level statistical cards summarizing averages, current consistency streak, and completion metrics.
- **Daily Wellness Charts**: Visual bar charts for Sleep (hrs), Hydration (glasses), Exercise (mins), and Study (hrs) over 7, 14, or 30 days.
- **Your Wellness Analysis**: Personalized analysis identifying behavioral patterns and habit consistency based on the student's actual logged data.
- **Areas to Improve**: Targeted, actionable suggestions addressing low-scoring or irregular habits.

### 4. ⚖️ BMI & Machine Learning Health Assessment
- **Clinical & ML Insights**: Combines standard BMI calculation with trained machine learning models for holistic health classification and lifestyle risk prediction.
- **Integrated Health Disclaimers**: Clear non-clinical advisories emphasizing self-awareness and student healthcare center resources.

### 5. 🏆 Gamification & Positive Habit Formation
- **Streak Tracking**: Encourages daily engagement by rewarding consecutive logging days.
- **Points & Badges**: Students earn points by completing daily wellness logs and challenges, unlocking milestone badges.

### 6. 🛡️ Administrative Portal
- **Aggregated Analytics**: Campus-wide, anonymized wellness metrics and distribution charts protecting student privacy.
- **Challenge & Tip Management**: Administrative CRUD tools for campus wellness challenges and health tips.
- **Student Account Management**: Secure student activation and deactivation controls.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite | Modern Single Page Application (SPA) with fast HMR |
| **Styling** | Vanilla CSS3, Glassmorphism | Custom design tokens, dark wellness palette, responsive layouts |
| **Icons & UI** | Lucide React | Clean, modern iconography |
| **Backend** | Python 3.10+, Flask 3.x | Modular REST API with Application Factory pattern |
| **Database** | MySQL 8.0+ / SQLite | Relational schema with 7 normalized tables |
| **Authentication** | Flask Sessions, Werkzeug | Secure password hashing (`scrypt` / `pbkdf2:sha256`), RBAC |
| **AI Companion** | Official Google GenAI SDK | `gemini-2.5-flash` / `gemini-3.5-flash` with local fallback engine |
| **Machine Learning**| Scikit-Learn, Joblib | Health Status and Lifestyle Risk classification models |
| **Testing** | Pytest, Flask Test Client | 74 automated unit, integration, and security tests (100% pass) |

---

## 📁 Repository Structure

```text
Wellvia/
├── app/
│   ├── models/             # Database connection and parameterized query runner
│   ├── routes/
│   │   ├── api.py          # Unified JSON REST API (/api/*)
│   │   ├── auth.py         # Authentication routes
│   │   ├── student.py      # Student profile & wellness endpoints
│   │   └── admin.py        # Administrative endpoints
│   ├── services/
│   │   ├── chat_service.py # AI Chatbot (Gemini SDK, safety, dashboard context, fallback)
│   │   ├── ml_service.py   # Machine learning health & lifestyle classifiers
│   │   ├── scoring.py      # Rule-based wellness score calculation (0–100)
│   │   ├── wellness.py     # Daily wellness record logging & upsert
│   │   ├── gamification.py # Streak calculation, points, and badge awards
│   │   ├── analytics.py    # Student history & trend aggregation
│   │   └── admin_analytics.py # Anonymized administrative reporting
│   └── utils/              # BMI formulas, decorators, input validation
├── frontend/
│   ├── src/
│   │   ├── api/            # Centralized API client (api.js)
│   │   ├── components/     # Reusable UI (Navbar, ChatbotDrawer, ProtectedRoute, etc.)
│   │   ├── pages/
│   │   │   ├── student/    # Dashboard, DailyLog, Progress, Challenges, Tips, BMI
│   │   │   ├── admin/      # AdminDashboard, AdminUsers, AdminTips, AdminChallenges
│   │   │   └── auth/       # Login, Register, ForgotPassword
│   │   └── styles/         # Custom CSS design system (main.css)
│   ├── package.json
│   └── vite.config.js
├── tests/                  # Pytest test suite (74 tests)
├── models/                 # Pre-trained ML model binaries (.pkl)
├── schema.sql              # Database DDL schema (7 tables)
├── seed.sql                # Default initial tips, challenges & badges
├── init_db.py              # Database initialization and migration script
├── requirements.txt        # Python package dependencies
└── run.py                  # Backend application launcher
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- MySQL Server (or SQLite fallback)

### 1. Backend Setup
1. Clone the repository and navigate into the project directory:
   ```bash
   cd Wellvia
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`:
   ```ini
   SECRET_KEY=your_secret_key_here
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=wellvia_db
   DB_PORT=3306
   GEMINI_API_KEY=your_google_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
5. Initialize the database schema and default records:
   ```bash
   python init_db.py
   ```
6. Start the Flask server:
   ```bash
   python run.py
   ```
   *The backend will run on `http://127.0.0.1:5000`.*

---

### 2. Frontend Setup
1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Build production assets or start Vite development server:
   ```bash
   # Development server:
   npm run dev
   # Or build for production served by Flask:
   npm run build
   ```
   *When built, Flask serves the compiled SPA directly from `frontend/dist` at `http://127.0.0.1:5000`.*

---

## 🔑 Default Accounts

For evaluation and demonstration purposes:

| Role | Email / Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Demo Student** | `student@wellvia.edu` / `Kelly` | `Password123` | Pre-populated with 6 days of wellness records, BMI data, and 990 points. |
| **Administrator** | `admin@wellvia.edu` / `admin` | `Admin@123` | Full access to user management, tip curation, and aggregated analytics. |

---

## 🧪 Testing & Quality Assurance

Run the comprehensive automated test suite with pytest:
```bash
pytest
```
*All 74 tests pass across authentication, authorization, BMI calculations, ML integrations, progress analytics, gamification, and AI chatbot safety/personalization.*

---

## 🔒 Privacy & Safety Notice

Wellvia is designed strictly as a **wellness self-awareness and habit-tracking platform**. It does not perform clinical diagnosis, prescribe medication, or replace professional psychological therapy. All student health records remain strictly confidential and are isolated by user session. Aggregated administrative analytics are fully anonymized.
