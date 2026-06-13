import React, { useState, useRef, useEffect } from 'react';

export default function ChatWindow({
  messages,
  onSendMessage,
  isGenerating,
  onSidebarToggle,
  sidebarOpen
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const welcomePrompts = [
    {
      title: "Hujjatlar ro'yxatini ko'rish",
      subtitle: "Menda qanday hujjatlar borligini SatoriDocs'dan so'rash",
      prompt: "Mening barcha hujjatlarim ro'yxatini chiqar"
    },
    {
      title: "Clean Architecture bo'limini o'zgartirish",
      subtitle: "SatoriDocs'dagi hujjat bo'limini yangilash",
      prompt: "SatoriDocs'dagi Clean Architecture hujjatini topib, 'Introduction' bo'limi matnini 'Ushbu tizim ASP.NET Core va React asosida yozilgan' deb taxrirlab ber"
    },
    {
      title: "Shaxsiy ma'lumotni eslab qolish",
      subtitle: "SatoriAI xotirasiga (RAG) ma'lumot kiritish",
      prompt: "Mening ismim Bexruz va men C# hamda Python dasturchisiman. Ushbu ma'lumotni eslab qol."
    },
    {
      title: "Satori loyihasining arxitekturasi",
      subtitle: "Qaysi servislar borligini so'rash",
      prompt: "Satori loyihasida qanday servislar va microservicelar ishlaydi?"
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim() || isGenerating) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Helper to format messages (basic markdown conversion)
  const renderMessageContent = (text) => {
    if (!text) return null;

    // Splitting by code blocks: ```code```
    const parts = text.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        // Extract language and code content
        const lines = part.slice(3, -3).trim().split('\n');
        let language = 'code';
        let codeContent = lines.join('\n');
        
        if (lines[0] && lines[0].length < 15 && !lines[0].includes(' ') && lines[0] === lines[0].toLowerCase()) {
          language = lines[0];
          codeContent = lines.slice(1).join('\n');
        }

        return (
          <pre key={index}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', marginBottom: '8px', textTransform: 'uppercase', fontWeight: 600 }}>
              {language}
            </div>
            <code>{codeContent}</code>
          </pre>
        );
      }

      // Format bold (**text**) and bullet points (- item)
      const formattedLines = part.split('\n').map((line, lIdx) => {
        let renderedLine = line;

        // Bold match
        const boldRegex = /\*\*(.*?)\*\*/g;
        if (boldRegex.test(renderedLine)) {
          const parts = renderedLine.split(boldRegex);
          renderedLine = parts.map((p, pIdx) => pIdx % 2 === 1 ? <strong key={pIdx}>{p}</strong> : p);
        }

        // Inline code match `code`
        const inlineCodeRegex = /`(.*?)`/g;
        if (inlineCodeRegex.test(line)) {
          // If already react objects, map through them
          if (Array.isArray(renderedLine)) {
            renderedLine = renderedLine.map(item => {
              if (typeof item === 'string') {
                const subParts = item.split(inlineCodeRegex);
                return subParts.map((sp, spIdx) => spIdx % 2 === 1 ? <code key={spIdx}>{sp}</code> : sp);
              }
              return item;
            });
          } else {
            const subParts = renderedLine.split(inlineCodeRegex);
            renderedLine = subParts.map((sp, spIdx) => spIdx % 2 === 1 ? <code key={spIdx}>{sp}</code> : sp);
          }
        }

        // Check list items
        if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
          return (
            <li key={lIdx} style={{ marginLeft: '20px', marginBottom: '4px' }}>
              {Array.isArray(renderedLine) ? renderedLine.slice(1) : (typeof renderedLine === 'string' ? renderedLine.substring(2) : renderedLine)}
            </li>
          );
        }

        // Check headers
        if (line.trim().startsWith('### ')) {
          return <h3 key={lIdx} style={{ margin: '18px 0 10px 0', color: 'var(--text-main)', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>{line.substring(4)}</h3>;
        }
        if (line.trim().startsWith('## ')) {
          return <h2 key={lIdx} style={{ margin: '22px 0 12px 0', color: 'var(--text-main)', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>{line.substring(3)}</h2>;
        }

        return <p key={lIdx}>{renderedLine}</p>;
      });

      return <React.Fragment key={index}>{formattedLines}</React.Fragment>;
    });
  };

  return (
    <div className="main-chat">
      <div className="chat-header">
        {!sidebarOpen && (
          <button 
            className="toggle-sidebar-btn" 
            onClick={onSidebarToggle}
            title="Suhbatlar tarixi"
          >
            ☰
          </button>
        )}
        <div style={{ marginLeft: sidebarOpen ? '0' : '12px', fontSize: '15px', fontWeight: 600 }}>
          SatoriAI Assistant
        </div>
        <div style={{ width: '40px' }}></div> {/* Spacer */}
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <h1 className="welcome-title">
              Salom, <span>Bexruz</span>
            </h1>
            <p className="welcome-subtitle">
              SatoriAI markaziy koordinatori tayyor. SatoriDocs hujjatlaridan ma'lumot olishingiz, ularni chat orqali taxrirlashingiz va shaxsiy ma'lumotlarni xotirada saqlashingiz mumkin.
            </p>
            <div className="cards-grid">
              {welcomePrompts.map((card, idx) => (
                <div 
                  key={idx} 
                  className="prompt-card"
                  onClick={() => setInput(card.prompt)}
                >
                  <h4>{card.title}</h4>
                  <p>{card.subtitle}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message-row ${msg.role}`}>
              <div className={`avatar ${msg.role === 'user' ? 'user' : 'ai'}`}>
                {msg.role === 'user' ? 'U' : 'AI'}
              </div>
              <div className="message-bubble">
                {renderMessageContent(msg.content)}
              </div>
            </div>
          ))
        )}

        {isGenerating && (
          <div className="message-row assistant">
            <div className="avatar ai">AI</div>
            <div className="message-bubble">
              {/* Fake status showing doc service integration */}
              {messages[messages.length - 1]?.content?.toLowerCase().includes('hujjat') && (
                <div className="tool-status">
                  <div className="spinner"></div>
                  SatoriDocs API port 8000 ga bog'lanilmoqda va hujjatlar o'qilmoqda...
                </div>
              )}
              {messages[messages.length - 1]?.content?.toLowerCase().includes('eslab') && (
                <div className="tool-status">
                  <div className="spinner"></div>
                  RAG profil ma'lumotlar bazasiga yozilmoqda...
                </div>
              )}
              <div className="thinking-container">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-bar">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="SatoriAI ga xabar yuboring..."
            disabled={isGenerating}
          />
          <button 
            type="submit" 
            className="send-btn" 
            disabled={!input.trim() || isGenerating}
            title="Xabar yuborish"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
        <p className="input-disclaimer">
          SatoriAI xatoliklarga yo'l qo'yishi mumkin. Muhim ma'lumotlarni tekshirib oling.
        </p>
      </div>
    </div>
  );
}
