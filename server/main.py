from fastapi import FastAPI, Cookie, Response, HTTPException
from history.db import db
from rag import retrieve_docs, build_augmented_message, get_llm_response
import uuid

from pydantic import BaseModel

class MessageRequest(BaseModel):
    thread_id: str | None = None
    message: str

app = FastAPI()

SYSTEM_PROMPT = """You are a helpful assistant of Dev Archive, a RAG pipeline
to help query and analyze software engineering case studies."""

@app.get("/api/threads")
def show_threads(response: Response, session_id: str = Cookie(default=None)):
    if not session_id:
      session_id = str(uuid.uuid4())
      response.set_cookie(key="session_id", value=session_id)

    threads = db.get_session_threads(session_id)
    return {"session_id": session_id, "threads": threads}

@app.post("/api/message")
def send_message(body: MessageRequest, session_id: str = Cookie(default=None)):
    thread_id = body.thread_id
    message = body.message

    if not session_id:
        raise HTTPException(status_code=401, detail="No session")
    
    thread_messages = db.get_thread_messages(thread_id)

    if thread_id and not thread_messages:
        raise HTTPException(status_code=404, detail="Thread not found")

    # if no thread_id, this is a new thread
    if not thread_id:
        thread_id = str(uuid.uuid4())

    docs = retrieve_docs(message)
    augmented = build_augmented_message(message, docs)

    history = [
        {"role": "developer", "content": SYSTEM_PROMPT},
        *thread_messages,
        {"role": "user", "content": augmented},
    ]
    llm_response = get_llm_response(history)

    thread_messages.append({"role": "user", "content": message})
    thread_messages.append({"role": "assistant", "content": llm_response})

    db.save_thread(thread_id, session_id, thread_messages)

    return {"thread_id": thread_id, "messages": thread_messages}

