import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

const DEFAULT_AI_URL = 'http://localhost:8002';
const DEFAULT_DOCS_URL = 'http://localhost:8000';
const DEFAULT_BACKEND_URL = 'http://localhost:8080';

export default function App() {
  // Authentication states
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('satori_user') || 'null');
    } catch (e) {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('satori_token') || '');
  const [backendUrl, setBackendUrl] = useState(() => localStorage.getItem('satori_backend_url') || DEFAULT_BACKEND_URL);

  // Auth screen form states
  const [activeTab, setActiveTab] = useState('login'); // 'login' or 'register'
  const [authUsername, setAuthUsername] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authFullName, setAuthFullName] = useState('');
  const [authError, setAuthError] = useState('');
  const [authSuccess, setAuthSuccess] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // Config states for microservices
  const [aiApiUrl, setAiApiUrl] = useState(() => localStorage.getItem('satori_ai_url') || DEFAULT_AI_URL);
  const [docsApiUrl, setDocsApiUrl] = useState(() => localStorage.getItem('satori_docs_url') || DEFAULT_DOCS_URL);

  // Layout and dialog states
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showTokenModal, setShowTokenModal] = useState(false);

  // App domain states
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // RAG memory states
  const [ragFacts, setRagFacts] = useState([]);
  const [newFactText, setNewFactText] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);

  // Global error helper
  const [errorMessage, setErrorMessage] = useState('');

  // Fetch unique chat sessions from backend database
  const fetchSessions = useCallback(async () => {
    if (!token) return;
    try {
      const response = await fetch(`${aiApiUrl}/api/v1/ai/sessions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
      } else {
        console.error('Failed to load chat sessions', response.statusText);
      }
    } catch (err) {
      console.error('Connection error when loading sessions', err);
    }
  }, [aiApiUrl, token]);

  // Initial load
  useEffect(() => {
    if (user && token) {
      fetchSessions();
    }
  }, [user, token, fetchSessions]);

  // Load chat messages when activeSessionId changes
  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }
    if (!token) return;

    const fetchHistory = async () => {
      try {
        const response = await fetch(`${aiApiUrl}/api/v1/ai/history/${activeSessionId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          }
        });
        if (response.ok) {
          const data = await response.json();
          setMessages(data.map(m => ({
            role: m.role,
            content: m.content
          })));
        } else {
          setErrorMessage('Suhbat tarixini yuklab bo\'lmadi.');
        }
      } catch (err) {
        setErrorMessage('Suhbat tarixini yuklashda tarmoq xatoligi yuz berdi.');
      }
    };

    fetchHistory();
  }, [activeSessionId, aiApiUrl, token]);

  // Fetch all RAG profile facts from backend database
  const fetchProfileFacts = useCallback(async () => {
    if (!token) return;
    setProfileLoading(true);
    try {
      const response = await fetch(`${aiApiUrl}/api/v1/ai/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setRagFacts(data);
      } else {
        console.error('Failed to fetch profile facts');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setProfileLoading(false);
    }
  }, [aiApiUrl, token]);

  // Trigger loading RAG facts when modal opens
  useEffect(() => {
    if (showProfileModal) {
      fetchProfileFacts();
    }
  }, [showProfileModal, fetchProfileFacts]);

  // Handle Login or Registration submission
  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthSuccess('');
    setAuthLoading(true);

    const isLogin = activeTab === 'login';
    const endpoint = isLogin ? '/api/Login' : '/api/Register';
    const url = `${backendUrl}${endpoint}`;

    try {
      const payload = isLogin
        ? { Username: authUsername, Password: authPassword }
        : { Username: authUsername, Password: authPassword, FullName: authFullName };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        if (isLogin) {
          // SatoriBackend returns { userData: { username: "...", fullName: "..." }, token: "..." }
          const userObj = data.userData;
          const tokenStr = data.token;

          localStorage.setItem('satori_user', JSON.stringify(userObj));
          localStorage.setItem('satori_token', tokenStr);
          localStorage.setItem('satori_backend_url', backendUrl);

          setUser(userObj);
          setToken(tokenStr);
          
          setAuthUsername('');
          setAuthPassword('');
        } else {
          setAuthSuccess('Muvaffaqiyatli ro\'yxatdan o\'tdingiz! Endi tizimga kiring.');
          setActiveTab('login');
          setAuthPassword('');
        }
      } else {
        const errText = await response.text();
        let errMsg = isLogin 
          ? 'Tizimga kirishda xatolik yuz berdi. Foydalanuvchi nomi yoki parolni tekshiring.' 
          : 'Ro\'yxatdan o\'tishda xatolik yuz berdi. Foydalanuvchi nomi band bo\'lishi mumkin.';
        try {
          const errData = JSON.parse(errText);
          errMsg = errData.detail || errData.message || errMsg;
        } catch {
          if (response.status === 401) {
            errMsg = 'Foydalanuvchi nomi yoki parol noto\'g\'ri.';
          }
        }
        setAuthError(errMsg);
      }
    } catch (err) {
      setAuthError('Tarmoq xatoligi: Satori Backend API (port 8080) ishlayotganligini va CORS yoqilganligini tekshiring.');
    } finally {
      setAuthLoading(false);
    }
  };

  // Logout function
  const handleLogout = () => {
    if (!window.confirm('Tizimdan chiqishni xohlaysizmi?')) return;
    localStorage.removeItem('satori_user');
    localStorage.removeItem('satori_token');
    setUser(null);
    setToken('');
    setSessions([]);
    setActiveSessionId(null);
    setMessages([]);
  };

  // Add a custom fact/learning to the database
  const handleAddFact = async (e) => {
    e.preventDefault();
    if (!newFactText.trim()) return;

    setProfileLoading(true);
    try {
      const response = await fetch(`${aiApiUrl}/api/v1/ai/profile`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ fact: newFactText.trim() })
      });
      if (response.ok) {
        setNewFactText('');
        fetchProfileFacts();
      } else {
        const errorData = await response.json();
        alert(`Xatolik: ${errorData.detail || 'Ma\'lumotni eslab qolib bo\'lmadi'}`);
      }
    } catch (err) {
      alert('Tarmoq xatoligi. Backend yoqilganligini tekshiring.');
    } finally {
      setProfileLoading(false);
    }
  };

  // Delete a fact from database
  const handleDeleteFact = async (factId) => {
    if (!window.confirm('Ushbu eslatmani o\'chirishni xohlaysizmi?')) return;
    
    setProfileLoading(true);
    try {
      const response = await fetch(`${aiApiUrl}/api/v1/ai/profile/${factId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        fetchProfileFacts();
      } else {
        alert('Ma\'lumotni o\'chirib bo\'lmadi.');
      }
    } catch (err) {
      alert('Tarmoq xatoligi.');
    } finally {
      setProfileLoading(false);
    }
  };

  // Send message to chatbot agent
  const handleSendMessage = async (text) => {
    if (!text.trim() || isGenerating) return;

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setIsGenerating(true);
    setErrorMessage('');

    try {
      const response = await fetch(`${aiApiUrl}/api/v1/ai/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          message: text,
          session_id: activeSessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // If it was a new session, backend will generate and return a session_id
        if (!activeSessionId) {
          setActiveSessionId(data.session_id);
          fetchSessions();
        }

        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response
        }]);
      } else {
        const errData = await response.json().catch(() => ({}));
        setErrorMessage(errData.detail || 'Server javob berishda xatolikka yo\'l qo\'ydi.');
      }
    } catch (err) {
      setErrorMessage('Tarmoq xatoligi: SatoriAI API serveri (port 8002) ishlayotganligini tekshiring.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
  };

  // Render Login screen if user is not authenticated
  if (!user || !token) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-logo">
            Satori<span>AI</span>
          </div>
          <div className="auth-subtitle">
            Hujjatlarni boshqarish va AI tahlil tizimi
          </div>

          <div className="auth-tabs">
            <button 
              className={`auth-tab ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => { setActiveTab('login'); setAuthError(''); setAuthSuccess(''); }}
            >
              Kirish
            </button>
            <button 
              className={`auth-tab ${activeTab === 'register' ? 'active' : ''}`}
              onClick={() => { setActiveTab('register'); setAuthError(''); setAuthSuccess(''); }}
            >
              Ro'yxatdan o'tish
            </button>
          </div>

          <form className="auth-form" onSubmit={handleAuthSubmit}>
            {authError && <div className="auth-error">{authError}</div>}
            {authSuccess && <div className="auth-success">{authSuccess}</div>}

            <div className="input-group">
              <label>Foydalanuvchi nomi</label>
              <input 
                type="text" 
                placeholder="Username kiriting..." 
                value={authUsername}
                onChange={(e) => setAuthUsername(e.target.value)}
                required 
              />
            </div>

            {activeTab === 'register' && (
              <div className="input-group">
                <label>To'liq ism-sharifingiz</label>
                <input 
                  type="text" 
                  placeholder="Ismingizni kiriting..." 
                  value={authFullName}
                  onChange={(e) => setAuthFullName(e.target.value)}
                  required 
                />
              </div>
            )}

            <div className="input-group">
              <label>Parol</label>
              <input 
                type="password" 
                placeholder="Parol kiriting..." 
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                required 
              />
            </div>

            <div className="input-group">
              <label>Satori Backend API URL</label>
              <input 
                type="text" 
                value={backendUrl}
                onChange={(e) => setBackendUrl(e.target.value)}
                placeholder="http://localhost:8080"
                required 
              />
            </div>

            <button type="submit" className="modal-action-btn" disabled={authLoading}>
              {authLoading ? 'Yuklanmoqda...' : (activeTab === 'login' ? 'Tizimga kirish' : 'Ro\'yxatdan o\'tish')}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Render main app workspace
  return (
    <div className="app-container">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
        onNewChat={handleNewChat}
        onOpenProfileModal={() => setShowProfileModal(true)}
        onOpenTokenModal={() => setShowTokenModal(true)}
        onLogout={handleLogout}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <ChatWindow
        messages={messages}
        onSendMessage={handleSendMessage}
        isGenerating={isGenerating}
        onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
      />

      {errorMessage && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          backgroundColor: '#ef4444',
          color: '#ffffff',
          padding: '12px 20px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '14px',
          maxWidth: '400px'
        }}>
          <span>{errorMessage}</span>
          <button 
            onClick={() => setErrorMessage('')} 
            style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* RAG Memory Modal */}
      {showProfileModal && (
        <div className="modal-overlay" onClick={() => setShowProfileModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h2>Mening xotiram (RAG)</h2>
              <button className="modal-close-btn" onClick={() => setShowProfileModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '10px' }}>
                SatoriAI {user.fullName} haqingizdagi ma'lumotlarni eslab qolib, kelajakda javoblarni moslashtirish uchun vector database'dan foydalanadi.
              </p>
              
              <form onSubmit={handleAddFact} style={{ display: 'flex', gap: '10px' }}>
                <input
                  type="text"
                  placeholder="Yangi ma'lumot kiriting (masalan: Mening ismim Bexruz)..."
                  value={newFactText}
                  onChange={(e) => setNewFactText(e.target.value)}
                  style={{ 
                    flex: 1, 
                    backgroundColor: 'var(--bg-deep)', 
                    border: '1px solid var(--border-color)', 
                    color: 'var(--text-main)', 
                    padding: '10px 14px', 
                    borderRadius: '8px', 
                    outline: 'none',
                    fontSize: '14px'
                  }}
                  required
                  disabled={profileLoading}
                />
                <button 
                  type="submit" 
                  className="modal-action-btn" 
                  style={{ padding: '0 20px', whiteSpace: 'nowrap' }} 
                  disabled={profileLoading}
                >
                  {profileLoading ? 'Yozilmoqda...' : 'Eslab qol'}
                </button>
              </form>

              <div style={{ marginTop: '20px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '10px', color: 'var(--text-main)' }}>
                  Saqlangan ma'lumotlar ({ragFacts.length})
                </h4>
                {profileLoading && ragFacts.length === 0 ? (
                  <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Yuklanmoqda...</div>
                ) : ragFacts.length === 0 ? (
                  <div style={{ 
                    padding: '20px', 
                    textAlign: 'center', 
                    color: 'var(--text-muted)', 
                    fontSize: '13px', 
                    border: '1px dashed var(--border-color)', 
                    borderRadius: '8px' 
                  }}>
                    Xotirada hozircha hech qanday ma'lumot saqlanmagan.
                  </div>
                ) : (
                  <div style={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    gap: '8px', 
                    maxHeight: '300px', 
                    overflowY: 'auto', 
                    paddingRight: '4px' 
                  }}>
                    {ragFacts.map((fact) => (
                      <div 
                        key={fact.id} 
                        style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center', 
                          backgroundColor: 'var(--bg-deep)', 
                          border: '1px solid var(--border-color)', 
                          padding: '10px 14px', 
                          borderRadius: '8px' 
                        }}
                      >
                        <span style={{ fontSize: '13px', color: 'var(--text-main)', flex: 1, marginRight: '10px' }}>
                          {fact.fact}
                        </span>
                        <button
                          onClick={() => handleDeleteFact(fact.id)}
                          style={{ 
                            background: 'transparent', 
                            border: 'none', 
                            color: '#ef4444', 
                            cursor: 'pointer', 
                            fontSize: '14px', 
                            padding: '4px' 
                          }}
                          title="O'chirish"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Developer Tokens Modal */}
      {showTokenModal && (
        <div className="modal-overlay" onClick={() => setShowTokenModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Developer Sozlamalari</h2>
              <button className="modal-close-btn" onClick={() => setShowTokenModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="input-group">
                <label>SatoriAi API URL</label>
                <input
                  type="text"
                  value={aiApiUrl}
                  onChange={(e) => setAiApiUrl(e.target.value)}
                  placeholder="http://localhost:8002"
                />
              </div>
              <div className="input-group">
                <label>SatoriDocs API URL</label>
                <input
                  type="text"
                  value={docsApiUrl}
                  onChange={(e) => setDocsApiUrl(e.target.value)}
                  placeholder="http://localhost:8000"
                />
              </div>
              <div className="input-group">
                <label>JWT Token</label>
                <textarea
                  rows={5}
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="JWT tokenini kiriting..."
                  style={{ 
                    backgroundColor: 'var(--bg-deep)', 
                    border: '1px solid var(--border-color)', 
                    color: 'var(--text-main)', 
                    padding: '10px 14px', 
                    borderRadius: '8px', 
                    outline: 'none', 
                    resize: 'none', 
                    fontSize: '11px', 
                    fontFamily: 'monospace' 
                  }}
                />
              </div>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                SatoriAI ushbu JWT token orqali SatoriDocs (port 8000) servisi bilan bog'lanadi. Token auth signature tekshiruvidan muvaffaqiyatli o'tishi zarur.
              </p>
              <button 
                className="modal-action-btn" 
                onClick={() => {
                  localStorage.setItem('satori_token', token);
                  localStorage.setItem('satori_ai_url', aiApiUrl);
                  localStorage.setItem('satori_docs_url', docsApiUrl);
                  setShowTokenModal(false);
                  fetchSessions();
                }}
              >
                Sozlamalarni saqlash
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
