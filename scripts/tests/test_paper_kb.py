import importlib.util
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import uuid
import zipfile
from contextlib import closing
from pathlib import Path


try:
    import pypdf  # noqa: F401
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


SCRIPT = Path(__file__).resolve().parents[1] / "paper_kb.py"


def load_module():
    spec = importlib.util.spec_from_file_location("paper_kb", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _WritableTempDir:
    """A temp directory created with plain os.mkdir.

    tempfile.TemporaryDirectory/mkdtemp is unusable under the DeepSeek
    Harness Windows sandbox: mkdtemp creates 0o700-mode directories that the
    sandbox write-protects (files inside cannot be created or removed). A
    probe file verifies the directory is actually writable, not merely
    creatable. Platform temp first; working directory as fallback.
    """

    def __init__(self):
        self.name: str | None = None
        last_error: OSError | None = None
        for base in (tempfile.gettempdir(), str(Path.cwd())):
            candidate = Path(base) / f"paper-kb-test-{uuid.uuid4().hex[:12]}"
            try:
                os.mkdir(str(candidate))
                probe = candidate / "probe.txt"
                probe.write_text("probe", encoding="utf-8")
                probe.unlink()
            except OSError as exc:
                last_error = exc
                shutil.rmtree(candidate, ignore_errors=True)
                continue
            self.name = str(candidate)
            return
        raise OSError(f"could not create a writable temporary directory: {last_error}")

    def cleanup(self):
        if self.name is not None:
            shutil.rmtree(self.name, ignore_errors=True)
            self.name = None


class PaperKnowledgeBaseTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = _WritableTempDir()
        self.root = Path(self.tempdir.name)
        self.db = self.root / "paper-writing.sqlite"

    def tearDown(self):
        self.tempdir.cleanup()

    def test_ingest_text_and_return_source_grounded_search_results(self):
        kb = load_module()
        source = self.root / "notes.md"
        source.write_text(
            "# Methods\nReport software versions and enough detail for replication.\n\n"
            "# Discussion\nSeparate supported conclusions from speculation.",
            encoding="utf-8",
        )

        result = kb.ingest_source(self.db, source, title="Editorial notes")
        matches = kb.search(self.db, "software replication", limit=3)

        self.assertEqual(result["status"], "ingested")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["title"], "Editorial notes")
        self.assertEqual(matches[0]["path"], str(source.resolve()))
        self.assertIn("software versions", matches[0]["text"])
        self.assertTrue(matches[0]["locator"].startswith("paragraph"))

    def test_ingest_epub_without_ocr(self):
        kb = load_module()
        source = self.root / "scientific-writing.epub"
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("mimetype", "application/epub+zip")
            archive.writestr(
                "OEBPS/chapter.xhtml",
                "<html><body><h1>Methods</h1><p>Describe the analysis so others can reproduce it.</p></body></html>",
            )

        result = kb.ingest_source(self.db, source)
        matches = kb.search(self.db, "reproduce analysis")

        self.assertEqual(result["status"], "ingested")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["locator"], "chapter.xhtml")

    def test_ingest_docx_and_query_after_source_is_removed(self):
        kb = load_module()
        source = self.root / "scientific-writing.docx"
        document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body>
            <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Results</w:t></w:r></w:p>
            <w:p><w:r><w:t>Report effect sizes and uncertainty intervals.</w:t></w:r></w:p>
          </w:body>
        </w:document>"""
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("word/document.xml", document_xml)

        result = kb.ingest_source(self.db, source, title="Scientific writing guide", ocr="never")
        source.unlink()
        matches = kb.search(self.db, "effect sizes uncertainty")

        self.assertEqual(result["metadata"]["extraction"], "DOCX WordprocessingML text")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["locator"], "Results")
        self.assertIn("uncertainty intervals", matches[0]["text"])

    def test_portable_source_id_does_not_expose_or_depend_on_build_path(self):
        kb = load_module()
        source = self.root / "licensed-book.txt"
        source.write_text("Methods should permit independent replication.", encoding="utf-8")

        kb.ingest_source(
            self.db,
            source,
            title="Book",
            source_id="urn:isbn:9781316640432",
        )
        source.unlink()
        match = kb.search(self.db, "independent replication")[0]

        self.assertEqual(match["path"], "urn:isbn:9781316640432")
        self.assertNotIn(str(self.root), str(kb.status(self.db)))

    def test_reingesting_unchanged_source_is_idempotent(self):
        kb = load_module()
        source = self.root / "notes.txt"
        source.write_text("Use effect sizes and uncertainty intervals.", encoding="utf-8")

        first = kb.ingest_source(self.db, source)
        second = kb.ingest_source(self.db, source)

        self.assertEqual(first["status"], "ingested")
        self.assertEqual(second["status"], "unchanged")
        with closing(sqlite3.connect(self.db)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 1)

    def test_changed_source_replaces_old_chunks(self):
        kb = load_module()
        source = self.root / "notes.txt"
        source.write_text("Old guidance about alpha thresholds.", encoding="utf-8")
        kb.ingest_source(self.db, source)

        source.write_text("New guidance emphasizes effect sizes.", encoding="utf-8")
        result = kb.ingest_source(self.db, source)

        self.assertEqual(result["status"], "updated")
        self.assertEqual(kb.search(self.db, "effect sizes")[0]["title"], "notes")
        self.assertEqual(kb.search(self.db, "alpha thresholds"), [])

    @unittest.skipUnless(HAS_PYPDF, "pypdf not installed")
    def test_blank_scanned_pdf_without_ocr_fails_actionably(self):
        kb = load_module()
        from pypdf import PdfWriter

        source = self.root / "scan.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        with source.open("wb") as stream:
            writer.write(stream)

        with self.assertRaisesRegex(RuntimeError, "OCR.*tesseract"):
            kb.ingest_source(self.db, source, ocr="never")

    def test_query_with_no_index_reports_clear_error(self):
        kb = load_module()
        with self.assertRaisesRegex(FileNotFoundError, "knowledge base does not exist"):
            kb.search(self.db, "abstract")

    def test_cli_emits_utf8_even_when_parent_requests_ascii(self):
        kb = load_module()
        source = self.root / "symbols.txt"
        source.write_text("Copyright © guidance for authors.", encoding="utf-8")
        kb.ingest_source(self.db, source)
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "ascii"
        stdout_path = self.root / "cli-stdout.txt"
        stderr_path = self.root / "cli-stderr.txt"
        with stdout_path.open("wb") as out_stream, stderr_path.open("wb") as err_stream:
            process = subprocess.run(
                [sys.executable, str(SCRIPT), "query", "--db", str(self.db), "Copyright"],
                stdout=out_stream,
                stderr=err_stream,
                env=environment,
            )

        self.assertEqual(process.returncode, 0, stderr_path.read_text(encoding="utf-8", errors="replace"))
        self.assertIn("©", stdout_path.read_text(encoding="utf-8"))


    def test_stemmed_terms_and_or_fallback_find_related_chunks(self):
        kb = load_module()
        source = self.root / "peer-review.txt"
        source.write_text(
            "The authors responded to the reviewers' comments in detail.\n\n"
            "The alpha variant behaved differently.\n\n"
            "The beta variant behaved the same way.",
            encoding="utf-8",
        )
        kb.ingest_source(self.db, source, title="Peer review notes")

        stemmed = kb.search(self.db, "respond reviewer")
        self.assertTrue(any("responded to the reviewers" in m["text"] for m in stemmed))

        fallback = kb.search(self.db, "alpha beta")
        self.assertEqual(len(fallback), 2)

    def test_source_filter_limits_results_to_matching_document(self):
        kb = load_module()
        doc_a = self.root / "alpha.txt"
        doc_b = self.root / "beta.txt"
        doc_a.write_text("Effect sizes guide interpretation.", encoding="utf-8")
        doc_b.write_text("Effect sizes mislead when unchecked.", encoding="utf-8")
        kb.ingest_source(self.db, doc_a, title="Book Alpha", source_id="urn:x:alpha")
        kb.ingest_source(self.db, doc_b, title="Book Beta", source_id="urn:x:beta")

        self.assertEqual(len(kb.search(self.db, "effect sizes")), 2)

        only_a = kb.search(self.db, "effect sizes", source="urn:x:alpha")
        self.assertEqual(len(only_a), 1)
        self.assertEqual(only_a[0]["path"], "urn:x:alpha")

        by_title = kb.search(self.db, "effect sizes", source="Book Beta")
        self.assertEqual(len(by_title), 1)
        self.assertEqual(by_title[0]["path"], "urn:x:beta")

    def test_source_filter_without_match_returns_nothing(self):
        kb = load_module()
        doc_a = self.root / "gamma.txt"
        doc_a.write_text("Effect sizes guide interpretation.", encoding="utf-8")
        kb.ingest_source(self.db, doc_a, title="Book Gamma", source_id="urn:x:gamma")

        self.assertEqual(kb.search(self.db, "effect sizes", source="urn:x:missing"), [])

    def test_status_reports_per_document_chunk_counts(self):
        kb = load_module()
        source = self.root / "delta.txt"
        source.write_text("One. Two. Three.", encoding="utf-8")
        kb.ingest_source(self.db, source, title="Book Delta")

        info = kb.status(self.db)
        self.assertEqual(info["document_count"], 1)
        self.assertEqual(info["chunk_count"], 1)
        self.assertEqual(info["documents"][0]["chunk_count"], 1)

    def test_reindex_preserves_chunks_and_restores_search(self):
        kb = load_module()
        source = self.root / "epsilon.txt"
        source.write_text("Reported results were reviewed by two assessors.", encoding="utf-8")
        kb.ingest_source(self.db, source, title="Book Epsilon")

        rebuilt = kb.reindex(self.db)
        self.assertEqual(rebuilt, 1)
        match = kb.search(self.db, "assessors reviewed")
        self.assertEqual(len(match), 1)
        self.assertIn("assessors", match[0]["text"])

    def test_clean_extracted_text_removes_invisible_characters(self):
        kb = load_module()
        raw = "acknowledg\u00adments \u2060and \ufefftitle"
        self.assertEqual(kb.clean_extracted_text(raw), "acknowledgments and title")

    def test_check_artifacts_reports_damaged_tokens(self):
        kb = load_module()
        source = self.root / "damaged.txt"
        source.write_text(
            "See note 1G3 on page 201G and the index entry G8G. "
            "The copyright line says 201G. \u6f0f character present.",
            encoding="utf-8",
        )
        kb.ingest_source(self.db, source, title="Damaged sample")

        report = kb.check_artifacts(self.db)
        self.assertGreaterEqual(report["issues_by_kind"].get("g_digit_token", 0), 3)
        self.assertGreaterEqual(report["issues_by_kind"].get("cjk_in_latin", 0), 1)
        kinds = {issue["kind"] for issue in report["issues"]}
        self.assertIn("g_digit_token", kinds)
        self.assertIn("cjk_in_latin", kinds)

    def test_check_artifacts_reports_no_issues_for_clean_text(self):
        kb = load_module()
        source = self.root / "clean.txt"
        source.write_text(
            "Report effect sizes with 95 percent confidence intervals. "
            "The second edition revised the 1998 guidelines.",
            encoding="utf-8",
        )
        kb.ingest_source(self.db, source, title="Clean sample")

        report = kb.check_artifacts(self.db)
        self.assertEqual(report["issue_count"], 0)

    def test_ingest_units_replaces_document_by_source_key(self):
        kb = load_module()
        first = kb.ingest_units(
            self.db,
            "Sample book",
            "urn:x:sample",
            "a" * 64,
            "unit",
            [("Intro", "First pass of the introduction."), ("Methods", "Methods text.")],
            {"note": "first"},
        )
        self.assertEqual(first["status"], "ingested")
        second = kb.ingest_units(
            self.db,
            "Sample book",
            "urn:x:sample",
            "b" * 64,
            "unit",
            [
                ("Intro", "Second pass of the introduction."),
                ("Methods", "Methods text again."),
                ("Results", "Results text."),
            ],
            {"note": "second"},
        )
        self.assertEqual(second["status"], "updated")
        with closing(sqlite3.connect(self.db)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0], 1)
        self.assertEqual(kb.search(self.db, "second pass introduction")[0]["locator"], "Intro")
        # "First" only existed in the replaced (old) document text.
        self.assertEqual(kb.search(self.db, "First"), [])

    @unittest.skipUnless(os.name == "nt", "pdftotext shim test uses a .bat stub")
    def test_pdftotext_fallback_extracts_pages(self):
        kb = load_module()
        fake_pdf = self.root / "sample.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake")
        shim = self.root / "fake-pdftotext.bat"
        shim.write_text(
            '@echo off\r\ncopy /y "%~dp0fake-pdf-output.txt" "%2"\r\n',
            encoding="ascii",
        )
        (self.root / "fake-pdf-output.txt").write_bytes(
            b"Alpha guidance text for the first page of the book\r\n\x0c"
            b"Beta guidance text for the second page of the book\r\n"
        )

        saved = sys.modules.get("pypdf", "absent")
        sys.modules["pypdf"] = None
        try:
            units, blank_pages, engine = kb._extract_pdf_text(
                fake_pdf, pdftotext_path=str(shim)
            )
        finally:
            if saved == "absent":
                sys.modules.pop("pypdf", None)
            else:
                sys.modules["pypdf"] = saved

        self.assertEqual(len(units), 2)
        self.assertEqual(blank_pages, 0)
        self.assertIn("pdftotext", engine)
        self.assertIn("Alpha guidance", units[0][1])
        self.assertIn("Beta guidance", units[1][1])


if __name__ == "__main__":
    unittest.main()
