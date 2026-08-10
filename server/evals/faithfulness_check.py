"""
First RAGAS trial: check whether responses from handle_rag_query are grounded
in the chunks retrieve_docs() actually returned (i.e. an automated hallucination check).

Run from server/: poetry run python evals/faithfulness_check.py
"""

import asyncio
import csv
import os
import sys

from dotenv import load_dotenv
from openai import AsyncOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.rag import build_augmented_query, get_llm_response, retrieve_docs

load_dotenv()

from ragas.llms.base import llm_factory
from ragas.metrics.collections import Faithfulness

EVALS_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evals.csv")
JUDGE_MODEL = "gpt-4o"


def load_queries() -> list[str]:
    with open(EVALS_CSV) as f:
        rows = list(csv.DictReader(f))
    return [r["User Query"] for r in rows if r["User Query"].strip()]


def doc_to_context(doc: dict) -> str:
    # Mirrors the fields build_augmented_query actually shows the generator,
    # so the NLI check judges statements against what the model really saw.
    return (
        f"Project: {doc['project_name']}\n"
        f"Section: {doc['section_title']}\n"
        f"{doc['chunk_text']}"
    )


async def run_one(query: str, metric: Faithfulness) -> None:
    docs = retrieve_docs(query)
    augmented_query = build_augmented_query(query, docs)
    history = [
        {"role": "developer", "content": "You are a helpful assistant of Dev Archive, a RAG pipeline to help query and analyze software engineering case studies."},
        {"role": "user", "content": augmented_query},
    ]
    response_text = get_llm_response(history)
    retrieved_contexts = [doc_to_context(d) for d in docs]

    statements = await metric._create_statements(query, response_text)
    verdicts = await metric._create_verdicts(statements, "\n\n".join(retrieved_contexts))
    score = metric._compute_score(verdicts)

    print("=" * 80)
    print(f"QUERY: {query}")
    print("-" * 80)
    print(f"RESPONSE:\n{response_text}")
    print("-" * 80)
    print(f"FAITHFULNESS SCORE: {score:.2f}  ({sum(s.verdict for s in verdicts.statements)}/{len(verdicts.statements)} statements supported)")
    print("-" * 80)
    for s in verdicts.statements:
        mark = "✓" if s.verdict else "✗"
        print(f"  [{mark}] {s.statement}")
        print(f"      reason: {s.reason}")
    print()


async def main():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    llm = llm_factory(JUDGE_MODEL, client=client, max_tokens=4096)
    metric = Faithfulness(llm=llm)

    queries = load_queries()
    print(f"Running faithfulness check on {len(queries)} queries from evals.csv, judge model: {JUDGE_MODEL}\n")

    for query in queries:
        await run_one(query, metric)


if __name__ == "__main__":
    asyncio.run(main())
