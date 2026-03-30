# dev-archive
RAG pipeline to query and analyze software engineering case studies

## Server setup
```
cd server
pipx install poetry
poetry install
poetry env activate
fastapi dev
```
Pinecone Setup
```
Create Index "dev-archive"
Create Namespace "case-studies"
```