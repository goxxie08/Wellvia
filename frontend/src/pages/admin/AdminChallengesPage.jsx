pythonimport React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Award, PlusCircle, Trash2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export function AdminChallengesPage() {
  const [challenges, setChallenges] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [challengeType, setChallengeType] = useState('daily');
  const [points, setPoints] = useState(20);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      const res = await api.getAdminChallenges();
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

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;

    setError('');
    setSuccess('');
    setSubmitting(true);

    try {
      const res = await api.createAdminChallenge({
        title: title.trim(),
        description: description.trim(),
        challenge_type: challengeType,
        points: parseInt(points, 10)
      });
      if (res.success) {
        setSuccess('New challenge created successfully!');
        setTitle('');
        setDescription('');
        setPoints(20);
        await fetchChallenges();
      }
    } catch (err) {
      setError(err.message || 'Failed to create challenge.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggle = async (challengeId) => {
    try {
      const res = await api.toggleAdminChallenge(challengeId);
      if (res.success) {
        setChallenges((prev) =>
          prev.map((c) => (c.id === challengeId ? { ...c, is_active: res.is_active } : c))
        );
      }
    } catch (err) {
      alert(err.message || 'Failed to toggle challenge status.');
    }
  };

  const handleDelete = async (challengeId) => {
    if (!window.confirm('Delete this challenge?')) return;
    try {
      const res = await api.deleteAdminChallenge(challengeId);
      if (res.success) {
        setChallenges((prev) => prev.filter((c) => c.id !== challengeId));
      }
    } catch (err) {
      alert(err.message || 'Failed to delete challenge.');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading challenges...</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Award size={28} style={{ color: 'var(--purple-primary)' }} />
          Manage Challenges
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Create and activate student daily and weekly quests with gamification reward points.
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

      <div className="grid-2" style={{ alignItems: 'start' }}>

        {/* Create Challenge Form */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <PlusCircle size={18} style={{ color: 'var(--teal-primary)' }} /> Create New Challenge
          </h2>

          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label className="form-label">Challenge Title</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. 8-Hour Sleep Night"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description / Instructions</label>
              <textarea
                className="form-textarea"
                rows={3}
                placeholder="Explain the required wellness action..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Schedule Type</label>
                <select className="form-select" value={challengeType} onChange={(e) => setChallengeType(e.target.value)}>
                  <option value="daily">Daily Quest</option>
                  <option value="weekly">Weekly Milestone</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Points Award</label>
                <input
                  type="number"
                  min="5"
                  max="500"
                  className="form-input"
                  value={points}
                  onChange={(e) => setPoints(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              disabled={submitting || !title.trim()}
            >
              {submitting ? 'Creating...' : 'Create Challenge'}
            </button>
          </form>
        </div>

        {/* Existing Challenges List */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '1rem' }}>
            Existing Challenges ({challenges.length})
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '540px', overflowY: 'auto', paddingRight: '4px' }}>
            {challenges.map((c) => (
              <div
                key={c.id}
                style={{
                  background: 'rgba(15, 23, 42, 0.5)',
                  border: '1px solid var(--bg-card-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.85rem 1rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: '0.75rem'
                }}
              >
                <div>
                  <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.35rem' }}>
                    <span className="badge badge-teal">{c.challenge_type}</span>
                    <span className="badge badge-amber">+{c.points} pts</span>
                    {c.is_active ? (
                      <span className="badge badge-emerald">Active</span>
                    ) : (
                      <span className="badge badge-rose">Inactive</span>
                    )}
                  </div>
                  <h3 style={{ fontSize: '0.98rem', fontWeight: 600, color: '#fff' }}>{c.title}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '0.2rem' }}>
                    {c.description}
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                  <button
                    onClick={() => handleToggle(c.id)}
                    className="btn-secondary"
                    style={{ padding: '0.35rem 0.6rem', fontSize: '0.75rem' }}
                    title="Toggle active state"
                  >
                    {c.is_active ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    onClick={() => handleDelete(c.id)}
                    className="btn-danger"
                    style={{ padding: '0.35rem 0.6rem' }}
                    title="Delete challenge"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
