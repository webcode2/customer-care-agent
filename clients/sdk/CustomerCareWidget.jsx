import React, { useState, useEffect } from 'react';

/**
 * CustomerCareWidget - Embeddable AI Agent
 * @param {string} orgId - The organization ID
 * @param {string} token - The public API key or JWT for the agent
 */
export const CustomerCareWidget = ({ orgId, token }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI assistant. How can I help you today?", isBot: true }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = { text: query, isBot: false };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response, isBot: true }]);
    } catch (err) {
      setMessages(prev => [...prev, { text: "Sorry, I'm having trouble connecting right now.", isBot: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="cc-sdk-container" style={{ position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 9999, fontFamily: 'Inter, sans-serif' }}>
      {!isOpen ? (
        <button 
          onClick={() => setIsOpen(true)}
          style={{
            width: '60px', height: '60px', borderRadius: '50%', background: '#10b981', 
            border: 'none', cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white'
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </button>
      ) : (
        <div style={{
          width: '350px', height: '500px', background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '16px', display: 'flex', flexDirection: 'column', overflow: 'hidden',
          boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
        }}>
          <header style={{ padding: '1rem', background: '#1e293b', display: 'flex', justifyContent: 'space-between', color: 'white' }}>
            <span style={{ fontWeight: 600 }}>AI Assistant</span>
            <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}>×</button>
          </header>

          <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {messages.map((m, i) => (
              <div key={i} style={{
                alignSelf: m.isBot ? 'flex-start' : 'flex-end',
                background: m.isBot ? '#1e293b' : '#10b981',
                color: 'white', padding: '0.75rem', borderRadius: '12px',
                maxWidth: '80%', fontSize: '0.9rem', lineHeight: '1.4'
              }}>
                {m.text}
              </div>
            ))}
            {isLoading && <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>AI is thinking...</div>}
          </div>

          <form onSubmit={sendMessage} style={{ padding: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            <input 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question..."
              style={{
                width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                padding: '0.75rem', borderRadius: '8px', color: 'white'
              }}
            />
          </form>
        </div>
      )}
    </div>
  );
};
