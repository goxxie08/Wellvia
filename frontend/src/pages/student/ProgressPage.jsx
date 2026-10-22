import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { 
  BarChart2, 
  TrendingUp, 
  Sparkles, 
  Calendar, 
  PieChart as PieIcon, 
  Activity, 
  Scale 
} from 'lucide-react';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export function ProgressPage() {
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchProgress = async (selectedDays) => {
    try {
      setLoading(true);
      const res = await api.getProgress(selectedDays);
      if (res.success) {
        setData(res);
      }
    } catch (err) {
      setError(err.message || 'Failed to load progress analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProgress(days);
  }, [days]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Compiling wellness time-series charts...</p>
      </div>
    );
  }

  const chartData = data?.chart_data || {};
  const insights = data?.insights || [];
  const labels = chartData.labels || [];

  // Line Chart 1: Score & Sleep & Study Trends
  const trendLineData = {
    labels,
    datasets: [
      {
        label: 'Wellness Score',
        data: chartData.score || [],
        borderColor: '#14b8a6',
        backgroundColor: 'rgba(20, 184, 166, 0.12)',
        fill: true,
        tension: 0.35,
        yAxisID: 'yScore',
      },
      {
        label: 'Sleep (Hours)',
        data: chartData.sleep || [],
        borderColor: '#8b5cf6',
        backgroundColor: 'transparent',
        borderDash: [4, 4],
        tension: 0.3,
        yAxisID: 'yHours',
      },
      {
        label: 'Study (Hours)',
        data: chartData.study || [],
        borderColor: '#f59e0b',
        backgroundColor: 'transparent',
        tension: 0.3,
        yAxisID: 'yHours',
      }
    ]
  };

  const trendLineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        labels: { color: '#94a3b8', font: { family: 'Inter' } }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#fff',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#64748b' }
      },
      yScore: {
        type: 'linear',
        position: 'left',
        min: 0,
        max: 100,
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#14b8a6' },
        title: { display: true, text: 'Score', color: '#14b8a6' }
      },
      yHours: {
        type: 'linear',
        position: 'right',
        min: 0,
        max: 16,
        grid: { drawOnChartArea: false },
        ticks: { color: '#f59e0b' },
        title: { display: true, text: 'Hours', color: '#f59e0b' }
      }
    }
  };

  // Doughnut Chart: Habit Logging Completeness
  const habitCompletion = chartData.habit_completion || { labels: [], counts: [] };
  const doughnutData = {
    labels: habitCompletion.labels,
    datasets: [
      {
        data: habitCompletion.counts,
        backgroundColor: [
          '#8b5cf6', // Sleep
          '#0ea5e9', // Hydration
          '#10b981', // Exercise
          '#f59e0b', // Mood
          '#f43f5e', // Stress
          '#14b8a6'  // Study
        ],
        borderWidth: 2,
        borderColor: '#0f172a'
      }
    ]
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
      }
    }
  };

  // Line Chart: BMI and Weight Progression
  const bmiHist = chartData.bmi_history || { labels: [], bmi: [], weight: [] };
  const bmiTrendData = {
    labels: bmiHist.labels,
    datasets: [
      {
        label: 'BMI Trend',
        data: bmiHist.bmi,
        borderColor: '#0ea5e9',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        fill: true,
        tension: 0.25,
        yAxisID: 'yBMI'
      },
      {
        label: 'Weight (kg)',
        data: bmiHist.weight,
        borderColor: '#ec4899',
        backgroundColor: 'transparent',
        tension: 0.25,
        yAxisID: 'yWeight'
      }
    ]
  };

  const bmiTrendOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#94a3b8' } }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#64748b' }
      },
      yBMI: {
        type: 'linear',
        position: 'left',
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#0ea5e9' },
        title: { display: true, text: 'BMI', color: '#0ea5e9' }
      },
      yWeight: {
        type: 'linear',
        position: 'right',
        grid: { drawOnChartArea: false },
        ticks: { color: '#ec4899' },
        title: { display: true, text: 'Weight (kg)', color: '#ec4899' }
      }
    }
  };

  return (
    <div>
      {/* Header with Days Filter */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <TrendingUp size={28} style={{ color: 'var(--teal-primary)' }} />
            Progress & Wellness Analytics
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Time-series data visualizations tracking your physical health and lifestyle trends.
          </p>
        </div>

        {/* Filter Buttons */}
        <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(15, 23, 42, 0.8)', padding: '0.35rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--bg-card-border)' }}>
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

      {/* Automated Behavioral Insights Box */}
      {insights.length > 0 && (
        <div className="glass-card" style={{ marginBottom: '2rem', borderLeft: '4px solid var(--teal-primary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>
            <Sparkles size={18} style={{ color: 'var(--amber-primary)' }} />
            Behavioral Pattern Insights
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {insights.map((insight, idx) => (
              <div key={idx} style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
                • {insight}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Multi-Metric Trend Chart */}
      <div className="glass-card" style={{ marginBottom: '2rem', height: '380px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={18} style={{ color: 'var(--teal-primary)' }} /> Score, Sleep & Study Trajectory
        </h2>
        <div style={{ height: '300px' }}>
          <Line data={trendLineData} options={trendLineOptions} />
        </div>
      </div>

      {/* Two Column Grid: Habit Completion Doughnut & BMI Trend */}
      <div className="grid-2">
        
        {/* Habit Completion Doughnut */}
        <div className="glass-card" style={{ height: '360px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <PieIcon size={18} style={{ color: 'var(--purple-primary)' }} /> Habit Logging Consistency
          </h2>
          <div style={{ height: '270px' }}>
            <Doughnut data={doughnutData} options={doughnutOptions} />
          </div>
        </div>

        {/* BMI & Weight Progression */}
        <div className="glass-card" style={{ height: '360px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Scale size={18} style={{ color: 'var(--cyan-primary)' }} /> Longitudinal Body Metrics Trend
          </h2>
          <div style={{ height: '270px' }}>
            {bmiHist.labels.length > 0 ? (
              <Line data={bmiTrendData} options={bmiTrendOptions} />
            ) : (
              <div style={{ textAlign: 'center', padding: '4rem 1rem', color: 'var(--text-muted)' }}>
                Record body metrics on multiple days to view your progression curve.
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
