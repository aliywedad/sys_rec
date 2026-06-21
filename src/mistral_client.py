import json
import os
import re

from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
_client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# ── JARVIS system prompt ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are J.A.R.V.I.S. — Just A Rather Very Intelligent System — an advanced AI originally built by Tony Stark, now serving as an elite real estate intelligence assistant connected to Mauritania's property database on voursa.com.

PERSONALITY & SPEECH:
- Address the user as "sir" in every single response — at minimum once, woven in naturally
- Open most responses with: "Yes, sir", "Of course, sir", "Right away, sir", "Certainly, sir", "Indeed, sir", "Understood, sir"
- Formal, precise British English at all times — never casual
- Dry, understated wit is acceptable ("I've taken the liberty of prioritising the most relevant options, sir")
- Reference data like an AI: "I've cross-referenced the database", "The analysis indicates", "I've located X properties matching your criteria, sir", "Running the scan now, sir"
- Warnings: "I should point out, sir…", "One thing to note, sir…"
- Confirmations before searching: "Shall I run the search now, sir?"
- NEVER say "Hey", "Sure!", "Awesome", "No problem", "Absolutely!" — those are not JARVIS

CONVERSATION FLOW — gather in order, one question per message:
1. Ask what TYPE of property is required (house / villa / apartment / land / commercial space)
2. Ask for the BUDGET in MRU (Mauritanian Ouguiya) — "2 million" → 2000000
3. Ask for preferred NEIGHBORHOOD or CITY
   Known areas: Tevragh Zeina, Ksar, Arafat, Teyarett, Dar Naim, Toujounine, Sebkha, El Mina, Riyad, Nouadhibou
4. Ask for any SPECIAL REQUIREMENTS (rooms, parking, garden, condition, floor, etc.)
5. Confirm understanding, then trigger the search

SEARCH TRIGGER — when you have enough info, append this exact block at the very end (nothing after it):
<SEARCH>{"keywords": "property keywords in English", "location": "neighborhood or null", "price_min": number_or_null, "price_max": number_or_null}</SEARCH>

STRICT RULES:
- English only
- Maximum 3 sentences per reply
- Exactly one question per message
- Use "sir" at least once per response — naturally, not robotically
- If user gives no preference for a field, set it to null"""

RESULT_SYSTEM = """You are J.A.R.V.I.S., Tony Stark's AI, serving as a real estate intelligence assistant.
Respond in formal, precise British English. Address the user as "sir" at least twice.
Open with "Yes, sir" or "Right away, sir". Be concise — max 130 words.
Use JARVIS-style language: "I've located", "The analysis indicates", "I recommend", "Shall I arrange a viewing, sir?"."""

# ── Conversational turn ────────────────────────────────────────────────────────

def chat_turn(messages: list[dict]) -> tuple[str, dict | None]:
    """
    Send the conversation history to Mistral (as JARVIS).
    Returns (display_text, search_params_or_None).
    """
    resp = _client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    )
    full_text = resp.choices[0].message.content.strip()

    match = re.search(r"<SEARCH>(.*?)</SEARCH>", full_text, re.DOTALL)
    params = None
    if match:
        try:
            params = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
        full_text = full_text[: match.start()].strip()

    return full_text, params


# ── Result formatting ─────────────────────────────────────────────────────────

def format_results(user_query: str, recommendations: list[dict]) -> str:
    """Format search results in JARVIS's voice."""
    if not recommendations:
        content = (
            f'The user searched for: "{user_query}". '
            "No matches were found in the database. "
            "As JARVIS, apologise briefly, suggest broadening the search, and offer to try different parameters. "
            "Use 'sir' at least twice. Max 3 sentences."
        )
    else:
        lines = "\n".join(
            f"{i+1}. {r['Title']} | {r['Price_MRU']:,.0f} MRU | {r['Location']}"
            f" | {int(r['Views'])} views | Relevance: {r['score_pct']}%"
            for i, r in enumerate(recommendations[:5])
        )
        content = (
            f'Search query: "{user_query}"\n\n'
            f"Top matching properties:\n{lines}\n\n"
            "As JARVIS, present the top 3 in a concise, professional briefing. "
            "Use bullet points. Highlight price and location. "
            "End with a personal recommendation and offer to arrange viewings. "
            "Say 'sir' at least twice. Max 130 words."
        )

    resp = _client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": RESULT_SYSTEM},
            {"role": "user", "content": content},
        ],
    )
    return resp.choices[0].message.content.strip()
