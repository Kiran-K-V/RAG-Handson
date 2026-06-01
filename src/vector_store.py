"""
Vector Store Module for the IITD Helpdesk RAG Pipeline.

This module manages ChromaDB — our persistent vector database. ChromaDB stores
three things together for each chunk: the raw text, its embedding vector, and
metadata (which file it came from, its chunk ID). Persistence means we embed
our documents once and the vectors survive across program restarts — no need
to re-run the expensive embedding step every time.
"""

from typing import Any


def get_chroma_client(persist_directory: str = "chroma_db") -> Any:
    """Initialise and return a persistent ChromaDB client.

    ChromaDB can run in-memory (ephemeral) or persist to disk. We use
    persistent mode so that once we've indexed the IITD documents, the
    embeddings are saved and ready for instant retrieval on the next run.

    Args:
        persist_directory: Path to the directory where ChromaDB stores its files.
            Defaults to "chroma_db" in the project root.

    Returns:
        A ChromaDB PersistentClient instance.

    Story:
        Without persistence, every time a student starts the chatbot, it would
        have to re-embed all documents from scratch — that's slow and wasteful.
        The chroma_db/ folder is our helpdesk's "memory".
    """
    # Persistence is key — ChromaDB writes its index to disk so we only pay
    # the embedding cost once during the --build step.

    # TODO 1 — Import chromadb.
    # Hint: import chromadb
    # ---
    # TODO 2 — Create a PersistentClient pointing at the persist_directory.
    # Hint: chromadb.PersistentClient(path=persist_directory)
    raise NotImplementedError("Step 1-2: Create a persistent ChromaDB client")


def create_collection(client: Any, collection_name: str = "iitd_helpdesk") -> Any:
    """Create or retrieve a named ChromaDB collection.

    A collection in ChromaDB is like a table in a database — it holds vectors,
    documents, and metadata under a single namespace. We use one collection
    for all IITD helpdesk documents.

    Args:
        client: A ChromaDB client instance (from get_chroma_client).
        collection_name: Name for the vector collection.
            Defaults to "iitd_helpdesk".

    Returns:
        A ChromaDB Collection object.

    Story:
        All three documents (handbook, attendance, placement) go into one
        collection called "iitd_helpdesk". This way a single query searches
        across all documents at once — the student doesn't need to know which
        file contains the answer.
    """
    # get_or_create_collection is idempotent — it returns the existing
    # collection if it already exists, or creates a new one if it doesn't.

    # TODO 3 — Use the client's get_or_create_collection method.
    # Hint: client.get_or_create_collection(name=collection_name)
    raise NotImplementedError("Step 3: Create or retrieve the ChromaDB collection")


def add_chunks(
    collection: Any,
    chunks: list[dict[str, str]],
    embeddings: list[list[float]],
) -> None:
    """Add document chunks with their embeddings and metadata to the collection.

    This is where everything comes together: the chunk text, its vector
    representation, and the metadata (source file, chunk ID) all get stored
    together in ChromaDB.

    Args:
        collection: A ChromaDB Collection (from create_collection).
        chunks: List of chunk dictionaries, each with "text", "source", "chunk_id".
        embeddings: Corresponding embedding vectors (same order as chunks).

    Returns:
        None. Chunks are added to the collection as a side effect.

    Story:
        After this function runs, ChromaDB contains everything the helpdesk
        needs to answer questions: searchable vectors linked to the original
        text and source document. The metadata lets us say "According to
        attendance_policy.txt..." when citing answers.
    """
    # ChromaDB stores metadata alongside vectors — this is what allows us to
    # show the source document when returning answers. Without metadata, we'd
    # have vectors but no way to trace them back to their origin.

    # TODO 4 — Extract the list of texts from the chunks.
    # Hint: [chunk["text"] for chunk in chunks]
    # ---
    # TODO 5 — Extract the list of chunk_ids (these become ChromaDB's document IDs).
    # Hint: [chunk["chunk_id"] for chunk in chunks]
    # ---
    # TODO 6 — Build the metadata list (each entry needs "source" and "chunk_id").
    # Hint: [{"source": chunk["source"], "chunk_id": chunk["chunk_id"]} for chunk in chunks]
    # ---
    # TODO 7 — Call collection.add() with ids, documents, embeddings, and metadatas.
    # Hint: collection.add(ids=..., documents=..., embeddings=..., metadatas=...)
    raise NotImplementedError("Step 4-7: Add chunks, embeddings, and metadata to ChromaDB")
