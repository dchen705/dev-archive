import { useState, useRef, useEffect } from 'react';
import { getThreads, getThread, ragQuery } from './services';
import { SideNav, ChatCanvas, Footer } from './components';
import type { Message, Thread } from './types';

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
      setMessages([]);
      setActiveThread(null);
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
    setMessages((prev) => [...prev, { role: 'user', content: input }]);
    setInput('');

    try {
      const { thread, reply } = await ragQuery(input, activeThread?.id);

      if (!activeThread) {
        setThreads((prev) => [...prev, thread]);
        setActiveThread(thread);
      }

      setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <SideNav
        threads={threads}
        activeThreadId={activeThread?.id}
        onThreadSelect={handleThreadSelect}
      />
      <ChatCanvas messages={messages} chatEndRef={chatEndRef} />
      <Footer
        input={input}
        isLoading={isLoading}
        onInputChange={setInput}
        onSend={handleSend}
      />
    </div>
  );
}
