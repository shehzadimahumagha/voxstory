"""
VoxStory — agent/chain.py

LangChain LCEL chains wiring together the LLM, prompts, and output parser.
All chain functions accept an optional github_context string for code-aware generation.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

from agent.prompts import (
    TRANSCRIPT_PROMPT,
    REFINEMENT_PROMPT,
    TECHNICAL_PROMPT,
    SOLUTION_MAP_PROMPT,
    SYNTHESIS_PROMPT,
)

load_dotenv()


def get_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Make sure your .env file exists and contains the key."
        )
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=api_key,
    )


def _context_prefix(github_context: str) -> str:
    """Returns context block with separator, or empty string."""
    return f"{github_context.strip()}\n\n---\n\n" if github_context.strip() else ""


def run_transcript_mode(transcript: str, github_context: str = "") -> str:
    """
    Takes a raw meeting transcript or stakeholder notes.
    Returns structured Agile artifacts as a markdown string.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")
    llm = get_llm()
    chain = TRANSCRIPT_PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "input": transcript.strip(),
            "github_context": _context_prefix(github_context),
        }
    )


def run_refinement_mode(story: str, github_context: str = "") -> str:
    """
    Takes a vague or incomplete user story.
    Returns a polished, INVEST-compliant story with full acceptance criteria.
    """
    if not story or not story.strip():
        raise ValueError("User story cannot be empty.")
    llm = get_llm()
    chain = REFINEMENT_PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "input": story.strip(),
            "github_context": _context_prefix(github_context),
        }
    )


def run_technical_mode(input_text: str, github_context: str = "") -> str:
    """
    Takes complex technical requirements, architecture notes, or spec documents.
    Returns implementation-ready user stories with API contracts, data requirements,
    and technical acceptance criteria.
    """
    if not input_text or not input_text.strip():
        raise ValueError("Input cannot be empty.")
    llm = get_llm()
    chain = TECHNICAL_PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "input": input_text.strip(),
            "github_context": _context_prefix(github_context),
        }
    )


def run_solution_mapping(input_text: str, github_context: str = "") -> str:
    """
    Takes user stories or requirements (can be multiple).
    Returns a Solution Architecture Map with component breakdown, API design,
    data model, implementation roadmap, and risk register.
    """
    if not input_text or not input_text.strip():
        raise ValueError("Input cannot be empty.")
    llm = get_llm()
    chain = SOLUTION_MAP_PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "input": input_text.strip(),
            "github_context": _context_prefix(github_context),
        }
    )


def run_synthesis(contributions_text: str, github_context: str = "") -> str:
    """
    Takes pre-formatted multi-stakeholder contributions text.
    Returns a Collaboration Synthesis Report with perspective alignment table,
    one consolidated user story, alignment gaps, and solution overview.
    """
    if not contributions_text or not contributions_text.strip():
        raise ValueError("Contributions cannot be empty.")
    llm = get_llm()
    chain = SYNTHESIS_PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "input": contributions_text.strip(),
            "github_context": _context_prefix(github_context),
        }
    )
