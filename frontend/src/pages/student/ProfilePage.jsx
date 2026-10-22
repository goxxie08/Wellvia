import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { User, Award, Flame, Scale, CheckCircle, Lock, Calendar, Star } from 'lucide-react';

export function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const res = await api.getProfile();
        if (res.success) {
          setProfile(res);
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading student profile & achievements...</p>
      </div>
    );
  }

  const user = profile?.user || {};
  const streak = profile?.streak || 0;
  const achievements = profile?.achievements || [];
  const unlockedCount = profile?.unlocked_count || 0;
  const totalCount = profile?.total_achievements || achievements.length;
  const bmiInfo = profile?.bmi_info;

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <User size={28} style={{ color: 'var(--teal-primary)' }} />
          Student Profile & Achievements
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          View your wellness milestones, streak records, reward points, and unlocked badges.
        </p>
      </div>

      {/* Profile Overview Banner */}
      <div className="glass-card" style={{ marginBottom: '2rem', padding: '2rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <div style={{
              width: '68px',
              height: '68px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--teal-primary), var(--cyan-primary))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '1.8rem',
              fontWeight: 700,
              boxShadow: '0 8px 25px var(--teal-glow)'
            }}>
              {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
            </div>
            <div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff' }}>{user.username}</h2>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{user.email}</div>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.4rem' }}>
                <span className="badge badge-teal">Student Account</span>
                {user.created_at && (
                  <span className="badge badge-purple" style={{ textTransform: 'none' }}>
                    Joined {user.created_at.slice(0, 10)}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1.25rem', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem', color: 'var(--amber-primary)', fontWeight: 600, fontSize: '0.82rem' }}>
                <Star size={15} /> Total Points
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', marginTop: '0.2rem' }}>
                {user.total_points || 0}
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1.25rem', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem', color: 'var(--rose-primary)', fontWeight: 600, fontSize: '0.82rem' }}>
                <Flame size={15} /> Active Streak
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', marginTop: '0.2rem' }}>
                {streak} Days
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1.25rem', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem', color: 'var(--purple-primary)', fontWeight: 600, fontSize: '0.82rem' }}>
                <Award size={15} /> Badges
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', marginTop: '0.2rem' }}>
                {unlockedCount} / {totalCount}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Achievement Badges Grid */}
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Award size={20} style={{ color: 'var(--purple-primary)' }} /> Gamification Badges ({unlockedCount}/{totalCount})
        </h2>

        <div className="grid-4">
          {achievements.map((ach) => {
            const isUnlocked = Boolean(ach.unlocked);
            return (
              <div
                key={ach.id}
                className="glass-card"
                style={{
                  opacity: isUnlocked ? 1 : 0.6,
                  border: isUnlocked ? '1px solid rgba(20, 184, 166, 0.4)' : '1px solid var(--bg-card-border)',
                  background: isUnlocked ? 'rgba(20, 184, 166, 0.05)' : 'rgba(15, 23, 42, 0.4)',
                  textAlign: 'center',
                  padding: '1.5rem 1rem'
                }}
              >
                <div style={{
                  width: '54px',
                  height: '54px',
                  borderRadius: '50%',
                  margin: '0 auto 0.75rem auto',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: isUnlocked ? 'linear-gradient(135deg, var(--teal-primary), var(--cyan-primary))' : 'rgba(255, 255, 255, 0.06)',
                  color: isUnlocked ? '#fff' : 'var(--text-muted)',
                  boxShadow: isUnlocked ? '0 6px 18px var(--teal-glow)' : 'none'
                }}>
                  {isUnlocked ? <Award size={26} /> : <Lock size={20} />}
                </div>

                <h3 style={{ fontSize: '0.98rem', fontWeight: 600, color: isUnlocked ? '#fff' : 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  {ach.name}
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {ach.description}
                </p>

                <div style={{ marginTop: '0.85rem' }}>
                  {isUnlocked ? (
                    <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>
                      <CheckCircle size={12} /> Unlocked
                    </span>
                  ) : (
                    <span className="badge badge-purple" style={{ fontSize: '0.7rem', opacity: 0.8 }}>
                      In Progress
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
