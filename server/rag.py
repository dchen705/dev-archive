import os
from pydoc import source_synopsis
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
dense_index = Pinecone(api_key=os.getenv("PINECONE_API_KEY")).Index(os.getenv("PINECONE_INDEX_NAME"))
PINECONE_INDEX_NAMESPACE = os.getenv("PINECONE_INDEX_NAMESPACE")
MODEL = "gpt-4o-mini"

def title_thread(query: str) -> str:
    prompt = f"""
    Generate a short, descriptive title for a conversation thread based on the user's initial message.
    
    ### Requirements:
    - Maximum 5-7 words.
    - Use Title Case.
    - Do not use quotes around the title.
    - Respond with ONLY the title text, nothing else.

    ### Initial message:
    {query}
    """

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text

def retrieve_docs(query: str, top_k: int = 10) -> list[dict]:
    results = dense_index.search(
        namespace=PINECONE_INDEX_NAMESPACE,
        query={
            "top_k": top_k,
            "inputs": {
                "text": query
            }
        }
    )

    docs = []
    documentation = ""
    for hit in results['result']['hits']:
        fields = hit.get('fields', {})
        chunk_text = fields.get('chunk_text')
        docs.append({
            "chunk_text":       fields.get("chunk_text", ""),
            "project_name":     fields.get("project_name", ""),
            "url":              fields.get("url", ""),
            "section_title":    fields.get("section_title", ""),
            "section_category":       fields.get("section_category", ""),
            "chunk_type":       fields.get("chunk_type", ""),
            "technologies":     fields.get("technologies", "")
        })

    return docs


def build_augmented_query(user_input: str, docs: list[dict]) -> str:
    references = ""
    for i, doc in enumerate(docs, 1):
        references += (
            f"\n[{i}] Project: {doc['project_name']}"
            f"\nURL: {doc['url']}"
            f"\nSection: {doc['section_title']}"
            f"\nSection Category: {doc['section_category']}"
            f"\nChunk Type: {doc['chunk_type']}"
            f"\nTechnologies: {doc['technologies']}"
            f"\n{doc['chunk_text']}"
            f"---------------------------------------------"
        )
    return f"""Use the numbered references below to answer the user's question.

CITATION RULES:
- When you use information from a reference, cite it inline like [1], [2], etc.
- Only cite references you actually use in your answer.
- If multiple references support a point, cite all of them like [1][3].

References:
{references}

User Query:
{user_input}
"""

def extract_cited_urls(response_text: str, docs: list[dict]) -> list[dict]:
    import re
    cited_numbers = set(int(n) for n in re.findall(r'\[(\d+)\]', response_text))

    cited_sources = []
    seen_urls = set()
    for n in sorted(cited_numbers):
        if 1 <= n <= len(docs):
            doc = docs[n - 1]
            # Deduplicate by URL (multiple chunks from same project)
            if doc["url"] not in seen_urls:
                cited_sources.append({
                    "ref_number":   n,
                    "project_name": doc["project_name"],
                    "url":          doc["url"],
                })
                seen_urls.add(doc["url"])

    return cited_sources


def get_llm_response(history: list) -> str:
    response = client.responses.create(
        model=MODEL,
        input=history
    )
    return response.output_text

def handle_rag_query(query: str, thread_history: list):
    SYSTEM_PROMPT = """You are a helpful assistant of Dev Archive, a RAG pipeline
to help query and analyze software engineering case studies."""

    docs = retrieve_docs(query)
    augmented_query = build_augmented_query(query, docs)

    history = [
        {"role": "developer", "content": SYSTEM_PROMPT},
        *thread_history,
        {"role": "user", "content": augmented_query},
    ]

    response = get_llm_response(history)
    citations = extract_cited_urls(response, docs)

    if citations:
        sources = "\n\n".join(
            f"[{c['ref_number']}] {c['project_name']}: {c['url']}"
            for c in citations
        )
        response += f"""
        \n\n--------
        \n\nSources:
        \n\n{sources}
        """

    return response