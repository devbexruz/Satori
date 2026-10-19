"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
backend/app/services/pii_scrubber.py

PII (Shaxsiy ma'lumotlar) va secret ma'lumotlarni
loglardan tozalovchi filtr.

Nimalar tozalanadi:
  - API kalitlar: sk-..., AIza..., ghp_..., ya29...
  - .env qiymatlar: KEY=value shakli
  - Bank karta raqamlari
  - IPv4 manzillar (shaxsiy tarmoq)
  - Parol pattern lar
"""

import re
from typing import Any

# === Regex Patternlar ===

_PATTERNS = [
    # OpenAI API key
    (re.compile(r'\bsk-[A-Za-z0-9]{20,}\b'), "[REDACTED_OPENAI_KEY]"),
    # Google API key
    (re.compile(r'\bAIza[A-Za-z0-9\-_]{35}\b'), "[REDACTED_GOOGLE_KEY]"),
    # GitHub token
    (re.compile(r'\bghp_[A-Za-z0-9]{36}\b'), "[REDACTED_GITHUB_TOKEN]"),
    # Google OAuth token
    (re.compile(r'\bya29\.[A-Za-z0-9\-_]+\b'), "[REDACTED_OAUTH_TOKEN]"),
    # Generic Bearer token
    (re.compile(r'\bBearer\s+[A-Za-z0-9\-_.]+\b', re.IGNORECASE), "Bearer [REDACTED]"),
    # .env format: KEY=value yoki KEY="value"
    (re.compile(r'([A-Z_]{3,}(?:KEY|SECRET|TOKEN|PASSWORD|PASS|PWD))\s*=\s*["\']?[^\s"\']{4,}["\']?',
                re.IGNORECASE), r'\1=[REDACTED_SECRET]'),
    # Bank karta raqami
    (re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'), "[REDACTED_CARD]"),
    # Parol pattern
    (re.compile(r'(?:password|passwd|pwd)\s*[:=]\s*\S+', re.IGNORECASE), "password=[REDACTED]"),
]


def scrub_text(text: str) -> str:
    """Matn ichidagi maxfiy ma'lumotlarni tozalash."""
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def scrub_dict(data: dict | Any) -> dict | Any:
    """
    Dict yoki nested strukturadagi barcha string qiymatlarni tozalash.
    JSON payload lar uchun ishlatiladi.
    """
    if isinstance(data, str):
        return scrub_text(data)
    elif isinstance(data, dict):
        return {k: scrub_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [scrub_dict(item) for item in data]
    else:
        return data
