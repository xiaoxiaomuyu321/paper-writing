#!/usr/bin/env python3
"""Build and query a source-grounded SQLite FTS5 knowledge base.

Multiple sources (for example two reference books) can share one database;
every result carries the document title and portable source id, and query
accepts --source to restrict search to one document by title or source id.
Search uses porter-stemmed AND matching and falls back to bm25-ranked OR
matching when the AND query finds nothing.

DOCX, EPUB, Markdown, and text ingestion use only Python's standard library.
PDF ingestion uses pypdf when installed and otherwise falls back to a
`pdftotext` executable (for example from poppler-utils or a TeX distribution);
pass --pdftotext-path to name one explicitly.
OCR of scanned PDFs additionally requires the `tesseract` executable,
`pypdfium2`, and Pillow. The database stores portable source identifiers (or
paths), hashes, locators, and extracted text so every result is auditable.
Querying and `status` never touch the source files: once a database is built
it is fully self-contained, and source files are only needed to ingest or
rebuild it.
"""

from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence
from html.parser import HTMLParser


BUNDLED_DB = Path(__file__).resolve().parents[1] / "references" / "book-knowledge.sqlite"
WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Porter stemming lets "respond" match "responds/responded" and "reviewer"
# match "reviewers"; remove_diacritics 2 normalizes accented letters.
FTS_TOKENIZER = "porter unicode61 remove_diacritics 2"


SCHEMA = f"""
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    source_type TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{{}}'
);
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    locator TEXT NOT NULL,
    text TEXT NOT NULL,
    UNIQUE(document_id, ordinal)
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    title,
    path UNINDEXED,
    locator UNINDEXED,
    text,
    tokenize='{FTS_TOKENIZER}'
);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _configure_utf8_stdio() -> None:
    """Make Unicode JSON reliable on legacy Windows console encodings."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@contextmanager
def _temporary_dir(prefix: str):
    """Yield a writable temp directory, preferring the platform temp area.

    Directory creation avoids tempfile.mkdtemp on purpose: mkdtemp creates
    0o700-mode directories that some Windows sandboxes (for example the
    DeepSeek Harness workspace sandbox) write-protect. A plain os.mkdir
    works there. If the platform temp area is denied, fall back to the
    current working directory.
    """
    last_error: Exception | None = None
    name: Path | None = None
    for base in (tempfile.gettempdir(), str(Path.cwd())):
        try:
            name = Path(base) / f"{prefix}{uuid.uuid4().hex[:12]}"
            os.mkdir(str(name))
            probe = name / "probe.txt"
            probe.write_text("probe", encoding="utf-8")
            probe.unlink()
        except OSError as exc:
            last_error = exc
            if name is not None:
                shutil.rmtree(name, ignore_errors=True)
            name = None
            continue
        try:
            yield str(name)
        finally:
            shutil.rmtree(name, ignore_errors=True)
        return
    raise RuntimeError(f"could not create a writable temporary directory: {last_error}")


def _connect(db_path: Path, create: bool = True) -> sqlite3.Connection:
    db_path = Path(db_path)
    if not create and not db_path.exists():
        raise FileNotFoundError(f"knowledge base does not exist: {db_path}")
    if create:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    if create:
        connection.executescript(SCHEMA)
    return connection


def _normalize(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Invisible characters that PDF text layers (and some ebook conversions)
# inject inside words. They are never meaningful in stored text.
_INVISIBLE_CHARS = "\u00ad\u200b\u200c\u200d\u2060\ufeff"


def clean_extracted_text(text: str) -> str:
    """Remove invisible formatting characters from extracted text."""
    return "".join(ch for ch in text if ch not in _INVISIBLE_CHARS)


def _chunk_text(text: str, max_chars: int, overlap: int) -> Iterator[str]:
    text = _normalize(text)
    if not text:
        return
    if max_chars < 200:
        raise ValueError("max_chars must be at least 200")
    if overlap < 0 or overlap >= max_chars:
        raise ValueError("overlap must be non-negative and smaller than max_chars")

    start = 0
    length = len(text)
    while start < length:
        end = min(start + max_chars, length)
        if end < length:
            candidates = [
                text.rfind("\n\n", start + max_chars // 2, end),
                text.rfind(". ", start + max_chars // 2, end),
                text.rfind("。", start + max_chars // 2, end),
            ]
            boundary = max(candidates)
            if boundary > start:
                end = boundary + (1 if text[boundary] == "。" else 2)
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end >= length:
            break
        start = max(end - overlap, start + 1)


def _text_units(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    return [(f"paragraph {index}", paragraph) for index, paragraph in enumerate(paragraphs, 1)]


class _EpubTextParser(HTMLParser):
    """Small dependency-free EPUB XHTML text extractor."""

    _BLOCK_TAGS = {"p", "div", "section", "article", "h1", "h2", "h3", "h4", "li", "blockquote"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._buffer: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._buffer.append(data.strip())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._BLOCK_TAGS and self._buffer:
            self.parts.append(" ".join(self._buffer))
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag in self._BLOCK_TAGS and self._buffer:
            self.parts.append(" ".join(self._buffer))
            self._buffer = []

    def close(self) -> None:
        super().close()
        if self._buffer:
            self.parts.append(" ".join(self._buffer))
            self._buffer = []


def _epub_units(path: Path) -> list[tuple[str, str]]:
    units: list[tuple[str, str]] = []
    with zipfile.ZipFile(path) as archive:
        members = sorted(
            name for name in archive.namelist()
            if name.lower().endswith((".xhtml", ".html", ".htm"))
        )
        for member in members:
            parser = _EpubTextParser()
            parser.feed(archive.read(member).decode("utf-8", errors="replace"))
            parser.close()
            text = _normalize("\n\n".join(parser.parts))
            if text:
                units.append((Path(member).name, text))
    if not units:
        raise RuntimeError("EPUB contains no extractable XHTML/HTML text")
    return units


def _docx_units(path: Path) -> list[tuple[str, str]]:
    """Extract section-oriented text directly from WordprocessingML."""
    with zipfile.ZipFile(path) as archive:
        try:
            root = ET.fromstring(archive.read("word/document.xml"))
        except KeyError as exc:
            raise RuntimeError("DOCX is missing word/document.xml") from exc
        except ET.ParseError as exc:
            raise RuntimeError("DOCX contains invalid WordprocessingML") from exc

    units: list[tuple[str, str]] = []
    locator = "document"
    paragraphs: list[str] = []

    def flush() -> None:
        nonlocal paragraphs
        text = _normalize("\n\n".join(paragraphs))
        if text:
            units.append((locator, text))
        paragraphs = []

    for paragraph in root.iter(f"{WORD_NS}p"):
        text = _normalize("".join(node.text or "" for node in paragraph.iter(f"{WORD_NS}t")))
        if not text:
            continue
        style_node = paragraph.find(f"./{WORD_NS}pPr/{WORD_NS}pStyle")
        style = style_node.get(f"{WORD_NS}val", "") if style_node is not None else ""
        if style.lower().replace(" ", "").startswith(("heading", "title")):
            flush()
            locator = text
            paragraphs.append(text)
        else:
            paragraphs.append(text)
    flush()
    if not units:
        raise RuntimeError("DOCX contains no extractable WordprocessingML text")
    return units


def extract_pdf_pages(path: Path, pdftotext_path: str | None = None) -> tuple[list[str], str]:
    """Return (per_page_text, engine) for a PDF.

    Uses pypdf when installed and otherwise the pdftotext CLI (poppler-utils
    or any TeX distribution that ships it). Invisible formatting characters
    (soft hyphens, zero-width spaces) are removed from the returned text.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        pass
    else:
        reader = PdfReader(str(path))
        pages = [clean_extracted_text(page.extract_text() or "") for page in reader.pages]
        return pages, "embedded PDF text (pypdf)"

    executable = pdftotext_path or shutil.which("pdftotext")
    if not executable:
        raise RuntimeError(
            "PDF ingestion requires the pypdf package or a pdftotext executable "
            "(poppler-utils); pass --pdftotext-path to point at one"
        )
    with _temporary_dir("paper-kb-pdf-") as temp_dir:
        out_path = Path(temp_dir) / "page.txt"
        process = subprocess.run(
            [executable, str(path), str(out_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if process.returncode != 0 or not out_path.exists():
            detail = (process.stderr or "pdftotext failed").strip().splitlines()
            raise RuntimeError(f"pdftotext failed: {detail[-1] if detail else 'unknown error'}")
        raw = clean_extracted_text(out_path.read_text(encoding="utf-8", errors="replace"))
    return raw.split("\f"), "embedded PDF text (pdftotext)"


def _extract_pdf_text(
    path: Path, pdftotext_path: str | None = None
) -> tuple[list[tuple[str, str]], int, str]:
    """Per-page units for ingestion. Returns (units, blank_pages, engine)."""
    pages, engine = extract_pdf_pages(path, pdftotext_path)
    units: list[tuple[str, str]] = []
    blank_pages = 0
    for index, page in enumerate(pages, 1):
        text = _normalize(page)
        if len(re.sub(r"\s+", "", text)) < 40:
            blank_pages += 1
        else:
            units.append((f"page {index}", text))
    return units, blank_pages, engine


def _resolve_tesseract(tesseract_path: str | None) -> str | None:
    if tesseract_path:
        candidate = Path(tesseract_path)
        return str(candidate) if candidate.is_file() else None
    return shutil.which("tesseract")


def _ocr_pdf(
    path: Path,
    tesseract_path: str | None,
    languages: str,
    scale: float,
) -> list[tuple[str, str]]:
    executable = _resolve_tesseract(tesseract_path)
    if not executable:
        raise RuntimeError(
            "OCR is required for this scanned PDF, but the tesseract executable was not found. "
            "Install Tesseract OCR with the needed language packs, then rerun with "
            "--ocr tesseract and optionally --tesseract-path."
        )
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise RuntimeError("OCR rendering requires pypdfium2 and Pillow") from exc

    document = pdfium.PdfDocument(str(path))
    units: list[tuple[str, str]] = []
    with _temporary_dir("paper-kb-ocr-") as temp_dir:
        temp_root = Path(temp_dir)
        for zero_index, page in enumerate(document):
            page_number = zero_index + 1
            image_path = temp_root / f"page-{page_number:05d}.png"
            page.render(scale=scale).to_pil().save(image_path)
            command = [executable, str(image_path), "stdout", "-l", languages, "--psm", "6"]
            process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            if process.returncode != 0:
                detail = process.stderr.strip() or "unknown Tesseract error"
                raise RuntimeError(f"OCR failed on page {page_number}: {detail}")
            text = _normalize(process.stdout)
            if text:
                units.append((f"page {page_number}", text))
    if not units:
        raise RuntimeError("OCR completed but produced no extractable text")
    return units


def _source_units(
    path: Path,
    ocr: str,
    tesseract_path: str | None,
    languages: str,
    ocr_scale: float,
    pdftotext_path: str | None = None,
) -> tuple[list[tuple[str, str]], dict]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return _text_units(path), {"extraction": "utf-8 text"}
    if suffix == ".epub":
        return _epub_units(path), {"extraction": "EPUB XHTML text"}
    if suffix == ".docx":
        return _docx_units(path), {"extraction": "DOCX WordprocessingML text"}
    if suffix != ".pdf":
        raise ValueError("supported source types are PDF, DOCX, EPUB, TXT, and Markdown")

    units, blank_pages, engine = _extract_pdf_text(path, pdftotext_path)
    if units and (ocr == "never" or blank_pages == 0):
        return units, {"extraction": engine, "pages_needing_ocr": blank_pages}
    if ocr == "never":
        raise RuntimeError(
            "OCR with tesseract is required because this PDF has no usable extractable text; "
            "rerun with --ocr tesseract after installing Tesseract OCR."
        )
    if ocr not in {"auto", "tesseract"}:
        raise ValueError("ocr must be one of: auto, never, tesseract")
    ocr_units = _ocr_pdf(path, tesseract_path, languages, ocr_scale)
    return ocr_units, {"extraction": "tesseract OCR", "languages": languages}


def ingest_units(
    db_path: Path | str,
    title: str,
    source_key: str,
    source_hash: str,
    source_type: str,
    units: Sequence[tuple[str, str]],
    metadata: dict,
    *,
    max_chars: int = 1800,
    overlap: int = 180,
) -> dict:
    """Store (locator, text) units as one document, replacing any document
    already registered under the same source key. Used by ingest_source and
    by build scripts that produce their own unit sequences."""
    chunk_rows: list[tuple[int, str, str]] = []
    ordinal = 0
    for locator, unit_text in units:
        for chunk in _chunk_text(unit_text, max_chars, overlap):
            ordinal += 1
            chunk_rows.append((ordinal, locator, chunk))
    if not chunk_rows:
        raise RuntimeError("source produced no indexable text")

    with closing(_connect(Path(db_path), create=True)) as connection:
        existing = connection.execute(
            "SELECT id FROM documents WHERE path = ?", (source_key,)
        ).fetchone()

        status = "updated" if existing else "ingested"
        if existing:
            chunk_ids = connection.execute(
                "SELECT id FROM chunks WHERE document_id = ?", (existing["id"],)
            ).fetchall()
            connection.executemany(
                "DELETE FROM chunks_fts WHERE rowid = ?", [(row["id"],) for row in chunk_ids]
            )
            connection.execute("DELETE FROM documents WHERE id = ?", (existing["id"],))

        cursor = connection.execute(
            """INSERT INTO documents(path, title, sha256, source_type, ingested_at, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                source_key,
                title,
                source_hash,
                source_type,
                _utc_now(),
                json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            ),
        )
        document_id = cursor.lastrowid
        for row_ordinal, locator, chunk in chunk_rows:
            chunk_cursor = connection.execute(
                "INSERT INTO chunks(document_id, ordinal, locator, text) VALUES (?, ?, ?, ?)",
                (document_id, row_ordinal, locator, chunk),
            )
            connection.execute(
                "INSERT INTO chunks_fts(rowid, title, path, locator, text) VALUES (?, ?, ?, ?, ?)",
                (chunk_cursor.lastrowid, title, source_key, locator, chunk),
            )
        connection.commit()
        return {
            "status": status,
            "document_id": document_id,
            "chunks": len(chunk_rows),
            "sha256": source_hash,
            "metadata": metadata,
        }


def ingest_source(
    db_path: Path | str,
    source_path: Path | str,
    title: str | None = None,
    *,
    source_id: str | None = None,
    ocr: str = "auto",
    tesseract_path: str | None = None,
    languages: str = "eng+chi_sim",
    ocr_scale: float = 2.5,
    pdftotext_path: str | None = None,
    max_chars: int = 1800,
    overlap: int = 180,
) -> dict:
    source = Path(source_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"source does not exist: {source}")
    source_hash = _sha256(source)
    document_title = title or source.stem
    source_key = source_id or str(source)

    with closing(_connect(Path(db_path), create=True)) as connection:
        existing = connection.execute(
            "SELECT id, sha256 FROM documents WHERE path = ?", (source_key,)
        ).fetchone()
        if existing and existing["sha256"] == source_hash:
            count = connection.execute(
                "SELECT COUNT(*) FROM chunks WHERE document_id = ?", (existing["id"],)
            ).fetchone()[0]
            return {"status": "unchanged", "document_id": existing["id"], "chunks": count}

    units, metadata = _source_units(
        source, ocr, tesseract_path, languages, ocr_scale, pdftotext_path
    )
    return ingest_units(
        db_path,
        document_title,
        source_key,
        source_hash,
        source.suffix.lower().lstrip("."),
        units,
        metadata,
        max_chars=max_chars,
        overlap=overlap,
    )


def _fts_terms(query: str) -> list[str]:
    tokens = re.findall(r"[^\W_]+", query, flags=re.UNICODE)
    if not tokens:
        raise ValueError("query must contain at least one word or number")
    return [token.replace('"', '""') for token in tokens]


def _fts_query(query: str, joiner: str = " AND ") -> str:
    return joiner.join(f'"{token}"' for token in _fts_terms(query))


def _run_fts_search(
    connection: sqlite3.Connection,
    expression: str,
    limit: int,
    source: str | None,
) -> list[sqlite3.Row]:
    parameters: list[str | int] = [expression]
    clause = "WHERE chunks_fts MATCH ?"
    if source:
        clause += " AND (f.path LIKE ? OR f.title LIKE ?)"
        like = f"%{source}%"
        parameters.extend([like, like])
    parameters.append(limit)
    return connection.execute(
        f"""SELECT f.title, f.path, f.locator, c.text, bm25(chunks_fts) AS score
            FROM chunks_fts AS f
            JOIN chunks AS c ON c.id = f.rowid
            {clause}
            ORDER BY score
            LIMIT ?""",
        parameters,
    ).fetchall()


def search(
    db_path: Path | str,
    query: str,
    limit: int = 5,
    source: str | None = None,
) -> list[dict]:
    """Search indexed sources; `source` optionally filters by title or source id.

    Matching is AND across all query terms (porter stemming applies). When the
    AND query returns nothing and the query has several terms, the search
    falls back to OR matching ranked by bm25, so relevant chunks that use
    different word forms or phrasings are still found.
    """
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    with closing(_connect(Path(db_path), create=False)) as connection:
        rows = _run_fts_search(connection, _fts_query(query), limit, source)
        if not rows and len(_fts_terms(query)) > 1:
            rows = _run_fts_search(connection, _fts_query(query, " OR "), limit, source)
    return [dict(row) for row in rows]


def reindex(db_path: Path | str) -> int:
    """Rebuild the FTS5 index from stored chunks (e.g. after a tokenizer change)."""
    with closing(_connect(Path(db_path), create=False)) as connection:
        connection.execute("DROP TABLE IF EXISTS chunks_fts")
        connection.execute(
            f"""CREATE VIRTUAL TABLE chunks_fts USING fts5(
                title,
                path UNINDEXED,
                locator UNINDEXED,
                text,
                tokenize='{FTS_TOKENIZER}'
            )"""
        )
        cursor = connection.execute(
            """INSERT INTO chunks_fts(rowid, title, path, locator, text)
               SELECT c.id, d.title, d.path, c.locator, c.text
               FROM chunks AS c
               JOIN documents AS d ON d.id = c.document_id"""
        )
        connection.commit()
        return cursor.rowcount if cursor.rowcount is not None else 0


def status(db_path: Path | str) -> dict:
    with closing(_connect(Path(db_path), create=False)) as connection:
        documents = connection.execute(
            """SELECT d.id, d.title, d.path, d.sha256, d.source_type, d.ingested_at,
               d.metadata_json,
               (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id) AS chunk_count
               FROM documents d ORDER BY d.id"""
        ).fetchall()
        chunk_count = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    return {
        "database": str(Path(db_path).resolve()),
        "documents": [dict(row) for row in documents],
        "document_count": len(documents),
        "chunk_count": chunk_count,
    }


# Patterns that indicate extraction damage in stored text. Each kind maps to a
# compiled regex; tokens are reported with surrounding context so a damaged
# passage can be repaired against the original source.
_ARTIFACT_PATTERNS = {
    "cjk_in_latin": re.compile(
        r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\ufe30-\ufe4f]"
    ),
    "replacement_char": re.compile(r"[\ufffd\ufeff]"),
    "invisible_char": re.compile(r"[\u00ad\u200b\u200c\u200d\u2060]"),
    # Alphanumeric tokens mixing the letter G with digits are the signature of
    # a mis-recognized digit (converter damage such as "1G3", "G8G", "201G").
    "g_digit_token": re.compile(r"\b[A-Za-z0-9]+\b"),
}

# Lettered page/section references that legitimately combine G with digits:
# Turabian's citation examples ("G6v", "G26-G27" poster numbers). A section
# letter leads the token; converter damage embeds G between digits ("2G3",
# "19G8") or inside long digit runs ("9781440842G27") instead.
_LEGIT_G_TOKEN = re.compile(r"^G\d{1,2}[a-z]?$")


def _context(text: str, start: int, end: int, pad: int = 40) -> str:
    lo = max(0, start - pad)
    hi = min(len(text), end + pad)
    return text[lo:hi].replace("\n", " ")


def check_artifacts(db_path: Path | str, max_issues: int = 200) -> dict:
    """Scan every chunk for known extraction-artifact patterns.

    Read-only. Returns per-kind counts and up to `max_issues` detailed
    findings so a build can be audited before the database is shipped.
    """
    issues: list[dict] = []
    kind_counts: dict[str, int] = {}
    with closing(_connect(Path(db_path), create=False)) as connection:
        rows = connection.execute(
            """SELECT c.id, c.ordinal, c.locator, c.text, d.id AS document_id, d.title
               FROM chunks c JOIN documents d ON d.id = c.document_id
               ORDER BY d.id, c.ordinal"""
        ).fetchall()
    scanned = len(rows)
    for row in rows:
        text = row["text"]
        for kind, pattern in _ARTIFACT_PATTERNS.items():
            for match in pattern.finditer(text):
                token = match.group(0)
                if kind == "g_digit_token":
                    if not ("G" in token and any(ch.isdigit() for ch in token)):
                        continue  # only G mixed with digits is suspicious
                    if _LEGIT_G_TOKEN.match(token):
                        continue  # legitimate lettered page/section reference
                kind_counts[kind] = kind_counts.get(kind, 0) + 1
                if len(issues) < max_issues:
                    issues.append(
                        {
                            "document_id": row["document_id"],
                            "chunk_id": row["id"],
                            "ordinal": row["ordinal"],
                            "locator": row["locator"],
                            "kind": kind,
                            "token": token,
                            "context": _context(text, match.start(), match.end()),
                        }
                    )
    return {
        "database": str(Path(db_path).resolve()),
        "chunks_scanned": scanned,
        "issue_count": sum(kind_counts.values()),
        "issues_by_kind": kind_counts,
        "issues": issues,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="ingest a PDF, DOCX, EPUB, TXT, or Markdown source")
    ingest.add_argument("--db", required=True, type=Path)
    ingest.add_argument("source", type=Path)
    ingest.add_argument("--title")
    ingest.add_argument("--source-id", help="portable identifier stored instead of the build-machine path")
    ingest.add_argument("--ocr", choices=("auto", "never", "tesseract"), default="auto")
    ingest.add_argument("--tesseract-path")
    ingest.add_argument("--pdftotext-path", help="explicit pdftotext executable (poppler) used when pypdf is absent")
    ingest.add_argument("--languages", default="eng+chi_sim")
    ingest.add_argument("--ocr-scale", type=float, default=2.5)
    ingest.add_argument("--max-chars", type=int, default=1800)
    ingest.add_argument("--overlap", type=int, default=180)

    query_parser = subparsers.add_parser("query", help="search indexed sources")
    query_parser.add_argument("--db", default=BUNDLED_DB, type=Path)
    query_parser.add_argument("query")
    query_parser.add_argument("--limit", type=int, default=5)
    query_parser.add_argument(
        "--source",
        help="only search documents whose title or source id contains this string",
    )

    status_parser = subparsers.add_parser("status", help="show indexed sources and counts")
    status_parser.add_argument("--db", default=BUNDLED_DB, type=Path)

    reindex_parser = subparsers.add_parser(
        "reindex",
        help="rebuild the FTS index from stored chunks (tokenizer migration)",
    )
    reindex_parser.add_argument("--db", default=BUNDLED_DB, type=Path)

    check_parser = subparsers.add_parser(
        "check",
        help="scan stored chunks for extraction artifacts (read-only QA)",
    )
    check_parser.add_argument("--db", default=BUNDLED_DB, type=Path)
    check_parser.add_argument("--max-issues", type=int, default=200)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_utf8_stdio()
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "ingest":
            result = ingest_source(
                args.db,
                args.source,
                args.title,
                source_id=args.source_id,
                ocr=args.ocr,
                tesseract_path=args.tesseract_path,
                pdftotext_path=args.pdftotext_path,
                languages=args.languages,
                ocr_scale=args.ocr_scale,
                max_chars=args.max_chars,
                overlap=args.overlap,
            )
        elif args.command == "query":
            result = search(args.db, args.query, args.limit, source=args.source)
        elif args.command == "reindex":
            count = reindex(args.db)
            result = {"status": "reindexed", "chunks": count}
        elif args.command == "check":
            result = check_artifacts(args.db, max_issues=args.max_issues)
        else:
            result = status(args.db)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
