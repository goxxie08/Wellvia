import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Users, CheckCircle, XCircle, Search, AlertCircle } from 'lucide-react';

export function AdminUsersPage() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [togglingId, setTogglingId] = useState(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.getAdminUsers();
      if (res.success) {
        setStudents(res.students || []);
      }
    } catch (err) {
      setError(err.message || 'Failed to load students.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleToggle = async (userId) => {
    try {
      setTogglingId(userId);
      const res = await api.toggleUser(userId);
      if (res.success) {
        setStudents((prev) =>
          prev.map((s) => (s.id === userId ? { ...s, is_active: res.is_active } : s))
        );
      }
    } catch (err) {
      alert(err.message || 'Failed to update account status.');
    } finally {
      setTogglingId(null);
    }
  };

  const filtered = students.filter((s) => {
    const q = search.toLowerCase();
    return s.username.toLowerCase().includes(q) || s.email.toLowerCase().includes(q);
  });

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading student accounts...</p>
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
            <Users size={28} style={{ color: 'var(--teal-primary)' }} />
            Student Account Management
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            View student enrollment, activity engagement, and manage access status.
          </p>
        </div>

        {/* Search input */}
        <div style={{ position: 'relative', width: '280px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="form-input"
            placeholder="Search student or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: '2.4rem', fontSize: '0.88rem' }}
          />
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
          marginBottom: '1.5rem'
        }}>
          {error}
        </div>
      )}

      <div className="glass-card" style={{ padding: '0.5rem 1rem 1.5rem 1rem', overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student User</th>
              <th>Email</th>
              <th>Points</th>
              <th>Wellness Logs</th>
              <th>Registered</th>
              <th>Account Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => (
              <tr key={s.id}>
                <td style={{ color: 'var(--text-muted)' }}>#{s.id}</td>
                <td style={{ fontWeight: 600, color: '#fff' }}>{s.username}</td>
                <td style={{ color: 'var(--text-secondary)' }}>{s.email}</td>
                <td>
                  <span className="badge badge-amber">{s.total_points || 0} pts</span>
                </td>
                <td>{s.log_count || 0} logs</td>
                <td style={{ color: 'var(--text-muted)' }}>{String(s.created_at).slice(0, 10)}</td>
                <td>
                  {s.is_active ? (
                    <span className="badge badge-emerald">
                      <CheckCircle size={12} /> Active
                    </span>
                  ) : (
                    <span className="badge badge-rose">
                      <XCircle size={12} /> Deactivated
                    </span>
                  )}
                </td>
                <td>
                  <button
                    onClick={() => handleToggle(s.id)}
                    disabled={togglingId === s.id}
                    className={s.is_active ? 'btn-danger' : 'btn-secondary'}
                    style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                  >
                    {togglingId === s.id ? 'Updating...' : (s.is_active ? 'Deactivate' : 'Activate')}
                  </button>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                  No students matched your search query.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
