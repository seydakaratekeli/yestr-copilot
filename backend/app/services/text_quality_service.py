import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextQualityResult:
    score: float
    is_searchable: bool
    reasons: list[str]


def evaluate_text_quality(
    text: str,
    *,
    minimum_characters: int = 80,
    minimum_words: int = 8,
    acceptance_score: float = 0.55,
) -> TextQualityResult:
    normalized = text.strip()

    reasons: list[str] = []

    if not normalized:
        return TextQualityResult(
            score=0.0,
            is_searchable=False,
            reasons=["Metin boş."],
        )

    character_count = len(normalized)

    words = re.findall(
        r"\b[\wÇĞİÖŞÜçğıöşü]+\b",
        normalized,
        flags=re.UNICODE,
    )

    word_count = len(words)

    alphabetic_characters = sum(
        character.isalpha()
        for character in normalized
    )

    alphanumeric_characters = sum(
        character.isalnum()
        for character in normalized
    )

    replacement_character_count = normalized.count("�")

    unusual_character_count = len(
        re.findall(
            r"[^\w\sÇĞİÖŞÜçğıöşü.,;:!?%()/'\"+-]",
            normalized,
            flags=re.UNICODE,
        )
    )

    unique_word_ratio = (
        len(set(word.lower() for word in words))
        / word_count
        if word_count > 0
        else 0.0
    )

    alphabetic_ratio = (
        alphabetic_characters / character_count
    )

    alphanumeric_ratio = (
        alphanumeric_characters / character_count
    )

    unusual_character_ratio = (
        unusual_character_count / character_count
    )

    replacement_ratio = (
        replacement_character_count / character_count
    )

    score = 1.0

    if character_count < minimum_characters:
        score -= 0.30
        reasons.append("Metin çok kısa.")

    if word_count < minimum_words:
        score -= 0.25
        reasons.append("Kelime sayısı yetersiz.")

    if alphabetic_ratio < 0.45:
        score -= 0.25
        reasons.append(
            "Metinde alfabetik karakter oranı düşük."
        )

    if alphanumeric_ratio < 0.55:
        score -= 0.15
        reasons.append(
            "Metinde okunabilir karakter oranı düşük."
        )

    if unusual_character_ratio > 0.10:
        score -= 0.20
        reasons.append(
            "Metinde olağan dışı karakter oranı yüksek."
        )

    if replacement_ratio > 0.01:
        score -= 0.20
        reasons.append(
            "Metinde bozuk karakterler bulunuyor."
        )

    if word_count >= minimum_words and unique_word_ratio < 0.25:
        score -= 0.15
        reasons.append(
            "Metinde aşırı kelime tekrarı bulunuyor."
        )

    score = max(0.0, min(1.0, score))

    return TextQualityResult(
        score=round(score, 4),
        is_searchable=score >= acceptance_score,
        reasons=reasons,
    )