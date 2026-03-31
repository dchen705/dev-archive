import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getThreads, getThread, ragQuery } from './services';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Thread {
  id: string,
  title: string
}

export default function App() {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeThread, setActiveThread] = useState<Thread | null>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getThreads().then(({ threads }) => {
      setThreads(threads);
    });
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleThreadSelect = async (thread: Thread) => {
    if (thread.id === activeThread?.id) {
      setMessages([])
      setActiveThread(null)
      return;
    }

    const { messages: fetched } = await getThread(thread.id);
    setMessages(fetched.map((msg) => ({
      role: msg.role as Message['role'],
      content: msg.content,
    })));
    setActiveThread(thread);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    const userMessage: Message = {
      role: 'user',
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      const { thread, reply } = await ragQuery(input, activeThread?.id);

      if (!activeThread) {
        setThreads((prev) => [...prev, thread]);
        setActiveThread(thread);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: reply,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Side Nav */}
      <nav className="side-nav">
        <h3>Your Threads</h3>
        {threads.map((thread) => (
          <button
            key={thread.id}
            type="button"
            className={activeThread?.id === thread.id ? 'active' : ''}
            onClick={() => handleThreadSelect(thread)}
          >
            {thread.title}
          </button>
        ))}
      </nav>

      {/* Chat Canvas */}
      <main className="chat-canvas">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="message-group"
            >
              <div className="message-content">
                <div className={`message-header ${msg.role}`}>
                  {msg.role === 'user' ? 'User' : 'Assistant'}
                </div>
                {msg.role === 'assistant'
                  ? <div className="text"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{ a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a> }}>{msg.content}</ReactMarkdown></div>
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
            disabled={isLoading}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <div className="input-actions">
            <button className="send-btn" onClick={handleSend} disabled={isLoading}>
              <span>{isLoading ? 'Thinking...' : 'Send'}</span>
            </button>
          </div>
        </div>

      </footer>
    </div>
  );
}
