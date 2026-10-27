import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { Award, CheckCircle, Clock, Flame, Sparkles, AlertCircle } from 'lucide-react';
import confetti from 'canvas-confetti';

export function ChallengesPage() {
  const { refreshUser } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [completingId, setCompletingId] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      const res = await api.getChallenges();
      if (res.success) {
        setChallenges(res.challenges || []);
      }
    } catch (err) {
      setError(err.message || 'Failed to load challenges.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChallenges();
  }, []);

  const handleComplete = async (ch) => {
    try {
      setCompletingId(ch.id);
      setError('');
      setSuccess('');
      const res = await api.completeChallenge(ch.id);
      if (res.success) {
        setSuccess(`🎉 Challenge "${ch.title}" completed! +${res.points_awarded} Points awarded.`);
        confetti({
          particleCount: 90,
          spread: 70,
          origin: { y: 0.6 }
        });
        if (refreshUser) {
          await refreshUser();
        }
        await fetchChallenges();
      }
    } catch (err) {
      setError(err.message || 'Could not complete challenge.');
    } finally {
      setCompletingId(null);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading wellness challenges...</p>
      </div>
    );
  }

  const dailyChallenges = challenges.filter((c) => c.challenge_type === 'daily');
  const weeklyChallenges = challenges.filter((c) => c.challenge_type === 'weekly');

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Award size={28} style={{ color: 'var(--purple-primary)' }} />
          Wellness Challenges & Habits
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Complete bite-sized daily tasks and weekly wellness goals to earn reward points and unlock achievements.
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

      {success && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem 1rem',
          color: '#6ee7b7',
          fontSize: '0.9rem',
          marginBottom: '1.5rem'
        }}>
          {success}
        </div>
      )}

      {/* Daily Challenges Section */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Clock size={20} style={{ color: 'var(--teal-primary)' }} /> Daily Habit Quests
        </h2>

        <div className="grid-3">
          {dailyChallenges.map((ch) => (
            <div key={ch.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <span className="badge badge-teal">Daily Quest</span>
                  <span className="badge badge-amber">+{ch.points} pts</span>
                </div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>
                  {ch.title}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.5 }}>
                  {ch.description}
                </p>
              </div>

              <div style={{ marginTop: '1.25rem' }}>
                {ch.is_completed ? (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem',
                    color: 'var(--emerald-primary)',
                    fontWeight: 600,
                    fontSize: '0.88rem',
                    padding: '0.5rem',
                    background: 'rgba(16, 185, 129, 0.1)',
                    borderRadius: 'var(--radius-sm)'
                  }}>
                    <CheckCircle size={16} /> Completed Today
                  </div>
                ) : (
                  <button
                    onClick={() => handleComplete(ch)}
                    disabled={completingId === ch.id}
                    className="btn-primary"
                    style={{ width: '100%', justifyContent: 'center', fontSize: '0.88rem' }}
                  >
                    {completingId === ch.id ? 'Claiming...' : 'Mark as Completed'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weekly Challenges Section */}
      {weeklyChallenges.length > 0 && (
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Flame size={20} style={{ color: 'var(--amber-primary)' }} /> Weekly Consistency Milestones
          </h2>

          <div className="grid-2">
            {weeklyChallenges.map((ch) => (
              <div key={ch.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <span className="badge badge-purple">Weekly Challenge</span>
                    <span className="badge badge-amber">+{ch.points} pts</span>
                  </div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>
                    {ch.title}
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.5 }}>
                    {ch.description}
                  </p>
                </div>

                <div style={{ marginTop: '1.25rem' }}>
                  {ch.is_completed ? (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.4rem',
                      color: 'var(--emerald-primary)',
                      fontWeight: 600,
                      fontSize: '0.88rem',
                      padding: '0.5rem',
                      background: 'rgba(16, 185, 129, 0.1)',
                      borderRadius: 'var(--radius-sm)'
                    }}>
                      <CheckCircle size={16} /> Completed
                    </div>
                  ) : (
                    <button
                      onClick={() => handleComplete(ch)}
                      disabled={completingId === ch.id}
                      className="btn-secondary"
                      style={{ width: '100%', justifyContent: 'center', fontSize: '0.88rem' }}
                    >
                      {completingId === ch.id ? 'Claiming...' : 'Mark Complete (+50 pts)'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
