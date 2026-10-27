import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client';
import { 
  TrendingUp, 
  Calendar, 
  Moon, 
  Droplet, 
  Activity, 
  BookOpen, 
  Smile, 
  HeartPulse, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  ArrowRight,
  Target,
  Info
} from 'lucide-react';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export function ProgressPage() {
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const fetchProgress = async (selectedDays, isManualRefresh = false) => {
    try {
      if (isManualRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');
      const res = await api.getProgress(selectedDays);
      if (res && res.success) {
        setData(res);
      } else {
        setError('Failed to retrieve progress data.');
      }
    } catch (err) {
      setError(err.message || 'Failed to load progress analytics.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProgress(days);
  }, [days]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading your personalized wellness analytics...</p>
      </div>
    );
  }

  const chartData = data?.chart_data || {};
  const overview = data?.overview || chartData?.overview || {};
  const analysis = data?.analysis || chartData?.analysis || [];
  const areasToImprove = data?.areas_to_improve || chartData?.areas_to_improve || [];
  const labels = chartData.labels || [];

  // Common chart scales and plugin styles
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#ffffff',
        bodyColor: '#e2e8f0',
        borderColor: 'rgba(255, 255, 255, 0.12)',
        borderWidth: 1,
        padding: 10,
        boxPadding: 4,
        usePointStyle: true,
        cornerRadius: 8,
        titleFont: { family: 'Inter', size: 12, weight: '600' },
        bodyFont: { family: 'Inter', size: 12 }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
      }
    }
  };

  // 1. Sleep Bar Chart
  const sleepChartData = {
    labels,
    datasets: [
      {
        label: 'Sleep Duration (hrs)',
        data: chartData.sleep || [],
        backgroundColor: 'rgba(139, 92, 246, 0.75)',
        hoverBackgroundColor: '#8b5cf6',
        borderRadius: 6,
        borderSkipped: false
      }
    ]
  };

  const sleepOptions = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales.y,
        beginAtZero: true,
        suggestedMax: 10,
        ticks: {
          color: '#8b5cf6',
          font: { family: 'Inter', size: 11 },
          callback: (val) => `${val}h`
        }
      }
    },
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        ...commonOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => {
            const val = ctx.raw;
            if (val === null || val === undefined) return ' Sleep: Not logged';
            const status = val >= 7 && val <= 9 ? ' (On Target)' : val < 7 ? ' (Below Target)' : ' (Above Target)';
            return ` Sleep: ${val} hrs${status}`;
          }
        }
      }
    }
  };

  // 2. Hydration Bar Chart
  const waterChartData = {
    labels,
    datasets: [
      {
        label: 'Water Intake (glasses)',
        data: chartData.water || [],
        backgroundColor: 'rgba(14, 165, 233, 0.75)',
        hoverBackgroundColor: '#0ea5e9',
        borderRadius: 6,
        borderSkipped: false
      }
    ]
  };

  const waterOptions = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales.y,
        beginAtZero: true,
        suggestedMax: 10,
        ticks: {
          color: '#0ea5e9',
          font: { family: 'Inter', size: 11 },
          callback: (val) => `${val} gl`
        }
      }
    },
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        ...commonOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => {
            const val = ctx.raw;
            if (val === null || val === undefined) return ' Hydration: Not logged';
            const liters = (val * 0.25).toFixed(1);
            const status = val >= 8 ? ' (Target Met)' : ' (Goal: 8 gl)';
            return ` Hydration: ${val} glasses (~${liters}L)${status}`;
          }
        }
      }
    }
  };

  // 3. Physical Activity Bar Chart
  const exerciseChartData = {
    labels,
    datasets: [
      {
        label: 'Exercise Duration (mins)',
        data: chartData.exercise || [],
        backgroundColor: 'rgba(16, 185, 129, 0.75)',
        hoverBackgroundColor: '#10b981',
        borderRadius: 6,
        borderSkipped: false
      }
    ]
  };

  const exerciseOptions = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales.y,
        beginAtZero: true,
        suggestedMax: 60,
        ticks: {
          color: '#10b981',
          font: { family: 'Inter', size: 11 },
          callback: (val) => `${val}m`
        }
      }
    },
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        ...commonOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => {
            const val = ctx.raw;
            if (val === null || val === undefined) return ' Activity: Not logged';
            const status = val >= 30 ? ' (Target Met)' : ' (Goal: 30+ mins)';
            return ` Activity: ${val} mins${status}`;
          }
        }
      }
    }
  };

  // 4. Study Hours Bar Chart
  const studyChartData = {
    labels,
    datasets: [
      {
        label: 'Study Duration (hrs)',
        data: chartData.study || [],
        backgroundColor: 'rgba(245, 158, 11, 0.75)',
        hoverBackgroundColor: '#f59e0b',
        borderRadius: 6,
        borderSkipped: false
      }
    ]
  };

  const studyOptions = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales.y,
        beginAtZero: true,
        suggestedMax: 8,
        ticks: {
          color: '#f59e0b',
          font: { family: 'Inter', size: 11 },
          callback: (val) => `${val}h`
        }
      }
    },
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        ...commonOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => {
            const val = ctx.raw;
            if (val === null || val === undefined) return ' Study: Not logged';
            return ` Study: ${val} hrs`;
          }
        }
      }
    }
  };

  // 5. Stress Level Bar Chart (Discrete Scale 1-5)
  const stressChartData = {
    labels,
    datasets: [
      {
        label: 'Stress Rating (1-5)',
        data: chartData.stress || [],
        backgroundColor: (context) => {
          const val = context.raw;
          if (val == null) return 'transparent';
          if (val >= 4) return 'rgba(244, 63, 94, 0.85)';
          if (val === 3) return 'rgba(245, 158, 11, 0.85)';
          return 'rgba(20, 184, 166, 0.85)';
        },
        borderRadius: 6,
        borderSkipped: false
      }
    ]
  };

  const stressOptions = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales.y,
        min: 1,
        max: 5,
        ticks: {
          stepSize: 1,
          color: '#f43f5e',
          font: { family: 'Inter', size: 10 },
          callback: (val) => {
            const map = { 1: 'Calm', 2: 'Low', 3: 'Mod', 4: 'High', 5: 'Sev' };
            return map[val] || val;
          }
        }
      }
    },
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        ...commonOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => {
            const val = ctx.raw;
            if (val === null || val === undefined) return ' Stress: Not logged';
            const labelsMap = { 
              1: '1 - Calm 🧘', 
              2: '2 - Low 😌', 
              3: '3 - Moderate 😐', 
              4: '4 - High 😰', 
              5: '5 - Severe 😫' 
            };
            return ` Stress: ${labelsMap[val] || `${val}/5`}`;
          }
        }
      }
    }
  };

  // 6. Mood Categorical Bar Chart
  const moodChartData = {
    labels,
    datasets: [
      {
        label: 'Mood Category',
        data: chartData.mood || [],
        backgroundColor: (context) => {
          const val = context.raw;
          if (val == null) return 'transparent';
          const colors = {
            5: 'rgba(16, 185, 129, 0.85)',
            4: 'rgba(20, 184, 166, 0.85)',
            3: 'rgba(245, 158, 11, 0.85)',
            2: 'rgba(249, 115, 22, 0.85)',
            1: 'rgba(244, 63, 94, 0.85)'
          };
          return colors[val] || 'rgba(148, 163, 184, 0.5)';
        },
        borderRadius: 6,
        borderSkipped: false
      }
    ]
  };

  const moodOptions = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales.y,
        min: 1,
        max: 5,
        ticks: {
          stepSize: 1,
          color: '#14b8a6',
          font: { family: 'Inter', size: 10 },
          callback: (val) => {
            const map = { 1: 'Sad 😞', 2: 'Low 🙁', 3: 'Neutral 😐', 4: 'Good 🙂', 5: 'Great 😊' };
            return map[val] || val;
          }
        }
      }
    },
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        ...commonOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => {
            const val = ctx.raw;
            if (val === null || val === undefined) return ' Mood: Not logged';
            const map = {
              5: 'Great 😊 (Very Happy / Energized)',
              4: 'Good 🙂 (Content)',
              3: 'Neutral 😐 (Neutral / Okay)',
              2: 'Low 🙁 (Down)',
              1: 'Sad 😞 (Depressed)'
            };
            return ` Mood: ${map[val] || `Category ${val}`}`;
          }
        }
      }
    }
  };

  // Helper for analysis badge styles
  const getAnalysisBadge = (status) => {
    switch (status) {
      case 'good':
        return {
          text: 'On Track',
          bg: 'rgba(16, 185, 129, 0.15)',
          color: '#34d399',
          border: '1px solid rgba(16, 185, 129, 0.3)'
        };
      case 'moderate':
        return {
          text: 'Moderate',
          bg: 'rgba(20, 184, 166, 0.15)',
          color: '#2dd4bf',
          border: '1px solid rgba(20, 184, 166, 0.3)'
        };
      case 'needs_improvement':
        return {
          text: 'Needs Focus',
          bg: 'rgba(244, 63, 94, 0.15)',
          color: '#fb7185',
          border: '1px solid rgba(244, 63, 94, 0.3)'
        };
      case 'attention':
        return {
          text: 'Elevated',
          bg: 'rgba(245, 158, 11, 0.15)',
          color: '#fbbf24',
          border: '1px solid rgba(245, 158, 11, 0.3)'
        };
      default:
        return {
          text: 'Needs Data',
          bg: 'rgba(100, 116, 139, 0.15)',
          color: '#94a3b8',
          border: '1px solid rgba(100, 116, 139, 0.3)'
        };
    }
  };

  const getMetricIcon = (key) => {
    switch (key) {
      case 'sleep': return <Moon size={18} style={{ color: 'var(--purple-primary)' }} />;
      case 'water': return <Droplet size={18} style={{ color: 'var(--cyan-primary)' }} />;
      case 'exercise': return <Activity size={18} style={{ color: 'var(--emerald-primary)' }} />;
      case 'stress': return <HeartPulse size={18} style={{ color: 'var(--rose-primary)' }} />;
      case 'mood': return <Smile size={18} style={{ color: 'var(--teal-primary)' }} />;
      case 'study': return <BookOpen size={18} style={{ color: 'var(--amber-primary)' }} />;
      default: return <Sparkles size={18} style={{ color: 'var(--teal-primary)' }} />;
    }
  };

  return (
    <div>
      {/* Top Header with Title, Refresh, and Days Filter */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem',
        marginBottom: '1.75rem'
      }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <TrendingUp size={28} style={{ color: 'var(--teal-primary)' }} />
            Progress & Wellness Analytics
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Personalized habit analysis, daily wellness metrics, and actionable areas to improve.
          </p>
        </div>

        {/* Filter and Refresh Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={() => fetchProgress(days, true)}
            disabled={refreshing}
            className="btn-secondary"
            title="Refresh latest saved wellness records"
            style={{
              padding: '0.45rem 0.75rem',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              cursor: refreshing ? 'not-allowed' : 'pointer'
            }}
          >
            <RefreshCw size={14} className={refreshing ? 'spin-icon' : ''} />
            <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>

          <div style={{
            display: 'flex',
            gap: '0.35rem',
            background: 'rgba(15, 23, 42, 0.8)',
            padding: '0.3rem',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--bg-card-border)'
          }}>
            {[7, 14, 30].map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={days === d ? 'btn-primary' : 'btn-secondary'}
                style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }}
              >
                {d} Days
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem 1rem',
          color: '#fca5a5',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.5rem'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* =========================================================================
          SECTION 1: WELLNESS OVERVIEW
          ========================================================================= */}
      <section style={{ marginBottom: '2.5rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.5rem',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Calendar size={20} style={{ color: 'var(--cyan-primary)' }} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff' }}>Wellness Overview</h2>
          </div>
          <span style={{
            fontSize: '0.85rem',
            color: 'var(--text-muted)',
            background: 'rgba(255, 255, 255, 0.04)',
            padding: '0.25rem 0.65rem',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--bg-card-border)'
          }}>
            {overview.date_range_label || `Past ${days} Days`} • {overview.logged_days_count ?? 0} of {days} days logged
          </span>
        </div>

        {overview.logged_days_count === 0 ? (
          <div className="glass-card" style={{ padding: '1.75rem', textAlign: 'center' }}>
            <Info size={28} style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fff', marginBottom: '0.35rem' }}>
              No wellness records logged in this timeframe
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
              Start recording your sleep, hydration, and activity to view your personalized averages and progress trends.
            </p>
            <Link to="/wellness" className="btn-primary" style={{ padding: '0.45rem 1rem', fontSize: '0.85rem', textDecoration: 'none', display: 'inline-block' }}>
              Log Today's Wellness
            </Link>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '1rem'
          }}>
            {/* Sleep Summary Card */}
            <div className="glass-card" style={{ padding: '1.1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Avg Sleep</span>
                <Moon size={16} style={{ color: 'var(--purple-primary)' }} />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 700, color: '#fff' }}>
                {overview.sleep?.avg != null ? `${overview.sleep.avg} hrs` : <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Not logged</span>}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {overview.sleep?.avg != null ? `${overview.sleep.days_logged} nights logged • Target 7-9h` : 'No sleep data recorded'}
              </div>
            </div>

            {/* Hydration Summary Card */}
            <div className="glass-card" style={{ padding: '1.1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Daily Water</span>
                <Droplet size={16} style={{ color: 'var(--cyan-primary)' }} />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 700, color: '#fff' }}>
                {overview.water?.avg != null ? `${overview.water.avg} gl` : <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Not logged</span>}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {overview.water?.avg != null ? `~${(overview.water.avg * 0.25).toFixed(1)}L/day • Target 8 gl` : 'No water data recorded'}
              </div>
            </div>

            {/* Activity Summary Card */}
            <div className="glass-card" style={{ padding: '1.1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Physical Activity</span>
                <Activity size={16} style={{ color: 'var(--emerald-primary)' }} />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 700, color: '#fff' }}>
                {overview.exercise?.avg != null ? `${overview.exercise.avg} mins` : <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Not logged</span>}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {overview.exercise?.total != null ? `Total: ${overview.exercise.total} mins • Target 30m` : 'No exercise recorded'}
              </div>
            </div>

            {/* Study Summary Card */}
            <div className="glass-card" style={{ padding: '1.1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Study Hours</span>
                <BookOpen size={16} style={{ color: 'var(--amber-primary)' }} />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 700, color: '#fff' }}>
                {overview.study?.avg != null ? `${overview.study.avg} hrs` : <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Not logged</span>}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {overview.study?.total != null ? `Total: ${overview.study.total} hrs logged` : 'No study data recorded'}
              </div>
            </div>

            {/* Mood Summary Card */}
            <div className="glass-card" style={{ padding: '1.1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Recent Mood</span>
                <Smile size={16} style={{ color: 'var(--teal-primary)' }} />
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>
                {overview.mood?.dominant ? overview.mood.dominant : <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Not logged</span>}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {overview.mood?.days_logged > 0 ? `${overview.mood.days_logged} check-ins recorded` : 'No mood check-ins'}
              </div>
            </div>

            {/* Stress Summary Card */}
            <div className="glass-card" style={{ padding: '1.1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Stress Pattern</span>
                <HeartPulse size={16} style={{ color: 'var(--rose-primary)' }} />
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>
                {overview.stress?.label ? `${overview.stress.label}` : <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Not logged</span>}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {overview.stress?.avg != null ? `Avg ${overview.stress.avg}/5 • ${overview.stress.days_logged} logged` : 'No stress records'}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* =========================================================================
          SECTION 2: DAILY WELLNESS CHARTS (RESPONSIVE BAR CHARTS)
          ========================================================================= */}
      <section style={{ marginBottom: '2.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={20} style={{ color: 'var(--teal-primary)' }} /> Daily Wellness Charts
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Compare your day-to-day wellness activities. Empty days are left blank to preserve true data accuracy.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.25rem'
        }}>
          {/* Chart 1: Sleep Duration */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fff', fontSize: '0.98rem' }}>
                <Moon size={18} style={{ color: 'var(--purple-primary)' }} /> Sleep Duration
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--purple-primary)', background: 'rgba(139, 92, 246, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                Unit: Hours (Goal: 7–9h)
              </span>
            </div>
            <div style={{ height: '220px' }}>
              <Bar data={sleepChartData} options={sleepOptions} />
            </div>
          </div>

          {/* Chart 2: Water Intake */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fff', fontSize: '0.98rem' }}>
                <Droplet size={18} style={{ color: 'var(--cyan-primary)' }} /> Water Intake
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--cyan-primary)', background: 'rgba(14, 165, 233, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                Unit: Glasses (Goal: 8 gl)
              </span>
            </div>
            <div style={{ height: '220px' }}>
              <Bar data={waterChartData} options={waterOptions} />
            </div>
          </div>

          {/* Chart 3: Physical Activity */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fff', fontSize: '0.98rem' }}>
                <Activity size={18} style={{ color: 'var(--emerald-primary)' }} /> Physical Movement
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--emerald-primary)', background: 'rgba(16, 185, 129, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                Unit: Minutes (Goal: 30+m)
              </span>
            </div>
            <div style={{ height: '220px' }}>
              <Bar data={exerciseChartData} options={exerciseOptions} />
            </div>
          </div>

          {/* Chart 4: Academic Study */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fff', fontSize: '0.98rem' }}>
                <BookOpen size={18} style={{ color: 'var(--amber-primary)' }} /> Academic Study Hours
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--amber-primary)', background: 'rgba(245, 158, 11, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                Unit: Hours
              </span>
            </div>
            <div style={{ height: '220px' }}>
              <Bar data={studyChartData} options={studyOptions} />
            </div>
          </div>

          {/* Chart 5: Stress Levels */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fff', fontSize: '0.98rem' }}>
                <HeartPulse size={18} style={{ color: 'var(--rose-primary)' }} /> Stress Level Rating
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--rose-primary)', background: 'rgba(244, 63, 94, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                Scale: 1 (Calm) – 5 (Severe)
              </span>
            </div>
            <div style={{ height: '220px' }}>
              <Bar data={stressChartData} options={stressOptions} />
            </div>
          </div>

          {/* Chart 6: Mood (Categorical Bar Chart) */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fff', fontSize: '0.98rem' }}>
                <Smile size={18} style={{ color: 'var(--teal-primary)' }} /> Daily Mood State
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--teal-primary)', background: 'rgba(20, 184, 166, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                Categorical: Sad to Great
              </span>
            </div>
            <div style={{ height: '220px' }}>
              <Bar data={moodChartData} options={moodOptions} />
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 3: YOUR WELLNESS ANALYSIS
          ========================================================================= */}
      <section style={{ marginBottom: '2.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={20} style={{ color: 'var(--amber-primary)' }} /> Your Wellness Analysis
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Observations and practical suggestions derived from your recent self-reported habits.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.25rem'
        }}>
          {analysis.map((item) => {
            const badge = getAnalysisBadge(item.status);
            return (
              <div
                key={item.key}
                className="glass-card"
                style={{
                  padding: '1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.85rem'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontWeight: 600, color: '#fff', fontSize: '0.98rem' }}>
                      {getMetricIcon(item.key)}
                      {item.title}
                    </div>
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      padding: '0.2rem 0.55rem',
                      borderRadius: '12px',
                      background: badge.bg,
                      color: badge.color,
                      border: badge.border
                    }}>
                      {badge.text}
                    </span>
                  </div>

                  <div style={{
                    fontSize: '0.78rem',
                    color: 'var(--text-muted)',
                    marginBottom: '0.65rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span>{item.target_label}</span>
                    {item.logged_count > 0 && <span>• {item.logged_count} days logged</span>}
                  </div>

                  <p style={{ color: 'var(--text-primary)', fontSize: '0.88rem', lineHeight: '1.5' }}>
                    {item.observation}
                  </p>
                </div>

                <div style={{
                  background: 'rgba(15, 23, 42, 0.65)',
                  border: '1px solid var(--bg-card-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.75rem',
                  fontSize: '0.82rem',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.45rem'
                }}>
                  <Sparkles size={14} style={{ color: 'var(--teal-primary)', flexShrink: 0, marginTop: '2px' }} />
                  <span>{item.recommendation}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* =========================================================================
          SECTION 4: AREAS TO IMPROVE
          ========================================================================= */}
      <section style={{ marginBottom: '2.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Target size={20} style={{ color: 'var(--rose-primary)' }} /> Areas to Improve
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Actionable habit focus areas prioritized from your recent records to help you make manageable improvements.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {areasToImprove.map((area, idx) => {
            const isAllGood = area.is_all_good;
            const isInsufficient = area.is_insufficient;

            let borderTheme = '4px solid var(--teal-primary)';
            if (isAllGood) {
              borderTheme = '4px solid var(--emerald-primary)';
            } else if (isInsufficient) {
              borderTheme = '4px solid var(--cyan-primary)';
            } else if (idx === 0) {
              borderTheme = '4px solid var(--amber-primary)';
            }

            return (
              <div
                key={idx}
                className="glass-card"
                style={{
                  padding: '1.25rem 1.5rem',
                  borderLeft: borderTheme
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '0.5rem',
                  marginBottom: '0.5rem'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    {isAllGood ? (
                      <CheckCircle2 size={20} style={{ color: 'var(--emerald-primary)' }} />
                    ) : isInsufficient ? (
                      <Info size={20} style={{ color: 'var(--cyan-primary)' }} />
                    ) : (
                      <Target size={20} style={{ color: idx === 0 ? 'var(--amber-primary)' : 'var(--teal-primary)' }} />
                    )}
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fff' }}>
                      {area.headline}
                    </h3>
                  </div>

                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '12px',
                    background: isAllGood
                      ? 'rgba(16, 185, 129, 0.15)'
                      : isInsufficient
                      ? 'rgba(14, 165, 233, 0.15)'
                      : idx === 0
                      ? 'rgba(245, 158, 11, 0.15)'
                      : 'rgba(20, 184, 166, 0.15)',
                    color: isAllGood
                      ? '#34d399'
                      : isInsufficient
                      ? '#38bdf8'
                      : idx === 0
                      ? '#fbbf24'
                      : '#2dd4bf'
                  }}>
                    {isAllGood ? 'Healthy Habits' : isInsufficient ? 'Getting Started' : `Priority #${area.priority}`}
                  </span>
                </div>

                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.85rem', lineHeight: '1.5' }}>
                  {area.reason}
                </p>

                <div style={{
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: '1px solid var(--bg-card-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.85rem 1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '0.75rem'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff', fontSize: '0.88rem' }}>
                    <span style={{ fontWeight: 600, color: 'var(--teal-primary)' }}>Recommended Next Step:</span>
                    <span>{area.action_step}</span>
                  </div>

                  <Link
                    to="/wellness"
                    className="btn-secondary"
                    style={{
                      padding: '0.35rem 0.8rem',
                      fontSize: '0.8rem',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem'
                    }}
                  >
                    <span>Log Habit</span>
                    <ArrowRight size={14} />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

