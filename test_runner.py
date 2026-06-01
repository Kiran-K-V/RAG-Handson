"""
IIT Dholakpur RAG Pipeline — Comic Test Runner UI.

A Flask-based web application that runs pipeline tests with a
Chhota Bheem themed comic-book interface. Bheem guides you through
each test with animations, speech bubbles, and ladoo-based scoring.

Usage:
    python test_runner.py

Then open http://localhost:5555 in your browser.
"""

import traceback
from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    """Serve the comic test UI."""
    return render_template("test_ui.html")


@app.route("/static/images/<path:filename>")
def serve_image(filename: str):
    """Serve static image assets."""
    return send_from_directory("static/images", filename)


@app.route("/run_test/load_documents")
def test_load_documents():
    """Test: Can we load all 3 documents from data/?"""
    try:
        from src.load_docs import load_documents

        docs = load_documents("data")

        assert isinstance(docs, dict), f"Expected dict, got {type(docs).__name__}"
        assert len(docs) == 3, f"Expected 3 documents, got {len(docs)}"

        for key, value in docs.items():
            assert key.endswith(".txt"), f"Key '{key}' doesn't end with .txt"
            assert isinstance(value, str) and len(value) > 0, f"Empty content for '{key}'"

        filenames = sorted(docs.keys())
        return jsonify({
            "passed": True,
            "message": (
                f"Loaded {len(docs)} documents successfully!\n"
                f"Files: {', '.join(filenames)}\n"
                f"Total characters: {sum(len(v) for v in docs.values()):,}"
            ),
        })

    except NotImplementedError as e:
        return jsonify({
            "passed": False,
            "message": f"Not implemented yet! TODO: {e}",
        })
    except Exception as e:
        return jsonify({
            "passed": False,
            "message": f"{type(e).__name__}: {e}\n\n{traceback.format_exc()[-500:]}",
        })


@app.route("/run_test/chunking")
def test_chunking():
    """Test: Does chunking produce overlapping chunks of correct size?"""
    try:
        from src.chunking import chunk_text

        test_text = "A" * 600
        chunks = chunk_text(test_text, chunk_size=300, overlap=50)

        assert len(chunks) >= 2, f"Expected >=2 chunks, got {len(chunks)}"

        last_50 = chunks[0][-50:]
        first_50 = chunks[1][:50]
        assert last_50 == first_50, (
            f"Overlap mismatch!\nEnd of chunk[0]: '{last_50[:20]}...'\n"
            f"Start of chunk[1]: '{first_50[:20]}...'"
        )

        for i, chunk in enumerate(chunks):
            assert len(chunk) <= 300, f"Chunk {i} exceeds max size: {len(chunk)} chars"

        # Also test with real documents
        from src.chunking import chunk_all_documents
        from src.load_docs import load_documents

        docs = load_documents("data")
        all_chunks = chunk_all_documents(docs)

        assert len(all_chunks) > 0, "chunk_all_documents returned empty list"
        assert all("text" in c and "source" in c and "chunk_id" in c for c in all_chunks), \
            "Chunks missing required keys (text, source, chunk_id)"

        return jsonify({
            "passed": True,
            "message": (
                f"Chunking works perfectly!\n"
                f"- Test: 600 chars → {len(chunks)} chunks (overlap verified ✓)\n"
                f"- Real docs: {len(all_chunks)} total chunks created\n"
                f"- All chunks have text, source, and chunk_id keys ✓"
            ),
        })

    except NotImplementedError as e:
        return jsonify({
            "passed": False,
            "message": f"Not implemented yet! TODO: {e}",
        })
    except Exception as e:
        return jsonify({
            "passed": False,
            "message": f"{type(e).__name__}: {e}\n\n{traceback.format_exc()[-500:]}",
        })


@app.route("/run_test/embeddings")
def test_embeddings():
    """Test: Do embeddings have the correct 384-dimensional shape?"""
    try:
        from src.embeddings import embed_query, embed_texts, load_embedding_model

        model = load_embedding_model()

        texts = ["What is the attendance policy?", "Where is the canteen?"]
        embeddings = embed_texts(model, texts)

        assert isinstance(embeddings, list), f"Expected list, got {type(embeddings).__name__}"
        assert len(embeddings) == 2, f"Expected 2 embeddings, got {len(embeddings)}"

        for i, emb in enumerate(embeddings):
            assert len(emb) == 384, f"Embedding {i} has {len(emb)} dims, expected 384"
            assert isinstance(emb[0], float), f"Embedding values should be float, got {type(emb[0])}"

        query_emb = embed_query(model, "How many ladoos can Bheem eat?")
        assert len(query_emb) == 384, f"Query embedding has {len(query_emb)} dims, expected 384"

        return jsonify({
            "passed": True,
            "message": (
                f"Embeddings working at full power!\n"
                f"- Model: all-MiniLM-L6-v2 loaded ✓\n"
                f"- Batch embed: 2 texts → 2 vectors (384D each) ✓\n"
                f"- Query embed: 1 query → 1 vector (384D) ✓\n"
                f"- Sample values: [{embeddings[0][0]:.4f}, {embeddings[0][1]:.4f}, ...]"
            ),
        })

    except NotImplementedError as e:
        return jsonify({
            "passed": False,
            "message": f"Not implemented yet! TODO: {e}",
        })
    except Exception as e:
        return jsonify({
            "passed": False,
            "message": f"{type(e).__name__}: {e}\n\n{traceback.format_exc()[-500:]}",
        })


@app.route("/run_test/chroma")
def test_chroma():
    """Test: Can ChromaDB store and retrieve chunks by similarity?"""
    try:
        import chromadb

        from src.embeddings import embed_query, embed_texts, load_embedding_model
        from src.retrieve import retrieve_chunks
        from src.vector_store import add_chunks, create_collection

        client = chromadb.Client()
        collection = create_collection(client, collection_name="test_arena")

        test_chunks = [
            {"text": "The minimum attendance at IIT Dholakpur is 75 percent",
             "source": "attendance_policy.txt", "chunk_id": "test_att_0"},
            {"text": "Bheem's Kitchen canteen opens at 7:30 AM daily",
             "source": "college_handbook.txt", "chunk_id": "test_hb_0"},
            {"text": "Minimum CGPA of 6.0 required for placement eligibility",
             "source": "placement_guidelines.txt", "chunk_id": "test_pl_0"},
        ]

        model = load_embedding_model()
        texts = [c["text"] for c in test_chunks]
        embeddings = embed_texts(model, texts)

        add_chunks(collection, test_chunks, embeddings)
        assert collection.count() == 3, f"Expected 3 in collection, got {collection.count()}"

        query_emb = embed_query(model, "What is the attendance requirement?")
        results = retrieve_chunks(collection, query_emb, n_results=2)

        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        assert "text" in results[0], "Result missing 'text' key"
        assert "source" in results[0], "Result missing 'source' key"

        top_text = results[0]["text"].lower()
        assert "attendance" in top_text or "75" in top_text, \
            f"Top result doesn't mention attendance: '{results[0]['text'][:50]}...'"

        return jsonify({
            "passed": True,
            "message": (
                f"ChromaDB memory shield is STRONG!\n"
                f"- Stored 3 test chunks ✓\n"
                f"- Query: 'What is the attendance requirement?'\n"
                f"- Top result: '{results[0]['text'][:60]}...'\n"
                f"- Source: {results[0]['source']} ✓\n"
                f"- Relevance confirmed ✓"
            ),
        })

    except NotImplementedError as e:
        return jsonify({
            "passed": False,
            "message": f"Not implemented yet! TODO: {e}",
        })
    except Exception as e:
        return jsonify({
            "passed": False,
            "message": f"{type(e).__name__}: {e}\n\n{traceback.format_exc()[-500:]}",
        })


@app.route("/run_test/full_pipeline")
def test_full_pipeline():
    """Test: Does the entire pipeline work end-to-end (without LLM)?"""
    try:
        import chromadb

        from src.chunking import chunk_all_documents
        from src.embeddings import embed_query, embed_texts, load_embedding_model
        from src.load_docs import load_documents
        from src.retrieve import format_context, retrieve_chunks
        from src.vector_store import add_chunks, create_collection

        # Stage 1: Load
        docs = load_documents("data")
        assert len(docs) == 3

        # Stage 2: Chunk
        chunks = chunk_all_documents(docs)
        assert len(chunks) > 0

        # Stage 3: Embed
        model = load_embedding_model()
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(model, texts)
        assert len(embeddings) == len(chunks)
        assert all(len(e) == 384 for e in embeddings)

        # Stage 4: Store
        client = chromadb.Client()
        collection = create_collection(client, collection_name="test_full_dholakpur")
        add_chunks(collection, chunks, embeddings)
        assert collection.count() == len(chunks)

        # Stage 5: Retrieve
        query = "What is the attendance policy at IIT Dholakpur?"
        query_emb = embed_query(model, query)
        results = retrieve_chunks(collection, query_emb, n_results=3)

        assert len(results) == 3
        top_text = results[0]["text"].lower()
        assert "attendance" in top_text or "75" in top_text

        # Format context
        context = format_context(results)
        assert "[Source:" in context
        assert len(context) > 0

        return jsonify({
            "passed": True,
            "message": (
                f"🎉 FULL PIPELINE MEGA PUNCH LANDED!\n\n"
                f"Stage 1 — Load:     {len(docs)} documents ✓\n"
                f"Stage 2 — Chunk:    {len(chunks)} chunks ✓\n"
                f"Stage 3 — Embed:    {len(embeddings)} vectors (384D) ✓\n"
                f"Stage 4 — Store:    {collection.count()} entries in ChromaDB ✓\n"
                f"Stage 5 — Retrieve: Top result from '{results[0]['source']}' ✓\n\n"
                f"Query: '{query}'\n"
                f"Answer source: {results[0]['source']}\n"
                f"Preview: '{results[0]['text'][:80]}...'"
            ),
        })

    except NotImplementedError as e:
        return jsonify({
            "passed": False,
            "message": f"Not implemented yet! TODO: {e}",
        })
    except Exception as e:
        return jsonify({
            "passed": False,
            "message": f"{type(e).__name__}: {e}\n\n{traceback.format_exc()[-500:]}",
        })


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ⚡ IIT DHOLAKPUR — RAG PIPELINE TEST ARENA ⚡")
    print("  Open http://localhost:5555 in your browser")
    print("  Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5555, debug=True)
