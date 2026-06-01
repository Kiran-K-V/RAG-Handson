"""
Text Chunking Module for the IITD Helpdesk RAG Pipeline.

This module splits long documents into smaller, overlapping chunks. Chunking
is necessary because embedding models and LLMs have limited context windows —
we can't feed an entire 400-word document to the model at once and expect
precise retrieval. Think of it like giving someone one page of a textbook
at a time rather than dropping the whole book on their desk.
"""


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split a single document's text into overlapping character-level chunks.

    We use overlapping windows so that important information that falls on a
    chunk boundary doesn't get lost. If a sentence starts at the end of one
    chunk, the overlap ensures it also appears at the beginning of the next.

    Args:
        text: The full text content of a single document.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of characters that overlap between consecutive chunks.
            This preserves semantic continuity across boundaries.

    Returns:
        A list of text chunks (strings), each at most chunk_size characters long.

    Story:
        The college handbook is too long to embed as a single vector. If we did,
        a question about "canteen timings" would get diluted by all the other
        unrelated information in the same embedding. Chunking lets us create
        focused, searchable pieces.
    """
    # We chunk because LLMs have a context window limit — we can't feed the
    # entire handbook at once. Overlap ensures no sentence gets cut in half
    # without appearing in the next chunk too.

    # TODO 1 — Handle edge cases: if the text is shorter than chunk_size,
    # just return the full text as a single-element list.
    # Hint: A simple len() check is enough here.
    # ---
    # TODO 2 — Use a sliding window to create chunks with overlap.
    # Start at position 0, take chunk_size characters, then move forward
    # by (chunk_size - overlap) characters for the next chunk.
    # Hint: A while loop with a 'start' pointer works well here.
    # The step size is (chunk_size - overlap), not chunk_size.
    # ---
    # TODO 3 — Return the list of chunks. Make sure to strip any empty chunks.
    raise NotImplementedError("Step 1-3: Implement sliding-window chunking with overlap")


def chunk_all_documents(
    documents: dict[str, str],
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[dict[str, str]]:
    """Apply chunking to every document and tag each chunk with its source.

    Each chunk needs metadata so that when we retrieve it later, we can tell
    the user "this answer came from attendance_policy.txt". The chunk_id helps
    us identify the specific chunk within a document.

    Args:
        documents: Dictionary mapping filename → full text (output of load_documents).
        chunk_size: Maximum characters per chunk (passed to chunk_text).
        overlap: Overlap characters between chunks (passed to chunk_text).

    Returns:
        A list of dictionaries, each with keys:
            - "text": the chunk content (str)
            - "source": the filename it came from (str)
            - "chunk_id": a unique identifier like "college_handbook.txt_chunk_0" (str)

    Story:
        When a student asks "what is the attendance policy?", the chatbot needs
        to not only find the right chunk but also say "According to
        attendance_policy.txt..." — that's what the source metadata enables.
    """
    # The chunk_id is crucial for deduplication and traceability. Without it,
    # we'd have no way to know which piece of which document a vector came from.

    # TODO 4 — Loop through each document in the dictionary.
    # Hint: documents.items() gives you (filename, text) pairs.
    # ---
    # TODO 5 — Call chunk_text() on each document's text.
    # ---
    # TODO 6 — For each resulting chunk, create a dict with "text", "source",
    # and "chunk_id". The chunk_id format should be "{filename}_chunk_{index}".
    # Hint: Use enumerate() to get the index of each chunk.
    # ---
    # TODO 7 — Collect all chunk dicts into a single list and return it.
    raise NotImplementedError("Step 4-7: Chunk all documents and attach metadata")
