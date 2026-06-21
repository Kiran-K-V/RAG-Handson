"""
Text Chunking Module for the IITD Helpdesk RAG Pipeline.

This module splits long documents into smaller, overlapping chunks. Chunking
is necessary because embedding models and LLMs have limited context windows —
we can't feed an entire 400-word document to the model at once and expect
precise retrieval.
"""


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split a single document's text into overlapping character-level chunks.

    Args:
        text: The full text content of a single document.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of characters that overlap between consecutive chunks.

    Returns:
        A list of text chunks (strings), each at most chunk_size characters long.

    """
    # SAMPLE RETURN:
    #   chunk_text("ABCDEFGHIJ", chunk_size=5, overlap=2)
    #   →  ["ABCDE", "DEFGH", "GHIJ"]
    #   chunk_text("Hi", chunk_size=300, overlap=50)
    #   →  ["Hi"]

    # TODO 1 — Handle edge case: text shorter than chunk_size → return it as-is
    #   in a single-element list.
    # ---

    # TODO 2 — Sliding window: start at 0, slice chunk_size chars, advance by
    #   (chunk_size - overlap). Keep going until you've consumed the full text.
    # ---

    raise NotImplementedError("Implement chunk_text")


def chunk_all_documents(
    documents: dict[str, str],
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[dict[str, str]]:
    """Apply chunking to every document and tag each chunk with its source.

    Args:
        documents: Dictionary mapping filename → full text (output of load_documents).
        chunk_size: Maximum characters per chunk (passed to chunk_text).
        overlap: Overlap characters between chunks (passed to chunk_text).

    Returns:
        A list of dictionaries, each with keys:
            - "text": the chunk content (str)
            - "source": the filename it came from (str)
            - "chunk_id": a unique identifier like "college_handbook.txt_chunk_0" (str)

    """
    # SAMPLE RETURN:
    #   chunk_all_documents({"file.txt": "some long text..."})
    #   →  [
    #       {"text": "some long", "source": "file.txt", "chunk_id": "file.txt_chunk_0"},
    #       {"text": "ng text...", "source": "file.txt", "chunk_id": "file.txt_chunk_1"},
    #   ]

    # TODO 3 — Iterate over each (filename, text) pair in documents.
    # ---

    # TODO 4 — For each document, call chunk_text() and build the list of dicts
    #   with "text", "source", and "chunk_id" keys.
    # ---

    raise NotImplementedError("Implement chunk_all_documents")
