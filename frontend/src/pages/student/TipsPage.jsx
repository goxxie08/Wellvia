import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { BookOpen, Sparkles, Filter, Moon, Droplet, Activity, Smile, Book } from 'lucide-react';

export function TipsPage() {
  const [tips, setTips] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchTips = async (cat = '') => {
    try {
      setLoading(true);
      const res = await api.getTips(cat);
      if (res.success) {
        setTips(res.tips || []);
        if (res.categories) setCategories(['All', ...res.categories]);
      }
    } catch (err) {
      console.error('Failed to load tips:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTips(selectedCategory);
  }, [selectedCategory]);

  const getCategoryIcon = (cat) => {
    switch (cat.toLowerCase()) {
      case 'sleep': return <Moon size={16} style={{ color: 'var(--purple-primary)' }} />;
      case 'hydration': return <Droplet size={16} style={{ color: 'var(--cyan-primary)' }} />;
      case 'exercise': return <Activity size={16} style={{ color: 'var(--emerald-primary)' }} />;
      case 'stress': return <Smile size={16} style={{ color: 'var(--amber-primary)' }} />;
      case 'study': return <Book size={16} style={{ color: 'var(--teal-primary)' }} />;
      default: return <Sparkles size={16} style={{ color: 'var(--rose-primary)' }} />;
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Sparkles size={28} style={{ color: 'var(--amber-primary)' }} />
          Curated Student Wellness Tips
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Evidence-based strategies for sleep hygiene, exam stress, hydration, and academic life balance.
        </p>
      </div>

      {/* Category Filter Pills */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '2rem' }}>
        {categories.map((c) => {
          const isSelected = (!selectedCategory && c === 'All') || selectedCategory === c;
          return (
            <button
              key={c}
              onClick={() => setSelectedCategory(c === 'All' ? '' : c)}
              className={isSelected ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '0.45rem 1rem', fontSize: '0.88rem' }}
            >
              {c}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0' }}>
          <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
          <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading wellness tips...</p>
        </div>
      ) : (
        <div className="grid-3">
          {tips.map((t) => (
            <div key={t.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.75rem' }}>
                  {getCategoryIcon(t.category)}
                  <span className="badge badge-teal">{t.category}</span>
                </div>
                <p style={{ color: 'var(--text-primary)', fontSize: '0.92rem', lineHeight: 1.6 }}>
                  "{t.content}"
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid var(--bg-card-border)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Wellvia Curated Strategy
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
