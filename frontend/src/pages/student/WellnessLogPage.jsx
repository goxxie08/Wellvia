import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { 
  Moon, 
  Droplet, 
  Activity, 
  Smile, 
  BookOpen, 
  CheckCircle, 
  AlertCircle, 
  Award, 
  Sparkles 
} from 'lucide-react';
import confetti from 'canvas-confetti';

export function WellnessLogPage() {
  const { refreshUser } = useAuth();
  const [form, setForm] = useState({
    sleep_hours: '',
    sleep_quality: '3',
    water_glasses: '',
    exercise_type: 'Walk',
    exercise_duration: '',
    exercise_intensity: 'Medium',
    mood: '4',
    stress_level: '2',
    study_hours: '',
    study_sessions: '1',
    study_subject: ''
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [newBadges, setNewBadges] = useState([]);

  const navigate = useNavigate();

  const populateFromRecord = (r) => {
    if (!r) return;
    setForm({
      sleep_hours: r.sleep_hours != null ? String(r.sleep_hours) : '',
      sleep_quality: r.sleep_quality != null ? String(r.sleep_quality) : '3',
      water_glasses: r.water_glasses != null ? String(r.water_glasses) : '',
      exercise_type: r.exercise_type || 'Walk',
      exercise_duration: r.exercise_duration != null ? String(r.exercise_duration) : '',
      exercise_intensity: r.exercise_intensity || 'Medium',
      mood: r.mood != null ? String(r.mood) : '4',
      stress_level: r.stress_level != null ? String(r.stress_level) : '2',
      study_hours: r.study_hours != null ? String(r.study_hours) : '',
      study_sessions: r.study_sessions != null ? String(r.study_sessions) : '1',
      study_subject: r.study_subject || ''
    });
  };

  useEffect(() => {
    const fetchToday = async () => {
      try {
        setLoading(true);
        const res = await api.getTodayWellness();
        if (res.success && res.record) {
          populateFromRecord(res.record);
        }
      } catch (err) {
        console.warn('Could not load today record', err);
        setError(err.message || 'Could not retrieve today\'s recorded metrics.');
      } finally {
        setLoading(false);
      }
    };
    fetchToday();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    setNewBadges([]);

    try {
      const res = await api.logWellness(form);
      if (res.success) {
        setSuccess('Wellness habits logged successfully! +10 Points awarded.');
        if (res.record) {
          populateFromRecord(res.record);
        }
        if (refreshUser) {
          await refreshUser();
        }
        if (res.result && res.result.new_badges && res.result.new_badges.length > 0) {
          setNewBadges(res.result.new_badges);
          confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
          });
        }
        setTimeout(() => {
          navigate('/dashboard');
        }, 1800);
      }
    } catch (err) {
      if (err.data && err.data.errors) {
        setError(err.data.errors.join(' • '));
      } else {
        setError(err.message || 'Failed to save wellness log.');
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading today's wellness logger...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '860px', margin: '0 auto' }}>
      
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Activity size={30} style={{ color: 'var(--teal-primary)' }} />
          Log Today's Wellness Habits
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Record your daily physical, mental, and academic metrics to track self-awareness and earn reward points.
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
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.5rem'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem 1rem',
          color: '#6ee7b7',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.5rem'
        }}>
          <CheckCircle size={18} />
          <span>{success}</span>
        </div>
      )}

      {newBadges.length > 0 && (
        <div style={{
          background: 'rgba(139, 92, 246, 0.15)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '1rem',
          color: '#c4b5fd',
          marginBottom: '1.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, marginBottom: '0.3rem' }}>
            <Sparkles size={18} style={{ color: 'var(--amber-primary)' }} />
            Achievement Unlocked!
          </div>
          {newBadges.map((b, idx) => (
            <div key={idx} style={{ fontSize: '0.9rem', marginLeft: '1.5rem' }}>🏆 {b}</div>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Sleep Section */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Moon size={20} style={{ color: 'var(--purple-primary)' }} /> Rest & Sleep
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Sleep Duration (Hours)</label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="24"
                name="sleep_hours"
                className="form-input"
                placeholder="e.g. 7.5"
                value={form.sleep_hours}
                onChange={handleChange}
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Sleep Quality</label>
              <select name="sleep_quality" className="form-select" value={form.sleep_quality} onChange={handleChange}>
                <option value="5">5 - Excellent (Refreshed)</option>
                <option value="4">4 - Good</option>
                <option value="3">3 - Fair</option>
                <option value="2">2 - Restless</option>
                <option value="1">1 - Very Poor</option>
              </select>
            </div>
          </div>
        </div>

        {/* Hydration Section */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Droplet size={20} style={{ color: 'var(--cyan-primary)' }} /> Daily Hydration
          </h2>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Water Glasses Consumed (approx. 250ml each)</label>
            <input
              type="number"
              min="0"
              max="25"
              name="water_glasses"
              className="form-input"
              placeholder="e.g. 8"
              value={form.water_glasses}
              onChange={handleChange}
            />
          </div>
        </div>

        {/* Physical Exercise Section */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Activity size={20} style={{ color: 'var(--emerald-primary)' }} /> Physical Exercise & Movement
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div>
              <label className="form-label">Exercise Type</label>
              <select name="exercise_type" className="form-select" value={form.exercise_type} onChange={handleChange}>
                <option value="Walk">Brisk Walking</option>
                <option value="Running">Running / Jogging</option>
                <option value="Gym">Gym & Strength</option>
                <option value="Yoga">Yoga & Stretches</option>
                <option value="Cycling">Cycling</option>
                <option value="Sports">Sports / Badminton</option>
                <option value="Other">Other Movement</option>
              </select>
            </div>
            <div>
              <label className="form-label">Duration (Minutes)</label>
              <input
                type="number"
                min="0"
                max="300"
                name="exercise_duration"
                className="form-input"
                placeholder="e.g. 30"
                value={form.exercise_duration}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="form-label">Intensity Level</label>
              <select name="exercise_intensity" className="form-select" value={form.exercise_intensity} onChange={handleChange}>
                <option value="Low">Low / Gentle</option>
                <option value="Medium">Medium / Moderate</option>
                <option value="High">High / Intense</option>
              </select>
            </div>
          </div>
        </div>

        {/* Mental Health Section */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Smile size={20} style={{ color: 'var(--amber-primary)' }} /> Mental Wellness & Emotion
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label className="form-label">Today's Mood Rating</label>
              <select name="mood" className="form-select" value={form.mood} onChange={handleChange}>
                <option value="5">5 - Very Happy / Energized 😊</option>
                <option value="4">4 - Good / Content 🙂</option>
                <option value="3">3 - Neutral / Okay 😐</option>
                <option value="2">2 - Low / Down 🙁</option>
                <option value="1">1 - Very Sad / Depressed 😞</option>
              </select>
            </div>
            <div>
              <label className="form-label">Stress Level</label>
              <select name="stress_level" className="form-select" value={form.stress_level} onChange={handleChange}>
                <option value="1">1 - Very Low / Calm 🧘</option>
                <option value="2">2 - Low</option>
                <option value="3">3 - Moderate</option>
                <option value="4">4 - High / Pressured 😰</option>
                <option value="5">5 - Severe / Overwhelmed 😫</option>
              </select>
            </div>
          </div>
        </div>

        {/* Academic Study Section */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <BookOpen size={20} style={{ color: 'var(--teal-primary)' }} /> Academic Habit Tracking
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.5fr', gap: '1rem' }}>
            <div>
              <label className="form-label">Total Study Time (Hrs)</label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="24"
                name="study_hours"
                className="form-input"
                placeholder="e.g. 4.5"
                value={form.study_hours}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="form-label">Study Sessions</label>
              <input
                type="number"
                min="1"
                max="10"
                name="study_sessions"
                className="form-input"
                value={form.study_sessions}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="form-label">Primary Subject / Topic</label>
              <input
                type="text"
                name="study_subject"
                className="form-input"
                placeholder="e.g. Machine Learning, Physics"
                value={form.study_subject}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary"
          style={{ width: '100%', justifyContent: 'center', padding: '0.85rem', fontSize: '1rem' }}
          disabled={saving}
        >
          {saving ? 'Computing Score & Saving...' : 'Save Daily Metrics & Update Score'}
        </button>

      </form>

    </div>
  );
}
