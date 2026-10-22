import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client';
import { Calendar, PlusCircle, Activity, Moon, Droplet, Smile, BookOpen, AlertCircle } from 'lucide-react';

export function HistoryPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const res = await api.getWellnessHistory();
        if (res.success) {
          setRecords(res.records || []);
        }
      } catch (err) {
        setError(err.message || 'Failed to load wellness history.');
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const getScoreBadge = (sc) => {
    if (sc == null) return <span className="badge badge-teal">N/A</span>;
    if (sc >= 80) return <span className="badge badge-emerald">{sc} / 100</span>;
    if (sc >= 60) return <span className="badge badge-teal">{sc} / 100</span>;
    if (sc >= 40) return <span className="badge badge-amber">{sc} / 100</span>;
    return <span className="badge badge-rose">{sc} / 100</span>;
  };

  const getMoodEmoji = (val) => {
    switch (Number(val)) {
      case 5: return '😊 Great';
      case 4: return '🙂 Good';
      case 3: return '😐 Neutral';
      case 2: return '🙁 Low';
      case 1: return '😞 Sad';
      default: return '—';
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading wellness record history...</p>
      </div>
    );
  }

  return (
    <div>
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
            <Calendar size={28} style={{ color: 'var(--teal-primary)' }} />
            Wellness Log History
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Review your daily habit entries, wellness score patterns, and mood trends.
          </p>
        </div>

        <Link to="/wellness" className="btn-primary" style={{ fontSize: '0.9rem' }}>
          <PlusCircle size={16} /> Log Today's Entry
        </Link>
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

      <div className="glass-card" style={{ padding: '0.5rem 1rem 1.5rem 1rem', overflowX: 'auto' }}>
        {records.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Wellness Score</th>
                <th>Sleep</th>
                <th>Hydration</th>
                <th>Exercise</th>
                <th>Mood</th>
                <th>Study Time</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id}>
                  <td style={{ fontWeight: 600, color: '#fff' }}>
                    {String(r.record_date).slice(0, 10)}
                  </td>
                  <td>{getScoreBadge(r.wellness_score)}</td>
                  <td>
                    {r.sleep_hours != null ? `${r.sleep_hours} hrs` : '—'}
                  </td>
                  <td>
                    {r.water_glasses != null ? `${r.water_glasses} glasses` : '—'}
                  </td>
                  <td>
                    {r.exercise_duration != null ? `${r.exercise_duration}m (${r.exercise_type || 'Walk'})` : '—'}
                  </td>
                  <td>{getMoodEmoji(r.mood)}</td>
                  <td>
                    {r.study_hours != null ? `${r.study_hours} hrs` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <Calendar size={36} style={{ margin: '0 auto 0.75rem auto', opacity: 0.5 }} />
            <p>No historical wellness logs recorded yet.</p>
            <Link to="/wellness" className="btn-primary" style={{ marginTop: '1rem', display: 'inline-flex' }}>
              Create Your First Log
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
