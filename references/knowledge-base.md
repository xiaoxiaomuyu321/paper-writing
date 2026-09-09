# Bundled scientific-writing knowledge base

## Runtime contract

The skill includes `references/book-knowledge.sqlite`, a self-contained SQLite FTS5 dataset built from two authorized English editions:

1. **Book 1 — `urn:isbn:9781316640432`**: Barbara Gastel and Robert A. Day, *How to Write and Publish a Scientific Paper*, 8th edition (2016). Journal-article writing and the publication process: abstracts, IMRaD sections, data and statistics presentation, figures/tables, peer review, responses to reviewers, cover letters, ethics statements, AI and open-science policy.
2. **Book 2 — `urn:isbn:9780226823379`**: Kate L. Turabian, *A Manual for Writers of Research Papers, Theses, and Dissertations: Chicago Style for Students and Researchers*, 7th edition (2003; 2007 paperback printing). The research process (questions, working hypotheses, claims, sources, note-taking, argument planning, drafting, revision), Chicago citation in both systems (notes-bibliography and parenthetical author-date), Chicago style for student writing, and thesis/dissertation format and submission.

Runtime retrieval reads the database only. It does not require the source books, OCR, an API key, or network access.

From the skill directory, query with any available Python 3 interpreter (`python`, `python3`, `py -3`, or an absolute path):

```powershell
python scripts/paper_kb.py status
python scripts/paper_kb.py query "responding to reviewers" --limit 5
python scripts/paper_kb.py query "author date reference list" --source "A Manual for Writers" --limit 5
python scripts/paper_kb.py query "dissertation format" --source "9780226823379" --limit 5
```

Matching is porter-stemmed AND across the query terms, ranked by bm25; if the AND query finds nothing and the query has several terms, the search automatically falls back to OR matching, so phrasing variants still surface relevant chunks. Prefer two to four concrete English keywords. `--source` restricts search to one book by a substring of its title or source id (useful to keep one book's advice from being mixed with the other's). `status` lists every indexed document with its chunk count, title, source id, and SHA-256.

Retain each result's title, source id (`path` field), and section locator in working notes so book-grounded advice stays traceable.

## Two-tier use of the book content

The books are the **authority on writing technique** for every journal (see the craft-priority
rule in `../SKILL.md`). Use them in two tiers:

1. **Distilled craft layer — first stop.** `craft/craft-core.md` (always loaded) plus the
   condition-loaded `craft/section-craft.md`, `craft/language-craft.md`, `craft/argument-craft.md`,
   and `craft/citation-prose.md` hold the books' techniques already condensed, organized by use
   case, and annotated with the section locator of the source passage. Apply these as operating
   rules when drafting or revising.
2. **This knowledge base — deep source.** Query the dataset (below) when the craft layer does not
   cover the point, when the user asks what the book says, or when you need the original wording
   as evidence. Every craft-layer anchor names a KB locator, so you can verify any technique
   against the source text on demand.

## Choosing between the two books

- Journal article for a research journal, any part of the publication cycle, reporting statements: query Book 1 (no `--source` needed; its chapters dominate, but you may also add `--source "How to Write and Publish"`).
- Research planning and argument-building, source evaluation and note-taking, plagiarism prevention, long student reports, thesis/dissertation structure and submission: query Book 2 (`--source "A Manual for Writers"`).
- Chicago citation or Chicago style mechanics: Book 2 only.
- Cross-cutting topics (abstracts, revision, tables/figures, citations in general): query without `--source` and read hits from both books; agree or consciously pick the recommendation that fits the target venue or institution.

## Dataset behavior

- The bundled database contains extracted text and section locators, so deleting or moving the source books does not affect retrieval.
- `scripts/paper_kb.py` defaults `query`, `status`, and `reindex` to the bundled database path resolved relative to the script.
- The SHA-256 of both build sources of each book (PDF text authority + DOCX structure source) is retained in the `documents` table for provenance; the stored source identifiers are URNs, not machine-specific paths.
- DOCX and EPUB are parsed directly with the Python standard library; no OCR is used.
- The bundled dataset was built by `scripts/build_kb.py`, which aligns every section unit against the PDF text layer, repairs damaged units from the PDF, and records alignment statistics per document. **Do not rebuild the two bundled URNs (`urn:isbn:9781316640432`, `urn:isbn:9780226823379`) with plain `ingest`** — that would discard the PDF-verified text and alignment provenance. Rebuild them only with `build_kb.py` (requires the original DOCX + PDF pairs).
- For separately authorized sources, `ingest` also accepts PDF, DOCX, EPUB, Markdown, and UTF-8 text. Use a different database unless intentionally rebuilding the bundled dataset. `reindex` rebuilds the search index from stored chunks after tokenizer changes without re-reading any source. `check` scans the stored chunks for extraction-artifact patterns (the current bundled dataset passes with zero issues).

Example portable ingestion:

```powershell
python scripts/paper_kb.py ingest --db private-notes.sqlite "licensed-book.docx" `
  --title "Licensed scientific-writing guide" --source-id "urn:isbn:..." --ocr never
```

## Retrieval discipline

1. Query the dataset only when book-level craft or publication guidance is useful; current target-journal instructions, university regulations, and reporting standards remain controlling.
2. Read several hits because a keyword can occur in unrelated chapters; compare at least two hits before acting.
3. Check which book each hit comes from (title/source id) and do not attribute one book's recommendation to the other.
4. Paraphrase guidance and avoid reproducing long passages.
5. Do not use the book dataset as evidence for the manuscript's scientific claims.
6. The stored text was verified unit-by-unit against the PDFs of both editions (2026-09-08; the `check` artifact scan passes with zero issues), so numerals, ISBNs, dates, and citation examples can be relied on for what the books themselves say. The only exceptions are the documented residuals in [book-dataset-profile.md](book-dataset-profile.md) (all cosmetic or absent-by-damage: one decorative decade line missing from the HTW copyright page, a few units that keep their undamaged DOCX form, and a handful of word fragments at chunk overlaps). Use the dataset for the books' concepts and workflow guidance; it is not a verification source for facts about the world, and anything time-sensitive still needs the authoritative source.
7. Both editions predate current AI, open-access, and some electronic-citation policies. For anything time-sensitive, verify through [source-registry.md](source-registry.md) and the target journal or university.

The database is intended for local/private use consistent with the user's access rights to the supplied editions.
