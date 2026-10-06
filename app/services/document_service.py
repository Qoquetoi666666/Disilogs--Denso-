from pathlib import Path
import json
import re
import uuid

from pypdf import PdfReader


UPLOAD_DIR = Path("uploads/documents")
EXTRACTED_DIR = Path("data/extracted")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) -> str:
    name = Path(name).name

    stem = Path(name).stem
    suffix = Path(name).suffix.lower()

    stem = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        stem,
    )

    return f"{stem}{suffix}"


def save_pdf(
    filename: str,
    content: bytes,
) -> dict:
    clean_name = safe_filename(
        filename
    )

    if not clean_name.lower().endswith(
        ".pdf"
    ):
        raise ValueError(
            "Only PDF files are supported."
        )

    document_key = uuid.uuid4().hex[:12]

    stored_name = (
        f"{document_key}_{clean_name}"
    )

    pdf_path = (
        UPLOAD_DIR / stored_name
    )

    pdf_path.write_bytes(
        content
    )

    return {
        "document_key": document_key,
        "filename": clean_name,
        "stored_filename": stored_name,
        "pdf_path": str(pdf_path),
    }


def extract_pdf_pages(
    pdf_path: str,
    document_key: str,
) -> dict:
    reader = PdfReader(
        pdf_path
    )

    pages = []

    total_characters = 0

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        try:
            text = (
                page.extract_text()
                or ""
            )
        except Exception:
            text = ""

        text = text.strip()

        total_characters += len(
            text
        )

        pages.append(
            {
                "page": page_number,
                "text": text,
                "characters": len(text),
            }
        )

    extracted_path = (
        EXTRACTED_DIR
        / f"{document_key}.json"
    )

    payload = {
        "document_key": document_key,
        "source_pdf": pdf_path,
        "page_count": len(pages),
        "total_characters":
            total_characters,
        "pages": pages,
    }

    extracted_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        **payload,
        "extracted_path":
            str(extracted_path),
    }


def process_pdf(
    filename: str,
    content: bytes,
) -> dict:
    saved = save_pdf(
        filename,
        content,
    )

    extracted = extract_pdf_pages(
        saved["pdf_path"],
        saved["document_key"],
    )

    return {
        **saved,
        **extracted,
    }


def load_extracted_document(
    document_key: str,
) -> dict:
    path = (
        EXTRACTED_DIR
        / f"{document_key}.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Extracted document "
            f"{document_key} not found."
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
