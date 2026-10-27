# 🎨 Wellvia Frontend — React Single Page Application (SPA)

The frontend of Wellvia is a modern, responsive Single Page Application built with **React 18** and **Vite**, styled using a bespoke vanilla CSS design system featuring dark glassmorphism, fluid typography, and micro-animations.

---

## 🚀 Key Features & Components

### 1. Unified Navigation & Routing
- Configured with React Router (`react-router-dom`) in `src/App.jsx`.
- Role-based route guard in `src/components/common/ProtectedRoute.jsx` for protecting student and administrator portals.

### 2. Intelligent AI Wellness Companion
- Located in `src/components/common/ChatbotDrawer.jsx`.
- Connects to `/api/chat/message` with conversation history and student context.
- Formats markdown messages (bullet points, bold text) smoothly and manages auto-scroll with fallback retry options.
- Includes crisis intervention badges and emergency resource display.

### 3. Redesigned Progress & Analytics Page
- Located in `src/pages/student/ProgressPage.jsx`.
- **Wellness Overview**: Summary cards showing averages, total habits logged, and streak metrics.
- **Daily Wellness Charts**: Dynamic bar charts for Sleep (hrs), Hydration (glasses), Exercise (mins), and Study (hrs) over 7, 14, or 30 days.
- **Your Wellness Analysis**: Personalized habit evaluations highlighting consistency patterns.
- **Areas to Improve**: Actionable targeted advice for low-scoring habit areas.

### 4. Interactive Student Dashboard
- Located in `src/pages/student/DashboardPage.jsx`.
- Displays real-time wellness score (0–100), BMI and Machine Learning Health status, habit quickview cards, rotating daily tips, and active challenges.

### 5. Daily Wellness Logging
- Located in `src/pages/student/DailyLogPage.jsx`.
- Interactive inputs for sleep hours & quality (1–5), water glasses, workout duration & intensity, mood (1–5), stress (1–5), and study hours.

### 6. Administrative Portal
- `src/pages/admin/AdminDashboardPage.jsx`: Visual aggregated campus wellness statistics.
- `src/pages/admin/AdminUsersPage.jsx`: Student account list and activation toggles.
- `src/pages/admin/AdminTipsPage.jsx`: Tip creation, category tagging, and status toggle.
- `src/pages/admin/AdminChallengesPage.jsx`: Challenge creation and reward point assignment.

---

## 📁 Source Directory Structure

```text
frontend/src/
├── api/
│   └── client.js             # Centralized API client wrapper for Flask backend
├── components/
│   ├── common/
│   │   ├── ChatbotDrawer.jsx       # AI Companion chat drawer interface
│   │   ├── FloatingChatButton.jsx  # Floating trigger button for AI Companion
│   │   ├── Navbar.jsx              # Responsive navigation header
│   │   └── ProtectedRoute.jsx      # Authentication & role guard
│   └── student/                    # Student-specific reusable subcomponents
├── pages/
│   ├── auth/
│   │   ├── LoginPage.jsx           # Student & Admin login form
│   │   ├── RegisterPage.jsx        # Student registration form
│   │   └── ForgotPasswordPage.jsx  # Password recovery form
│   ├── student/
│   │   ├── DashboardPage.jsx       # Main student dashboard
│   │   ├── DailyLogPage.jsx        # Daily wellness entry form
│   │   ├── HistoryPage.jsx         # Historical wellness log table
│   │   ├── ProgressPage.jsx        # Redesigned 4-section analytics page
│   │   ├── ChallengesPage.jsx      # Active challenges & progress
│   │   ├── TipsPage.jsx            # Curated wellness tips
│   │   └── BodyMetricsPage.jsx     # BMI calculator & ML health assessment
│   └── admin/
│       ├── AdminDashboardPage.jsx  # Anonymized aggregated reporting
│       ├── AdminUsersPage.jsx      # Student account management
│       ├── AdminTipsPage.jsx       # Campus tip curation
│       └── AdminChallengesPage.jsx # Wellness challenge administration
├── styles/
│   └── main.css                    # Comprehensive CSS tokens, theme & components
├── App.jsx                         # Main route configuration
└── main.jsx                        # React root entry point
```

---

## 🛠️ Development & Build Commands

Inside the `frontend/` directory:

```bash
# Install dependencies
npm install

# Start Vite local development server with Hot Module Replacement (HMR)
npm run dev

# Build production bundle into frontend/dist/ (served automatically by Flask)
npm run build

# Preview the production build locally
npm run preview
```

---

## 🎨 Design System

All styling is consolidated in `src/styles/main.css` utilizing custom CSS custom properties (variables):
- **Theme Palette**: Deep dark background (`#0b1329` / `#0f172a`), emerald brand accents (`#10b981`), cyan highlights (`#06b6d4`), and soft purple indicators (`#8b5cf6`).
- **Glassmorphism**: Translucent card backgrounds (`rgba(15, 23, 42, 0.75)`) with backdrop blur (`blur(12px)`) and subtle borders (`rgba(255, 255, 255, 0.08)`).
- **Typography**: Responsive, modern sans-serif fonts with clear hierarchy.
