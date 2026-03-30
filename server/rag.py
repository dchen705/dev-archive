import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
dense_index = Pinecone(api_key=os.getenv("PINECONE_API_KEY")).Index(os.getenv("PINECONE_INDEX_NAME"))
PINECONE_INDEX_NAMESPACE = os.getenv("PINECONE_INDEX_NAMESPACE")
MODEL = "gpt-4o-mini"


def retrieve_docs(query: str) -> str:
    results = dense_index.search(
        namespace=PINECONE_INDEX_NAMESPACE,
        query={
            "top_k": 12,
            "inputs": {
                "text": query
            }
        }
    )

    documentation = ""
    for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get('chunk_text')
        documentation += chunk_text

    return documentation


def build_augmented_message(user_input: str, documentation: str) -> str:
    return f"""Please use whatever relevant info in the following referenced texts
to answer the user query.
References: {documentation}

User Prompt: {user_input}
"""


def get_llm_response(history: list) -> str:
    response = client.responses.create(
        model=MODEL,
        input=history
    )
    return response.output_text
