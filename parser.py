from io import BytesIO

from pypdf import PdfReader

MAX_FILE_MB = 2
MAX_PAGES = 5
MIN_CV_CHARS = 200
MAX_CV_CHARS = 15000


class CVError(Exception):
    """A problem with the uploaded file that the user can fix."""


def extract_cv_text(data: bytes) -> str:
    if len(data) > MAX_FILE_MB * 1024 * 1024:
        raise CVError(f"The file is larger than {MAX_FILE_MB} MB. Please upload a smaller PDF.")
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise CVError("This PDF is password-protected. Remove the password and try again.")
        pages = reader.pages[:MAX_PAGES]
        raw = "\n".join(page.extract_text() or "" for page in pages)
    except CVError:
        raise
    except Exception as exc:
        raise CVError("This file could not be read as a PDF.") from exc

    lines = [" ".join(line.split()) for line in raw.splitlines()]
    text = "\n".join(line for line in lines if line)
    if len(text) < MIN_CV_CHARS:
        raise CVError(
            "Almost no text was found. Scanned or image-only resumes are not supported. "
            "Export your resume as a text PDF from Word or Google Docs."
        )
    return text[:MAX_CV_CHARS]
