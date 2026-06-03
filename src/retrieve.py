"""
Retrieval Module for the IITD Helpdesk RAG Pipeline.

This module handles the "R" in RAG — Retrieval. Given a student's question
(as an embedding vector), it searches ChromaDB for the most semantically
similar document chunks. Think of it as a librarian who finds the three most
relevant pages before handing them to the LLM to read and summarise.
"""

from typing import Any


def retrieve_chunks(
    collection: Any,
    query_embedding: list[float],
    n_results: int = 5,
) -> list[dict[str, Any]]:
    """Query ChromaDB for the top-n most similar chunks to a query.

    ChromaDB uses cosine similarity under the hood — conceptually, it measures
    the angle between two vectors. Vectors pointing in the same direction
    (similar meaning) get a high score; perpendicular vectors (unrelated
    meaning) get a low score.

    Args:
        collection: A ChromaDB Collection containing indexed document chunks.
        query_embedding: The embedding vector of the user's question.
        n_results: How many chunks to retrieve. More results = broader context
            but potentially less focused. Fewer results = more precise but might
            miss relevant information. 5 is a reasonable default for our 3 documents.

    Returns:
        A list of dictionaries, each containing:
            - "text": the chunk content
            - "source": the source filename
            - "chunk_id": the unique chunk identifier
            - "distance": the similarity distance (lower = more similar)

    Story:
        A student asks "What is the CGPA cutoff for placements?" — this function
        finds the 5 chunks most likely to contain the answer. It retrieves
        before the LLM generates, so the LLM's answer is grounded in real
        documents rather than its own training data.
    """
    # We retrieve BEFORE generating — this is what makes RAG different from
    # a plain chatbot. The LLM only sees relevant chunks, not its own training
    # data, which prevents hallucination about made-up policies.

    # SAMPLE RETURN — what your implementation should produce:
    #   retrieve_chunks(collection, query_embedding, n_results=2)
    #   →  [
    #       {"text": "Minimum attendance is 75%...", "source": "attendance_policy.txt",
    #        "chunk_id": "attendance_policy.txt_chunk_0", "distance": 0.4521},
    #       {"text": "Students whose attendance...", "source": "attendance_policy.txt",
    #        "chunk_id": "attendance_policy.txt_chunk_2", "distance": 0.6103},
    #   ]

    # TODO 1 — Call collection.query() with the query embedding.
    # Hint: collection.query(query_embeddings=[query_embedding], n_results=n_results)
    # Note: query_embeddings takes a LIST of embeddings (even for one query).
    # ---
    # TODO 2 — Parse the results from ChromaDB's response format.
    # ChromaDB returns: {"ids": [[...]], "documents": [[...]], "metadatas": [[...]], "distances": [[...]]}
    # Each is a list of lists (one per query). We only have one query, so take index [0].
    # Extract: documents = results["documents"][0]
    #          metadatas = results["metadatas"][0]
    #          distances = results["distances"][0]
    # ---
    # TODO 3 — Build and return a list of dicts with "text", "source", "chunk_id", "distance".
    # Loop through each result using indexing or zip, and build a dict for each:
    #   for i in range(len(documents)):
    #       chunks.append({"text": documents[i], "source": metadatas[i]["source"], ...})
    raise NotImplementedError("Step 1-3: Query ChromaDB and format the results")


def format_context(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks into a single context string for the LLM prompt.

    The LLM needs the retrieved information as plain text in its prompt.
    We format each chunk with its source so the LLM can cite where the
    information came from in its response.

    Args:
        chunks: List of retrieved chunk dictionaries (from retrieve_chunks).

    Returns:
        A single formatted string containing all chunk texts with source
        attribution, separated by dividers. Ready to be inserted into the
        LLM prompt.

    Story:
        Before the LLM answers "What is the attendance policy?", it needs
        to READ the relevant chunks. This function assembles those chunks
        into a readable context block, labelled by source, so the LLM can
        say "According to attendance_policy.txt, the minimum is 75%."
    """
    # We include the source label so the LLM can cite it in the answer.
    # Without source attribution, the chatbot gives answers but the student
    # can't verify where the information came from.

    # SAMPLE RETURN — what your implementation should produce:
    #   format_context([{"text": "Min attendance is 75%", "source": "attendance_policy.txt", ...}])
    #   →  "[Source: attendance_policy.txt]\nMin attendance is 75%\n---"

    # TODO 4 — Loop through each chunk and format it as:
    # "[Source: {source}]\n{text}\n---"
    # Hint: Use a list comprehension or a for loop with string formatting.
    # ---
    # TODO 5 — Join all formatted chunks with newlines and return the result.
    # Hint: "\n".join(formatted_pieces)
    raise NotImplementedError("Step 4-5: Format chunks into a context string with source labels")
