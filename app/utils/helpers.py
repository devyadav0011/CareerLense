import os
import re
from typing import Dict, Any, Optional

def clean_text(text: Optional[str]) -> str:
    """Normalize whitespace and strip unprintable characters."""
    if not text:
        return ""
    # Normalize unicode spaces and newlines
    text = re.sub(r'[\r\n]+', '\n', text)
    text = re.sub(r'[ \t\f\v]+', ' ', text)
    # Remove null bytes or control characters except newlines/tabs
    text = "".join(ch for ch in text if ch == '\n' or ch == '\t' or ord(ch) >= 32)
    return text.strip()

def safe_remove_file(filepath: Optional[str]) -> bool:
    """Safely delete a file if it exists."""
    if not filepath or not os.path.isfile(filepath):
        return False
    try:
        os.remove(filepath)
        return True
    except Exception:
        return False
