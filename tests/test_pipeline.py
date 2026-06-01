"""
Smoke Tests for the IITD Helpdesk RAG Pipeline.

These tests verify that each stage of the pipeline produces output of the
correct shape and type. They are not exhaustive unit tests — they are
"does it work at all?" checks that give you confidence as you implement
each module.

Run with: pytest tests/test_pipeline.py -v
"""


def test_load_documents_returns_dict():
    """Verify that load_documents returns a dict with filename keys and string values.

    Expected behaviour:
        - Return type is dict
        - Keys are strings ending in .txt
        - Values are non-empty strings
        - There should be exactly 3 documents in our data/ folder
    """
    # TODO — Import load_documents from src.load_docs
    # Call it with "data" as the folder path
    # Assert the return type is dict
    # Assert it has 3 keys
    # Assert each key ends with .txt
    # Assert each value is a non-empty string
    raise NotImplementedError("Write your test here")


def test_chunking_produces_overlap():
    """Verify that chunking creates overlapping chunks of the correct size.

    Expected behaviour:
        - A text of 600 characters with chunk_size=300 and overlap=50 should
          produce at least 2 chunks
        - The end of chunk[0] should overlap with the start of chunk[1]
        - No chunk exceeds chunk_size in length
    """
    # TODO — Import chunk_text from src.chunking
    # Create a test string of ~600 characters
    # Call chunk_text with chunk_size=300, overlap=50
    # Assert len(chunks) >= 2
    # Assert the last 50 chars of chunks[0] appear in chunks[1]
    # Assert all chunks are <= 300 characters
    raise NotImplementedError("Write your test here")


def test_embeddings_correct_dimension():
    """Verify that embeddings have the expected 384-dimensional shape.

    Expected behaviour:
        - embed_texts returns a list of lists
        - Each inner list has exactly 384 elements (floats)
        - embed_query returns a single list of 384 floats
    """
    # TODO — Import load_embedding_model, embed_texts, embed_query from src.embeddings
    # Load the model
    # Embed a few test strings
    # Assert each embedding has length 384
    # Embed a single query and assert its length is 384
    raise NotImplementedError("Write your test here")


def test_chroma_add_and_retrieve():
    """Verify that chunks can be added to ChromaDB and retrieved by similarity.

    Expected behaviour:
        - After adding chunks, the collection count should match
        - Querying with a relevant embedding should return the correct chunk
        - Results should include text, source, and distance fields
    """
    # TODO — Import vector_store functions and embedding functions
    # Create a temporary in-memory ChromaDB client (chromadb.Client())
    # Create a collection
    # Create some test chunks with metadata
    # Embed them and add to the collection
    # Query with one of the same texts and verify it comes back as top result
    raise NotImplementedError("Write your test here")


def test_full_pipeline_smoke():
    """Verify the end-to-end pipeline works without errors.

    Expected behaviour:
        - load_documents succeeds with the data/ folder
        - chunk_all_documents produces a non-empty list
        - Embedding all chunks produces vectors of the right shape
        - Adding to ChromaDB succeeds
        - Querying returns relevant results

    Note: This test does NOT call the LLM (to avoid API key requirements).
        It tests everything up to and including retrieval.
    """
    # TODO — Import all necessary modules
    # Load documents from "data"
    # Chunk them all
    # Load embedding model and embed all chunks
    # Store in an in-memory ChromaDB (so tests don't pollute the real DB)
    # Embed a test query like "What is the attendance policy?"
    # Retrieve chunks and verify we get results
    # Verify the top result mentions attendance or 75%
    raise NotImplementedError("Write your test here")
