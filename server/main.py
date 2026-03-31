from fastapi import FastAPI, Cookie, Response, HTTPException
from history.db import db
from rag import title_thread, handle_rag_query
import uuid

from pydantic import BaseModel

class MessageRequest(BaseModel):
    thread_id: str | None = None
    message: str

app = FastAPI()

@app.get("/api/threads")
def get_threads(response: Response, session_id: str = Cookie(default=None)):
    if not session_id:
      session_id = str(uuid.uuid4())
      response.set_cookie(key="session_id", value=session_id)

    threads = db.get_session_threads(session_id)
    return {"session_id": session_id, "threads": threads}

@app.get("/api/threads/{thread_id}")
def get_thread(thread_id: str, session_id: str = Cookie(default=None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="No session")

    messages = db.get_thread_messages(thread_id)

    if not messages:
        raise HTTPException(status_code=404, detail="Thread not found")

    return {"messages": messages}

@app.post("/api/query")
def save_query_and_response(body: MessageRequest, session_id: str = Cookie(default=None)):
    thread_id = body.thread_id
    message = body.message

    if not session_id:
        raise HTTPException(status_code=401, detail="No session")
    
    thread_messages = db.get_thread_messages(thread_id)

    if thread_id and not thread_messages:
        raise HTTPException(status_code=404, detail="Thread not found")

    # if no thread_id, this is a new thread
    thread_title = None
    if not thread_id:
        thread_id = str(uuid.uuid4())
        thread_title = title_thread(message)

    response = handle_rag_query(message, thread_messages)

    thread_messages.append({"role": "user", "content": message})
    thread_messages.append({"role": "assistant", "content": response})

    db.save_thread(thread_id, session_id, thread_title, thread_messages)

    return {"thread": {"id": thread_id, "title": thread_title}, "reply": response}

