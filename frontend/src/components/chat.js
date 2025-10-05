// src/components/Chat.js
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const greetingLoadedRef = useRef(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load proactive greeting on mount (only once)
  useEffect(() => {
    if (!greetingLoadedRef.current && messages.length === 0) {
      loadGreeting();
      greetingLoadedRef.current = true;
    }
  }, []);

  const loadGreeting = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chat/greeting');
      const data = await response.json();
      
      setMessages([{
        type: 'assistant',
        content: data.greeting,
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Error loading greeting:', error);
      setMessages([{
        type: 'assistant',
        content: 'Hello! How can I help you manage your inventory today?',
        timestamp: new Date()
      }]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to UI
    const newUserMsg = {
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newUserMsg]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        })
      });

      const data = await response.json();

      // Update session ID if new
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      // Add assistant response
      const assistantMsg = {
        type: 'assistant',
        content: data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMsg]);

    } catch (error) {
      console.error('Error:', error);
      const errorMsg = {
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      backgroundColor: 'white' 
    }}>
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.map((msg, index) => (
          <div 
            key={index} 
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.type === 'user' ? 'flex-end' : 'flex-start',
              gap: '4px'
            }}
          >
            <div style={{
              maxWidth: '80%',
              padding: '12px 16px',
              borderRadius: '18px',
              backgroundColor: msg.type === 'user' ? '#3b82f6' : '#f3f4f6',
              color: msg.type === 'user' ? 'white' : '#1f2937',
              fontSize: '14px',
              textAlign: 'left',
              lineHeight: '1.4',
              wordWrap: 'break-word'
            }}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
            <div style={{
              fontSize: '12px',
              color: '#6b7280',
              marginLeft: msg.type === 'user' ? '0' : '16px',
              marginRight: msg.type === 'user' ? '16px' : '0'
            }}>
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {loading && (
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '4px'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '18px',
              backgroundColor: '#f3f4f6',
              color: '#1f2937',
              fontSize: '14px'
            }}>
              <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                <span style={{ animation: 'pulse 1.5s ease-in-out infinite' }}>●</span>
                <span style={{ animation: 'pulse 1.5s ease-in-out infinite 0.5s' }}>●</span>
                <span style={{ animation: 'pulse 1.5s ease-in-out infinite 1s' }}>●</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div style={{
        padding: '20px',
        borderTop: '1px solid #e5e7eb',
        backgroundColor: '#f8fafc'
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about inventory, trends, or recommendations..."
            rows="2"
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '12px',
              resize: 'none',
              fontSize: '14px',
              fontFamily: 'system-ui, -apple-system, sans-serif',
              outline: 'none',
              transition: 'border-color 0.2s ease',
              backgroundColor: 'white'
            }}
            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
            onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
          />
          <button 
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{
              padding: '12px 20px',
              backgroundColor: loading || !input.trim() ? '#d1d5db' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'background-color 0.2s ease'
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
