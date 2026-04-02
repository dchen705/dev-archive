import { motion, AnimatePresence } from 'motion/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message, Thread } from './types';

interface SideNavProps {
  threads: Thread[];
  activeThreadId: string | undefined;
  onThreadSelect: (thread: Thread) => void;
}

export function SideNav({ threads, activeThreadId, onThreadSelect }: SideNavProps) {
  return (
    <nav className="side-nav">
      <h3>Your Threads</h3>
      {threads.map((thread) => (
        <button
          key={thread.id}
          type="button"
          className={activeThreadId === thread.id ? 'active' : ''}
          onClick={() => onThreadSelect(thread)}
        >
          {thread.title}
        </button>
      ))}
    </nav>
  );
}

interface ChatCanvasProps {
  messages: Message[];
  chatEndRef: React.RefObject<HTMLDivElement | null>;
}

export function ChatCanvas({ messages, chatEndRef }: ChatCanvasProps) {
  return (
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
                ? (
                  <div className="text">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{ a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a> }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )
                : <div className="text">{msg.content}</div>
              }
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      <div ref={chatEndRef} />
    </main>
  );
}

interface FooterProps {
  input: string;
  isLoading: boolean;
  onInputChange: (value: string) => void;
  onSend: () => void;
}

export function Footer({ input, isLoading, onInputChange, onSend }: FooterProps) {
  return (
    <footer className="footer">
      <div className="input-wrapper">
        <textarea
          className="chat-input"
          placeholder="Search and ask questions about software engineering case studies..."
          rows={1}
          value={input}
          disabled={isLoading}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
        />
        <div className="input-actions">
          <button className="send-btn" onClick={onSend} disabled={isLoading}>
            <span>{isLoading ? 'Thinking...' : 'Send'}</span>
          </button>
        </div>
      </div>
    </footer>
  );
}
