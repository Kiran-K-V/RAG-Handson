"""
Main Application for the IITD Helpdesk RAG Chatbot.

This is the entry point — the file students run to build the index and ask
questions. It ties together every stage of the RAG pipeline: loading documents,
chunking them, generating embeddings, storing them in ChromaDB, and then
retrieving + generating answers at query time.

Usage:
    python src/app.py --build    # Index the documents (run once)
    python src/app.py            # Start the interactive question loop
"""

import argparse
import os
from dotenv import load_dotenv


def build_index() -> None:
    """Run the full indexing pipeline: load → chunk → embed → store.

    This function is called when the user runs the app with --build.
    It processes all documents in the data/ folder and stores their
    embeddings in ChromaDB. It prints progress at each step so the
    student can see the pipeline in action.

    Should check if the collection already has documents and skip
    re-indexing if so (to avoid duplicate entries on repeated runs).

    Returns:
        None. Side effect: populates the ChromaDB vector store.

    Story:
        This is the "setup" step — like a librarian cataloguing new books.
        The student runs this once, and the chatbot is ready to answer
        questions. Every subsequent run of the app uses the stored index.
    """
    # TODO 1 — Load documents from the data/ folder using load_docs.load_documents().
    # Print how many documents were loaded.
    # Hint: from src.load_docs import load_documents
    # ---
    # TODO 2 — Chunk all documents using chunking.chunk_all_documents().
    # Print how many total chunks were created.
    # Hint: from src.chunking import chunk_all_documents
    # ---
    # TODO 3 — Load the embedding model using embeddings.load_embedding_model().
    # Print a message indicating the model is loaded.
    # Hint: from src.embeddings import load_embedding_model
    # ---
    # TODO 4 — Embed all chunk texts using embeddings.embed_texts().
    # Hint: Extract just the "text" from each chunk dict, pass the list to embed_texts.
    # ---
    # TODO 5 — Get the ChromaDB client and create/get the collection.
    # Check if the collection already has documents (collection.count() > 0).
    # If it does, print a message and skip adding. Otherwise, add the chunks.
    # Hint: from src.vector_store import get_chroma_client, create_collection, add_chunks
    # ---
    # TODO 6 — Print a success message with the total number of chunks indexed.
    raise NotImplementedError("Step 1-6: Implement the full indexing pipeline")


def query_helpdesk(question: str) -> str:
    """Run the full query pipeline: embed question → retrieve → generate.

    Takes a student's question, finds the most relevant document chunks,
    and generates a grounded answer using the LLM.

    Args:
        question: The student's natural language question.

    Returns:
        The generated answer string, grounded in the retrieved documents.

    Story:
        This is what makes the helpdesk "smart" — a student types a question,
        and instead of searching through PDFs manually, the chatbot finds
        the answer in seconds, citing exactly which document it came from.
    """
    # TODO 7 — Load the embedding model.
    # Hint: In production you'd cache this, but for the workshop loading each time is fine.
    # ---
    # TODO 8 — Embed the question using embeddings.embed_query().
    # ---
    # TODO 9 — Get the ChromaDB client and collection.
    # ---
    # TODO 10 — Retrieve the top relevant chunks using retrieve.retrieve_chunks().
    # ---
    # TODO 11 — Format the context using retrieve.format_context().
    # ---
    # TODO 12 — Get the API key from environment variables.
    # Also get optional base_url and model overrides from env vars.
    # Hint: os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_BASE_URL"), os.getenv("OPENAI_MODEL")
    # ---
    # TODO 13 — Generate and return the answer using generate.generate_answer().
    raise NotImplementedError("Step 7-13: Implement the full query pipeline")


def main() -> None:
    """Entry point: parse arguments and run the appropriate mode.

    With --build: runs the indexing pipeline.
    Without flags: starts an interactive loop where the student can type
    questions and get answers until they type 'quit' or 'exit'.

    Returns:
        None.

    Story:
        This is the function a student calls. First they run
        `python src/app.py --build` to index the documents, then
        `python src/app.py` to start asking questions. The interactive
        loop keeps going until they type 'quit'.
    """
    # Load environment variables from .env file
    load_dotenv()

    # TODO 14 — Set up argparse with a --build flag.
    # Hint: parser = argparse.ArgumentParser(description="IITD Helpdesk RAG Chatbot")
    #       parser.add_argument("--build", action="store_true", help="Build the document index")
    # ---
    # TODO 15 — If --build is set, call build_index() and return.
    # ---
    # TODO 16 — Otherwise, start an interactive loop:
    #   - Print a welcome message
    #   - Loop: prompt for input with "🎓 Ask IITD Helpdesk: "
    #   - If input is "quit" or "exit", break
    #   - Otherwise, call query_helpdesk() and print the answer
    #   - Handle KeyboardInterrupt gracefully (print goodbye, exit)
    raise NotImplementedError("Step 14-16: Set up CLI argument parsing and interactive loop")


if __name__ == "__main__":
    main()
