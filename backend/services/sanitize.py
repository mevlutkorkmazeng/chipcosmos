"""Kullanıcı sorgusu için basit çok katmanlı girdi temizleme.

vectorvault-enterprise'daki '6 katmanlı query sanitization' fikrinin
sadeleştirilmiş bir karşılığı. Tam bir güvenlik çözümü değildir — savunmanın
ilk katmanı olarak, modelin sistem talimatını görmezden gelmesini isteyen en
yaygın kalıpları redakte eder ve girdiyi normalize eder.
"""

import re
import unicodedata

MAX_QUERY_LENGTH = 2000

# Bilinen prompt-injection kalıpları (İngilizce/Türkçe en yaygın varyantlar).
INJECTION_PATTERNS = [
    r"ignore (all|any|the)? ?(previous|prior|above) instructions?",
    r"disregard (all|any|the)? ?(previous|prior|above) instructions?",
    r"forget (all|any|the)? ?(previous|prior|above) instructions?",
    r"reveal (your|the) system prompt",
    r"show (me )?(your|the) (system )?prompt",
    r"override (your|the) (instructions|rules|guidelines)",
    r"you are now (a |an )?(dan|jailbroken|unrestricted|unfiltered|free)\b.*",
    r"act as (if you (are|were)|a) .*",
    r"pretend (you are|to be) .*",
    r"new instructions?\s*:",
    r"önceki talimatları (yok say|görmezden gel)",
    r"sistem promptunu (göster|paylaş|açıkla)",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def sanitize_query(text: str) -> str:
    """Kullanıcı sorgusunu birkaç katmanda temizler:

    1) Unicode normalizasyonu (NFKC)
    2) Kontrol karakterlerini kaldırma (newline/tab hariç)
    3) Fazla boşlukları daraltma
    4) Bilinen prompt-injection kalıplarını '[REDACTED]' ile değiştirme
    5) Maksimum uzunluk sınırı (MAX_QUERY_LENGTH)
    """
    text = unicodedata.normalize("NFKC", text)

    text = "".join(
        ch for ch in text if ch in ("\n", "\t") or unicodedata.category(ch)[0] != "C"
    )

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    for pattern in _COMPILED_PATTERNS:
        text = pattern.sub("[REDACTED]", text)

    if len(text) > MAX_QUERY_LENGTH:
        text = text[:MAX_QUERY_LENGTH]

    return text


def is_blank(text: str) -> bool:
    return len(text.strip()) == 0
