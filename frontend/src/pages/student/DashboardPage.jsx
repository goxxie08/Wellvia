import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { 
  Activity, 
  Flame, 
  Droplet, 
  Moon, 
  BookOpen, 
  Smile, 
  CheckCircle, 
  ArrowRight, 
  Sparkles, 
  Award, 
  Scale, 
  PlusCircle, 
  Clock,
  AlertCircle
} from 'lucide-react';
import confetti from 'canvas-confetti';

export function DashboardPage() {
  const { refreshUser } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completingId, setCompletingId] = useState(null);
  const [error, setError] = useState('');

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.getDashboard();
      if (res.success) {
        setData(res);
      }
    } catch (err) {
      console.error('Failed to load student dashboard:', err);
      setError(err.message || 'Failed to load your wellness dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleCompleteChallenge = async (challengeId) => {
    try {
      setCompletingId(challengeId);
      const res = await api.completeChallenge(challengeId);
      if (res.success) {
        confetti({
          particleCount: 80,
          spread: 60,
          origin: { y: 0.7 }
        });
        if (refreshUser) {
          await refreshUser();
        }
        await fetchDashboard();
      }
    } catch (err) {
      alert(err.message || 'Could not complete challenge.');
    } finally {
      setCompletingId(null);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading your wellness dashboard...</p>
      </div>
    );
  }

  const user = data?.user || {};
  const record = data?.today_record;
  const streak = data?.streak || 0;
  const dailyTip = data?.daily_tip;
  const challenges = data?.challenges || [];
  const bmiInfo = data?.bmi_info;
  const score = record?.wellness_score || 0;

  // Score color helper
  const getScoreColor = (sc) => {
    if (sc >= 80) return 'var(--emerald-primary)';
    if (sc >= 60) return 'var(--teal-primary)';
    if (sc >= 40) return 'var(--amber-primary)';
    return 'var(--rose-primary)';
  };

  return (
    <div>
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

      {/* Welcome & Streak Banner */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1.25rem',
        marginBottom: '2rem'
      }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff' }}>
            Good day, <span style={{ color: 'var(--teal-primary)' }}>{user.username}</span> 👋
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Here is your daily physical and mental wellness breakdown.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="glass-card" style={{ padding: '0.65rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Flame size={24} style={{ color: 'var(--amber-primary)' }} />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Streak</div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>{streak} {streak === 1 ? 'Day' : 'Days'}</div>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '0.65rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Award size={24} style={{ color: 'var(--purple-primary)' }} />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Points</div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>{user.total_points || 0} pts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid-3" style={{ marginBottom: '2rem' }}>
        
        {/* Wellness Score Card */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Today's Wellness Score
              </span>
              <Activity size={18} style={{ color: getScoreColor(score) }} />
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '3rem', fontWeight: 800, color: getScoreColor(score), lineHeight: 1 }}>
                {record ? score : '—'}
              </span>
              <span style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>/ 100</span>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
              {record 
                ? (score >= 80 ? 'Outstanding balance across sleep, hydration & study!' : 'Keep logging metrics to improve your score.')
                : 'No habits logged yet today. Track your day to earn +10 points!'}
            </p>
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <Link to="/wellness" className="btn-primary" style={{ width: '100%', justifyContent: 'center', fontSize: '0.9rem' }}>
              <PlusCircle size={16} />
              {record ? 'Update Daily Log' : 'Log Today’s Habits'}
            </Link>
          </div>
        </div>

        {/* Physical Health & BMI Overview */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Body Metrics & ML Health
              </span>
              <Scale size={18} style={{ color: 'var(--cyan-primary)' }} />
            </div>

            {bmiInfo ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '2.2rem', fontWeight: 800, color: '#fff' }}>
                    {bmiInfo.bmi_formatted}
                  </span>
                  <span className="badge badge-teal" style={{ fontSize: '0.75rem' }}>
                    {bmiInfo.category}
                  </span>
                </div>

                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.5rem' }}>
                  <div>Height: <strong>{user.height} cm</strong> &bull; Weight: <strong>{user.weight} kg</strong></div>
                  {user.ml_health_status && (
                    <div style={{ color: 'var(--teal-primary)' }}>
                      ML Classifier: <strong>{user.ml_health_status}</strong>
                    </div>
                  )}
                  {user.ml_lifestyle_risk && (
                    <div style={{ color: 'var(--purple-primary)' }}>
                      Lifestyle Risk: <strong>{user.ml_lifestyle_risk}</strong>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '0.5rem 0 1rem 0' }}>
                  Enter your height and weight to calculate your BMI and unlock machine-learning health classification.
                </p>
              </div>
            )}
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <Link to="/body-metrics" className="btn-secondary" style={{ width: '100%', justifyContent: 'center', fontSize: '0.9rem' }}>
              {bmiInfo ? 'Re-assess Metrics' : 'Set Up Body Metrics'}
            </Link>
          </div>
        </div>

        {/* Daily Curated Wellness Tip */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Tip of the Day
              </span>
              <Sparkles size={18} style={{ color: 'var(--amber-primary)' }} />
            </div>

            {dailyTip ? (
              <div>
                <span className="badge badge-purple" style={{ marginBottom: '0.75rem' }}>
                  {dailyTip.category}
                </span>
                <p style={{ color: 'var(--text-primary)', fontSize: '0.92rem', fontStyle: 'italic', lineHeight: 1.5 }}>
                  "{dailyTip.content}"
                </p>
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)' }}>Stay hydrated and take a brisk 5-minute study walk!</p>
            )}
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <Link to="/tips" className="btn-secondary" style={{ width: '100%', justifyContent: 'center', fontSize: '0.9rem' }}>
              Explore All Tips
            </Link>
          </div>
        </div>

      </div>

      {/* Lower Section: Today's Logged Metrics & Active Challenges */}
      <div className="grid-2">
        
        {/* Today's Habits Summary */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff' }}>Today's Recorded Habits</h2>
            <Link to="/wellness/history" style={{ color: 'var(--teal-primary)', fontSize: '0.85rem', textDecoration: 'none' }}>
              View History
            </Link>
          </div>

          {record ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  <Moon size={15} style={{ color: 'var(--purple-primary)' }} /> Sleep
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '0.2rem' }}>
                  {record.sleep_hours != null ? `${record.sleep_hours} hrs` : '—'}
                </div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  <Droplet size={15} style={{ color: 'var(--cyan-primary)' }} /> Hydration
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '0.2rem' }}>
                  {record.water_glasses != null ? `${record.water_glasses} glasses` : '—'}
                </div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  <Activity size={15} style={{ color: 'var(--emerald-primary)' }} /> Exercise
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '0.2rem' }}>
                  {record.exercise_duration != null ? `${record.exercise_duration} mins` : '—'}
                </div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  <BookOpen size={15} style={{ color: 'var(--amber-primary)' }} /> Study
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '0.2rem' }}>
                  {record.study_hours != null ? `${record.study_hours} hrs` : '—'}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
              <Clock size={32} style={{ margin: '0 auto 0.75rem auto', opacity: 0.5 }} />
              <p style={{ fontSize: '0.9rem' }}>You haven't recorded your wellness metrics yet today.</p>
              <Link to="/wellness" className="btn-primary" style={{ marginTop: '1rem', display: 'inline-flex' }}>
                Log Habits Now
              </Link>
            </div>
          )}
        </div>

        {/* Daily Challenges */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff' }}>Daily Challenges</h2>
            <Link to="/challenges" style={{ color: 'var(--teal-primary)', fontSize: '0.85rem', textDecoration: 'none' }}>
              View All
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {challenges.length > 0 ? (
              challenges.map((ch) => (
                <div
                  key={ch.id}
                  style={{
                    background: 'rgba(15, 23, 42, 0.5)',
                    border: '1px solid var(--bg-card-border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.85rem 1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '1rem'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#fff' }}>{ch.title}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{ch.description}</div>
                  </div>

                  {ch.is_completed ? (
                    <span className="badge badge-emerald">
                      <CheckCircle size={13} /> Completed
                    </span>
                  ) : (
                    <button
                      onClick={() => handleCompleteChallenge(ch.id)}
                      disabled={completingId === ch.id}
                      className="btn-primary"
                      style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', flexShrink: 0 }}
                    >
                      +{ch.points} pts
                    </button>
                  )}
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No challenges available today.</p>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
