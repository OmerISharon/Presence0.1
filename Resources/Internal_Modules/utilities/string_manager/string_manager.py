import re


def normalize_hebrew(text: str) -> str:
    """
    If the first “word” contains any Hebrew letters,
    assume the entire string was sent reversed,
    so flip it back.
    """
    heb_chars = re.compile(r'[\u0590-\u05FF]')

    # trim leading/trailing whitespace, look at first word
    first = text.strip().split(maxsplit=1)[0]
    if heb_chars.search(first):
        return text[::-1]
    return text