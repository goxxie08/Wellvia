import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  Activity, 
  Flame, 
  Star, 
  LogOut, 
  User, 
  Menu, 
  X, 
  Bot, 
  ShieldCheck, 
  BarChart2, 
  Calendar, 
  CheckCircle, 
  BookOpen, 
  Users 
} from 'lucide-react';

export function Navbar({ onOpenChat, isChatOpen }) {
  const { user, isAuthenticated, isStudent, isAdmin, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className={`navbar-custom ${mobileMenuOpen ? 'mobile-menu-open' : ''}`}>
      <div style={{ maxWidth: '1240px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
        
        {/* Brand */}
        <Link to={isAuthenticated ? (isAdmin ? '/admin' : '/dashboard') : '/login'} className="navbar-brand">
          <div className="logo-icon">
            <Activity size={22} />
          </div>
          <span>Wellvia</span>
        </Link>

        {/* Navigation Links */}
        {isAuthenticated && (
          <ul className="nav-links">
            {isStudent && (
              <>
                <li>
                  <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Dashboard
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/wellness" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Daily Log
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/wellness/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    History
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/progress" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Progress
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/challenges" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Challenges
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/tips" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Tips
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/body-metrics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    BMI & Health
                  </NavLink>
                </li>
              </>
            )}

            {isAdmin && (
              <>
                <li>
                  <NavLink to="/admin" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Overview
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/admin/users" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Students
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/admin/tips" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Manage Tips
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/admin/challenges" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    Manage Challenges
                  </NavLink>
                </li>
              </>
            )}
          </ul>
        )}

        {/* Right Action Icons & Auth Profile */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {isAuthenticated ? (
            <>
              {/* Student Points & Streak */}
              {isStudent && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  <span className="badge badge-amber" title="Current Wellness Points">
                    <Flame size={14} />
                    {user?.total_points > 0 ? `${user?.total_points} pts` : '0 pts'}
                  </span>

                  {/* AI Wellness Chat Button */}
                  <button
                    onClick={onOpenChat}
                    className="btn-secondary"
                    style={{
                      padding: '0.45rem 0.75rem',
                      fontSize: '0.82rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                      color: isChatOpen ? 'var(--teal-primary)' : 'var(--text-secondary)',
                      borderColor: isChatOpen ? 'var(--teal-primary)' : undefined,
                      background: isChatOpen ? 'rgba(20, 184, 166, 0.12)' : undefined
                    }}
                    title="Open AI Wellness Companion"
                    aria-label="Open AI Wellness Companion"
                    id="navbarChatToggle"
                  >
                    <Bot size={15} />
                    <span className="hide-on-mobile">AI Chat</span>
                  </button>
                </div>
              )}

              {/* Profile Link */}
              <Link
                to={isAdmin ? '/admin' : '/profile'}
                className="btn-secondary"
                style={{ padding: '0.45rem 0.8rem', fontSize: '0.85rem' }}
                title="View Profile"
              >
                <User size={15} />
                <span>{user?.username}</span>
              </Link>

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="btn-secondary"
                style={{ padding: '0.45rem 0.75rem', color: 'var(--rose-primary)' }}
                title="Log Out Securely"
              >
                <LogOut size={16} />
              </button>
            </>
          ) : (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Link to="/login" className="btn-secondary" style={{ padding: '0.5rem 1rem' }}>
                Log In
              </Link>
              <Link to="/register" className="btn-primary" style={{ padding: '0.5rem 1rem' }}>
                Sign Up
              </Link>
            </div>
          )}

          {/* Mobile hamburger */}
          {isAuthenticated && (
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="btn-secondary"
              style={{ padding: '0.45rem', display: 'none' }}
              id="mobileMenuToggle"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          )}
        </div>

      </div>
    </nav>
  );
}
