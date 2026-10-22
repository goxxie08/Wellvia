import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Sparkles, PlusCircle, Trash2, CheckCircle, AlertCircle } from 'lucide-react';

export function AdminTipsPage() {
  const [tips, setTips] = useState([]);
  const [category, setCategory] = useState('Sleep');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchTips = async () => {
    try {
      setLoading(true);
      const res = await api.getAdminTips();
      if (res.success) {
        setTips(res.tips || []);
      }
    } catch (err) {
      setError(err.message || 'Failed to load tips.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTips();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    setError('');
    setSuccess('');
    setSubmitting(true);

    try {
      const res = await api.createAdminTip({ category, content: content.trim() });
      if (res.success) {
        setSuccess('New wellness tip published successfully!');
        setContent('');
        await fetchTips();
      }
    } catch (err) {
      setError(err.message || 'Failed to create tip.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (tipId) => {
    if (!window.confirm('Are you sure you want to delete this wellness tip?')) return;

    try {
      const res = await api.deleteAdminTip(tipId);
      if (res.success) {
        setTips((prev) => prev.filter((t) => t.id !== tipId));
      }
    } catch (err) {
      alert(err.message || 'Failed to delete tip.');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading wellness tips...</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Sparkles size={28} style={{ color: 'var(--amber-primary)' }} />
          Manage Wellness Tips
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Create and curate physical, sleep, mental health, and study strategies shown to students.
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
        
        {/* Create Tip Form */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <PlusCircle size={18} style={{ color: 'var(--teal-primary)' }} /> Publish New Strategy
          </h2>

          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label className="form-label">Category</label>
              <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="Sleep">Sleep Hygiene</option>
                <option value="Hydration">Hydration & Nutrition</option>
                <option value="Exercise">Physical Movement</option>
                <option value="Stress">Stress Management</option>
                <option value="Study">Academic Habits</option>
                <option value="General">General Wellness</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Tip Content</label>
              <textarea
                className="form-textarea"
                rows={4}
                placeholder="Write evidence-based student guidance..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              disabled={submitting || !content.trim()}
            >
              {submitting ? 'Publishing...' : 'Publish Tip'}
            </button>
          </form>
        </div>

        {/* Existing Tips List */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#fff', marginBottom: '1rem' }}>
            Published Strategies ({tips.length})
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '540px', overflowY: 'auto', paddingRight: '4px' }}>
            {tips.map((t) => (
              <div
                key={t.id}
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
                  <span className="badge badge-teal" style={{ marginBottom: '0.4rem' }}>{t.category}</span>
                  <p style={{ color: 'var(--text-primary)', fontSize: '0.88rem', lineHeight: 1.5 }}>
                    "{t.content}"
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(t.id)}
                  className="btn-danger"
                  style={{ padding: '0.35rem 0.6rem', flexShrink: 0 }}
                  title="Delete tip"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
