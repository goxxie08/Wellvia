# 🌱 Wellvia — Student Wellness Companion
## Complete Project Roadmap

> **Derived from:** [PROJECT_VISION.md](PROJECT_VISION.md) · [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) · [ARCHITECTURE.md](ARCHITECTURE.md)  
> **Version:** 2.0 · **Last Updated:** August 2026 · **Status:** ✅ Active Development

---

## Vision Statement

> *"Empower college students to proactively manage their holistic well-being through a centralized and engaging web platform — transforming daily habits into actionable insights."*

Wellvia is a **self-awareness and habit-tracking tool**, not a clinical tool. It helps students reflect on their routines and make informed choices about sleep, hydration, exercise, mood, stress, and study balance — all in one place.

---

## System Architecture at a Glance

```
┌──────────────────────────────────────────────────────┐
│               PRESENTATION LAYER                     │
│   HTML5 · CSS3 · Bootstrap 5 · Chart.js · Jinja2    │
├──────────────────────────────────────────────────────┤
│               APPLICATION LAYER (Flask)              │
│  Routes · Auth/RBAC · Business Logic · Score Engine  │
│  Gamification Engine · Analytics Engine              │
├──────────────────────────────────────────────────────┤
│              DATA ACCESS LAYER                       │
│          PyMySQL · Pandas · Parameterized SQL        │
├──────────────────────────────────────────────────────┤
│               DATABASE (MySQL / SQLite)              │
│  Users · WellnessRecords · Journals · Tips           │
│  Challenges · Achievements · UserAchievements        │
└──────────────────────────────────────────────────────┘
```

---

## Project Phases Overview

| Phase | Title | Focus Area | Status |
|-------|-------|-----------|--------|
| **Phase 0** | Project Foundation | Setup, Environment, Architecture | ✅ Done |
| **Phase 1** | Database & Schema | 8-table normalized schema | ✅ Done |
| **Phase 2** | Authentication & Security | Register · Login · RBAC · Sessions | ✅ Done |
| **Phase 3** | Wellness Tracking Core | 6-category daily logging engine | ✅ Done |
| **Phase 4** | Wellness Score Engine | Weighted 0–100 score formula | ✅ Done |
| **Phase 5** | Gamification System | Points · Streaks · Badges | ✅ Done |
| **Phase 6** | Wellness Toolkit | Journal · Tips · Challenges | ✅ Done |
| **Phase 7** | Analytics & Charts | Pandas + Chart.js visualization | ✅ Done |
| **Phase 8** | Admin Panel | User mgmt · Content mgmt · Analytics | ✅ Done |
| **Phase 9** | UI/UX & Templates | 18 Jinja2 templates · Responsive CSS | ✅ Done |
| **Phase 10** | Testing & Deployment | Unit tests · DB init · Git push | ✅ Done |

---

## Phase 0 — Project Foundation

**Goal:** Establish a clean, reproducible development environment and project structure.

### Deliverables
- [x] Project directory structure (`app/`, `config/`, `tests/`, `static/`, `templates/`)
- [x] `requirements.txt` — Flask 3.x, PyMySQL, Pandas, Werkzeug, python-dotenv
- [x] `.env` & `.env.example` — Database credentials and secret key
- [x] `config/settings.py` — Config classes loading from environment variables
- [x] `run.py` — Application entry point
- [x] `.gitignore` — Excludes `.env`, `wellness.db`, `__pycache__`

### Architecture Decisions
| Decision | Rationale |
|----------|-----------|
| Flask over Django | Lightweight, BCA-scope appropriate, manual auth as a learning exercise |
| Monolith SSR | Simplicity; avoids SPA complexity. Future: can evolve to REST + React |
| MySQL primary / SQLite fallback | Development portability without losing relational capabilities |

---

## Phase 1 — Database & Schema Design

**Goal:** Design and implement a normalized relational schema to store all application data.

### 8-Table Schema

```
Users ──────────┬──── WellnessRecords    (1 record/day/user)
                ├──── JournalEntries     (private, user-owned)
                ├──── ChallengeProgress  (many-to-many bridge)
                └──── UserAchievements   (many-to-many bridge)

Challenges ─────────── ChallengeProgress
Achievements ──────── UserAchievements
WellnessTips           (standalone, admin-managed)
```

### Table Summary

| Table | Purpose | Key Constraint |
|-------|---------|----------------|
| `users` | Accounts (students + admins) | `UNIQUE(email)`, `UNIQUE(username)` |
| `wellness_records` | Daily consolidated metrics | `UNIQUE(user_id, record_date)` |
| `journal_entries` | Private gratitude entries | FK `user_id` ON DELETE CASCADE |
| `wellness_tips` | Admin-curated tips by category | `is_active` flag |
| `challenges` | Daily/weekly wellness goals | `challenge_type` ENUM |
| `challenge_progress` | Student participation tracking | Composite FK |
| `achievements` | Badge definitions & criteria | `criteria_type` + `criteria_value` |
| `user_achievements` | Junction: earned badges | `UNIQUE(user_id, achievement_id)` |

### Normalization Level
- **1NF:** Atomic columns, single-valued attributes
- **2NF:** Non-key attributes fully dependent on PK
- **3NF:** No transitive dependencies (achievement definitions separated from awards)
- **Pragmatic wide table:** `wellness_records` uses nullable columns per metric to avoid dashboard join complexity

### Deliverables
- [x] `schema.sql` — Full DDL with CREATE TABLE, constraints, indexes
- [x] `seed.sql` — Pre-seeded achievements, tips, challenges
- [x] `init_db.py` — Auto-initializer with MySQL + SQLite fallback
- [x] Seeded admin: `admin@wellvia.edu` / `Admin@123`

---

## Phase 2 — Authentication & Security

**Goal:** Implement secure user authentication with role-based access control.

### User Flows

#### Registration Flow
```
Student fills form → Server validates → Check uniqueness →
Hash password (bcrypt/Werkzeug) → INSERT users → Redirect to Login
```

#### Login Flow
```
Submit credentials → Fetch user record → Check is_active flag →
Verify password hash → Create session {user_id, role} →
IF student → /dashboard | IF admin → /admin/dashboard
```

#### RBAC Decorators
```python
@login_required     → Any route requiring authentication
@student_required   → Student-only routes (/wellness, /journal)
@admin_required     → Admin-only routes (/admin/*)
```

### Security Measures

| Threat | Mitigation |
|--------|-----------|
| Plain-text passwords | Werkzeug `generate_password_hash()` (bcrypt) |
| SQL Injection | Parameterized queries: `execute("... WHERE id = %s", (id,))` |
| XSS | Jinja2 auto-escapes all template variables |
| Session hijacking | `HttpOnly` + `Secure` cookie flags; signed `SECRET_KEY` |
| CSRF | Session-backed token validation on POST requests |
| Unauthorized routes | 403 Forbidden on role mismatch |
| Password brute force | Failed login attempts logged at WARNING level |

### Deliverables
- [x] `app/routes/auth.py` — `/auth/register`, `/auth/login`, `/auth/logout`
- [x] `app/utils/decorators.py` — `@login_required`, `@student_required`, `@admin_required`
- [x] `app/utils/validation.py` — Server-side form validation helpers
- [x] Password minimum length + complexity rules enforced

---

## Phase 3 — Wellness Tracking Core

**Goal:** Allow students to log 6 dimensions of daily wellness in a single unified form.

### Tracked Metrics

| Category | Input Fields | Validation Rules |
|----------|-------------|-----------------|
| 😴 Sleep | `sleep_hours` (float), `sleep_quality` (1–5) | `0 ≤ hours ≤ 24`, quality 1–5 |
| 💧 Hydration | `water_glasses` (int) | `0 ≤ glasses ≤ 30` |
| 🏃 Exercise | `exercise_type`, `exercise_duration` (min), `exercise_intensity` | duration `≥ 0`, type ≤ 50 chars |
| 😊 Mood | `mood` (1–5 scale) | 1=Very Sad … 5=Very Happy |
| 🧠 Stress | `stress_level` (1–5 scale) | 1=Very Low … 5=Very High |
| 📚 Study | `study_hours` (float), `study_sessions` (int), `study_subject` | `0 ≤ hours ≤ 24` |

### Wellness Entry Data Flow
```
Student fills form
    → POST /wellness/log
    → Session check (@login_required)
    → Server-side validation (ranges, data types)
    → INSERT or UPDATE wellness_records (one record/day)
    → Trigger Wellness Score Engine
    → Trigger Gamification (points, streaks, badges)
    → Redirect to dashboard with success flash
```

### Gamification Points Earned per Activity

| Activity | Points |
|----------|--------|
| Log sleep | +10 pts |
| Log hydration | +10 pts |
| Log exercise | +15 pts |
| Record mood | +5 pts |
| Record stress level | +5 pts |
| Log study hours | +10 pts |
| Write journal entry | +15 pts |
| Complete daily challenge | +20 pts |
| Complete weekly challenge | +50 pts |

### Deliverables
- [x] `app/services/wellness.py` — Daily metrics log service
- [x] `app/routes/student.py` — Student feature routes
- [x] One-record-per-day constraint enforced via `UNIQUE(user_id, record_date)`
- [x] Partial daily entries supported (all metric fields nullable)

---

## Phase 4 — Wellness Score Engine

**Goal:** Calculate a meaningful 0–100 wellness score from logged daily inputs.

> ⚠️ **Disclaimer:** The wellness score is an **engagement and self-awareness indicator only**. It is not a medical assessment, psychological evaluation, or clinical diagnosis.

### Score Composition

| Component | Weight | Ideal Range | Scoring Logic |
|-----------|--------|-------------|---------------|
| 💧 Hydration | **20%** | 8+ glasses | Linear up to target, capped at 100 |
| 😴 Sleep | **20%** | 7–9 hours | Peak in ideal range, lower/higher = lower score |
| 🏃 Exercise | **15%** | 30+ minutes | Scales with duration; any exercise > 0 |
| 😊 Mood | **15%** | 4–5 (Happy) | Direct mapping from 1–5 scale |
| 🧠 Stress | **15%** | 1–2 (Low) | **Inverse** — lower stress = higher score |
| 📚 Study Balance | **15%** | 2–6 hours | Balanced range highest; extremes penalized |

### Sleep Normalization Example
```
< 4 hours  →  20 / 100
4–5 hours  →  40 / 100
5–6 hours  →  60 / 100
6–7 hours  →  80 / 100
7–9 hours  → 100 / 100  ← optimal
9–10 hours →  80 / 100
> 10 hours →  60 / 100
```

### Stress Inverse Normalization
```
Stress 1 (Very Low)  → 100 / 100
Stress 2 (Low)       →  80 / 100
Stress 3 (Moderate)  →  60 / 100
Stress 4 (High)      →  40 / 100
Stress 5 (Very High) →  20 / 100
```

### Formula
```
Wellness Score = (Hydration_sub × 0.20)
              + (Sleep_sub     × 0.20)
              + (Exercise_sub  × 0.15)
              + (Mood_sub      × 0.15)
              + (Stress_sub    × 0.15)
              + (Study_sub     × 0.15)
```

**Missing Data:** If a component is not logged, its weight is redistributed proportionally among the logged components. Minimum 2 components required for score calculation.

### Deliverables
- [x] `app/services/scoring.py` — Weighted 0–100 score engine with normalization functions
- [x] Score stored in `wellness_records.wellness_score` after each log
- [x] Recalculated on every wellness data update

---

## Phase 5 — Gamification System

**Goal:** Sustain student engagement through personal positive reinforcement — no leaderboards or inter-student competition.

### Three Gamification Pillars

```
Event Triggers         Gamification Engine         Persistent State
──────────────         ───────────────────         ────────────────
Wellness Logged  ───▶  Points Processor   ───▶    users.total_points
Journal Created  ───▶  Streak Calculator  ───▶    wellness_records
Challenge Done   ───▶  Achievement Checker ──▶    user_achievements
```

### Streak Calculation Logic
```
Student logs wellness data
    → Query: Does a record exist for yesterday?
        YES → Increment streak counter
        NO  → Reset streak to 1
    → Store updated streak
    → Check badge eligibility
```

### Achievement Badges

| Badge | Criteria | Icon |
|-------|----------|------|
| 🔥 3-Day Streak | Any habit × 3 consecutive days | `fire` |
| 🔥 7-Day Streak | Any habit × 7 consecutive days | `flame-fill` |
| 🏆 30-Day Streak | Any habit × 30 consecutive days | `trophy-fill` |
| 💧 Hydration Hero | Water logged × 7 consecutive days | `droplet-fill` |
| 🌙 Early Sleeper | 7+ hours sleep × 5 days | `moon-stars-fill` |
| 🏃 Active Student | Exercise × 7 days in a month | `activity` |
| 📓 Gratitude Starter | 5 journal entries written | `journal-bookmark-fill` |
| 📚 Gratitude Champion | 30 journal entries written | `book-half` |
| 🏅 Challenge Conqueror | 10 challenges completed | `award-fill` |
| 🧭 Wellness Explorer | All 6 categories logged in one day | `compass-fill` |

### Badge Eligibility Check Flow
```
Activity completed
    → Award points + update streak
    → Fetch all unearned achievement definitions
    → For each: check criteria_type vs. criteria_value
        IF met → INSERT into user_achievements
        → Display congratulations notification
```

### Deliverables
- [x] `app/services/gamification.py` — Points, streaks, achievement evaluator
- [x] Dynamic streak calculator (no separate table — computed from `wellness_records` dates)
- [x] 10 achievement badges pre-seeded via `init_db.py`

---

## Phase 6 — Wellness Toolkit

**Goal:** Provide students with additional tools for reflection, learning, and goal-setting.

### A. Gratitude Journal

Private daily reflection entries. **Privacy is paramount.**

| Operation | Implementation |
|-----------|---------------|
| **Create** | `user_id` set from `session['user_id']` — never from form input |
| **Read** | `WHERE user_id = session_user_id ORDER BY entry_date DESC` |
| **Delete** | `WHERE id = ? AND user_id = ?` — prevents cross-user deletion |
| **Admin Access** | ❌ **Zero** admin routes interact with `journal_entries` table |

Validation: non-empty content, max 2,000 characters, Jinja2 auto-escapes for XSS.

### B. Wellness Tips

Admin-curated practical advice displayed to students. Categories:
- 🌙 Sleep hygiene & bedtime routines
- 💧 Hydration throughout the day
- 🏃 Exercise & stretching during study breaks
- 🧠 Stress management (4-7-8 breathing, Pomodoro)
- 📚 Effective study strategies & time management
- 📱 Digital well-being (screen time reduction)

Tips rotate on dashboard (one per visit) and are browsable by category in a dedicated tips section.

### C. Wellness Challenges

| Type | Duration | Points | Examples |
|------|----------|--------|---------|
| Daily | Same day | 20 pts | Drink 8 glasses · 10-min stretch · Write gratitude |
| Weekly | 7 days | 50 pts | Exercise 3× · Log wellness every day |

Challenge completion validation: checks `challenge_progress` table — prevents same-day double completion.

### Deliverables
- [x] `app/services/journal.py` — CRUD with strict user session isolation
- [x] Journal templates: `journal/index.html`, `journal/edit.html`
- [x] 11 pre-seeded wellness tips (Sleep × 2, Hydration × 2, Exercise × 2, Stress × 2, Study × 2, General × 1)
- [x] 7 pre-seeded challenges (5 daily + 2 weekly)

---

## Phase 7 — Analytics & Data Visualization

**Goal:** Give students meaningful visual insights into their wellness patterns, while providing administrators anonymized aggregate statistics.

### Student Analytics (Personal — Scoped to `user_id`)

| Metric | Chart Type | Time Range |
|--------|-----------|------------|
| Sleep hours trend | Bar chart | Weekly / Monthly |
| Hydration vs. target | Bar chart with target line | Daily / Weekly |
| Exercise frequency & duration | Bar chart | 4-week rolling |
| Mood trend | Line chart | Weekly / Monthly |
| Stress trend | Line chart | Weekly / Monthly |
| Study hours distribution | Bar chart | Weekly / Monthly |
| Wellness score history | Line chart | Weekly / Monthly |
| Habit completion rate | Donut chart | Monthly |

**Pattern-Based Observations (non-clinical):**
> *"Your average stress level was lower on days when you recorded at least 7 hours of sleep."*  
> *"Your mood was generally higher during weeks when you maintained your hydration streak."*

These are computed from simple conditional averages — not AI predictions or clinical assessments.

### Admin Analytics (Aggregated — Anonymous)

Privacy boundary: Individual `user_id` is **never** included in admin query `SELECT` results.

| Metric | SQL Computation |
|--------|----------------|
| Average sleep duration | `AVG(sleep_hours) GROUP BY record_date` |
| Average hydration | `AVG(water_glasses) GROUP BY record_date` |
| Mood distribution | `COUNT(*) GROUP BY mood` (percentage-based) |
| Stress distribution | `COUNT(*) GROUP BY stress_level` |
| Average study hours | `AVG(study_hours) GROUP BY record_date` |
| Challenge participation | `COUNT(DISTINCT user_id) per challenge` |
| Habit completion trends | `COUNT(*) GROUP BY record_date` |

### Analytics Data Flow
```
Student requests /progress
    → Fetch wellness_records WHERE user_id = current_user
    → Pandas: group by date, fill missing days with null
    → Compute averages, trends, completion rates
    → Structure chart data (labels + datasets JSON)
    → Render template → Chart.js renders interactive charts
```

### Chart Types Used (Chart.js)
| Metric | Chart Type |
|--------|-----------|
| Sleep & Study Trend | Line Chart |
| Hydration (Daily vs Target) | Bar Chart |
| Mood vs Stress | Multi-axis Line Chart |
| Habit Completion Rate | Doughnut Chart |
| Admin: Mood Distribution | Pie Chart |

### Deliverables
- [x] `app/services/analytics.py` — Pandas student analytics (continuous date processing)
- [x] `app/services/admin_analytics.py` — Anonymized aggregate analytics
- [x] `app/static/js/charts.js` — Chart.js rendering helper functions
- [x] `app/routes/student.py` — `/api/my-charts` JSON endpoint for Chart.js

---

## Phase 8 — Administrative Panel

**Goal:** Provide campus wellness coordinators with tools to manage content, users, and view anonymized wellness trends.

### Admin Capabilities vs. Restrictions

| Can Do | Cannot Do |
|--------|-----------|
| View student list (username, email, status, date) | View individual wellness records |
| Activate / Deactivate student accounts | Read journal entries |
| Add / Edit / Delete wellness tips | See mood or stress for named individuals |
| Create / Edit / Retire challenges | Access `/wellness` or `/journal` routes |
| View anonymized aggregate analytics | Self-register (must be pre-seeded) |

### Admin Routes

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/admin/dashboard` | Aggregated stats overview |
| GET | `/admin/users` | Student account list |
| POST | `/admin/users/toggle/<id>` | Activate / Deactivate account |
| GET/POST | `/admin/tips` | Manage wellness tips (CRUD) |
| GET/POST | `/admin/challenges` | Manage challenges (CRUD) |

### Admin Security
- All `/admin/*` routes protected by `@admin_required` decorator
- Admin accounts are **pre-created only** — no public registration route
- Admin actions logged at INFO level (content creation, account changes)

### Deliverables
- [x] `app/routes/admin.py` — All admin panel routes
- [x] Admin templates: `admin/dashboard.html`, `admin/users.html`, `admin/tips.html`, `admin/challenges.html`
- [x] Pre-seeded admin account: `admin@wellvia.edu` / `Admin@123`

---

## Phase 9 — UI/UX & Frontend Templates

**Goal:** Build a responsive, accessible, and visually engaging frontend using Bootstrap 5 and Jinja2.

### Template Hierarchy

```
base.html               ← Head, Navbar, Flash messages, Footer
├── auth/
│   ├── login.html
│   └── register.html
├── dashboard.html
├── wellness/
│   ├── log.html
│   └── history.html
├── journal/
│   ├── index.html
│   └── edit.html
├── tips/
│   └── index.html
├── challenges/
│   └── index.html
├── progress.html
├── profile.html
├── admin/
│   ├── dashboard.html
│   ├── users.html
│   ├── tips.html
│   └── challenges.html
└── errors/
    ├── 403.html
    ├── 404.html
    └── 500.html
```

### Responsive Breakpoints
| Device | Resolution | Support |
|--------|-----------|---------|
| Desktop | 1920×1080+ | ✅ Full |
| Laptop | 1366×768 | ✅ Full |
| Tablet | 768×1024 | ✅ Bootstrap grid |
| Mobile | 360×640 | ✅ Hamburger nav |

### UI Components
- **Dashboard:** Score cards (Points, Streak, Wellness Score) → Active Challenge → Daily Tip → Mini-charts
- **Admin Dashboard:** Dark navbar variant, wide data tables, aggregate charts
- **Navigation:** Responsive collapse (hamburger on mobile) with role-aware menu items
- **Forms:** Bootstrap `.form-control` + client-side validation + server-side error flash
- **Alerts:** Flask `flash()` messages rendered as Bootstrap `.alert-dismissible`
- **Cards:** Standardized Bootstrap `.card` for tips and challenge widgets

### Deliverables
- [x] `app/static/css/style.css` — Custom responsive CSS with Wellvia design system
- [x] `app/static/js/charts.js` — Chart.js integration helpers
- [x] 18 Jinja2 HTML templates (listed above)
- [x] `base.html` with DRY template inheritance (`{% extends 'base.html' %}`)

---

## Phase 10 — Testing, Verification & Deployment

**Goal:** Verify system correctness, initialize production database, and push codebase to version control.

### Route Design Summary

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| GET/POST | `/auth/register` | Public | Student registration |
| GET/POST | `/auth/login` | Public | Authentication |
| GET | `/auth/logout` | Authenticated | Session destruction |
| GET | `/dashboard` | Student | Personalized daily hub |
| GET/POST | `/wellness/log` | Student | Submit daily wellness form |
| GET | `/wellness/history` | Student | View past records |
| GET | `/journal` | Student | Journal history |
| POST | `/journal/create` | Student | Create entry |
| POST | `/journal/delete/<id>` | Student | Delete own entry |
| GET | `/tips` | Student | Browse wellness tips |
| GET | `/challenges` | Student | View active challenges |
| POST | `/challenges/<id>/complete` | Student | Mark complete |
| GET | `/progress` | Student | Personal analytics & charts |
| GET | `/api/my-charts` | Student | JSON chart data for Chart.js |
| GET/POST | `/profile` | Student | View/edit profile |
| GET | `/admin/dashboard` | Admin | Aggregate stats |
| GET | `/admin/users` | Admin | User management |
| POST | `/admin/users/toggle/<id>` | Admin | Activate/deactivate |
| GET/POST | `/admin/tips` | Admin | Tips CRUD |
| GET/POST | `/admin/challenges` | Admin | Challenges CRUD |

### Test Cases

| ID | Feature | Scenario | Expected Result |
|----|---------|----------|----------------|
| TC-01 | Auth | Register with existing email | Form fails: "Email already in use" |
| TC-02 | Auth | Login with wrong password | Form fails: "Invalid credentials" |
| TC-03 | Wellness | Submit 30 hours sleep | Validation fails, DB unchanged |
| TC-04 | Wellness | Submit valid metrics | Success, dashboard updates |
| TC-05 | Journal | Student A tries Student B's entry ID | Returns 403 / 404 |
| TC-06 | Admin | Access `/admin/dashboard` as student | Returns 403 Forbidden |
| TC-07 | Admin | Create new tip | Tip appears in `wellness_tips` table |
| TC-08 | Scoring | Log only sleep (no other metrics) | Score calculated from 1 component |
| TC-09 | Gamification | 7 consecutive daily logs | "7-Day Streak" badge awarded |
| TC-10 | Privacy | Admin queries analytics | No user_id in returned data |

### Unit Test Results
```
python -m unittest discover tests
..............
Ran 14 tests in 0.001s
OK
```

### Error Handling
| Error | Response |
|-------|----------|
| 404 Not Found | Friendly "Page not found" template + dashboard link |
| 403 Forbidden | Role access denied page |
| 500 Internal Error | "Something went wrong" page (stack trace logged server-side) |
| Form errors | Flask `flash()` messages (masked DB errors) |

### Deliverables
- [x] `tests/test_scoring.py` — Wellness score formula unit tests
- [x] `tests/test_validation.py` — Input validation unit tests
- [x] `init_db.py` — Database initializer with MySQL + SQLite auto-fallback
- [x] `.gitignore` — Excludes `.env`, `wellness.db`, `__pycache__`
- [x] Git commit `7c48373` — Pushed to `https://github.com/goxxie08/Wellvia.git`

---

## Quick Start Guide

```powershell
# 1. Clone the repository
git clone https://github.com/goxxie08/Wellvia.git
cd Wellvia

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment (copy and edit credentials)
copy .env.example .env

# 4. Initialize database (auto-detects MySQL or falls back to SQLite)
python init_db.py

# 5. Run the development server
python run.py
```

Then open **http://localhost:5000** in your browser.

| Account Type | URL | Default Credentials |
|-------------|-----|-------------------|
| Student | `/auth/register` | Register a new account |
| Admin | `/auth/login` | `admin@wellvia.edu` / `Admin@123` |

---

## Future Enhancements (Out of Current Scope)

| Enhancement | Description |
|-------------|-------------|
| 🔌 REST API | Decouple frontend into React/Vue SPA communicating via JSON API |
| 📱 Mobile App | Android companion app consuming the REST API |
| 🔔 Push Notifications | Celery/Redis task queue for daily reminder emails |
| ⌚ Wearable Integration | Google Fit / Apple Health API data sync |
| 🤖 Smart Insights | ML-based pattern detection instead of rule-based observations |
| 🌍 Multi-Institution | Multi-tenant architecture for multiple colleges |

---

## Traceability Matrix

| Project Objective | Architecture Component | Module | Status |
|-------------------|----------------------|--------|--------|
| Holistic Wellness Tracking | Application Layer | Wellness Tracking Service | ✅ |
| Self-Awareness & Patterns | Data + Analytics | Analytics Service + Chart.js | ✅ |
| Gamification | Business Logic Layer | Gamification & Achievements | ✅ |
| Personal Reflection | Application + Data | Private Journal Module | ✅ |
| Content & Challenges | Application Layer | Tips + Challenge Modules | ✅ |
| Institutional Insights | Data Access Layer | Admin Analytics Reporting | ✅ |
| Privacy & Security | All Layers | RBAC + Parameterized SQL + Bcrypt | ✅ |
| Responsive UI | Presentation Layer | Bootstrap 5 + Jinja2 Templates | ✅ |

---

*Wellvia — Student Wellness Companion | Built with Flask · MySQL · Bootstrap 5 · Chart.js*
