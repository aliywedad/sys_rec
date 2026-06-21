import asyncio
import hashlib
import os
import re
import tempfile

import edge_tts
import speech_recognition as sr

_recognizer = sr.Recognizer()
_recognizer.energy_threshold = 300
_recognizer.dynamic_energy_threshold = True

# Jarvis-like voice: British male neural, clear and professional
JARVIS_VOICE = "en-GB-RyanNeural"   # British male neural — closest to Paul Bettany's JARVIS
ARABIC_VOICE = "ar-EG-ShakirNeural"
JARVIS_RATE  = "-5%"               # Slightly deliberate, authoritative pace


# ── Speech-to-Text ────────────────────────────────────────────────────────────

def transcribe_audio_bytes(audio_bytes: bytes) -> str | None:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        with sr.AudioFile(tmp) as source:
            audio = _recognizer.record(source)
        for lang in ("en-US", "ar-MA", "fr-FR"):
            try:
                text = _recognizer.recognize_google(audio, language=lang)
                if text and text.strip():
                    return text.strip()
            except (sr.UnknownValueError, sr.RequestError):
                continue
        return None
    finally:
        os.remove(tmp)


def audio_hash(audio_bytes: bytes) -> str:
    return hashlib.md5(audio_bytes).hexdigest()


# ── Text-to-Speech (edge-tts — neural quality) ───────────────────────────────

def _is_arabic(text: str) -> bool:
    arabic = sum(1 for c in text if "؀" <= c <= "ۿ")
    return arabic > len(text) * 0.25


def _sanitize_text_for_speech(text: str) -> str:
    """Remove markdown, backticks and simple HTML from text before TTS."""
    if not text:
        return text

    # Remove fenced code blocks and inline code ticks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Strip markdown emphasis and strong emphasis
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Convert markdown links to plain text and remove HTML tags
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)

    # Remove heading markers and collapse whitespace
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


async def _tts_async(text: str, voice: str) -> bytes:
    rate = "+0%" if voice == ARABIC_VOICE else JARVIS_RATE
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp = f.name
    await communicate.save(tmp)
    with open(tmp, "rb") as f:
        data = f.read()
    os.remove(tmp)
    return data


def text_to_speech_bytes(text: str) -> bytes:
    """Generate MP3 audio using Microsoft Neural TTS (Jarvis-like voice)."""
    text = _sanitize_text_for_speech(text)
    voice = ARABIC_VOICE if _is_arabic(text) else JARVIS_VOICE
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_tts_async(text, voice))
    finally:
        loop.close()
