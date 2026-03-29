import os
import json
import time
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
if not pc or not os.getenv("PINECONE_API_KEY"):
   raise Exception()

index_name = "dev-archive"
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )

dense_index = pc.Index(index_name)

with open("chunks.json", "r", encoding="utf-8") as f:
  chunks = json.load(f)

records = []
for i, chunk in enumerate(chunks):
   records.append(
      {
        "_id":              chunk["chunk_id"],
        "chunk_text":       chunk["text"],
        "project_name":     chunk["project_name"],
        "url":              chunk["url"],
        "chunk_type":       chunk["chunk_type"],
        "section_category": chunk["section_category"],
        "section_title":    chunk["section_title"],
        "technologies":     chunk.get("technologies", []),
        "token_estimate":   chunk["token_estimate"],
      }
   )

BATCH_SIZE = 96
NAMESPACE = "case-studies"

for i in range(0, len(records), BATCH_SIZE):
    batch = records[i : i + BATCH_SIZE]
    for attempt in range(3):
        try:
            dense_index.upsert_records(NAMESPACE, batch)
            break
        except Exception as e:
            if "429" in str(e):
                wait = 15 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    done = min(i + BATCH_SIZE, len(records))
    print(f"Embedded and Upserted {done}/{len(records)} chunks")
    time.sleep(3)