import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
from pinecone import Pinecone

load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'
MODEL_CONTEXT_LIMITS = {
  'gpt-4o-mini': 128_000,
}
client = OpenAI(api_key=API_KEY)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
PINECONE_INDEX_NAME=os.getenv("PINECONE_INDEX_NAME")
PINECONE_INDEX_NAMESPACE=os.getenv("PINECONE_INDEX_NAMESPACE")

dense_index = pc.Index(PINECONE_INDEX_NAME)

class Message(dict):
  def __init__(self, role, content):
      super().__init__(role=role, content=content)
      self.role = role
      self.content = content

class ChatHistory(list):
  def add(self, message):
      self.append(message)

class TokenManager:
  def __init__(self, model, max_tokens, history):
    self.encoding = tiktoken.encoding_for_model(model)
    self.max_tokens = max_tokens
    self.history = history

  def token_count(self):
    full_text = ''.join([m.content for m in self.history])
    tokens = self.encoding.encode(full_text)
    return len(tokens)

  def exceeds_limit(self):
    return self.token_count() > self.max_tokens

class ChatManager():
  def __init__(self, model, system_prompt):
    self.model = model
    self.history = ChatHistory()
    self.system_prompt = system_prompt
    self.user_input = None
    self.client = OpenAI(api_key=API_KEY)
    context_limit = MODEL_CONTEXT_LIMITS.get(model, 128_000)
    self.context_limit = context_limit
    self.token_manager = TokenManager(model, context_limit, self.history)

  def start(self):
    self.history.add(Message("developer", self.system_prompt))
    print("Welcome!")
    print("Enter 'exit' at any time to quit the application.")
    self.assistant_prompt("Assistant: How can I help you?")

  def assistant_prompt(self, prompt, do_print=True):
     if do_print:
       print(prompt)

     self.history.add(Message("assistant", prompt))

  def print_context_usage(self):
    used = self.token_manager.token_count()
    limit = self.context_limit
    percent = (used / limit) * 100 if limit else 0
    print(f"\n[Context: {used} / {limit} tokens used ({percent:.1f}%)]")

  def user_prompt(self):
     self.user_input = input("\nUser: ")
     if self.user_input == "exit":
       return

     results = dense_index.search(
       namespace=PINECONE_INDEX_NAMESPACE,
       query={
         "top_k": 12,
         "inputs": {
           "text": self.user_input
         }
       }
     )

     documentation = ""

     for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get('chunk_text')
        documentation += chunk_text

     self.history.add(Message("user", f"""
Please use whatever relevant info in the following referenced texts
to answer the user query.
References: {documentation}

User Prompt: {self.user_input}
                              """))

  def clear_history(self):
    self.history.clear()

  def save_history_summary_to_system_prompt(self, max_summary_tokens=500):
    history_text = ''.join(
      [f"{m.role}: {m.content}" for m in self.history]
    )
    summary_prompt = f"""Please summarize the following conversation in
{max_summary_tokens} tokens or less. Focus on key topics, decisions, and
important context that should be remembered:
{history_text}"""

    response = self.client.responses.create(
      model=self.model,
      input=summary_prompt
    )

    self.system_prompt = f"{self.system_prompt}\n\nSummary: {response.output_text}"

  def run(self):
    self.start()
    self.user_prompt()

    while self.user_input != "exit":
      stream = self.client.responses.create(
        model=self.model,
        input=self.history,
        stream = True
      )

      response_text = "\nAssistant: "
      print(response_text, end="", flush=True)

      for event in stream:
        if event.type == "response.output_text.delta":
          chunk = event.delta
          response_text += chunk
          print(chunk, end="", flush=True)

      self.assistant_prompt(response_text, do_print=False)
      self.print_context_usage()

      if self.token_manager.exceeds_limit():
        print("Conversation limit reached. Please enter to start free up memory.")
        input()
        print("Condensing and saving conversation history...")
        self.save_history_summary_to_system_prompt(500)
        self.clear_history()
        self.start()

      self.user_prompt()

SYSTEM_PROMPT = """
You are a helpful assistant of Dev Archive, a RAG pipeline
to help query and analyze software engineering case studies.
"""
chat = ChatManager(MODEL, SYSTEM_PROMPT)
chat.run()
