# Student Wellness Companion (Wellvia) — Comprehensive Project Roadmap

**Version:** 1.0  
**Status:** Approved & In Execution  
**Source of Truth:** [PROJECT_VISION.md](PROJECT_VISION.md), [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md), [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 1. Executive Summary & Vision Statement

The **Student Wellness Companion (Wellvia)** is a web-based platform designed specifically for college students to track, reflect on, and improve their daily physical, mental, and academic well-being. The system unifies tracking for sleep, hydration, exercise, mood, stress, and study habits with admin-curated tips, achievable challenges, and personalized analytics.

> **Disclaimer:** Wellvia is a **self-awareness and habit-tracking tool**. It does not perform medical diagnosis, provide clinical therapy, or replace healthcare professionals.

---

## 2. Technology Stack & Architecture

- **Architecture:** 3-Layer Monolithic Web Application (Presentation Layer, Application Layer, Data Access Layer)
- **Backend:** Python 3, Flask 3.x, Jinja2, Werkzeug (bcrypt security), PyMySQL, Pandas
- **Database:** MySQL 8.0+ / SQLite relational database (7 normalized tables)
- **Frontend:** HTML5, Custom Vanilla CSS, Bootstrap 5.3, JavaScript (ES6+), Chart.js 4.x
- **Privacy & Security:** Role-Based Access Control (RBAC), parameterized SQL execution, anonymized aggregate admin analytics.

---

## 3. High-Level Master Timeline

```mermaid
gantt
    title Student Wellness Companion — Master Project Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %b %d

    section Phase 1: Planning & Setup
    Environment & Architecture Setup     :p1, 2026-09-01, 2d
    section Phase 2: Data Access Layer
    Database Schema & Seed Pipeline      :p2, after p1, 3d
    section Phase 3: Core Security & Auth
    Auth Module, RBAC & Base Layout      :p3, after p2, 3d
    section Phase 4: Core Wellness Engine
    Daily Tracking & Scoring Engine      :p4, after p3, 4d
    section Phase 5: Gamification
    Streaks, Points & Badges Engine      :p5, after p4, 3d
    section Phase 6: Wellness Toolkit
    Tips & Challenges                    :p6, after p5, 3d
    section Phase 7: Data Analytics
    Pandas Processing & Chart.js         :p7, after p6, 4d
    section Phase 8: Admin Operations
    User Mgmt & Content Management       :p8, after p7, 3d
    section Phase 9: UI Polish & Aesthetics
    Responsive Styling & Glassmorphism   :p9, after p8, 3d
    section Phase 10: QA & Verification
    Unit Testing & E2E Validation        :p10, after p9, 3d
```

---

## 4. Phase-by-Phase Deliverables & Milestones

```mermaid
flowchart TD
    P1["Phase 1: Environment & Project Setup"] --> P2["Phase 2: Database Schema & Seeds"]
    P2 --> P3["Phase 3: App Factory & Auth Module"]
    P3 --> P4["Phase 4: Core Wellness Tracking & Scoring"]
    P4 --> P5["Phase 5: Gamification & Badges Engine"]
    P5 --> P6["Phase 6: Tips & Challenges"]
    P6 --> P7["Phase 7: Personal & Admin Analytics (Pandas + Chart.js)"]
    P7 --> P8["Phase 8: Administrative Panel"]
    P8 --> P9["Phase 9: Modern UI Styling & Polish"]
    P9 --> P10["Phase 10: Verification & Quality Assurance"]
```

### Phase 1 — Project Foundation & Configuration
- **Deliverables:**
  - Project workspace structure (`app/`, `config/`, `tests/`, `static/`, `templates/`).
  - Python dependencies manifest (`requirements.txt`).
  - Configuration settings class (`config/settings.py`) managing environment variables via `.env`.
  - Application entry point launcher (`run.py`).

### Phase 2 — Database Schema & Data Access Layer
- **Deliverables:**
  - `schema.sql`: DDL script defining 7 normalized database tables (`users`, `wellness_records`, `wellness_tips`, `challenges`, `challenge_progress`, `achievements`, `user_achievements`).
  - `seed.sql` & `init_db.py`: Database initializer seeding default achievements, wellness tips, challenges, and pre-created admin credentials (`admin@wellvia.edu` / `Admin@123`).
  - `app/models/db.py`: Database helper abstraction utilizing PyMySQL/SQLite with parameterized query execution.

### Phase 3 — Core Application Architecture & Auth Module
- **Deliverables:**
  - `app/__init__.py`: Flask Application Factory (`create_app()`).
  - `app/utils/decorators.py`: Security route decorators (`@login_required`, `@student_required`, `@admin_required`).
  - `app/utils/validation.py`: Server-side input validation functions.
  - `app/routes/auth.py`: Registration (`/register`), Login (`/login`), and Logout (`/logout`).
  - UI Templates: Master layout (`base.html`), login, registration, and error views (404, 403, 500).

### Phase 4 — Core Wellness Tracking & Scoring Engine
- **Deliverables:**
  - `app/services/scoring.py`: Rule-based Wellness Score calculation engine (0-100 score out of Hydration 20%, Sleep 20%, Exercise 15%, Mood 15%, Stress 15%, Study 15%) with missing data weight redistribution.
  - `app/services/wellness.py`: Daily metrics logger handling upserts on `wellness_records`.
  - `app/routes/student.py`: Student routes for `/dashboard` and `/wellness` log form.
  - `app/templates/dashboard.html` & `app/templates/wellness/log.html`: Student dashboard showing daily score, streak, hydration progress, tip of the day, and active challenge.

### Phase 5 — Gamification & Achievements Engine
- **Deliverables:**
  - `app/services/gamification.py`:
    - Running total points manager (+10 log, +20/+50 challenges).
    - Dynamic streak calculator inspecting consecutive logging dates.
    - Achievement condition evaluator awarding badges (e.g. 3-Day Streak, Hydration Hero, Early Sleeper, Challenge Conqueror).
  - `app/templates/profile.html`: Student profile view showcasing earned badge collection.

### Phase 6 — Wellness Toolkit (Tips & Challenges)
- **Deliverables:**
  - `app/templates/tips/index.html`: Curated wellness tips viewer with category filters.
  - `app/templates/challenges/index.html`: Active challenges hub supporting daily/weekly completion actions and point rewards.

### Phase 7 — Data Analytics & Visualization (Pandas + Chart.js)
- **Deliverables:**
  - `app/services/analytics.py`: Student analytics processing service using Pandas to compute continuous date series, moving averages, habit completion rates, and pattern-based observations.
  - `app/services/admin_analytics.py`: Admin aggregate analytics service producing anonymized summary stats.
  - `app/static/js/charts.js`: Modular Chart.js initialization script for Line, Bar, and Doughnut charts.
  - `app/templates/progress.html`: Student progress visualization dashboard.

### Phase 8 — Administrative Panel & Content Management
- **Deliverables:**
  - `app/routes/admin.py`: Admin routes for dashboard, user management, tip management, and challenge management.
  - Admin Templates: `admin/dashboard.html`, `admin/users.html`, `admin/tips.html`, `admin/challenges.html`.

### Phase 9 — Modern UI Aesthetics & Responsive Styling
- **Deliverables:**
  - `app/static/css/style.css`: Curated color palette (Deep Slate `#0f172a`, Teal `#0d9488`, Emerald `#10b981`), Inter/Outfit typography, glassmorphism cards, micro-animations, and full mobile responsiveness.

### Phase 10 — Testing & Quality Assurance
- **Deliverables:**
  - `tests/test_scoring.py`: Unit tests for score normalizations and composite score calculation.
  - `tests/test_validation.py`: Unit tests for input validators.
  - Automated test execution via Python `pytest` framework.

### Phase 11 — Modern React 18 SPA & Design System (Completed)
- **Deliverables:**
  - Decoupled single-page application built with React 18, Vite, and React Router (`frontend/src/`).
  - Modular component hierarchy (`components/common/`, `pages/student/`, `pages/admin/`, `pages/auth/`).
  - Bespoke dark-mode glassmorphic design system (`styles/main.css`) with emerald/cyan accent palettes and responsive layouts.
  - Clean removal of the mascot in favor of a modern, professional student experience.

### Phase 12 — Unified Flask REST API (Completed)
- **Deliverables:**
  - `app/routes/api.py`: Complete JSON REST endpoints for Auth (`/api/auth/*`), Student Dashboard & Habits (`/api/student/*`), Admin Operations (`/api/admin/*`), and AI Chat (`/api/chat/*`).
  - Session-based authentication with Werkzeug `scrypt` hashing and role-based route guards (`@api_login_required`, `@api_student_required`, `@api_admin_required`).

### Phase 13 — AI Wellness Companion & Dashboard Personalization (Completed)
- **Deliverables:**
  - `app/services/chat_service.py` & `frontend/src/components/common/ChatbotDrawer.jsx`:
    - Integration of official Google GenAI SDK (`gemini-2.5-flash` / `gemini-3.5-flash`).
    - **Dashboard Data Personalization**: Ingests the logged-in student's real-time body metrics (height, weight, BMI, category), ML status, today's logged habits (sleep, water, exercise, study), streak, and score into the AI prompt and fallback engine.
    - Crisis safety detection and immediate emergency support intervention (988 Lifeline, 741741 Crisis Text Line).
    - Multi-model failover chain and non-repetitive offline contextual fallback assistant (`wellvia_local_assistant`).

### Phase 14 — Machine Learning & 4-Section Progress Redesign (Completed)
- **Deliverables:**
  - `app/services/ml_service.py`: Pre-trained ML models classifying Health Status and Lifestyle Risk.
  - `frontend/src/pages/student/ProgressPage.jsx`: Redesigned analytics dashboard structured into 4 actionable sections:
    1. *Wellness Overview*: High-level summary cards (averages, streak, logged habits).
    2. *Daily Wellness Charts*: Dynamic bar charts for sleep, hydration, exercise, and study across 7, 14, or 30 days.
    3. *Your Wellness Analysis*: Real-time personalized habit evaluations based on logged data.
    4. *Areas to Improve*: Targeted, actionable recommendations for low-performing habits.
  - 74 automated pytest tests verifying 100% functionality and security.

---

## 5. Future Evolutionary Roadmap

The modern decoupled architecture provides a strong foundation for future innovations:

1. **Progressive Web App (PWA):** Service worker integration for offline logging and push reminders.
2. **Native Mobile App:** React Native companion app for iOS and Android consuming the `/api/*` REST endpoints.
3. **Wearable Integration:** Direct sync with Google Fit / Apple Health APIs.
4. **Expanded ML Predictive Coaching:** Long-term habit forecasting and proactive burnout warnings.
