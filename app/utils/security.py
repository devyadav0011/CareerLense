import os
import re
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def is_allowed_file(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def sanitize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    clean = secure_filename(base)
    # Remove any dangerous characters or traversal patterns
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean)
    if not clean:
        clean = "resume_upload"
    return clean

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(hashed: str, password: str) -> bool:
    return check_password_hash(hashed, password)

def validate_email(email: str) -> bool:
    if not email or len(email) > 120:
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))
