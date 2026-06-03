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

    Before we try to load documents, we need to make sure the folder actually
    exists and has text files in it. Otherwise we'd get confusing errors later
    in the pipeline.

    Args:
        folder_path: Path to the folder that should contain .txt document files.

    Returns:
        True if the folder exists and contains one or more .txt files, False otherwise.

    Story:
        The admin office gave us three text files — but what if someone moves
        the data/ folder or forgets to clone it? This function catches that
        problem early so we can give a helpful error message.
    """
    # SAMPLE RETURN — what your implementation should produce:
    #   validate_folder("data")  →  True
    #   validate_folder("nonexistent_folder")  →  False

    # TODO 1 — We need to confirm the folder exists before doing anything else.
    # Hint: pathlib.Path has an .exists() method and an .is_dir() method.
    # ---
    # TODO 2 — Check that there is at least one .txt file inside the folder.
    # Hint: pathlib.Path.glob("*.txt") returns a generator of matching paths.
    # Convert it to a list to check its length.
    raise NotImplementedError("Step 1-2: Validate that the folder path is real and contains .txt files")


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

    Story:
        The helpdesk has three source documents. We load them all into memory
        so that the next stage (chunking) can break them into smaller pieces.
        We keep track of which file each piece came from — that's how the chatbot
        will cite its sources later.
    """
    # SAMPLE RETURN — what your implementation should produce:
    #   load_documents("data")
    #   →  {
    #       "attendance_policy.txt": "IIT DHOLAKPUR — ATTENDANCE POLICY ...",
    #       "college_handbook.txt":  "IIT DHOLAKPUR (IITD) — STUDENT HANDBOOK ...",
    #       "placement_guidelines.txt": "IIT DHOLAKPUR — PLACEMENT GUIDELINES ...",
    #   }

    # TODO 3 — Use validate_folder() to check the path first.
    # If validation fails, raise a FileNotFoundError with a helpful message.
    # Hint: Call the function you just implemented above.
    # ---
    # TODO 4 — List all .txt files in the folder.
    # Hint: Use pathlib.Path(folder_path).glob("*.txt") to find them.
    # ---
    # TODO 5 — Read each file with UTF-8 encoding and store it in the dict.
    # The key should be just the filename (e.g., "college_handbook.txt"), not the full path.
    # Hint: Path objects have a .name attribute and a .read_text(encoding=...) method.
    # ---
    # TODO 6 — Return the completed dictionary.
    raise NotImplementedError("Step 3-6: Load .txt files from the folder into a dict")
