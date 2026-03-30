import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

export async function getThreads(): Promise<{ session_id: string; threads: any[] }> {
  const { data } = await api.get('/threads');
  return data;
}

export async function ragQuery(
  message: string,
  thread_id?: string | null
): Promise<{ thread_id: string; messages: string }> {
  const { data } = await api.post('/query', { message, thread_id: thread_id ?? null });
  return data;
}
