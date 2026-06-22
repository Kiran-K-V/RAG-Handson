"""
Document Loader for the IITD Helpdesk RAG Pipeline.

This module is responsible for reading the raw text files that the college
administration has provided. It is the very first step in the pipeline —
before we can chunk, embed, or search anything, we need to get the documents
off disk and into memory as Python strings.
"""

from pathlib import Path


def validate_folder(folder_path: str) -> bool:
    """Check that the given folder exists and contains at least one .txt file.

    Args:
        folder_path: Path to the folder that should contain .txt document files.

    Returns:
        True if the folder exists and contains one or more .txt files, False otherwise.

    """
    # SAMPLE RETURN:
    #   validate_folder("data")  →  True
    #   validate_folder("nonexistent_folder")  →  False

    # TODO 1 — Verify the folder exists and is actually a directory.
    # Use Path(folder_path).exists() and .is_dir() — return False if either fails.
    # ---

    # TODO 2 — Confirm there's at least one .txt file inside.
    # Use Path(folder_path).glob("*.txt") and check if the generator yields anything.
    # ---

    raise NotImplementedError("Implement validate_folder")


def load_documents(folder_path: str) -> dict[str, str]:
    """Load all .txt files from a folder into a dictionary.

    Each document becomes one entry: the filename (e.g., "college_handbook.txt")
    is the key, and the entire file content is the value.

    Args:
        folder_path: Path to the folder containing .txt document files.

    Returns:
        A dictionary mapping each filename (str) to its full text content (str).
        Example: {"college_handbook.txt": "IIT Dholakpur was established..."}

    Raises:
        FileNotFoundError: If the folder does not exist or contains no .txt files.

    """
    # SAMPLE RETURN:
    #   load_documents("data")
    #   →  {
    #       "attendance_policy.txt": "IIT DHOLAKPUR — ATTENDANCE POLICY ...",
    #       "college_handbook.txt":  "IIT DHOLAKPUR (IITD) — STUDENT HANDBOOK ...",
    #       "placement_guidelines.txt": "IIT DHOLAKPUR — PLACEMENT GUIDELINES ...",
    #   }

    # TODO 3 — Validate the folder first (use your function above).
    #   Return an empty dict or raise FileNotFoundError if invalid.
    # ---

    # TODO 4 — Find all .txt files in the folder.
    # Use Path(folder_path).glob("*.txt") to get an iterator of matching paths.
    # ---

    # TODO 5 — Read each file and build {filename: content} dict.
    # Use .name for the key and .read_text(encoding="utf-8") for the value.
    # ---

    raise NotImplementedError("Implement load_documents")
