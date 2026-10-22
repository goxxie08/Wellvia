import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { ShieldCheck, Users, Activity, Moon, Droplet, BookOpen, Smile, Award } from 'lucide-react';
import { Bar, Doughnut } from 'react-chartjs-2';

export function AdminDashboardPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const res = await api.getAdminAnalytics();
        if (res.success) {
          setAnalytics(res.analytics);
        }
      } catch (err) {
        setError(err.message || 'Failed to load administrative analytics.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Compiling aggregate population metrics...</p>
      </div>
    );
  }

  const a = analytics || {};

  // Mood chart
  const moodChartData = {
    labels: ['Very Happy', 'Happy', 'Neutral', 'Sad', 'Very Sad'],
    datasets: [{
      label: 'Student Responses (Past 30 Days)',
      data: a.mood_dist || [0, 0, 0, 0, 0],
      backgroundColor: ['#10b981', '#14b8a6', '#0ea5e9', '#f59e0b', '#f43f5e']
    }]
  };

  // Stress chart
  const stressChartData = {
    labels: ['Very Low', 'Low', 'Moderate', 'High', 'Severe'],
    datasets: [{
      label: 'Student Stress (Past 30 Days)',
      data: a.stress_dist || [0, 0, 0, 0, 0],
      backgroundColor: ['#10b981', '#0ea5e9', '#f59e0b', '#f97316', '#ef4444']
    }]
  };

  // Challenge completions chart
  const challengeChartData = {
    labels: a.challenge_labels || [],
    datasets: [{
      label: 'Completions Count',
      data: a.challenge_data || [],
      backgroundColor: '#8b5cf6',
      borderRadius: 6
    }]
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#94a3b8' } }
    },
    scales: {
      x: { ticks: { color: '#64748b' }, grid: { display: false } },
      y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <ShieldCheck size={30} style={{ color: 'var(--teal-primary)' }} />
          Administrator Executive Dashboard
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Anonymized population-level physical and psychological metrics across the university student cohort.
        </p>
      </div>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem 1rem',
          color: '#fca5a5',
          fontSize: '0.9rem',
          marginBottom: '1.5rem'
        }}>
          {error}
        </div>
      )}

      {/* Aggregate Population Metrics Grid */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem', textTransform: 'uppercase' }}>
            <Users size={16} style={{ color: 'var(--teal-primary)' }} /> Total Students
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fff', marginTop: '0.35rem' }}>
            {a.total_students || 0}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--emerald-primary)', marginTop: '0.2rem' }}>
            {a.active_students || 0} Active Accounts
          </div>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem', textTransform: 'uppercase' }}>
            <Activity size={16} style={{ color: 'var(--emerald-primary)' }} /> Average Score
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fff', marginTop: '0.35rem' }}>
            {a.avg_score != null ? a.avg_score : '—'} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Past 30 Days Mean
          </div>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem', textTransform: 'uppercase' }}>
            <Moon size={16} style={{ color: 'var(--purple-primary)' }} /> Average Sleep
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fff', marginTop: '0.35rem' }}>
            {a.avg_sleep != null ? `${a.avg_sleep} hrs` : '—'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Cohort Nightly Mean
          </div>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem', textTransform: 'uppercase' }}>
            <Droplet size={16} style={{ color: 'var(--cyan-primary)' }} /> Daily Water
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fff', marginTop: '0.35rem' }}>
            {a.avg_water != null ? `${a.avg_water} gls` : '—'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Hydration Mean
          </div>
        </div>
      </div>

      {/* Aggregate Charts Grid */}
      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        
        {/* Mood Distribution */}
        <div className="glass-card" style={{ height: '340px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Smile size={18} style={{ color: 'var(--teal-primary)' }} /> Cohort Mood Distribution
          </h2>
          <div style={{ height: '260px' }}>
            <Bar data={moodChartData} options={barOptions} />
          </div>
        </div>

        {/* Stress Distribution */}
        <div className="glass-card" style={{ height: '340px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Activity size={18} style={{ color: 'var(--rose-primary)' }} /> Cohort Stress Level Breakdown
          </h2>
          <div style={{ height: '260px' }}>
            <Bar data={stressChartData} options={barOptions} />
          </div>
        </div>

      </div>

      {/* Challenge Engagement Leaderboard */}
      {a.challenge_labels && a.challenge_labels.length > 0 && (
        <div className="glass-card" style={{ height: '340px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Award size={18} style={{ color: 'var(--purple-primary)' }} /> Challenge Engagement Volume
          </h2>
          <div style={{ height: '260px' }}>
            <Bar data={challengeChartData} options={barOptions} />
          </div>
        </div>
      )}

    </div>
  );
}
