# IITD Helpdesk — A RAG Workshop

## The Story

The student helpdesk at IIT Dolakhpur is drowning. Every semester, thousands of students
ask the same questions: *"What is the minimum attendance?" "Am I eligible for placements?"
"What time does the canteen close?"* The staff are overwhelmed, the phone lines are
jammed, and students end up hunting through 50-page PDFs for answers that should take
10 seconds to find.

You've been brought in as a junior developer to fix this. The administration has handed
you three text files — the college handbook, the attendance policy, and the placement
guidelines. Your mission: build an AI-powered chatbot that can answer any student query
accurately, grounded only in these documents. No hallucinations. No generic answers.
Every response must cite which document it came from.

## What You Will Build

By the end of this workshop, you will have a working RAG (Retrieval-Augmented Generation)
pipeline with six stages:

1. **Load** — Read the three source documents into memory.
2. **Chunk** — Break long documents into small, overlapping pieces.
3. **Embed** — Convert each piece into a numerical vector that captures its meaning.
4. **Store** — Save these vectors in a database for fast similarity search.
5. **Retrieve** — Given a question, find the most relevant pieces.
6. **Generate** — Feed those pieces to an LLM and get a grounded answer.

No LangChain. No LlamaIndex. No magic abstractions. You will build every piece yourself.

---

## Concepts First

Before you write a single line of code, let's make sure you understand *why* each
piece exists.

### What is RAG and why does it exist?

Large Language Models (LLMs) are trained on internet-scale data, but they don't know
about IIT Dolakhpur. If you ask GPT "What is the attendance policy at IITD?", it will
either hallucinate a plausible-sounding answer or admit it doesn't know. RAG solves this
by **retrieving** relevant documents first, then asking the LLM to **generate** an
answer using only those documents as context. The LLM becomes a reader, not a guesser.

### What is a vector embedding?

Imagine a city map where every street represents a topic. "Canteen timings" and "Where
can I eat on campus?" would be on the same street — different words, same meaning.
An embedding model converts text into coordinates on this map (a list of 384 numbers).
Similar meanings → nearby coordinates → easy to find.

### What is semantic search?

Traditional keyword search looks for exact word matches. Semantic search finds results
by *meaning*. When a student asks "Can I skip classes?", semantic search finds chunks
about "attendance policy" and "minimum 75% requirement" — even though the student never
used those words. This works because both the question and the document chunks are
converted into embeddings, and we find the closest matches.

### What does ChromaDB actually store?

For each document chunk, ChromaDB stores three things together:
- The **raw text** (so we can show it to the LLM)
- The **embedding vector** (so we can search by similarity)
- **Metadata** (source filename, chunk ID — so we can cite our sources)

When you query ChromaDB, it compares your question's embedding against all stored
embeddings and returns the closest matches.

---

## Setup

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key (or a local model server like Ollama)

### Step-by-step

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd rag-workshop

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (or configure Ollama)

# 5. Verify everything installed correctly
python -c "import chromadb; import sentence_transformers; print('Ready!')"
```

### Using Ollama (free, local alternative to OpenAI)

If you don't have an OpenAI key, install [Ollama](https://ollama.ai), pull a model,
and configure your `.env`:

```bash
ollama pull llama3
# Then in .env:
# OPENAI_API_KEY=ollama
# OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_MODEL=llama3
```

---

## Workshop Tasks

### Task 1: Load the Documents (`src/load_docs.py`)

**Context:** The helpdesk has three source files sitting in the `data/` folder. Before
we can do anything intelligent with them, we need to get them off the filesystem and
into Python memory. This is the simplest step, but it sets up everything that follows.

**Open:** `src/load_docs.py`

**Implement:** `validate_folder()` and `load_documents()`

**Expected outcome:** After implementation, this should work:
```python
from src.load_docs import load_documents
docs = load_documents("data")
print(docs.keys())  # dict_keys(['college_handbook.txt', 'attendance_policy.txt', 'placement_guidelines.txt'])
```

---

### Task 2: Chunk the Documents (`src/chunking.py`)

**Context:** Each document is ~400 words. That's too long for a single embedding to
capture focused meaning. Imagine trying to point at a specific building on a map that
covers an entire city — you'd lose precision. Chunking splits documents into small,
focused pieces with overlap so nothing falls between the cracks.

**Open:** `src/chunking.py`

**Implement:** `chunk_text()` and `chunk_all_documents()`

**Expected outcome:**
```python
from src.chunking import chunk_all_documents
from src.load_docs import load_documents
docs = load_documents("data")
chunks = chunk_all_documents(docs)
print(f"{len(chunks)} chunks created")  # Should be around 15-20 chunks
print(chunks[0].keys())  # dict_keys(['text', 'source', 'chunk_id'])
```

---

### Task 3: Generate Embeddings (`src/embeddings.py`)

**Context:** Now we need to give each chunk a "position in meaning-space". The
SentenceTransformer model reads each chunk and outputs 384 numbers that represent
its meaning. Chunks about "attendance" will cluster together. Chunks about "placements"
will cluster elsewhere. This is what makes semantic search possible.

**Open:** `src/embeddings.py`

**Implement:** `load_embedding_model()`, `embed_texts()`, and `embed_query()`

**Expected outcome:**
```python
from src.embeddings import load_embedding_model, embed_texts
model = load_embedding_model()
vectors = embed_texts(model, ["What is the attendance policy?", "canteen timings"])
print(len(vectors[0]))  # 384
```

---

### Task 4: Store in ChromaDB (`src/vector_store.py`)

**Context:** We now have chunks and their embeddings. We need to store them somewhere
persistent so we don't have to re-embed every time the chatbot starts. ChromaDB acts
as our helpdesk's long-term memory — it saves vectors to disk and makes them searchable.

**Open:** `src/vector_store.py`

**Implement:** `get_chroma_client()`, `create_collection()`, and `add_chunks()`

**Expected outcome:**
```python
from src.vector_store import get_chroma_client, create_collection
client = get_chroma_client()
collection = create_collection(client)
print(collection.count())  # 0 (empty until we add chunks)
```

---

### Task 5: Retrieve Relevant Chunks (`src/retrieve.py`)

**Context:** This is where the "R" in RAG happens. A student asks a question, we embed
it, and ChromaDB returns the 5 chunks whose embeddings are closest to the question's
embedding. It's like a librarian who reads your question, walks to the right shelf,
and pulls out the most relevant pages.

**Open:** `src/retrieve.py`

**Implement:** `retrieve_chunks()` and `format_context()`

**Expected outcome:** After building the index:
```python
from src.retrieve import retrieve_chunks, format_context
# (assuming collection is populated)
results = retrieve_chunks(collection, query_embedding, n_results=3)
print(results[0]["source"])  # e.g., "attendance_policy.txt"
context = format_context(results)
print(context[:100])  # Formatted context string
```

---

### Task 6: Generate Answers (`src/generate.py`)

**Context:** We have the relevant chunks. Now we feed them to the LLM with a carefully
crafted prompt that says "ONLY answer from this context, and cite your source." This is
the anti-hallucination guard. Without it, the LLM might invent policies that don't exist.

**Open:** `src/generate.py`

**Implement:** `build_prompt()`, `call_llm()`, and `generate_answer()`

**Expected outcome:** The LLM returns a grounded, cited answer.

---

### Task 7: Wire It All Together (`src/app.py`)

**Context:** Every piece works individually. Now connect them into a working chatbot.
The `--build` flag indexes documents, and the interactive loop answers questions.

**Open:** `src/app.py`

**Implement:** `build_index()`, `query_helpdesk()`, and `main()`

**Expected outcome:**
```bash
python src/app.py --build
# ✓ Loaded 3 documents
# ✓ Created 18 chunks
# ✓ Embedding model loaded
# ✓ Indexed 18 chunks into ChromaDB

python src/app.py
# 🎓 Ask IITD Helpdesk: What is the minimum attendance?
# According to attendance_policy.txt, every student must maintain...
```

---

## Running the App

```bash
# Step 1: Build the document index (run once)
python src/app.py --build

# Step 2: Start asking questions
python src/app.py
```

The interactive loop will keep running until you type `quit` or `exit`.

---

## Hints & Gotchas

- **"ModuleNotFoundError: No module named 'src'"** — Run from the project root directory,
  not from inside `src/`.
- **ChromaDB duplicates** — If you run `--build` twice, you'll get duplicate chunks.
  Your `build_index()` should check `collection.count()` before adding.
- **Embedding model download** — The first time you load `all-MiniLM-L6-v2`, it
  downloads ~80MB. Be patient and make sure you have internet.
- **API key errors** — Make sure your `.env` file exists (not just `.env.example`)
  and that your key is valid. `load_dotenv()` must be called before `os.getenv()`.
- **pathlib vs os.path** — Use `Path` objects everywhere. `Path("data").glob("*.txt")`
  not `os.listdir("data")`.
- **ChromaDB ID uniqueness** — If you add chunks with duplicate IDs, ChromaDB will
  silently overwrite. Make sure your `chunk_id` format is unique.
- **Overlap must be less than chunk_size** — If overlap >= chunk_size, you'll get
  infinite loops. Add a sanity check.

---

## Instructor Notes

This section is for workshop facilitators only.

- The **`solution` branch** contains the complete, working implementation. Never push
  it to the public repository.
- Each `src/` file in the solution branch has `# SOLUTION` markers above implemented
  blocks for easy diffing.
- The solution is designed to run end-to-end with: `python src/app.py --build` followed
  by interactive questions.
- Expected indexing time: ~10 seconds on a modern laptop (embedding 15-20 chunks).
- Recommended workshop duration: 3-4 hours for all tasks.
- Students can verify progress incrementally by running `pytest tests/test_pipeline.py -v`
  after each task.
- To grade: checkout the student's branch and run `pytest tests/test_pipeline.py -v`.
  All 5 tests should pass.
