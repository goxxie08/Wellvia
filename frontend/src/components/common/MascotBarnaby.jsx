import React, { useState } from 'react';
import { X, Sparkles, Bot } from 'lucide-react';

const BARNABY_TIPS = [
  "Hi! I'm Barnaby 🐻✨ Don't forget to drink at least 8 glasses of water today! 💧",
  "Taking a 5-minute stretch break every hour keeps your mind sharp! 🏃‍♂️",
  "Aim for 7 to 9 hours of restful sleep to boost your memory & mood 😴",
  "Feeling stressed? Try 4s inhale, 7s hold, 8s exhale breathing 🧘",
  "You're doing amazing! Keep your habit logging streak alive 🔥",
  "Log your daily metrics to track progress & earn reward points 🌟",
  "Balancing study time with rest is the key to preventing burnout 📚"
];

export function MascotBarnaby({ onOpenChat }) {
  const [tipIndex, setTipIndex] = useState(0);
  const [showBubble, setShowBubble] = useState(true);
  const [bounce, setBounce] = useState(false);

  const handleClick = () => {
    setBounce(true);
    setTimeout(() => setBounce(false), 500);
    setShowBubble(true);
    setTipIndex((prev) => (prev + 1) % BARNABY_TIPS.length);
  };

  return (
    <div className="mascot-container">
      {showBubble && (
        <div className="mascot-bubble">
          <button
            onClick={() => setShowBubble(false)}
            style={{
              position: 'absolute',
              top: '6px',
              right: '6px',
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer'
            }}
            title="Dismiss tip"
          >
            <X size={14} />
          </button>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem', paddingRight: '12px' }}>
            <Sparkles size={16} style={{ color: 'var(--amber-primary)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <span>{BARNABY_TIPS[tipIndex]}</span>
              {onOpenChat && (
                <div style={{ marginTop: '0.45rem' }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onOpenChat();
                    }}
                    style={{
                      background: 'rgba(20, 184, 166, 0.15)',
                      border: '1px solid rgba(20, 184, 166, 0.35)',
                      borderRadius: '6px',
                      color: 'var(--teal-primary)',
                      padding: '3px 8px',
                      fontSize: '0.74rem',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontWeight: 600
                    }}
                  >
                    <Bot size={12} /> Ask Wellvia AI
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <button
        onClick={handleClick}
        className={`mascot-button ${bounce ? 'mascot-bounce' : ''}`}
        title="Click Barnaby for wellness encouragement!"
        style={{
          transform: bounce ? 'scale(1.2) translateY(-6px)' : undefined,
          transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
        }}
      >
        <span>🐻</span>
      </button>
    </div>
  );
}
