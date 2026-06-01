# RAG Workshop — Build a College Helpdesk from Scratch

## What This Is

A hands-on workshop where you build a working RAG (Retrieval-Augmented Generation) pipeline. No LangChain. No LlamaIndex. No abstractions. You implement every stage yourself — document loading, chunking, embedding, vector storage, retrieval, and generation.

The corpus is three text files for a fictional college helpdesk (IIT Dholakpur): a handbook, an attendance policy, and placement guidelines. By the end, your system answers student queries accurately, grounded only in these documents, with source citations.

## What You Will Build

Six stages, implemented in order:

| Stage | File | What it does |
|-------|------|-------------|
| 1. Load | `src/load_docs.py` | Read `.txt` files from `data/` into a Python dict |
| 2. Chunk | `src/chunking.py` | Split documents into overlapping character windows |
| 3. Embed | `src/embeddings.py` | Convert chunks into 384-dim vectors (all-MiniLM-L6-v2) |
| 4. Store | `src/vector_store.py` | Persist vectors + metadata in ChromaDB |
| 5. Retrieve | `src/retrieve.py` | Semantic search — find chunks closest to a question |
| 6. Generate | `src/generate.py` | Build a grounded prompt, call an LLM, return a cited answer |

Final integration: `src/app.py` wires all stages into a CLI chatbot.

---

## Setup

**Requirements:** Python 3.10+, ~200MB disk (embedding model download).

```bash
# Clone and enter the project
git clone <your-repo-url>
cd RAG-Handson

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set OPENAI_API_KEY (or configure Ollama, see below)

# Verify installation
python -c "import chromadb; import sentence_transformers; print('Ready')"
```

### Using Ollama (free, local, no API key needed)

```bash
ollama pull llama3
```

Then in `.env`:
```
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3
```

---

## The Playground UI

The project includes an interactive web UI where you can test each pipeline stage with real data, see actual outputs, and debug failures in real-time.

```bash
python test_runner.py
# → http://localhost:5555
```

**Six tabs map to six pipeline stages:**

1. **Documents** — Load and browse the source files. See character counts, line counts, word counts. Click to expand and read each document.
2. **Chunking** — Adjust `chunk_size` and `overlap` with sliders, re-chunk on the fly, see every chunk with its metadata.
3. **Embeddings** — Generate vectors, see the first 8 dimensions of each embedding. Use the cosine similarity explorer to compare any two texts.
4. **Retrieval** — Build the full index (load → chunk → embed → store), then search with a query. Results show ranked chunks with similarity scores.
5. **Generation** — Enter a question, see the constructed prompt (what actually gets sent to the LLM), the retrieved context, and the generated answer.
6. **Guide** — Industry context (who uses RAG in production), stage-by-stage debugging tips, chunking strategy comparisons, embedding model landscape.

When your code has a `NotImplementedError`, the UI shows a clear yellow message. When it raises a real bug, the UI shows the full traceback so you can debug without switching to the terminal.

---

## Tasks

### Task 1: Load the Documents

**File:** `src/load_docs.py`

**Implement:** `validate_folder()` and `load_documents()`

Read the three `.txt` files from `data/` into a `dict[str, str]` mapping filenames to content. Use `pathlib.Path` for file operations.

```python
from src.load_docs import load_documents
docs = load_documents("data")
# → {"attendance_policy.txt": "...", "college_handbook.txt": "...", "placement_guidelines.txt": "..."}
```

### Task 2: Chunk the Documents

**File:** `src/chunking.py`

**Implement:** `chunk_text()` and `chunk_all_documents()`

Sliding window: step = `chunk_size - overlap`. Each chunk gets `text`, `source`, and `chunk_id` metadata.

```python
from src.chunking import chunk_all_documents
from src.load_docs import load_documents
chunks = chunk_all_documents(load_documents("data"))
# → [{"text": "...", "source": "attendance_policy.txt", "chunk_id": "attendance_policy.txt_chunk_0"}, ...]
```

### Task 3: Generate Embeddings

**File:** `src/embeddings.py`

**Implement:** `load_embedding_model()`, `embed_texts()`, and `embed_query()`

`model.encode()` returns numpy arrays. Call `.tolist()` to convert to Python lists for ChromaDB.

```python
from src.embeddings import load_embedding_model, embed_texts
model = load_embedding_model()  # all-MiniLM-L6-v2, 384-dim
vectors = embed_texts(model, ["attendance policy", "canteen hours"])
len(vectors[0])  # → 384
```

### Task 4: Store in ChromaDB

**File:** `src/vector_store.py`

**Implement:** `get_chroma_client()`, `create_collection()`, and `add_chunks()`

Use `get_or_create_collection` (not `create_collection`) for idempotency. Store `ids`, `documents`, `embeddings`, and `metadatas`.

```python
from src.vector_store import get_chroma_client, create_collection
client = get_chroma_client()        # persists to chroma_db/
collection = create_collection(client)
collection.count()                   # → 0 until you add chunks
```

### Task 5: Retrieve Relevant Chunks

**File:** `src/retrieve.py`

**Implement:** `retrieve_chunks()` and `format_context()`

`collection.query()` returns double-nested lists: `{"documents": [[...]], "distances": [[...]]}`. Access with `[0]`.

```python
results = retrieve_chunks(collection, query_embedding, n_results=3)
# → [{"text": "...", "source": "attendance_policy.txt", "distance": 0.342}, ...]
context = format_context(results)
# → "[Source: attendance_policy.txt]\nMinimum attendance is 75%...\n---"
```

### Task 6: Generate Answers

**File:** `src/generate.py`

**Implement:** `build_prompt()`, `call_llm()`, and `generate_answer()`

The system prompt is the anti-hallucination guard. It tells the LLM to only answer from the provided context and cite sources.

### Task 7: Wire It Together

**File:** `src/app.py`

**Implement:** `build_index()`, `query_helpdesk()`, and `main()`

```bash
python src/app.py --build    # Index documents (run once)
python src/app.py            # Interactive Q&A loop
```

---

## Common Mistakes

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'src'` | Run from the project root, not from inside `src/` |
| Duplicate chunks after running `--build` twice | Check `collection.count()` before adding |
| `embed_texts` returns numpy arrays | Call `.tolist()` — ChromaDB expects `list[list[float]]` |
| Embedding model downloads 80MB on first run | Expected. Needs internet. Be patient. |
| API key errors | Make sure `.env` exists (not just `.env.example`). Call `load_dotenv()` before `os.getenv()`. |
| `create_collection` fails on second run | Use `get_or_create_collection` instead |
| Infinite loop in chunking | Overlap must be strictly less than chunk_size |
| ChromaDB query returns nested lists | Access results with `[0]`: `results["documents"][0]` |

---

## Project Structure

```
RAG-Handson/
├── data/                       # Source documents (3 .txt files)
│   ├── attendance_policy.txt
│   ├── college_handbook.txt
│   └── placement_guidelines.txt
├── src/                        # Your implementation (all stubs — fill these in)
│   ├── load_docs.py            # Stage 1
│   ├── chunking.py             # Stage 2
│   ├── embeddings.py           # Stage 3
│   ├── vector_store.py         # Stage 4
│   ├── retrieve.py             # Stage 5
│   ├── generate.py             # Stage 6
│   └── app.py                  # Final integration
├── tests/
│   └── test_pipeline.py        # pytest smoke tests
├── templates/
│   └── test_ui.html            # Playground UI
├── test_runner.py              # Flask server for the Playground (port 5555)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Running Tests

```bash
# Web playground (recommended — visual feedback at each stage)
python test_runner.py
# → http://localhost:5555

# CLI tests
pytest tests/test_pipeline.py -v
```

---

## Instructor Notes

- The **`solution` branch** has the complete working implementation. Do not push to the student-facing repo.
- Each `src/` file in the solution branch has `# SOLUTION` markers for easy diffing.
- Expected indexing time: ~10 seconds on a modern laptop.
- Recommended duration: 3-4 hours for all tasks.
- To grade: checkout the student's branch, run `pytest tests/test_pipeline.py -v`. All 5 tests should pass.
- The Playground UI (`python test_runner.py`) is the fastest way to triage student issues — have them share their screen and click through each tab.
