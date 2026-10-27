import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  X, 
  Sparkles, 
  RotateCcw, 
  ShieldAlert, 
  Lightbulb, 
  RefreshCw 
} from 'lucide-react';
import { api } from '../../api/client';
import { useAuth } from '../../context/AuthContext';

const INITIAL_WELCOME = {
  id: 'welcome-1',
  sender: 'bot',
  text: "Hello! I'm Wellvia, your student wellness companion 🌿.\n\nHow are you feeling today? Whether you're navigating exam anxiety, looking for sleep hygiene advice, or needing a quick relaxation pause, I'm here to support you.",
  time: 'Just now',
  source: 'welcome'
};

const SUGGESTED_PROMPTS = [
  "How can I manage exam stress & stay calm?",
  "Give me practical tips for deeper sleep tonight",
  "Guide me through a 2-minute breathing exercise",
  "What is the best study-break routine (Pomodoro)?",
  "How can I maintain healthy hydration during study sessions?"
];

// Helper to format inline bold, italic, and clean text
function formatInline(str) {
  if (!str) return '';
  const parts = str.split(/(\*\*[^*]+?\*\*)/g);
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={idx} style={{ color: 'var(--teal-primary)', fontWeight: 600 }}>
          {part.slice(2, -2)}
        </strong>
      );
    }
    if ((part.startsWith('*') && part.endsWith('*')) || (part.startsWith('_') && part.endsWith('_'))) {
      return <em key={idx}>{part.slice(1, -1)}</em>;
    }
    return part;
  });
}

// Helper to format multi-paragraph and list message content
function formatChatMessage(text) {
  if (!text) return null;

  // Split into paragraphs by double newlines
  const paragraphs = text.split(/\n\s*\n/);

  return paragraphs.map((para, pIdx) => {
    const lines = para.split('\n').filter((l) => l.trim().length > 0);
    const isBulletList = lines.length > 0 && lines.every((line) => line.trim().startsWith('* ') || line.trim().startsWith('- '));
    const isNumberedList = lines.length > 0 && lines.every((line) => /^\d+[.)]\s/.test(line.trim()));

    if (isBulletList) {
      return (
        <ul key={pIdx} className="chat-msg-list">
          {lines.map((line, lIdx) => {
            const content = line.trim().replace(/^[*\-]\s+/, '');
            return <li key={lIdx}>{formatInline(content)}</li>;
          })}
        </ul>
      );
    }

    if (isNumberedList) {
      return (
        <ol key={pIdx} className="chat-msg-list numbered">
          {lines.map((line, lIdx) => {
            const content = line.trim().replace(/^\d+[.)]\s+/, '');
            return <li key={lIdx}>{formatInline(content)}</li>;
          })}
        </ol>
      );
    }

    return (
      <p key={pIdx} className="chat-msg-para">
        {lines.map((line, lIdx) => (
          <React.Fragment key={lIdx}>
            {formatInline(line)}
            {lIdx < lines.length - 1 && <br />}
          </React.Fragment>
        ))}
      </p>
    );
  });
}

export function ChatbotDrawer({ isOpen, onClose, onToggle }) {
  const { user } = useAuth();
  const getStorageKey = (u) => `wellvia_chat_history_${u?.id || 'guest'}`;

  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(getStorageKey(user));
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Could not load chat messages from storage', e);
    }
    return [INITIAL_WELCOME];
  });

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPrompts, setShowPrompts] = useState(true);
  const [lastFailedMessage, setLastFailedMessage] = useState(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Sync to localStorage on update
  useEffect(() => {
    if (messages && messages.length > 0) {
      try {
        localStorage.setItem(getStorageKey(user), JSON.stringify(messages));
      } catch (e) {
        console.warn('Could not save chat messages to storage', e);
      }
    }
  }, [messages, user?.id]);

  // Reload history when active user account changes
  useEffect(() => {
    try {
      const saved = localStorage.getItem(getStorageKey(user));
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed);
          return;
        }
      }
    } catch (e) {
      console.warn('Could not reload chat messages on account change', e);
    }
    setMessages([INITIAL_WELCOME]);
  }, [user?.id]);

  const scrollToBottom = (behavior = 'smooth') => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior
      });
    } else {
      messagesEndRef.current?.scrollIntoView({ behavior });
    }
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom('smooth');
      const timer = setTimeout(() => inputRef.current?.focus(), 150);
      return () => clearTimeout(timer);
    }
  }, [messages, isOpen, loading]);

  // Format history according to backend contract: list of { role: 'user'|'model', text: '...' }
  const buildHistoryPayload = (currentMessages, currentMsgText = '') => {
    return currentMessages
      .filter((m) => 
        m.source !== 'welcome' &&
        !String(m.id || '').startsWith('welcome') &&
        !m.isError &&
        !m.isCrisis &&
        m.text &&
        (m.sender === 'user' || m.sender === 'bot')
      )
      // Exclude trailing user message if it matches currentMsgText (e.g. from retry)
      .filter((m, idx, arr) => {
        if (idx === arr.length - 1 && m.sender === 'user' && m.text.trim() === currentMsgText?.trim()) {
          return false;
        }
        return true;
      })
      .slice(-10) // Limit to 10 most recent turns per server limit
      .map((m) => ({
        role: m.sender === 'user' ? 'user' : 'model',
        text: m.text.slice(0, 1000)
      }));
  };

  const handleSend = async (e, promptText = null) => {
    if (e && e.preventDefault) e.preventDefault();
    const messageToSend = (promptText || input).trim();
    if (!messageToSend || loading) return;

    // Client-side length validation
    if (messageToSend.length > 1000) {
      alert("Please keep your message under 1,000 characters.");
      return;
    }

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: messageToSend,
      time: timestamp
    };

    // Calculate history before appending new user message
    const historyPayload = buildHistoryPayload(messages, messageToSend);

    // If retrying, remove previous error message and previous duplicate user message if present
    setMessages((prev) => {
      const nonError = prev.filter((m) => !m.isError);
      if (nonError.length > 0 && nonError[nonError.length - 1].sender === 'user' && nonError[nonError.length - 1].text.trim() === messageToSend) {
        return [...nonError.slice(0, -1), userMsg];
      }
      return [...nonError, userMsg];
    });

    setInput('');
    setLoading(true);
    setLastFailedMessage(null);
    setShowPrompts(false);

    try {
      const res = await api.sendChatMessage(messageToSend, historyPayload);
      const botMsg = {
        id: `bot-${Date.now() + 1}`,
        sender: 'bot',
        text: res.reply || "Take a deep breath. Every step forward counts toward your wellness.",
        source: res.source,
        isCrisis: res.source === 'crisis_safety_intervention',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("[Wellvia Chat Error]", err);
      const isAuthError = err.status === 401;
      const errorText = isAuthError 
        ? "Your session appears to have expired. Please log in again to continue chatting."
        : (err.message || "I couldn't connect to the wellness service. Please try again in a moment.");

      setLastFailedMessage({ text: messageToSend, history: historyPayload });
      const errMsg = {
        id: `err-${Date.now() + 1}`,
        sender: 'bot',
        text: errorText,
        isError: true,
        isAuthError,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (!lastFailedMessage) return;
    const { text } = lastFailedMessage;
    handleSend(null, text);
  };

  const handleClearConversation = () => {
    if (window.confirm("Start a new conversation? Prior chat history will be cleared.")) {
      const resetMsg = [{
        ...INITIAL_WELCOME,
        id: `welcome-${Date.now()}`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }];
      setMessages(resetMsg);
      try {
        localStorage.removeItem(getStorageKey(user));
      } catch (e) {
        console.warn('Could not clear storage', e);
      }
      setInput('');
      setLastFailedMessage(null);
      setShowPrompts(true);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  // Render floating trigger button when closed
  if (!isOpen) {
    return (
      <button
        onClick={onToggle || onClose}
        className="chat-floating-btn"
        title="Open Wellvia AI Wellness Chat"
        aria-label="Open AI Wellness Chat"
        id="openChatFloatingBtn"
      >
        <Bot size={19} />
        <span>AI Chat</span>
        <span className="online-indicator-dot" />
      </button>
    );
  }

  const hasOnlyWelcome = messages.length === 1;

  return (
    <div className="chatbot-drawer" role="dialog" aria-label="AI Wellness Chat" id="chatbotDrawer">
      {/* Header */}
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div className="chat-avatar-icon">
            <Bot size={18} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-primary)' }}>
                Wellvia Companion
              </span>
              <span className="online-status-badge">
                <span className="online-dot" /> Online
              </span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
              Physical & Mental Wellness Support
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          {/* New Chat / Reset Button */}
          <button
            onClick={handleClearConversation}
            className="chat-icon-btn"
            title="Start new conversation (clears history)"
            aria-label="Start new conversation"
          >
            <RotateCcw size={15} />
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="chat-icon-btn"
            title="Close chat"
            aria-label="Close chat"
          >
            <X size={17} />
          </button>
        </div>
      </div>

      {/* Privacy Notice Banner */}
      <div className="chat-privacy-notice">
        <span>✨ Personalized Companion • Tailored to your dashboard metrics & habits</span>
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-messages" id="chatMessagesContainer" ref={messagesContainerRef}>
        {messages.map((m) => (
          <div
            key={m.id}
            className={`chat-bubble ${m.sender} ${m.isCrisis ? 'crisis-intervention' : ''} ${m.isError ? 'error-bubble' : ''}`}
          >
            {m.isCrisis && (
              <div className="crisis-badge-banner">
                <ShieldAlert size={14} />
                <span>Immediate Safety Support</span>
              </div>
            )}

            <div className="chat-bubble-content">{formatChatMessage(m.text)}</div>

            {/* Error Retry Option */}
            {m.isError && lastFailedMessage && (
              <div style={{ marginTop: '0.6rem' }}>
                <button onClick={handleRetry} className="chat-retry-btn">
                  <RefreshCw size={12} /> Retry message
                </button>
              </div>
            )}

            {/* Message Footer (Time & Source) */}
            <div className="chat-bubble-footer">
              {m.source && m.source !== 'welcome' && (
                <span className={`chat-source-tag ${m.source === 'gemini' ? 'gemini' : m.source === 'crisis_safety_intervention' ? 'crisis' : ''}`}>
                  {m.source === 'gemini' ? '✦ Gemini AI' : m.source === 'crisis_safety_intervention' ? 'Crisis Lifeline' : 'Wellvia Guide'}
                </span>
              )}
              <span className="chat-time-label">{m.time}</span>
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="chat-bubble bot loading-bubble">
            <div className="typing-wrapper">
              <Sparkles size={14} className="typing-sparkle" />
              <span style={{ fontSize: '0.84rem' }}>Reflecting on wellness guidance...</span>
              <div className="typing-dots">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          </div>
        )}

        {/* Suggested Prompts Section */}
        {(hasOnlyWelcome || showPrompts) && !loading && (
          <div className="chat-suggested-prompts">
            <div className="suggested-prompts-title">
              <Lightbulb size={13} style={{ color: 'var(--amber-primary)' }} />
              <span>Suggested prompts:</span>
            </div>
            {SUGGESTED_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={(e) => handleSend(e, prompt)}
                className="chat-prompt-pill"
              >
                <span>{prompt}</span>
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => handleSend(e)} className="chat-input-row">
        <div style={{ position: 'relative', flex: 1 }}>
          <input
            ref={inputRef}
            type="text"
            className="form-input chat-input-field"
            placeholder="Ask for advice, relief tips, focus habits..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            maxLength={1000}
            id="chatMessageInput"
          />
          {input.length > 800 && (
            <span className="chat-char-counter">
              {1000 - input.length}
            </span>
          )}
        </div>

        <button
          type="submit"
          className="btn-primary chat-send-btn"
          disabled={loading || !input.trim()}
          title="Send message (Enter)"
          aria-label="Send message"
          id="chatSendButton"
        >
          <Send size={15} />
        </button>
      </form>
    </div>
  );
}
