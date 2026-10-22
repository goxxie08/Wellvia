import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  X, 
  Sparkles, 
  AlertCircle, 
  RotateCcw, 
  ShieldAlert, 
  Lightbulb, 
  RefreshCw 
} from 'lucide-react';
import { api } from '../../api/client';

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

export function ChatbotDrawer({ isOpen, onClose, onToggle }) {
  const [messages, setMessages] = useState([INITIAL_WELCOME]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPrompts, setShowPrompts] = useState(true);
  const [lastFailedMessage, setLastFailedMessage] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      // Auto-focus input when opened
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [messages, isOpen, loading]);

  // Format history according to backend contract: list of { role: 'user'|'model', text: '...' }
  const buildHistoryPayload = (currentMessages) => {
    return currentMessages
      .filter((m) => m.id !== 'welcome-1' && !m.isError && m.text)
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
    const historyPayload = buildHistoryPayload(messages);

    setMessages((prev) => [...prev, userMsg]);
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
    // Remove the trailing error message
    setMessages((prev) => prev.filter((m) => !m.isError));
    handleSend(null, text);
  };

  const handleClearConversation = () => {
    if (window.confirm("Start a new conversation? Prior chat history will be cleared.")) {
      setMessages([{
        ...INITIAL_WELCOME,
        id: `welcome-${Date.now()}`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
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
        <span>🔒 Confidential & Private • Your mood & health records are never shared with AI.</span>
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-messages" id="chatMessagesContainer">
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

            <div style={{ whiteSpace: 'pre-line' }}>{m.text}</div>

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
