"""
IIT Dholakpur — RAG Pipeline Interactive Playground.

A web-based interactive UI that lets students explore each stage of the RAG
pipeline with real data. Each tab maps to a pipeline stage: load documents,
chunk, embed, retrieve, and generate — with live results and detailed errors.

Usage:
    python test_runner.py
    # → http://localhost:5555
"""

import os
import traceback

from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates")

# ---------------------------------------------------------------------------
# Server-side pipeline cache — progressive state across tabs
# ---------------------------------------------------------------------------
_cache = {
    "documents": None,
    "chunks": None,
    "embeddings": None,
    "embedding_model": None,
    "collection": None,
    "chunk_params": {"chunk_size": 300, "overlap": 50},
}


def _error_response(e):
    """Build a structured error response from an exception."""
    is_not_impl = isinstance(e, NotImplementedError)
    return jsonify({
        "success": False,
        "not_implemented": is_not_impl,
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc() if not is_not_impl else None,
    })


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("test_ui.html")


@app.route("/static/images/<path:filename>")
def serve_image(filename: str):
    return send_from_directory("static/images", filename)


# ---------------------------------------------------------------------------
# API: Stage 1 — Load Documents
# ---------------------------------------------------------------------------
@app.route("/api/load-documents", methods=["POST"])
def api_load_documents():
    try:
        from src.load_docs import load_documents

        docs = load_documents("data")
        documents = []
        for filename, content in sorted(docs.items()):
            documents.append({
                "filename": filename,
                "content": content,
                "chars": len(content),
                "lines": content.count("\n") + 1,
                "words": len(content.split()),
            })
        _cache["documents"] = docs
        return jsonify({"success": True, "documents": documents})
    except Exception as e:
        _cache["documents"] = None
        return _error_response(e)


# ---------------------------------------------------------------------------
# API: Stage 2 — Chunking
# ---------------------------------------------------------------------------
@app.route("/api/chunk", methods=["POST"])
def api_chunk():
    try:
        from src.chunking import chunk_all_documents

        if _cache["documents"] is None:
            return jsonify({
                "success": False,
                "error": "Documents not loaded. Go to the Documents tab first.",
                "needs_prerequisite": "documents",
            })

        body = request.get_json(silent=True) or {}
        chunk_size = body.get("chunk_size", 300)
        overlap = body.get("overlap", 50)
        _cache["chunk_params"] = {"chunk_size": chunk_size, "overlap": overlap}

        chunks = chunk_all_documents(_cache["documents"], chunk_size=chunk_size, overlap=overlap)
        _cache["chunks"] = chunks

        by_source = {}
        total_chars = 0
        for c in chunks:
            src = c.get("source", "unknown")
            by_source[src] = by_source.get(src, 0) + 1
            total_chars += len(c.get("text", ""))

        chunk_list = []
        for c in chunks:
            chunk_list.append({
                "chunk_id": c.get("chunk_id", ""),
                "source": c.get("source", ""),
                "text": c.get("text", ""),
                "chars": len(c.get("text", "")),
            })

        return jsonify({
            "success": True,
            "chunks": chunk_list,
            "stats": {
                "total": len(chunks),
                "avg_size": round(total_chars / len(chunks)) if chunks else 0,
                "by_source": by_source,
            },
            "params": {"chunk_size": chunk_size, "overlap": overlap},
        })
    except Exception as e:
        _cache["chunks"] = None
        return _error_response(e)


# ---------------------------------------------------------------------------
# API: Stage 3 — Embeddings
# ---------------------------------------------------------------------------
@app.route("/api/embed", methods=["POST"])
def api_embed():
    try:
        from src.embeddings import embed_texts, load_embedding_model

        if _cache["chunks"] is None:
            return jsonify({
                "success": False,
                "error": "Chunks not available. Go to the Chunking tab first.",
                "needs_prerequisite": "chunking",
            })

        model = load_embedding_model()
        _cache["embedding_model"] = model

        texts = [c["text"] for c in _cache["chunks"]]
        embeddings = embed_texts(model, texts)
        _cache["embeddings"] = embeddings

        emb_list = []
        for i, c in enumerate(_cache["chunks"]):
            vec = embeddings[i]
            emb_list.append({
                "chunk_id": c.get("chunk_id", f"chunk_{i}"),
                "source": c.get("source", ""),
                "vector_preview": [round(v, 4) for v in vec[:8]],
                "dimension": len(vec),
            })

        return jsonify({
            "success": True,
            "embeddings": emb_list,
            "model_name": "all-MiniLM-L6-v2",
            "dimension": len(embeddings[0]) if embeddings else 0,
            "total": len(embeddings),
        })
    except Exception as e:
        _cache["embeddings"] = None
        return _error_response(e)


# ---------------------------------------------------------------------------
# API: Cosine Similarity demo
# ---------------------------------------------------------------------------
@app.route("/api/similarity", methods=["POST"])
def api_similarity():
    try:
        from src.embeddings import embed_texts, load_embedding_model

        body = request.get_json(silent=True) or {}
        text_a = body.get("text_a", "")
        text_b = body.get("text_b", "")

        if not text_a or not text_b:
            return jsonify({"success": False, "error": "Provide both text_a and text_b."})

        model = _cache.get("embedding_model")
        if model is None:
            model = load_embedding_model()
            _cache["embedding_model"] = model

        vecs = embed_texts(model, [text_a, text_b])
        va, vb = vecs[0], vecs[1]

        dot = sum(a * b for a, b in zip(va, vb))
        mag_a = sum(a * a for a in va) ** 0.5
        mag_b = sum(b * b for b in vb) ** 0.5
        similarity = dot / (mag_a * mag_b) if mag_a and mag_b else 0.0

        return jsonify({
            "success": True,
            "similarity": round(similarity, 6),
            "vector_a_preview": [round(v, 4) for v in va[:8]],
            "vector_b_preview": [round(v, 4) for v in vb[:8]],
        })
    except Exception as e:
        return _error_response(e)


# ---------------------------------------------------------------------------
# API: Build Index (full pipeline: load → chunk → embed → store)
# ---------------------------------------------------------------------------
@app.route("/api/build-index", methods=["POST"])
def api_build_index():
    try:
        import chromadb

        from src.chunking import chunk_all_documents
        from src.embeddings import embed_texts, load_embedding_model
        from src.load_docs import load_documents
        from src.vector_store import add_chunks, create_collection

        docs = load_documents("data")
        _cache["documents"] = docs

        body = request.get_json(silent=True) or {}
        chunk_size = body.get("chunk_size", _cache["chunk_params"]["chunk_size"])
        overlap = body.get("overlap", _cache["chunk_params"]["overlap"])

        chunks = chunk_all_documents(docs, chunk_size=chunk_size, overlap=overlap)
        _cache["chunks"] = chunks

        model = load_embedding_model()
        _cache["embedding_model"] = model

        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(model, texts)
        _cache["embeddings"] = embeddings

        client = chromadb.Client()
        collection = create_collection(client, collection_name="playground_index")
        add_chunks(collection, chunks, embeddings)
        _cache["collection"] = collection

        return jsonify({
            "success": True,
            "doc_count": len(docs),
            "chunk_count": len(chunks),
            "collection_count": collection.count(),
        })
    except Exception as e:
        return _error_response(e)


# ---------------------------------------------------------------------------
# API: Clear Database
# ---------------------------------------------------------------------------
@app.route("/api/clear-db", methods=["POST"])
def api_clear_db():
    try:
        import shutil

        db_path = "chroma_db"
        if os.path.isdir(db_path):
            shutil.rmtree(db_path)

        _cache["collection"] = None
        _cache["embeddings"] = None
        _cache["chunks"] = None
        _cache["documents"] = None
        _cache["embedding_model"] = None

        return jsonify({"success": True, "message": "Database cleared successfully."})
    except Exception as e:
        return _error_response(e)


# ---------------------------------------------------------------------------
# API: Stage 4 — Search / Retrieve
# ---------------------------------------------------------------------------
@app.route("/api/search", methods=["POST"])
def api_search():
    try:
        from src.embeddings import embed_query
        from src.retrieve import retrieve_chunks

        if _cache["collection"] is None:
            return jsonify({
                "success": False,
                "error": "Index not built. Click 'Build Index' first.",
                "needs_prerequisite": "index",
            })

        body = request.get_json(silent=True) or {}
        query = body.get("query", "")
        n_results = body.get("n_results", 5)
        search_type = body.get("search_type", "semantic")

        if not query.strip():
            return jsonify({"success": False, "error": "Enter a search query."})

        collection = _cache["collection"]

        if search_type == "keyword":
            results_raw = collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            documents = results_raw["documents"][0]
            metadatas = results_raw["metadatas"][0]
            distances = results_raw["distances"][0]

            result_list = []
            for i in range(len(documents)):
                result_list.append({
                    "text": documents[i],
                    "source": metadatas[i].get("source", ""),
                    "chunk_id": metadatas[i].get("chunk_id", ""),
                    "distance": round(distances[i], 6),
                })

            return jsonify({
                "success": True,
                "results": result_list,
                "query": query,
                "search_type": search_type,
            })

        elif search_type == "hybrid":
            model = _cache["embedding_model"]
            query_emb = embed_query(model, query)

            sem_raw = collection.query(
                query_embeddings=[query_emb],
                n_results=n_results,
            )
            kw_raw = collection.query(
                query_texts=[query],
                n_results=n_results,
            )

            seen = set()
            merged = []
            for source in [sem_raw, kw_raw]:
                docs = source["documents"][0]
                metas = source["metadatas"][0]
                dists = source["distances"][0]
                for i in range(len(docs)):
                    cid = metas[i].get("chunk_id", f"unknown_{i}")
                    if cid not in seen:
                        seen.add(cid)
                        merged.append({
                            "text": docs[i],
                            "source": metas[i].get("source", ""),
                            "chunk_id": cid,
                            "distance": round(dists[i], 6),
                        })

            merged.sort(key=lambda x: x["distance"])
            result_list = merged[:n_results]

            return jsonify({
                "success": True,
                "results": result_list,
                "query": query,
                "search_type": search_type,
                "query_vector_preview": [round(v, 4) for v in query_emb[:8]],
            })

        else:
            model = _cache["embedding_model"]
            query_emb = embed_query(model, query)
            results = retrieve_chunks(collection, query_emb, n_results=n_results)

            result_list = []
            for r in results:
                result_list.append({
                    "text": r.get("text", ""),
                    "source": r.get("source", ""),
                    "chunk_id": r.get("chunk_id", ""),
                    "distance": round(r.get("distance", 0), 6),
                })

            return jsonify({
                "success": True,
                "results": result_list,
                "query": query,
                "search_type": search_type,
                "query_vector_preview": [round(v, 4) for v in query_emb[:8]],
            })
    except Exception as e:
        return _error_response(e)


# ---------------------------------------------------------------------------
# API: Stage 5 — Generate
# ---------------------------------------------------------------------------
@app.route("/api/generate", methods=["POST"])
def api_generate():
    try:
        from src.embeddings import embed_query
        from src.generate import build_prompt, generate_answer
        from src.retrieve import format_context, retrieve_chunks

        if _cache["collection"] is None:
            return jsonify({
                "success": False,
                "error": "Index not built. Go to Retrieval tab and build the index first.",
                "needs_prerequisite": "index",
            })

        body = request.get_json(silent=True) or {}
        query = body.get("query", "")
        if not query.strip():
            return jsonify({"success": False, "error": "Enter a question."})

        model = _cache["embedding_model"]
        query_emb = embed_query(model, query)
        results = retrieve_chunks(_cache["collection"], query_emb, n_results=5)
        context = format_context(results)

        prompt = build_prompt(query, context)

        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL")
        llm_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        context_chunks = []
        for r in results:
            context_chunks.append({
                "text": r.get("text", ""),
                "source": r.get("source", ""),
                "chunk_id": r.get("chunk_id", ""),
                "distance": round(r.get("distance", 0), 6),
            })

        if not api_key or api_key == "your-key-here":
            return jsonify({
                "success": True,
                "prompt": prompt,
                "answer": None,
                "no_api_key": True,
                "model": llm_model,
                "context_chunks": context_chunks,
                "context_text": context,
            })

        answer = generate_answer(
            query=query, context=context,
            api_key=api_key, model=llm_model, base_url=base_url,
        )

        return jsonify({
            "success": True,
            "prompt": prompt,
            "answer": answer,
            "no_api_key": False,
            "model": llm_model,
            "context_chunks": context_chunks,
            "context_text": context,
        })
    except Exception as e:
        return _error_response(e)


# ---------------------------------------------------------------------------
# Legacy test endpoints (kept for backward compatibility)
# ---------------------------------------------------------------------------
def make_result(passed: bool, output: list[str]) -> dict:
    return {"passed": passed, "output": output}


@app.route("/run_test/load_documents")
def test_load_documents():
    try:
        from src.load_docs import load_documents
        docs = load_documents("data")
        lines = []
        assert isinstance(docs, dict), f"Expected dict, got {type(docs).__name__}"
        lines.append("✓ Returns a dict (correct type)")
        assert len(docs) == 3, f"Expected 3 documents, got {len(docs)}"
        lines.append("✓ Contains 3 documents")
        for key, value in docs.items():
            assert key.endswith(".txt"), f"Key '{key}' missing .txt extension"
            assert isinstance(value, str) and len(value) > 100
        lines.append("✓ All keys end with .txt, all values are non-empty strings")
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
    try:
        from src.chunking import chunk_all_documents, chunk_text
        lines = []
        test_text = "A" * 600
        chunks = chunk_text(test_text, chunk_size=300, overlap=50)
        assert len(chunks) >= 2, f"Expected >=2 chunks from 600 chars, got {len(chunks)}"
        lines.append(f"✓ 600 chars → {len(chunks)} chunks (chunk_size=300, overlap=50)")
        last_50 = chunks[0][-50:]
        first_50 = chunks[1][:50]
        assert last_50 == first_50, "Overlap mismatch between chunk[0] end and chunk[1] start"
        lines.append("✓ Overlap verified: last 50 chars of chunk[0] == first 50 of chunk[1]")
        for i, chunk in enumerate(chunks):
            assert len(chunk) <= 300, f"Chunk {i} is {len(chunk)} chars (max 300)"
        lines.append("✓ All chunks within size limit (≤300 chars)")
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
    try:
        from src.embeddings import embed_query, embed_texts, load_embedding_model
        lines = []
        model = load_embedding_model()
        lines.append("✓ Model loaded: all-MiniLM-L6-v2")
        texts = ["What is the attendance policy?", "canteen timings"]
        embeddings = embed_texts(model, texts)
        assert isinstance(embeddings, list) and len(embeddings) == 2
        lines.append("✓ embed_texts: 2 inputs → 2 vectors")
        assert len(embeddings[0]) == 384
        assert isinstance(embeddings[0][0], float)
        lines.append("✓ Each vector: 384 dimensions (float)")
        query_emb = embed_query(model, "minimum attendance requirement")
        assert len(query_emb) == 384
        lines.append("✓ embed_query: returns single 384-dim vector")
        lines.append(f"> First 5 values: [{', '.join(f'{v:.4f}' for v in embeddings[0][:5])}...]")
        return jsonify(make_result(True, lines))
    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


@app.route("/run_test/chroma")
def test_chroma():
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
        lines.append("✓ Added 3 chunks to collection (count verified)")
        query_emb = embed_query(model, "What is the attendance requirement?")
        results = retrieve_chunks(collection, query_emb, n_results=2)
        assert len(results) == 2
        assert "text" in results[0] and "source" in results[0] and "distance" in results[0]
        lines.append(f"✓ Query returned {len(results)} results with text, source, distance")
        top = results[0]
        assert "attendance" in top["text"].lower() or "75" in top["text"]
        lines.append("✓ Top result is semantically relevant")
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
        lines.append("✓ Context formatted with source citations")
        top = results[0]
        assert "attendance" in top["text"].lower() or "75" in top["text"].lower() \
            or "below" in top["text"].lower()
        lines.append("✓ Top result is relevant to attendance query")
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
    try:
        from src.generate import build_prompt, generate_answer
        lines = []
        test_context = "[Source: attendance_policy.txt]\nMinimum attendance is 75%.\n---"
        test_query = "What is the minimum attendance?"
        prompt = build_prompt(test_query, test_context)
        assert isinstance(prompt, str) and len(prompt) > 50
        lines.append("✓ build_prompt returns a non-empty string")
        assert "context" in prompt.lower() or "attendance" in prompt.lower()
        lines.append("✓ Prompt includes the provided context")
        assert test_query in prompt
        lines.append("✓ Prompt includes the user's question")
        prompt_lower = prompt.lower()
        has_grounding = ("only" in prompt_lower and "context" in prompt_lower) \
            or "provided" in prompt_lower or "cite" in prompt_lower
        assert has_grounding, "Prompt should instruct the LLM to only use provided context"
        lines.append("✓ Prompt includes grounding instruction (anti-hallucination)")
        lines.append(f"> Prompt length: {len(prompt)} chars")
        lines.append(f"> Preview: \"{prompt[:120]}...\"")
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        if not api_key or api_key == "your-key-here":
            lines.append("✗ No API key configured")
            lines.append("> Set OPENAI_API_KEY in your .env file")
            lines.append("> Or configure Ollama: OPENAI_BASE_URL=http://localhost:11434/v1")
            return jsonify(make_result(False, lines))
        answer = generate_answer(
            query=test_query, context=test_context,
            api_key=api_key, model=model, base_url=base_url,
        )
        assert isinstance(answer, str) and len(answer) > 10
        lines.append(f"✓ LLM responded ({len(answer)} chars)")
        lines.append(f"> Model: {model}")
        lines.append(f"> Answer: \"{answer[:200]}{'...' if len(answer) > 200 else ''}\"")
        return jsonify(make_result(True, lines))
    except NotImplementedError as e:
        return jsonify(make_result(False, [f"✗ Not implemented: {e}"]))
    except Exception as e:
        return jsonify(make_result(False, [f"✗ {type(e).__name__}: {e}"]))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print()
    print("  IIT Dholakpur — RAG Pipeline Playground")
    print("  http://localhost:5555")
    print()
    app.run(host="0.0.0.0", port=5555, debug=True)
