# Bundled book dataset profile

The bundled `references/book-knowledge.sqlite` index contains two full authorized English editions (2 documents, 1,502 FTS5 chunks). Every result carries its document title and portable source id, so hits are always attributable to one book or the other.

Since 2026-09-08 the text of both books is **PDF-verified**: the PDF embedded text layer is the text authority, the DOCX supplies the section structure, and every unit is aligned between the two before indexing (see [knowledge-base.md](knowledge-base.md) for the rebuild rule). The stored text passes the `paper_kb.py check` artifact scan with zero issues.

## Book 1 — Gastel & Day, journal-article writing

### Bibliographic identity

- Barbara Gastel and Robert A. Day, *How to Write and Publish a Scientific Paper*, 8th edition (2016)
- Paperback ISBN: 978-1-316-64043-2
- DOI: 10.1017/9781108105293
- Portable dataset identifier: `urn:isbn:9781316640432`
- Official edition record: <https://assets.cambridge.org/97813166/40432/frontmatter/9781316640432_frontmatter.pdf>

### Build provenance

- Build sources: user-supplied English PDF (text authority) + English DOCX (section structure)
- PDF SHA-256 (text authority): `9B8D562AA3F28F0F942990365E555D18F276B8F7E9BF53B742CF202F3B5422A7`
- DOCX SHA-256 (structure source): `C003927737427B690360559C0E773C04D31318BB18B0BCC90DFF101AA1241610`
- Extraction: PDF embedded text layer via `pdftotext` (347 pages); invisible characters (soft hyphens, zero-width spaces) removed; running heads and page numbers stripped from page margins; no OCR
- Structure: 411 section-oriented units from the DOCX (heading-based, with page-numbered table-of-contents locators)
- PDF-verified text: 353 of 411 units take their text from the aligned PDF — 90 units with converter damage repaired (the damage signature was digits misrecognized as "G", e.g. `9781440842G27` → `9781440842627`, `19G8` → `1968`), the remaining 263 verified clean against the original; 58 units keep DOCX text (multi-column abbreviation tables whose PDF reading order differs, front matter, and one section whose figure example is float-positioned differently — see Known residuals). Mean alignment coverage 0.997 (minimum 0.75, on that float-ordered section)
- Additional cleanup: 10 running-head lines ("N How to Write and Publish a Scientific Paper") embedded in the DOCX text removed; 2 verified character repairs in the SI-prefixes table (DOCX `10G` → `106` for mega, `10−G` → `10−6` for micro — the PDF's own copy of that table fragments the exponents); 6 damaged table-of-contents locators corrected against the PDF's own TOC (`2G` → `26`, `3G` → `36`, `2G3` → `263`, `2G9` → `269`, `27G` → `277`, "Historical Perspectives G" → "Historical Perspectives"); the PDF text layer also (a) inserted a stray space after the first letter of some words ("t here", "f actor", "a fter") — every such split was detected and rejoined (159 in non-"a" letters alone, plus a few "a"-letter ones), each verified by requiring the rejoined form to be a word that occurs intact elsewhere in the book, and (b) wrapped words across line breaks without a hyphen ("book w / ill demystify", "colleagues and o / thers") — 274 such splits were rejoined, each verified against the undamaged DOCX text, which is the clean copy of the same sentences: the merge is applied only when the surrounding context occurs in the DOCX and *every* occurrence continues with the two fragments as one complete word (a space inside — as in "to a / new point" or "add s / or es" — declines the merge), so legitimate standalone letters (the article "a", the "g" in "10 g", author initials, superscript "a, b, c", the "i" in the Croatian title) were never touched
- Indexed: 645 FTS5 chunks
- Build date: 2026-09-08, via `scripts/build_kb.py`

## Book 2 — Turabian, research process and Chicago style

### Bibliographic identity

- Kate L. Turabian, *A Manual for Writers of Research Papers, Theses, and Dissertations: Chicago Style for Students and Researchers*, 7th edition (2003; this copy is the 2007 paperback printing, © 2007 University of Chicago Press)
- Revised by Wayne C. Booth, Gregory G. Colomb, Joseph M. Williams, and University of Chicago Press editorial staff
- ISBN-13: 978-0-226-82337-9 (paper) · 978-0-226-82336-2 (cloth) · 978-0-226-82338-6 (electronic)
- ISBN-10: 0-226-82337-7 (paper) · 0-226-82336-9 (cloth)
- LCCN: LB2369.T8 2007 (2006025443)
- Portable dataset identifier: `urn:isbn:9780226823379`
- Edition note: the copy's front matter ("A Note to Students" and "Preface") states three times that this is the seventh edition; the preface records the series history as 5th edition 1987, 6th edition 1996, 7th edition 2003. Part I ("Research and Writing: From Planning to Production") is adapted from Booth, Colomb, and Williams' *The Craft of Research* (Chicago: University of Chicago Press, 2003), and the rest follows *The Chicago Manual of Style*, 15th edition (2003).

### Structure

- Part I, Research and Writing: From Planning to Production (Booth, Colomb, Williams): research aims and question types (conceptual/practical/applied), topic → question → working hypothesis → claim, storyboard planning, source finding/evaluation/engagement, note-taking, argument elements (claim, reasons, evidence, warrants, readers' objections), first drafts, quotations/paraphrase/summaries, plagiarism and inappropriate assistance, tables and figures, revising, alternative forums (oral, poster, conference proposal)
- Part II, Source Citation: general introduction to citation practices; notes-bibliography style (basic form, books, journal/magazine/newspaper articles, other source types, electronic sources); parenthetical citations–reference list ("author-date") style with the same source coverage
- Part III, Style: spelling, plurals/possessives, punctuation, numbers, abbreviations, names/titles, quotation mechanics, tables and figures mechanics
- Appendix: Paper Format and Submission (front matter, body, back matter, submission requirements)

### Build provenance

- Build sources: user-supplied English PDF (text authority) + English DOCX (section structure)
- PDF SHA-256 (text authority): `9D1156CA4F8347F53A5F7585EBDAD2FA74FF43AB0F84921DA208B3FE41371283`
- DOCX SHA-256 (structure source): `0EE848C55752AB1A4EF7612DFAE712282E1389262AE44CFAC812BA3FEE6B6C5E`
- Extraction: PDF embedded text layer via `pdftotext` (471 pages); no OCR
- Structure: 529 section-oriented units from the DOCX (34 chapter, 137 section, 357 subsection headings plus front matter)
- PDF-verified text: 515 of 529 units take their text from the aligned PDF; the alignment found no converter damage in this copy (mean coverage 0.999, minimum 0.90). The 14 units that keep DOCX text are tables and short front-matter units whose alignment coverage fell below the 0.90 adoption threshold
- Note: the lettered page-reference examples printed in this book (for example `G6v`, `G26–G27`, `176r`, `232r–v` — folio/recto-verso locators) are legitimate book content, not damage; the `check` artifact scan exempts exactly that token form
- Indexed: 857 FTS5 chunks
- Build date: 2026-09-08, via `scripts/build_kb.py`

## Shared index configuration

- Single FTS5 index over both documents; tokenizer `porter unicode61 remove_diacritics 2` (stemmed matching), chunks 1,800 chars with 180-char overlap
- Full PDF-verified rebuild on 2026-09-08 via `scripts/build_kb.py` (1,502 chunks)
- Search: porter-stemmed AND matching with bm25 ranking; automatic OR fallback when AND finds nothing; optional `--source` per-book filter (see [knowledge-base.md](knowledge-base.md))

## Known residuals

After PDF verification, `scripts/paper_kb.py check` reports **zero artifact issues** across all 1,502 chunks. These documented residuals remain:

1. **Book 1, copyright page**: the printer's decade line (the "20 19 18 … 7" year row) is absent from the index. Both the DOCX and the PDF's own text layer are damaged in that region (the PDF loses 15–7; the DOCX misread one digit as "G"), so the line was dropped instead of storing a damaged version. No informational content is lost.
2. **Book 1, SI-prefixes table (Appendix 3)**: the PDF's own text layer fragments the superscript exponents (most rows lose the "10" base), so this unit keeps the DOCX text with the two verified character repairs listed above. All other table values are correct.
3. **Book 1, appendix abbreviation tables and a few front-matter units**: the PDF lays these out as multi-column tables whose reading order differs from the DOCX; the units keep the (undamaged) DOCX text and list the complete abbreviation content.
4. **Book 1, "Types of Abstracts" section**: the worked example — the abstract of a fictional review article (Figure 9.3 in the book) — is float-positioned, so it sits at a different offset in the DOCX text than in the PDF layout. The unit keeps the DOCX text; the content is complete in both.
5. **Book 2**: no text damage found; 14 table/front-matter units keep DOCX text purely because their alignment coverage was below the adoption threshold.
6. **Both books, a few word fragments at chunk starts**: the sliding-window indexer (1,800-char chunks, 180-char overlap) occasionally opens a chunk mid-word, so a handful of chunks begin with a word fragment (for example "f your article", where the "o" sits in the preceding chunk's overlap, or "n after the battle"). The complete word is always present in the neighboring chunk's overlap, so no content or searchability is lost; the fragments are visible only if individual chunks are read in isolation.
7. **Book 1, one unrepaired mid-word line break**: the PDF's 274 non-hyphen word wraps were repaired as described above; a single spot remains — "…include quotations from o\nthers' work" in the CREDIT section — where the DOCX phrases the sentence differently, so the verification oracle (which only merges what the DOCX confirms) could not confirm the join. The letters are all present in order; the word "others" appears intact many times elsewhere.

## Independence boundary

The dataset contains the searchable text, titles, section locators, and source hashes of both editions. Once built, the source DOCX and PDF files are not read or required. Keep the original files separately only if desired for provenance or visual verification.

The distilled craft layer in `craft/` (five files, 2026-07-25) was mined from this verified dataset: each technique carries the KB locator of the chunk it came from, so every condensed claim can be traced back to the source text by query.

Both editions predate some current journal, reporting, open-science, electronic-citation, and AI policies (Gastel & Day: 2016 edition; Turabian: follows CMOS 15th, 2003). Use them for durable writing craft, research-process, citation, and publication-process concepts; verify time-sensitive requirements through [source-registry.md](source-registry.md), the target journal, or the relevant university.
