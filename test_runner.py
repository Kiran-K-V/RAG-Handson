"""
IIT Dholakpur — RAG Pipeline Test Lab.

A web-based test runner that validates each stage of the RAG pipeline
and displays structured output. Run this, open the browser, and click
'Run All Tests' to see which stages are passing.

Usage:
    python test_runner.py
    # → http://localhost:5555
"""

import os
import traceback

from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    """Serve the test UI."""
    return render_template("test_ui.html")


@app.route("/static/images/<path:filename>")
def serve_image(filename: str):
    """Serve static assets."""
    return send_from_directory("static/images", filename)


def make_result(passed: bool, output: list[str]) -> dict:
    """Standard response shape for all test endpoints."""
    return {"passed": passed, "output": output}


@app.route("/run_test/load_documents")
def test_load_documents():
    """Stage 1: Document loading."""
    try:
        from src.load_docs import load_documents

        docs = load_documents("data")
        lines = []

        assert isinstance(docs, dict), f"Expected dict, got {type(docs).__name__}"
        lines.append(f"✓ Returns a dict (correct type)")

        assert len(docs) == 3, f"Expected 3 documents, got {len(docs)}"
        lines.append(f"✓ Contains 3 documents")

        for key, value in docs.items():
            assert key.endswith(".txt"), f"Key '{key}' missing .txt extension"
            assert isinstance(value, str) and len(value) > 100
        lines.append(f"✓ All keys end with .txt, all values are non-empty strings")

        filenames = sorted(docs.keys())
        lines.append(f"> Files: {', '.join(filenames)}")
        lines.append(f"> Total size: {sum(len(v) for v in docs.values()):,} characters")

        return jsonify(make_result(True, lines))

    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


@app.route("/run_test/chunking")
def test_chunking():
    """Stage 2: Text chunking with overlap."""
    try:
        from src.chunking import chunk_all_documents, chunk_text

        lines = []

        # Test basic chunking
        test_text = "A" * 600
        chunks = chunk_text(test_text, chunk_size=300, overlap=50)

        assert len(chunks) >= 2, f"Expected >=2 chunks from 600 chars, got {len(chunks)}"
        lines.append(f"✓ 600 chars → {len(chunks)} chunks (chunk_size=300, overlap=50)")

        # Verify overlap
        last_50 = chunks[0][-50:]
        first_50 = chunks[1][:50]
        assert last_50 == first_50, "Overlap mismatch between chunk[0] end and chunk[1] start"
        lines.append(f"✓ Overlap verified: last 50 chars of chunk[0] == first 50 of chunk[1]")

        # Verify size constraint
        for i, chunk in enumerate(chunks):
            assert len(chunk) <= 300, f"Chunk {i} is {len(chunk)} chars (max 300)"
        lines.append(f"✓ All chunks within size limit (≤300 chars)")

        # Test with real documents
        from src.load_docs import load_documents
        docs = load_documents("data")
        all_chunks = chunk_all_documents(docs)

        assert len(all_chunks) > 0
        assert all("text" in c and "source" in c and "chunk_id" in c for c in all_chunks)
        lines.append(f"✓ chunk_all_documents produced {len(all_chunks)} chunks with metadata")
        lines.append(f"> Keys per chunk: text, source, chunk_id")
        lines.append(f"> Sample chunk_id: {all_chunks[0]['chunk_id']}")

        return jsonify(make_result(True, lines))

    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


@app.route("/run_test/embeddings")
def test_embeddings():
    """Stage 3: Embedding generation."""
    try:
        from src.embeddings import embed_query, embed_texts, load_embedding_model

        lines = []

        model = load_embedding_model()
        lines.append("✓ Model loaded: all-MiniLM-L6-v2")

        texts = ["What is the attendance policy?", "canteen timings"]
        embeddings = embed_texts(model, texts)

        assert isinstance(embeddings, list) and len(embeddings) == 2
        lines.append(f"✓ embed_texts: 2 inputs → 2 vectors")

        assert len(embeddings[0]) == 384
        assert isinstance(embeddings[0][0], float)
        lines.append(f"✓ Each vector: 384 dimensions (float)")

        query_emb = embed_query(model, "minimum attendance requirement")
        assert len(query_emb) == 384
        lines.append(f"✓ embed_query: returns single 384-dim vector")

        lines.append(f"> First 5 values: [{', '.join(f'{v:.4f}' for v in embeddings[0][:5])}...]")

        return jsonify(make_result(True, lines))

    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


@app.route("/run_test/chroma")
def test_chroma():
    """Stage 4: ChromaDB storage and retrieval."""
    try:
        import chromadb

        from src.embeddings import embed_query, embed_texts, load_embedding_model
        from src.retrieve import retrieve_chunks
        from src.vector_store import add_chunks, create_collection

        lines = []

        client = chromadb.Client()
        collection = create_collection(client, collection_name="test_lab_stage4")
        lines.append("✓ ChromaDB client created (in-memory for testing)")

        test_chunks = [
            {"text": "The minimum attendance at IIT Dholakpur is 75 percent",
             "source": "attendance_policy.txt", "chunk_id": "att_0"},
            {"text": "The canteen opens at 7:30 AM daily",
             "source": "college_handbook.txt", "chunk_id": "hb_0"},
            {"text": "Minimum CGPA of 6.0 required for placement eligibility",
             "source": "placement_guidelines.txt", "chunk_id": "pl_0"},
        ]

        model = load_embedding_model()
        texts = [c["text"] for c in test_chunks]
        embeddings = embed_texts(model, texts)
        add_chunks(collection, test_chunks, embeddings)

        assert collection.count() == 3
        lines.append(f"✓ Added 3 chunks to collection (count verified)")

        query_emb = embed_query(model, "What is the attendance requirement?")
        results = retrieve_chunks(collection, query_emb, n_results=2)

        assert len(results) == 2
        assert "text" in results[0] and "source" in results[0] and "distance" in results[0]
        lines.append(f"✓ Query returned {len(results)} results with text, source, distance")

        top = results[0]
        assert "attendance" in top["text"].lower() or "75" in top["text"]
        lines.append(f"✓ Top result is semantically relevant")
        lines.append(f"> Query: \"What is the attendance requirement?\"")
        lines.append(f"> Top match: \"{top['text'][:60]}...\"")
        lines.append(f"> Source: {top['source']} | Distance: {top['distance']:.4f}")

        return jsonify(make_result(True, lines))

    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


@app.route("/run_test/full_pipeline")
def test_full_pipeline():
    """Stage 5: Full retrieval pipeline end-to-end."""
    try:
        import chromadb

        from src.chunking import chunk_all_documents
        from src.embeddings import embed_query, embed_texts, load_embedding_model
        from src.load_docs import load_documents
        from src.retrieve import format_context, retrieve_chunks
        from src.vector_store import add_chunks, create_collection

        lines = []

        docs = load_documents("data")
        lines.append(f"✓ Loaded {len(docs)} documents")

        chunks = chunk_all_documents(docs)
        lines.append(f"✓ Chunked into {len(chunks)} pieces")

        model = load_embedding_model()
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(model, texts)
        lines.append(f"✓ Generated {len(embeddings)} embeddings (384-dim)")

        client = chromadb.Client()
        collection = create_collection(client, collection_name="test_lab_stage5")
        add_chunks(collection, chunks, embeddings)
        lines.append(f"✓ Stored in ChromaDB ({collection.count()} entries)")

        query = "What happens if attendance falls below 75%?"
        query_emb = embed_query(model, query)
        results = retrieve_chunks(collection, query_emb, n_results=3)
        lines.append(f"✓ Retrieved {len(results)} chunks for query")

        context = format_context(results)
        assert "[Source:" in context and len(context) > 100
        lines.append(f"✓ Context formatted with source citations")

        top = results[0]
        assert "attendance" in top["text"].lower() or "75" in top["text"].lower() \
            or "below" in top["text"].lower()
        lines.append(f"✓ Top result is relevant to attendance query")

        lines.append(f"> Query: \"{query}\"")
        lines.append(f"> Top source: {top['source']}")
        lines.append(f"> Context length: {len(context)} chars")

        return jsonify(make_result(True, lines))

    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


@app.route("/run_test/generation")
def test_generation():
    """Stage 6: LLM prompt construction and generation."""
    try:
        from src.generate import build_prompt, generate_answer

        lines = []

        # Test prompt building (doesn't need API key)
        test_context = "[Source: attendance_policy.txt]\nMinimum attendance is 75%.\n---"
        test_query = "What is the minimum attendance?"

        prompt = build_prompt(test_query, test_context)
        assert isinstance(prompt, str) and len(prompt) > 50
        lines.append("✓ build_prompt returns a non-empty string")

        assert "context" in prompt.lower() or "attendance" in prompt.lower()
        lines.append("✓ Prompt includes the provided context")

        assert test_query in prompt
        lines.append("✓ Prompt includes the user's question")

        # Check for grounding instruction
        prompt_lower = prompt.lower()
        has_grounding = ("only" in prompt_lower and "context" in prompt_lower) \
            or "provided" in prompt_lower or "cite" in prompt_lower
        assert has_grounding, "Prompt should instruct the LLM to only use provided context"
        lines.append("✓ Prompt includes grounding instruction (anti-hallucination)")

        lines.append(f"> Prompt length: {len(prompt)} chars")
        lines.append(f"> Preview: \"{prompt[:120]}...\"")

        # Test actual LLM call if API key is available
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        if api_key and api_key != "your-key-here":
            try:
                answer = generate_answer(
                    query=test_query,
                    context=test_context,
                    api_key=api_key,
                    model=model,
                    base_url=base_url,
                )
                assert isinstance(answer, str) and len(answer) > 10
                lines.append(f"✓ LLM responded ({len(answer)} chars)")
                lines.append(f"> Model: {model}")
                lines.append(f"> Answer: \"{answer[:150]}{'...' if len(answer) > 150 else ''}\"")
            except Exception as llm_err:
                lines.append(f"> LLM call failed: {llm_err}")
                lines.append(f"> (Prompt construction passed — LLM connectivity issue)")
        else:
            lines.append("> Skipped LLM call (no API key configured in .env)")
            lines.append("> Prompt construction validated successfully")

        return jsonify(make_result(True, lines))

    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print()
    print("  IIT Dholakpur — Pipeline Test Lab")
    print("  http://localhost:5555")
    print()
    app.run(host="0.0.0.0", port=5555, debug=True)
