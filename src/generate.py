"""
Generation Module for the IITD Helpdesk RAG Pipeline.

This module handles the "G" in RAG — Generation. It takes the retrieved
context and the student's question, constructs a carefully designed prompt,
and calls an LLM (via the OpenAI client) to produce a grounded answer.
"""

from typing import Any

from openai import OpenAI


def build_prompt(query: str, context: str) -> str:
    """Construct the final prompt string for the LLM.

    The prompt must constrain the LLM to answer ONLY from the provided context.

    Args:
        query: The student's original question.
        context: The formatted context string from retrieved chunks.

    Returns:
        A complete prompt string ready to send to the LLM, containing the
        system instruction, the context, and the user's question.

    """
    # SAMPLE RETURN:
    #   build_prompt("What is the attendance policy?", "[Source: ...]\nMin 75%\n---")
    #   →  "You are a helpful assistant for IIT Dholakpur...
    #       Context:\n[Source: ...]\nMin 75%\n---\n\nQuestion: ...\n\nAnswer:"

    # TODO 1 — Write a system instruction that:
    #   - Identifies the assistant as an IIT Dholakpur helpdesk
    #   - Constrains answers to ONLY the provided context
    #   - Requires citing the source document
    #   - Handles "I don't know" gracefully
    # ---

    # TODO 2 — Combine system instruction + context + question into final prompt.
    #   Format: "{instruction}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    # ---

    raise NotImplementedError("Implement build_prompt")


def call_llm(
    prompt: str,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    base_url: str | None = None,
) -> str:
    """Call an LLM via the OpenAI client (supports any OpenAI-compatible server).

    Args:
        prompt: The complete prompt string (from build_prompt).
        api_key: The API key for authentication.
        model: Which model to use. Defaults to "gpt-3.5-turbo".
        base_url: Optional base URL for the API (e.g. Ollama at localhost:11434/v1).

    Returns:
        The LLM's response text as a plain string.

    """
    # SAMPLE RETURN:
    #   call_llm("You are a helpful assistant...", api_key="sk-...")
    #   →  "According to attendance_policy.txt, the minimum attendance is 75%..."

    # TODO 3 — Create an OpenAI client with the given credentials.
    # Use: OpenAI(api_key=api_key, base_url=base_url)
    # ---

    # TODO 4 — Build the messages list and call chat.completions.create().
    # Messages format: [{"role": "user", "content": prompt}]
    # ---

    # TODO 5 — Extract and return the response content string.
    # Access: response.choices[0].message.content
    # ---

    raise NotImplementedError("Implement call_llm")


def generate_answer(
    query: str,
    context: str,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    base_url: str | None = None,
) -> str:
    """Orchestrate the full generation step: build prompt → call LLM → return answer.

    Args:
        query: The student's original question.
        context: The formatted context string from retrieved chunks.
        api_key: The API key for the LLM service.
        model: Which model to use. Defaults to "gpt-3.5-turbo".
        base_url: Optional base URL for an alternative API server.

    Returns:
        The LLM's generated answer as a plain string.

    """
    # TODO 6 — Call build_prompt(), then call_llm(), then return the answer.
    # ---

    raise NotImplementedError("Implement generate_answer")
