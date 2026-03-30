import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import ReactMarkdown from 'react-markdown';
import { getThreads, ragQuery } from './services';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [threadIds, setThreadIds] = useState<string[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getThreads().then(({ session_id, thread_ids }) => {
      setSessionId(session_id);
      setThreadIds(thread_ids);
    });
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    const { thread_id, messages: reply } = await ragQuery(input, activeThreadId);

    if (!activeThreadId) {
      setThreadIds((prev) => [...prev, thread_id]);
      setActiveThreadId(thread_id);
    }

    const assistantMessage: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: reply,
    };
    setMessages((prev) => [...prev, assistantMessage]);
  };

  return (
    <div className="app-container">
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
              <div className={`avatar ${msg.role}`}></div>
              <div className="message-content">
                <div className={`message-header ${msg.role}`}>
                  {msg.role === 'user' ? 'User' : 'Assistant'}
                </div>
                {msg.role === 'assistant'
                  ? <div className="text"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
                  : <div className="text">{msg.content}</div>
                }
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

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
            <button className="send-btn" onClick={handleSend}>
              <span>Send</span>
            </button>
          </div>
        </div>

      </footer>
    </div>
  );
}
