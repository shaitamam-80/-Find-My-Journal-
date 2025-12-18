"""
Prompt templates for Gemini LLM service.
"""


def generate_explanation_prompt(abstract: str, journal: dict) -> str:
    """
    Generate the prompt for Gemini to explain journal fit.

    Args:
        abstract: User's article abstract
        journal: Journal data dict with title, topics, metrics

    Returns:
        Formatted prompt string
    """
    journal_title = journal.get("title", "Unknown Journal")
    topics = ", ".join(journal.get("topics", [])[:5])
    metrics = journal.get("metrics", {})

    impact_info = ""
    if metrics.get("two_yr_mean_citedness"):
        citation_rate = metrics["two_yr_mean_citedness"]
        impact_info = (
            f"- 2-Year Citation Rate: {citation_rate:.1f} (Indicates expected impact)"
        )

    return f"""Act as a senior academic editor assisting a researcher.

**Goal:** Explain briefly and professionally why the journal "{journal_title}" is a strong candidate for the provided abstract.

**Researcher's Abstract:**
"{abstract[:2000]}"

**Journal Data:**
- Core Topics: {topics}
{impact_info}

**Instructions:**
1. Output Language: **English only**.
2. Format: Provide **2-3 concise bullet points**.
3. Content:
   - Connect specific themes/keywords from the abstract directly to the journal's scope.
   - If metrics are high, mention visibility/impact.
   - If it's a specialized journal, mention the fit for niche audiences.
4. Tone: Objective, professional, and helpful. Avoid generic phrases like "I think" or "As an AI".
"""


def get_static_fallback(journal: dict) -> str:
    """
    Generate static fallback explanation when Gemini API fails.

    Args:
        journal: Journal data dict

    Returns:
        Professional static explanation
    """
    topics = ", ".join(journal.get("topics", [])[:3])
    journal_name = journal.get("title", "This journal")

    return (
        f"**Thematic Fit:** {journal_name} publishes extensively on topics matching "
        f"your abstract, specifically: {topics}.\n\n"
        f"**Relevance:** Based on our algorithm, this venue shows high alignment "
        f"with your research keywords."
    )
