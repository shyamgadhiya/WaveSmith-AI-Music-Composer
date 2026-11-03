import os
from typing import Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


# =====================================================================
# 1. State Definition
# =====================================================================
class MusicState(TypedDict, total=False):
    """Clean, structured state schema for the music generation workflow."""
    musician_input: str       # Sanitized user input prompt
    style: str                # Musical style / period (e.g. Baroque, Romantic, Jazz)
    target_seconds: float     # Target piece length in seconds
    composition_data: Dict[str, Any]  # Structured notes, chords, BPM, meter
    midi_file: str            # Filepath to the generated .mid file
    error: Optional[str]      # Error logging if a stage fails


# =====================================================================
# 2. Resilient LLM Setup with Automatic Fallback
# =====================================================================
# Primary LLM: Google Gemini
primary_llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    max_retries=2,
    timeout=20.0
)

# Secondary Fallback LLM: Groq (handles rate limits, quota exhaustion, 5xx)
fallback_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_retries=2,
    timeout=20.0
)

# The active chain automatically fails over to Groq if Gemini hits errors
active_llm = primary_llm.with_fallbacks([fallback_llm])


# =====================================================================
# 3. Guardrails: Input Sanitization & Token Limitation
# =====================================================================
MAX_INPUT_CHARS = 300  # Equivalent to ~75 tokens: keeps prompts concise and cheap

def sanitize_user_input(text: str, max_chars: int = MAX_INPUT_CHARS) -> str:
    """Sanitizes and caps user query length to prevent token abuse."""
    cleaned = " ".join(text.strip().split())
    if len(cleaned) > max_chars:
        # Trim cleanly at the nearest space boundary
        return cleaned[:max_chars].rsplit(" ", 1)[0] + "..."
    return cleaned


# =====================================================================
# 4. Graph Construction (Lazy Loaded to Prevent Circular Imports)
# =====================================================================
_compiled_app = None

def get_app():
    """Lazily compiles and caches the StateGraph workflow."""
    global _compiled_app
    if _compiled_app is None:
        from component import composer_agent, midi_converter

        workflow = StateGraph(MusicState)

        # Register nodes
        workflow.add_node("composer", composer_agent)
        workflow.add_node("midi_converter", midi_converter)

        # Set flow: Start -> Composer Agent -> MIDI Converter -> END
        workflow.set_entry_point("composer")
        workflow.add_edge("composer", "midi_converter")
        workflow.add_edge("midi_converter", END)

        _compiled_app = workflow.compile()
    return _compiled_app


class _AppProxy:
    """Proxy object ensuring backward compatibility with code using `app.invoke()`."""
    def invoke(self, *args, **kwargs):
        return get_app().invoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        return get_app().stream(*args, **kwargs)

    def astream(self, *args, **kwargs):
        return get_app().astream(*args, **kwargs)


app = _AppProxy()


# =====================================================================
# 5. Pipeline Entry Point
# =====================================================================
def compose_music(musician_input: str, style: str = "Romantic era") -> Dict[str, Any]:
    """
    Sanitizes inputs and executes the music composition pipeline.
    
    Args:
        musician_input: Description of the song/duration.
        style: Musical aesthetic/genre.
    """
    safe_input = sanitize_user_input(musician_input)
    safe_style = sanitize_user_input(style, max_chars=60)

    initial_state: MusicState = {
        "musician_input": safe_input,
        "style": safe_style
    }
    
    return get_app().invoke(initial_state)
