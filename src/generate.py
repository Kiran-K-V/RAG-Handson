"""
Generation Module for the IITD Helpdesk RAG Pipeline.

This module handles the "G" in RAG — Generation. It takes the retrieved
context and the student's question, constructs a carefully designed prompt,
and calls an LLM (via LiteLLM) to produce a grounded answer. The key
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

    # SAMPLE RETURN — what your implementation should produce:
    #   build_prompt("What is the attendance policy?", "[Source: ...]\nMin 75%\n---")
    #   →  "You are a helpful assistant for IIT Dholakpur...
    #       Context:
    #       [Source: ...]\nMin 75%\n---
    #
    #       Question: What is the attendance policy?
    #
    #       Answer:"

    # TODO 1 — Define a system instruction string that tells the LLM:
    #   - It is a helpful assistant for IIT Dholakpur students
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
    """Call an LLM via LiteLLM (supports OpenAI, Ollama, and many other providers).

    This function wraps the LiteLLM library. The base_url parameter lets
    students point at any OpenAI-compatible server — including a local Ollama
    instance running llama3 — without changing any other code.

    Args:
        prompt: The complete prompt string (from build_prompt).
        api_key: The API key for authentication.
        model: Which model to use. Defaults to "gpt-3.5-turbo".
        base_url: Optional base URL for the API (e.g. LiteLLM proxy URL).
            Set to "http://localhost:11434/v1" for Ollama, for example.

    Returns:
        The LLM's response text as a plain string.

    Story:
        This is where the magic happens — the LLM reads the context we
        retrieved and generates a natural-language answer. But it's constrained
        by our prompt to only use the facts we gave it.
    """
    # LiteLLM provides a unified interface to 100+ LLM providers.
    # The same litellm.completion() call works for OpenAI, Ollama, etc.

    # A chat completion message list looks like:
    # [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    # The system message sets the LLM's behaviour, the user message is the query.

    # SAMPLE RETURN — what your implementation should produce:
    #   call_llm("You are a helpful assistant...\n\nQuestion: ...", api_key="sk-...")
    #   →  "According to attendance_policy.txt, the minimum attendance is 75%..."

    # TODO 3 — Import litellm.
    # Hint: import litellm
    # ---
    # TODO 4 — Create the messages list for the chat completion.
    # Use "user" role for the prompt.
    # Hint: [{"role": "user", "content": prompt}]
    # ---
    # TODO 5 — Call litellm.completion() with the model, messages, api_key,
    # and optional api_base.
    # Hint: response = litellm.completion(model=model, messages=messages,
    #                                     api_key=api_key, api_base=base_url)
    # ---
    # TODO 6 — Extract and return the response text.
    # Hint: response.choices[0].message.content
    raise NotImplementedError("Step 3-6: Call the LLM via LiteLLM and return the response")


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
    # SAMPLE RETURN — what your implementation should produce:
    #   generate_answer("What is attendance?", context, api_key="sk-...")
    #   →  "According to attendance_policy.txt, the minimum attendance is 75%..."

    # TODO 7 — Call build_prompt() to construct the prompt.
    # ---
    # TODO 8 — Call call_llm() with the prompt and API credentials.
    # ---
    # TODO 9 — Return the LLM's response.
    raise NotImplementedError("Step 7-9: Orchestrate prompt building and LLM call")
