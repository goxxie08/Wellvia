import React from 'react';
import { ShieldCheck, Heart } from 'lucide-react';

export function Footer() {
  return (
    <footer style={{
      borderTop: '1px solid var(--bg-card-border)',
      background: 'rgba(9, 13, 22, 0.75)',
      padding: '1.5rem',
      marginTop: 'auto',
      zIndex: 10
    }}>
      <div style={{
        maxWidth: '1240px',
        margin: '0 auto',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem',
        fontSize: '0.85rem',
        color: 'var(--text-muted)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <strong style={{ color: 'var(--text-secondary)' }}>Wellvia</strong> — Student Physical & Mental Health Companion © {new Date().getFullYear()}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
          <span className="badge badge-teal" style={{ textTransform: 'none', fontWeight: 500 }}>
            <ShieldCheck size={14} /> Web & Desktop Ready
          </span>
          <span>Self-Awareness & Habit Tracker</span>
        </div>
      </div>
    </footer>
  );
}
