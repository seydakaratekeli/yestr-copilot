import re
import unicodedata


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""

    normalized = unicodedata.normalize(
        "NFKC",
        text,
    )

    normalized = normalized.replace("\x00", " ")

    # Satır sonunda bölünmüş kelimeleri birleştirir.
    normalized = re.sub(
        r"(\w)-\s*\n\s*(\w)",
        r"\1\2",
        normalized,
    )

    # Gereksiz yatay boşlukları sadeleştirir.
    normalized = re.sub(
        r"[ \t]+",
        " ",
        normalized,
    )

    # Üç ve daha fazla satır sonunu ikiye indirir.
    normalized = re.sub(
        r"\n{3,}",
        "\n\n",
        normalized,
    )

    lines = [
        line.strip()
        for line in normalized.splitlines()
    ]

    normalized = "\n".join(
        line
        for line in lines
        if line
    )

    return normalized.strip()


def count_words(text: str) -> int:
    if not text:
        return 0

    return len(
        re.findall(
            r"\b[\wÇĞİÖŞÜçğıöşü]+\b",
            text,
            flags=re.UNICODE,
        )
    )