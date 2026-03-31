import axios from 'axios';

interface Thread {
  id: string,
  title: string
}

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

export async function getThreads(): Promise<{ session_id: string; threads: Thread[] }> {
  const { data } = await api.get('/threads');
  return data;
}

export async function getThread(
  thread_id: string
): Promise<{ messages: { role: string; content: string }[] }> {
  const { data } = await api.get(`/threads/${thread_id}`);
  return data;
}

export async function ragQuery(
  message: string,
  thread_id?: string | null
): Promise<{ thread: Thread; reply: string }> {
  const { data } = await api.post('/query', { message, thread_id: thread_id ?? null });
  return data;
}
