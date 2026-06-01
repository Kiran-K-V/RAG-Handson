"""
Generation Module for the IITD Helpdesk RAG Pipeline.

This module handles the "G" in RAG — Generation. It takes the retrieved
context and the student's question, constructs a carefully designed prompt,
and calls an OpenAI-compatible LLM to produce a grounded answer. The key
principle: the LLM must ONLY answer from the provided context and cite its
source. No hallucinations allowed in a college helpdesk.
"""

from typing import Any


def build_prompt(query: str, context: str) -> str:
    """Construct the final prompt string for the LLM.

    The prompt includes a system instruction that constrains the LLM to
    answer ONLY from the provided context. This is the single most important
    anti-hallucination measure in the entire pipeline — without it, the LLM
    might make up policies that don't exist.

    Args:
        query: The student's original question.
        context: The formatted context string from retrieved chunks
            (output of format_context).

    Returns:
        A complete prompt string ready to send to the LLM, containing the
        system instruction, the context, and the user's question.

    Story:
        If a student asks about a policy that's NOT in our documents, the
        system prompt tells the LLM to say "I don't have information about
        that" rather than inventing an answer. This is what makes a helpdesk
        trustworthy.
    """
    # The system prompt says "only use the context provided" — this prevents
    # hallucination. Without this constraint, the LLM would happily invent
    # policies, exam dates, and phone numbers that don't exist.

    # TODO 1 — Define a system instruction string that tells the LLM:
    #   - It is a helpful assistant for IIT Dolakhpur students
    #   - It must ONLY answer based on the provided context
    #   - It must cite the source document in its answer
    #   - If the context doesn't contain the answer, say so honestly
    # Hint: Use a multi-line f-string or triple-quoted string.
    # ---
    # TODO 2 — Combine the system instruction, context, and query into a
    # single prompt string with clear section delimiters.
    # Hint: Something like:
    #   f"{system_instruction}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    raise NotImplementedError("Step 1-2: Build a prompt that grounds the LLM in context")


def call_llm(
    prompt: str,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    base_url: str | None = None,
) -> str:
    """Call an OpenAI-compatible chat completion API.

    This function wraps the OpenAI API client. The base_url parameter lets
    students point at any OpenAI-compatible server — including a local Ollama
    instance running llama3 — without changing any other code.

    Args:
        prompt: The complete prompt string (from build_prompt).
        api_key: The API key for authentication.
        model: Which model to use. Defaults to "gpt-3.5-turbo".
        base_url: Optional base URL for the API. If None, uses OpenAI's default.
            Set to "http://localhost:11434/v1" for Ollama, for example.

    Returns:
        The LLM's response text as a plain string.

    Story:
        This is where the magic happens — the LLM reads the context we
        retrieved and generates a natural-language answer. But it's constrained
        by our prompt to only use the facts we gave it.
    """
    # The base_url parameter exists so students can use a local model server
    # (like Ollama) instead of paying for OpenAI API calls. The code stays
    # the same either way because Ollama exposes an OpenAI-compatible API.

    # A chat completion message list looks like:
    # [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    # The system message sets the LLM's behaviour, the user message is the query.

    # TODO 3 — Import the OpenAI client library.
    # Hint: from openai import OpenAI
    # ---
    # TODO 4 — Instantiate the OpenAI client with the api_key and optional base_url.
    # Hint: OpenAI(api_key=api_key, base_url=base_url) — base_url can be None.
    # ---
    # TODO 5 — Create the messages list for the chat completion.
    # Use "system" role for the grounding instruction and "user" role for the prompt.
    # Hint: [{"role": "user", "content": prompt}] — or split system/user if you prefer.
    # ---
    # TODO 6 — Call client.chat.completions.create() with the model and messages.
    # Hint: response = client.chat.completions.create(model=model, messages=messages)
    # ---
    # TODO 7 — Extract and return the response text.
    # Hint: response.choices[0].message.content
    raise NotImplementedError("Step 3-7: Call the OpenAI-compatible API and return the response")


def generate_answer(
    query: str,
    context: str,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    base_url: str | None = None,
) -> str:
    """Orchestrate the full generation step: build prompt → call LLM → return answer.

    This is a convenience function that ties build_prompt and call_llm together.
    It exists so that app.py can call a single function for the generation step.

    Args:
        query: The student's original question.
        context: The formatted context string from retrieved chunks.
        api_key: The API key for the LLM service.
        model: Which model to use. Defaults to "gpt-3.5-turbo".
        base_url: Optional base URL for an alternative API server.

    Returns:
        The LLM's generated answer as a plain string.

    Story:
        This function is the last step before the student sees an answer.
        It takes their question, the relevant document chunks, and produces
        a helpful, cited response.
    """
    # TODO 8 — Call build_prompt() to construct the prompt.
    # ---
    # TODO 9 — Call call_llm() with the prompt and API credentials.
    # ---
    # TODO 10 — Return the LLM's response.
    raise NotImplementedError("Step 8-10: Orchestrate prompt building and LLM call")
