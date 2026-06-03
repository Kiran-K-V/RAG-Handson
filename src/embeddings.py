"""
Embedding Module for the IITD Helpdesk RAG Pipeline.

This module converts text into numerical vectors (embeddings) that capture
semantic meaning. An embedding is like GPS coordinates for meaning — texts
with similar meanings end up at nearby coordinates in a high-dimensional
space. This is what makes semantic search possible: we find answers not by
keyword matching but by meaning proximity.
"""

from typing import Any


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> Any:
    """Load a SentenceTransformer model for generating embeddings.

    We use all-MiniLM-L6-v2 because it's small (80MB), fast, and produces
    high-quality 384-dimensional embeddings for English text. It strikes a
    good balance between speed and accuracy for a workshop setting.

    Args:
        model_name: The HuggingFace model identifier to load.
            Defaults to "all-MiniLM-L6-v2" — a lightweight but capable model.

    Returns:
        A loaded SentenceTransformer model object ready to encode text.

    Story:
        This is the "brain" that understands meaning. When a student types
        "Where do I eat on campus?", this model knows that's semantically
        close to "canteen timings" even though the words are different.
    """
    # We load the model once and reuse it — loading is expensive (downloads
    # weights the first time), but encoding after that is fast.

    # SAMPLE RETURN — what your implementation should produce:
    #   model = load_embedding_model()
    #   →  <SentenceTransformer object>   (a loaded model ready to call .encode())

    # TODO 1 — Import SentenceTransformer from the sentence_transformers library.
    # Hint: from sentence_transformers import SentenceTransformer
    # ---
    # TODO 2 — Instantiate the model with the given model_name and return it.
    # Hint: It's just SentenceTransformer(model_name). The first run downloads
    # the model weights (~80MB), subsequent runs use the cached version.
    raise NotImplementedError("Step 1-2: Load the SentenceTransformer model")


def embed_texts(model: Any, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of text strings.

    Each text string gets converted into a 384-dimensional vector. These
    vectors are what we store in ChromaDB and use for similarity search.

    Args:
        model: A loaded SentenceTransformer model (from load_embedding_model).
        texts: A list of text strings to embed (typically our document chunks).

    Returns:
        A list of embedding vectors, where each vector is a list of 384 floats.
        The order matches the input texts — embeddings[i] corresponds to texts[i].

    Story:
        We embed all our document chunks once during indexing. Later, when a
        student asks a question, we embed their question with the same model
        and find which chunk vectors are closest to the query vector.
    """
    # Both documents and queries MUST be embedded with the same model.
    # If we used different models, their vector spaces wouldn't align and
    # similarity search would return garbage results.

    # SAMPLE RETURN — what your implementation should produce:
    #   embed_texts(model, ["hello", "world"])
    #   →  [[0.0123, -0.0456, ..., 0.0789],    ← 384 floats (one per dimension)
    #       [0.0321, -0.0654, ..., 0.0987]]     ← 384 floats

    # TODO 3 — Use the model's .encode() method to embed all texts at once.
    # Hint: model.encode(texts) returns a numpy array. Convert it to a list
    # of lists using .tolist() so it's JSON-serializable for ChromaDB.
    raise NotImplementedError("Step 3: Embed a batch of texts into vectors")


def embed_query(model: Any, query: str) -> list[float]:
    """Embed a single query string for retrieval.

    This is a convenience wrapper around embed_texts for single queries.
    The query embedding will be compared against all stored chunk embeddings
    to find the most semantically similar ones.

    Args:
        model: A loaded SentenceTransformer model (from load_embedding_model).
        query: A single question or search string from the user.

    Returns:
        A single embedding vector (list of 384 floats) for the query.

    Story:
        When a student asks "What happens if my attendance drops below 75%?",
        this function turns that question into a vector that lives near the
        attendance policy chunks in embedding space.
    """
    # We embed the query with the same model used for documents — this ensures
    # both live in the same vector space and similarity scores are meaningful.

    # SAMPLE RETURN — what your implementation should produce:
    #   embed_query(model, "What is the attendance policy?")
    #   →  [0.0123, -0.0456, ..., 0.0789]    ← a single list of 384 floats

    # TODO 4 — Use the model's .encode() method on the single query string.
    # Hint: model.encode(query) works for a single string too. Call .tolist()
    # on the result to get a plain Python list of floats.
    raise NotImplementedError("Step 4: Embed a single query string")
