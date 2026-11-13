import io
import re
import pdfplumber
from docx import Document

SKILLS = ["python", "java", "javascript", "sql", "postgresql", "fastapi", "django",
          "flask", "react", "node", "html", "css", "git", "docker", "aws",
          "machine learning", "nlp", "pandas", "numpy", "mongodb", "c++"]

def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Only .pdf and .docx allowed")

def parse_resume(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone = re.search(r"(\+?\d[\d\s-]{8,13}\d)", text)
    years = re.search(r"(\d+)\+?\s*(?:years|yrs)", text, re.I)
    lower = text.lower()
    skills = [s for s in SKILLS if s in lower]
    return {
        "name": lines[0] if lines else None,
        "email": email.group(0) if email else None,
        "phone": phone.group(1).strip() if phone else None,
        "skills": skills,
        "experience": f"{years.group(1)} years" if years else "Fresher",
    }