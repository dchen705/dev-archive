/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Terminal,
  User,
  FileText,
  Database,
  Copy,
  Paperclip,
  Send,
  MoreHorizontal
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export default function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
      // {
      //   id: '1',
      //   role: 'user',
      //   content: 'How did Netflix implement the circuit breaker pattern during their migration to microservices? Focus on the Hystrix integration logic.',
      // },
      // {
      //   id: '2',
      //   role: 'assistant',
      //   content: 'Netflix utilized Hystrix to prevent cascading failures. Based on the 2014 architecture audit in your library, the primary implementation focused on wrapping network calls in command patterns.',
      // }
  ]);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages([...messages, newMessage]);
    setInput('');
  };

  return (
    <div className="app-container">
      {/* Header / Context Bar */}
      <header className="context-bar">
        <span className="context-label">Context:</span>
        <div className="chip">
          <FileText size={14} />
          distributed_systems_v3.pdf
        </div>
        <div className="chip">
          <Database size={14} />
          postgres_scaling_case_study.md
        </div>
        <div className="status-indicator">
          <div className="dot"></div>
          Index Synced
        </div>
      </header>

      {/* Chat Canvas */}
      <main className="chat-canvas">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="message-group"
            >
              <div className={`avatar ${msg.role}`}>
                {msg.role === 'user' ? <User size={18} /> : <Terminal size={18} />}
              </div>
              <div className="message-content">
                <div className={`message-header ${msg.role}`}>
                  {msg.role === 'user' ? 'User' : 'Assistant'}
                </div>
                <div className="text">
                  {msg.content}
                </div>

                {msg.role === 'assistant' && msg.id === '2' && (
                  <div className="text" style={{ marginTop: '24px' }}>
                    The system monitored the success/failure ratio. If the error threshold (defaulting to 50%) was exceeded within a 10s window, the circuit would open, and all subsequent calls would immediately trigger the <code style={{ backgroundColor: '#353436', padding: '2px 6px', borderRadius: '4px', color: '#b6c4ff', fontWeight: 600 }}>getFallback()</code> method.
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Suggestion Prompt */}
        {/* <div className="message-group" style={{ opacity: 0.4 }}>
          <div className="avatar" style={{ border: '1px dashed var(--outline)', background: 'none' }}>
            <MoreHorizontal size={18} />
          </div>
          <div className="message-content" style={{ paddingTop: '6px' }}>
            <div className="text" style={{ fontStyle: 'italic', fontSize: '16px' }}>
              Analyze memory overhead for 1000+ open circuits...
            </div>
          </div>
        </div> */}

        <div ref={chatEndRef} />
      </main>

      {/* Footer / Input */}
      <footer className="footer">
        <div className="input-wrapper">
          <textarea
            className="chat-input"
            placeholder="Ask about architectural patterns or codebase history..."
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <div className="input-actions">
            <button className="icon-btn">
              <Paperclip size={24} />
            </button>
            <button className="send-btn" onClick={handleSend}>
              <span>Send</span>
              <Send size={14} />
            </button>
          </div>
        </div>

        <div className="bottom-stats">
          <div className="stat-item">Contextual RAG: Active</div>
          <div className="stat-item">Model: GPT-4o-Turbo</div>
          <div className="stat-item">Latency: 142ms</div>
        </div>
      </footer>
    </div>
  );
}
