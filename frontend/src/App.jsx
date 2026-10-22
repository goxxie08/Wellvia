import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { MascotBarnaby } from './components/common/MascotBarnaby';
import { ChatbotDrawer } from './components/common/ChatbotDrawer';

// Auth Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { ForgotPasswordPage } from './pages/auth/ForgotPasswordPage';

// Student Pages
import { DashboardPage } from './pages/student/DashboardPage';
import { BodyMetricsPage } from './pages/student/BodyMetricsPage';
import { WellnessLogPage } from './pages/student/WellnessLogPage';
import { HistoryPage } from './pages/student/HistoryPage';
import { ProgressPage } from './pages/student/ProgressPage';
import { ChallengesPage } from './pages/student/ChallengesPage';
import { TipsPage } from './pages/student/TipsPage';
import { ProfilePage } from './pages/student/ProfilePage';

// Admin Pages
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage';
import { AdminUsersPage } from './pages/admin/AdminUsersPage';
import { AdminTipsPage } from './pages/admin/AdminTipsPage';
import { AdminChallengesPage } from './pages/admin/AdminChallengesPage';

function RootRedirect() {
  const { user, isAuthenticated, loading } = useAuth();
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role === 'admin') return <Navigate to="/admin" replace />;
  return <Navigate to="/dashboard" replace />;
}

function MainLayout() {
  const { isAuthenticated, isStudent } = useAuth();
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="app-container">
      {/* Ambient background blur elements */}
      <div className="ambient-background">
        <div className="ambient-blob blob-1" />
        <div className="ambient-blob blob-2" />
        <div className="ambient-blob blob-3" />
      </div>

      <Navbar onOpenChat={() => setChatOpen(true)} isChatOpen={chatOpen} />

      <main className="main-content">
        <Routes>
          {/* Root Redirect */}
          <Route path="/" element={<RootRedirect />} />

          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />

          {/* Student Protected Routes */}
          <Route path="/dashboard" element={<ProtectedRoute role="student"><DashboardPage /></ProtectedRoute>} />
          <Route path="/body-metrics" element={<ProtectedRoute role="student"><BodyMetricsPage /></ProtectedRoute>} />
          <Route path="/wellness" element={<ProtectedRoute role="student"><WellnessLogPage /></ProtectedRoute>} />
          <Route path="/wellness/history" element={<ProtectedRoute role="student"><HistoryPage /></ProtectedRoute>} />
          <Route path="/progress" element={<ProtectedRoute role="student"><ProgressPage /></ProtectedRoute>} />
          <Route path="/challenges" element={<ProtectedRoute role="student"><ChallengesPage /></ProtectedRoute>} />
          <Route path="/tips" element={<ProtectedRoute role="student"><TipsPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute role="student"><ProfilePage /></ProtectedRoute>} />

          {/* Admin Protected Routes */}
          <Route path="/admin" element={<ProtectedRoute role="admin"><AdminDashboardPage /></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute role="admin"><AdminUsersPage /></ProtectedRoute>} />
          <Route path="/admin/tips" element={<ProtectedRoute role="admin"><AdminTipsPage /></ProtectedRoute>} />
          <Route path="/admin/challenges" element={<ProtectedRoute role="admin"><AdminChallengesPage /></ProtectedRoute>} />

          {/* Catch-all */}
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </main>

      {/* Interactive Mascot Barnaby & AI Chatbot for logged-in students */}
      {isAuthenticated && isStudent && (
        <>
          <ChatbotDrawer
            isOpen={chatOpen}
            onClose={() => setChatOpen(false)}
            onToggle={() => setChatOpen((prev) => !prev)}
          />
          <MascotBarnaby
            onOpenChat={() => setChatOpen((prev) => !prev)}
            isChatOpen={chatOpen}
          />
        </>
      )}

      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </BrowserRouter>
  );
}
