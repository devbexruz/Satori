import React from 'react';

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onOpenProfileModal,
  onOpenTokenModal,
  onLogout,
  sidebarOpen,
  onToggleSidebar
}) {
  return (
    <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <div className="logo">
          Satori<span>AI</span>
        </div>
        <button 
          className="toggle-sidebar-btn" 
          onClick={onToggleSidebar}
          title="Close menu"
        >
          ✕
        </button>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Yangi suhbat
      </button>

      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div style={{ padding: '20px', color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center' }}>
            Suhbatlar tarixi mavjud emas
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${activeSessionId === session.id ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
              title={session.title}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              {session.title}
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <button className="footer-btn" onClick={onOpenProfileModal}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2a10 10 0 0 0-9 11.5c.6 3 2.5 5.5 5 7l1.5-1.2a1 1 0 0 1 1-.1 7 7 0 0 0 7 0 1 1 0 0 1 1 .1l1.5 1.2c2.5-1.5 4.4-4 5-7A10 10 0 0 0 12 2z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          Mening xotiram (RAG)
        </button>
        <button className="footer-btn" onClick={onOpenTokenModal}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          Developer Sozlamalari
        </button>
        <button className="footer-btn" onClick={onLogout} style={{ color: '#ef4444' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          Chiqish
        </button>
      </div>
    </aside>
  );
}
