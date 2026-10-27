import React from 'react';
import { MessageCircle, X } from 'lucide-react';

export function FloatingChatButton({ isOpen, onToggle }) {
  if (isOpen) {
    return null;
  }

  return (
    <button
      onClick={onToggle}
      className="floating-chat-btn"
      title="Open AI Wellness Companion"
      aria-label="Open AI Wellness Companion"
      type="button"
    >
      <MessageCircle size={24} />
    </button>
  );
}
