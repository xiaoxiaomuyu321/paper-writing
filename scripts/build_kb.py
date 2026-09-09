#!/usr/bin/env python3
"""Rebuild a book knowledge base with PDF-verified text.

For each source pair (a DOCX and the PDF of the same book):

* the DOCX provides the section structure (heading-based units and locators)
  and the fallback text;
* the PDF's embedded text layer (extracted with pypdf or pdftotext) is the
  authoritative text;
* every DOCX unit is aligned against the cleaned PDF text stream (running
  heads, page numbers, and embedded header lines are stripped first). Units
  that align confidently (coverage >= --adopt-coverage with head/tail
  confirmation) take their text from the PDF: damaged units (for example
  converter damage that turns digits into "G", such as "1G3" or "201G") are
  repaired this way, and clean units are verified against the original;
  units that do not align confidently (tables with a different column order,
  front matter) keep the DOCX text and are listed in the report;
* the result is written to the SQLite knowledge base with full provenance:
  both file hashes, the extraction engine, page counts, and per-unit
  alignment statistics.

Normal use of the finished database (query/status) never needs the source
files; they are only required to rebuild the database with this script.

Usage:
  python build_kb.py --db references/book-knowledge.sqlite \
      --source "title=...;id=urn:isbn:...;docx=path;pdf=path" \
      [--source ...] [--min-coverage 0.6] [--adopt-coverage 0.9] \
      [--report report.json] [--pdftotext-path PATH] [--dry-run]

Each --source is a semicolon-separated key=value string with keys title,
id, docx, and pdf.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import paper_kb as kb  # noqa: E402


NUMERIC_LINE = re.compile(r"^\d{1,4}$")
ROMAN_LINE = re.compile(r"^[ivxlcdm]{1,7}$")
ANALPHABETIC = re.compile(r"[^0-9a-z]")


def _norm_alnum(text: str) -> str:
    """Lowercase alphanumeric-only form used for alignment (case, spacing,
    punctuation, and hyphenation are all ignored)."""
    return ANALPHABETIC.sub("", text.lower())


def _norm_map(text: str) -> tuple[str, list[int]]:
    """Build (normalized_stream, position_map); position_map[i] is the index
    of the i-th normalized character in the original text."""
    chars: list[str] = []
    positions: list[int] = []
    for i, ch in enumerate(text):
        o = ord(ch)
        if "a" <= ch <= "z" or "A" <= ch <= "Z" or "0" <= ch <= "9":
            chars.append(ch.lower())
            positions.append(i)
        elif o > 0x2E7F and ch.isalnum():
            chars.append(ch.lower())
            positions.append(i)
    return "".join(chars), positions


def _clean_page_text(page: str) -> str:
    """Collapse whitespace artifacts inside one page of extracted text."""
    page = page.replace("\u2003", " ").replace("\u2002", " ").replace("\u2009", " ")
    page = re.sub(r"[ \t]+", " ", page)
    page = re.sub(r" ?\n ?", "\n", page)
    page = re.sub(r"\n{3,}", "\n\n", page)
    return page.strip()


def _strip_page_furniture(pages: list[str]) -> tuple[list[str], list[str]]:
    """Remove running heads and page numbers from the outer lines of pages.

    A line is treated as furniture when it appears in the first/last two
    non-empty lines of a page and either repeats on at least 10 distinct
    pages (running heads: book title, chapter titles) or looks like a page
    number while such numeric lines are common in the document. Only the
    outer line positions are touched, so identical text in the body is kept.
    Returns (cleaned_pages, furniture_strings).
    """
    candidates: dict[str, set[int]] = {}
    per_page: list[tuple[list[str], list[str]]] = []
    for index, page in enumerate(pages):
        lines = [line.strip() for line in page.split("\n")]
        nonempty = [(i, line) for i, line in enumerate(lines) if line]
        if not nonempty:
            per_page.append(([], []))
            continue
        first = [line for _, line in nonempty[:2]]
        last = [line for _, line in nonempty[-2:]]
        outer = [line for line in first + last if line]
        per_page.append((outer, lines))
        for line in outer:
            key = re.sub(r"\s+", " ", line)
            candidates.setdefault(key, set()).add(index)

    furniture: set[str] = set()
    numeric_keys = [
        key for key in candidates
        if NUMERIC_LINE.match(key) or ROMAN_LINE.match(key)
    ]
    # Page numbers are unique per page, so the signal is "many pages have a
    # numeric outer line", not "one number repeats".
    numeric_is_page_numbers = len(numeric_keys) >= 20
    for key, idxs in candidates.items():
        if len(idxs) >= 10:
            furniture.add(key)
        elif numeric_is_page_numbers and (
            NUMERIC_LINE.match(key) or ROMAN_LINE.match(key)
        ):
            furniture.add(key)

    cleaned: list[str] = []
    for _outer, lines in per_page:
        lines_out = list(lines)
        # touch only the first/last two non-empty positions
        nonempty_idx = [i for i, line in enumerate(lines) if line]
        if nonempty_idx:
            touch = set(nonempty_idx[:2]) | set(nonempty_idx[-2:])
            for i in touch:
                key = re.sub(r"\s+", " ", lines[i])
                if key in furniture:
                    lines_out[i] = ""
        cleaned.append("\n".join(lines_out))
    return cleaned, sorted(furniture)


def _find_all(haystack: str, needle: str, cap: int = 24) -> list[int]:
    hits: list[int] = []
    start = 0
    while len(hits) < cap:
        i = haystack.find(needle, start)
        if i == -1:
            break
        hits.append(i)
        start = i + 1
    return hits


def _clean_runs(s: str, min_len: int = 16, max_len: int = 48) -> list[tuple[int, str]]:
    """Maximal runs of normalized text that contain no digit/g corruption
    token, with their offsets. Long clean runs are truncated to max_len.
    Used as fallback anchors when a unit's head itself is corrupted."""
    bounds = [0]
    for i in range(1, len(s)):
        a, b = s[i - 1], s[i]
        if (a == "g" and b.isdigit()) or (b == "g" and a.isdigit()):
            bounds.append(i)
    bounds.append(len(s))
    runs: list[tuple[int, str]] = []
    for i in range(len(bounds) - 1):
        start = bounds[i]
        seg = s[start:bounds[i + 1]]
        if "g" in seg and any(ch.isdigit() for ch in seg):
            continue  # the corrupted token itself
        if len(seg) > max_len:
            seg = seg[:max_len]
        if len(seg) >= min_len:
            runs.append((start, seg))
    return runs


def _has_artifact(text: str) -> bool:
    """True when the text shows a known extraction artifact (see the check
    command patterns in paper_kb). Legitimate lettered references (G26, G6v)
    are exempted exactly as in paper_kb.check_artifacts."""
    for kind, pattern in kb._ARTIFACT_PATTERNS.items():
        for match in pattern.finditer(text):
            token = match.group(0)
            if kind == "g_digit_token":
                if not ("G" in token and any(ch.isdigit() for ch in token)):
                    continue
                if kb._LEGIT_G_TOKEN.match(token):
                    continue
            return True
    return False


# PDF text-layer kerning artifact: a space is inserted after the first letter
# of a word ("t here", "f actor", "a fter"). A pair is repaired only when the
# joined form occurs intact elsewhere in the corpus (the vocabulary of the PDF
# text plus the DOCX units), which makes legitimate standalone-letter usages
# safe without enumerating them: "s or es" (Turabian plural rule), "10 g"
# (grams), "n or nn" (note numbers), "and s are" (apostrophe rule), "i ceski
# kubizam" (a Croatian title in which "i" means "and"), "a book" (the
# article), and the superscript letters "a, b, or c" in affiliation
# designations. ("n", "or") joins to the real word "nor" in the vocabulary,
# but the book's "followed by n or (if two or more ...)" is legitimate, so it
# is excepted explicitly.
_KERN_PAIR_RE = re.compile(r"(?:(?<=^)|(?<=\s))([A-Za-z]) ([A-Za-z][A-Za-z']{1,})")
_KERN_PAIR_EXCEPTIONS = {("n", "or"), ("N", "or")}


def _kern_join(text: str, vocab: set[str]) -> str:
    def fix(match: re.Match[str]) -> str:
        letter, word = match.group(1), match.group(2)
        if (letter, word.lower()) in _KERN_PAIR_EXCEPTIONS:
            return match.group(0)
        if (letter + word).lower() in vocab:
            return letter + word
        return match.group(0)

    return _KERN_PAIR_RE.sub(fix, text)


def _build_vocab(full_pdf_text: str, docx_units: list[tuple[str, str]]) -> set[str]:
    """Lowercase word forms present in the books, used to validate kerning
    repairs (a split is repaired only when the rejoined word is a real word)."""
    vocab = set(re.findall(r"[A-Za-z][A-Za-z']*", full_pdf_text.lower()))
    vocab.update(
        word
        for _locator, text in docx_units
        for word in re.findall(r"[A-Za-z][A-Za-z']*", text.lower())
    )
    return vocab


_WORD_TAIL_RE = re.compile(r"([A-Za-z]{1,20})$")
_WORD_HEAD_RE = re.compile(r"^([A-Za-z]{1,12})")


def _join_word_line_splits(
    text: str, docx_raw: str, docx_vocab: set[str]
) -> str:
    """Rejoin a word that the PDF wrapped across a line break without a
    hyphen (e.g. "book w\\nill demystify" -> "book will demystify",
    "colleagues and o\\nthers" -> "colleagues and others").

    `docx_raw` is the undamaged DOCX text with whitespace collapsed — it
    still carries the real word boundaries the decision depends on (an
    alnum-only stream would fuse "a new" into "anew"). A boundary is
    repaired only when the up-to-24 characters preceding the fragment (the
    previous line included when the in-line context is shorter than 16
    characters) occur in the DOCX and, at *every* occurrence, the DOCX
    continues with the
    fragment and the next line's first word as one complete word — a space
    inside the joined form means a legitimate line end ("to a|new point",
    "add s|or es") and declines the merge. A mix of joined and separated
    continuations, or no occurrence at all, also declines. Lines ending in
    a genuine multi-letter word are filtered out before the oracle is
    consulted."""
    lines = text.split("\n")
    for index in range(len(lines) - 1):
        tail = _WORD_TAIL_RE.search(lines[index])
        head = _WORD_HEAD_RE.match(lines[index + 1])
        if not (tail and head):
            continue
        tail_word = tail.group(1)
        # A tail of 2+ letters that is a genuine word (including standalone
        # discussion letters such as "s", "or", "c") is never a split. A
        # single letter can be an author initial or a discussion letter in
        # the DOCX, so it cannot be filtered here — the oracle below
        # decides, and mixed votes always decline to merge.
        if len(tail_word) >= 2 and tail_word.lower() in docx_vocab:
            continue
        want = (tail_word + head.group(1)).lower()
        pre = lines[index][: tail.start(1)].strip()
        # Context cascade, most lenient first: the 24-char in-line context
        # is only consulted when it is strictly longer than the 20-char one
        # (a longer needle can miss DOCX-local quirks such as hyphenated
        # wraps or differently placed list numbers), and the previous line
        # is included only for a short in-line context (e.g. the line
        # "editors and o"), which is too ambiguous to match uniquely. The
        # first context whose occurrences all continue with the joined word
        # wins; every context is allowed to decline.
        candidates = [pre[-20:]]
        if len(pre) > 20:
            candidates.append(pre[-24:])
        if len(pre) < 16 and index > 0:
            candidates.append((lines[index - 1] + " " + pre)[-24:])
        merged = False
        for pre_ctx in candidates:
            pre_ctx = pre_ctx.lower()
            if len(pre_ctx) < 12:
                continue
            vote_join = 0
            vote_split = 0
            for pos in _find_all(docx_raw, pre_ctx):
                after = docx_raw[pos + len(pre_ctx):pos + len(pre_ctx) + len(want) + 2]
                after = after.lstrip(" ")
                if after.startswith(want) and (
                    len(after) == len(want) or not after[len(want)].isalpha()
                ):
                    vote_join += 1
                else:
                    vote_split += 1
            if vote_join and not vote_split:
                lines[index] = (
                    lines[index][: tail.start(1)] + tail_word + head.group(1)
                )
                lines[index + 1] = lines[index + 1][head.end(1):].lstrip()
                merged = True
                break
        if merged:
            continue
    return "\n".join(lines)


def _tidy_adopted(
    raw: str, vocab: set[str], docx_raw: str, docx_vocab: set[str]
) -> str:
    """Normalize a PDF-derived span for storage: tidy whitespace, remove
    line-wrap hyphenation (a hyphen before a newline followed by a lowercase
    letter), repair verified first-letter kerning splits (`vocab`: the
    combined PDF+DOCX vocabulary), rejoin words the PDF wrapped across a
    line break without a hyphen — verified against the undamaged DOCX text
    (`docx_raw` / `docx_vocab`) — and keep everything else verbatim."""
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r" ?\n ?", "\n", raw)
    raw = re.sub(r"-\n([a-z])", r"\1", raw)
    raw = _kern_join(raw, vocab)
    raw = _join_word_line_splits(raw, docx_raw, docx_vocab)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def _align_unit(
    unit_text: str,
    unit_norm: str,
    stream: str,
    positions: list[int],
    full: str,
    min_coverage: float,
    vocab: set[str],
    docx_raw: str,
    docx_vocab: set[str],
) -> dict:
    """Align one DOCX unit against the PDF stream.

    Candidate start positions are gathered by exact matching of several
    48-alphanumeric anchor windows across the unit head (voting), then the
    top candidates are verified with a local SequenceMatcher. The score is
    *coverage*: the fraction of the unit's alnum content found in the
    candidate window (1.0 for a clean match), which unlike a raw similarity
    ratio is fair to short units.

    Returns a dict with status ("adopted"|"kept"), coverage, artifact flag,
    and (when adopted) the replacement text.
    """
    L = len(unit_norm)
    info: dict = {"status": "kept", "coverage": None, "artifact": _has_artifact(unit_text)}
    if L < 16:
        info["note"] = "unit too short to align"
        return info

    anchor_len = min(48, L)
    votes: dict[int, int] = {}
    for offset in range(0, min(L - anchor_len + 1, 241), 24):
        anchor = unit_norm[offset:offset + anchor_len]
        for pos in _find_all(stream, anchor, cap=12):
            start_guess = pos - offset
            votes[start_guess] = votes.get(start_guess, 0) + anchor_len
    if not votes:
        # The head itself is corrupted (e.g. "2G3"): anchor on the clean
        # runs that survive around the corrupted tokens.
        for offset, run in _clean_runs(unit_norm[:240]):
            for pos in _find_all(stream, run, cap=12):
                start_guess = pos - offset
                votes[start_guess] = votes.get(start_guess, 0) + len(run)
    if not votes:
        info["note"] = "no anchor found in PDF stream"
        return info

    ordered = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))
    chosen: list[int] = []
    for guess, _weight in ordered:
        if all(abs(guess - g) > 200 for g in chosen):
            chosen.append(guess)
        if len(chosen) >= 6:
            break

    best: tuple[float, difflib.SequenceMatcher, int, float, bool] | None = None
    for guess in chosen:
        pad = min(300, max(100, L))
        win_start = max(0, guess - pad)
        win_end = min(len(stream), guess + L + pad)
        window = stream[win_start:win_end]
        matcher = difflib.SequenceMatcher(None, unit_norm, window, autojunk=False)
        blocks = matcher.get_matching_blocks()
        matched = sum(b.size for b in blocks)
        coverage = matched / L
        significant = [b for b in blocks if b.size >= 4]
        head_ok = bool(significant) and significant[0].a <= 0.25 * L
        tail_ok = bool(significant) and (significant[-1].a + significant[-1].size) >= 0.75 * L
        aligned_ok = head_ok and tail_ok
        score = coverage if aligned_ok else coverage * 0.5
        if best is None or score > best[0] + 1e-9:
            best = (score, matcher, win_start, coverage, aligned_ok)
        if coverage >= 0.99 and aligned_ok:
            break
    if best is None:
        info["note"] = "no candidate survived verification"
        return info

    _score, matcher, win_start, coverage, aligned_ok = best
    info["coverage"] = round(coverage, 4)
    info["aligned_ok"] = aligned_ok
    if coverage < min_coverage:
        info["note"] = f"coverage {coverage:.3f} below {min_coverage}"
        return info

    blocks = [b for b in matcher.get_matching_blocks() if b.size >= 6]
    if not blocks:
        info["note"] = "no significant matching block"
        return info
    first, last = blocks[0], blocks[-1]
    norm_lo = win_start + first.b
    norm_hi = win_start + last.b + last.size
    if norm_lo >= len(positions) or norm_hi - 1 >= len(positions):
        info["note"] = "alignment out of bounds"
        return info
    raw_lo = positions[norm_lo]
    raw_hi = positions[norm_hi - 1]
    adopted = _tidy_adopted(full[raw_lo:raw_hi + 1], vocab, docx_raw, docx_vocab)

    adopted_len = len(_norm_alnum(adopted))
    length_ratio = adopted_len / max(1, L)
    if not (0.3 <= length_ratio <= 3.0):
        info["note"] = f"adopted span length ratio {length_ratio:.2f} outside 0.3-3.0"
        return info

    # Preserve the unit's own heading line when the PDF span drops it
    # (e.g. the chapter number line was stripped as page furniture). A
    # damaged heading line is never preserved: the PDF span carries the
    # correct form.
    head_line = unit_text.split("\n", 1)[0].strip()
    if head_line and not _has_artifact(head_line):
        head_norm = _norm_alnum(head_line)
        if head_norm and _norm_alnum(adopted[:200]).find(head_norm) == -1:
            adopted = f"{head_line}\n{adopted}"

    info["status"] = "adopted"
    info["text"] = adopted
    return info


def _parse_source_spec(spec: str) -> dict:
    fields: dict[str, str] = {}
    for part in spec.split(";"):
        if not part.strip():
            continue
        if "=" not in part:
            raise ValueError(f"source spec part must be key=value: {part!r}")
        key, value = part.split("=", 1)
        fields[key.strip()] = value.strip()
    missing = {"title", "id", "docx", "pdf"} - set(fields)
    if missing:
        raise ValueError(f"source spec missing keys: {sorted(missing)}")
    return fields


def build_source(
    db_path: Path,
    fields: dict[str, str],
    *,
    min_coverage: float,
    adopt_coverage: float,
    pdftotext_path: str | None,
    dry_run: bool,
    max_chars: int,
    overlap: int,
) -> dict:
    docx_path = Path(fields["docx"])
    pdf_path = Path(fields["pdf"])
    for p in (docx_path, pdf_path):
        if not p.is_file():
            raise FileNotFoundError(f"source file does not exist: {p}")

    docx_hash = kb._sha256(docx_path)
    pdf_hash = kb._sha256(pdf_path)

    units = kb._docx_units(docx_path)

    # Some ebook conversions leave running heads (page number + book title)
    # inside the text. They match nothing in the PDF and pollute search, so
    # strip them from every unit before alignment.
    title_base = re.sub(r"\s*\([^)]*\)\s*$", "", fields["title"]).strip()
    headers_removed = 0
    if title_base:
        header_re = re.compile(
            rf"^[ \t]*\d{{1,4}}[ \t]+{re.escape(title_base)}[ \t]*\n?", re.M
        )
        cleaned: list[tuple[str, str]] = []
        for locator, text in units:
            text, n = header_re.subn("", text)
            headers_removed += n
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            cleaned.append((locator, text))
        units = cleaned

    pages, engine = kb.extract_pdf_pages(pdf_path, pdftotext_path)
    pages = [_clean_page_text(page) for page in pages]
    pages, furniture = _strip_page_furniture(pages)
    full = "\n".join(pages)
    stream, positions = _norm_map(full)
    vocab = _build_vocab(full, units)
    # The DOCX text is the *undamaged* copy of the same book (paragraph
    # based, with no line wraps): its whitespace-collapsed form is the
    # oracle that decides whether a PDF line break splits a word (it keeps
    # real word boundaries, which an alnum-only stream would fuse), and its
    # vocabulary filters out boundaries that end in a genuine word.
    docx_raw = re.sub(
        r"\s+", " ", "\n".join(text for _loc, text in units)
    ).lower()
    docx_vocab = _build_vocab("", units)

    records: list[dict] = []
    final_units: list[tuple[str, str]] = []
    artifacts_total = 0
    for locator, text in units:
        unit_norm = _norm_alnum(text)
        result = _align_unit(
            text, unit_norm, stream, positions, full, min_coverage, vocab,
            docx_raw, docx_vocab,
        )
        if result.get("artifact"):
            artifacts_total += 1
        record = {
            "locator": locator,
            "chars": len(text),
            "artifact": result.get("artifact"),
            "coverage": result.get("coverage"),
        }
        can_adopt = (
            result["status"] == "adopted"
            and result.get("aligned_ok")
            and (result.get("coverage") or 0) >= adopt_coverage
        )
        if can_adopt:
            # The PDF is the authoritative text: use it whenever a confident
            # counterpart exists. Artifact-bearing units are *repaired*; the
            # rest are *verified* against the original.
            record["status"] = (
                "repaired_from_pdf" if result.get("artifact") else "verified_from_pdf"
            )
            record["adopted_chars"] = len(result["text"])
            final_units.append((locator, result["text"]))
        else:
            record["status"] = "kept_docx"
            if result.get("note"):
                record["note"] = result["note"]
            elif result["status"] == "adopted":
                record["note"] = f"coverage {result.get('coverage'):.3f} < {adopt_coverage}"
            final_units.append((locator, text))
        records.append(record)

    curated_fixes = 0
    fixed_units: list[tuple[str, str]] = []
    for locator, text in final_units:
        for fix_loc, pattern, replacement in _CURATED_FIXES:
            if locator == fix_loc:
                text, n = pattern.subn(replacement, text)
                curated_fixes += n
        locator = _CURATED_LOCATOR_FIXES.get(locator, locator)
        fixed_units.append((locator, text))
    final_units = fixed_units

    from_pdf = sum(1 for r in records if r["status"] in ("repaired_from_pdf", "verified_from_pdf"))
    repaired = sum(1 for r in records if r["status"] == "repaired_from_pdf")
    verified = from_pdf - repaired
    unrepaired_artifacts = [
        r for r in records if r.get("artifact") and r["status"] != "repaired_from_pdf"
    ]
    coverages = [r["coverage"] for r in records if r.get("coverage") is not None]
    summary = {
        "title": fields["title"],
        "id": fields["id"],
        "docx_sha256": docx_hash,
        "pdf_sha256": pdf_hash,
        "pdf_pages": len(pages),
        "engine": engine,
        "units_total": len(records),
        "units_with_artifacts": artifacts_total,
        "units_repaired_from_pdf": repaired,
        "units_verified_from_pdf": verified,
        "units_kept_from_docx": len(records) - from_pdf,
        "unrepaired_artifact_units": len(unrepaired_artifacts),
        "headers_removed": headers_removed,
        "curated_fixes": curated_fixes,
        "min_coverage": min(coverages) if coverages else None,
        "mean_coverage": sum(coverages) / len(coverages) if coverages else None,
        "furniture_strings": furniture[:40],
        "min_coverage_threshold": min_coverage,
        "adopt_coverage_threshold": adopt_coverage,
        "records": records,
    }

    if not dry_run:
        metadata = {
            "text_authority": (
                f"PDF embedded text layer for {from_pdf} of {len(records)} units; "
                "remaining units kept from the DOCX"
                if from_pdf
                else "DOCX text (PDF-verified)"
            ),
            "structure_source": "DOCX WordprocessingML headings",
            "pdf_sha256": pdf_hash,
            "docx_sha256": docx_hash,
            "pdf_pages": len(pages),
            "extraction": engine,
            "units_total": len(records),
            "units_with_artifacts": artifacts_total,
            "units_repaired_from_pdf": repaired,
            "units_verified_from_pdf": verified,
            "headers_removed": headers_removed,
            "curated_fixes": curated_fixes,
            "alignment": {
                "min_coverage": summary["min_coverage"],
                "mean_coverage": round(summary["mean_coverage"] or 0.0, 4),
                "min_coverage_threshold": min_coverage,
                "adopt_coverage_threshold": adopt_coverage,
            },
            "furniture_strings": furniture[:40],
            "builder": "build_kb.py",
        }
        source_type = "docx+pdf" if from_pdf else "docx"
        primary_hash = pdf_hash if from_pdf else docx_hash
        kb.ingest_units(
            db_path,
            fields["title"],
            fields["id"],
            primary_hash,
            source_type,
            final_units,
            metadata,
            max_chars=max_chars,
            overlap=overlap,
        )
        summary["ingested"] = True
    return summary


# Curated character-level repairs for the single unit whose PDF counterpart is
# itself damaged: the SI prefix table (Appendix 3) fragments superscript
# exponents in the PDF text layer (most rows lose the "10" base entirely), so
# that unit is kept from the DOCX. The DOCX has two converter misreads there,
# "10G" where the mega row is 10^6 and "10−G" where the micro row is 10^-6 by
# definition; both are corrected in place. Documented in
# references/book-dataset-profile.md.
_CURATED_FIXES: list[tuple[str, "re.Pattern[str]", str]] = [
    ("No.PrefixAbbreviation", re.compile(r"10G(?=\s*\n\s*mega\b)"), "106"),
    ("No.PrefixAbbreviation", re.compile(r"10\u2212G(?=micro)"), "10\u22126"),
]

# The same converter misread also hit page numbers embedded in the table-of-
# contents locators of the HTW book. Each correction is verified against the
# PDF's own table of contents (chapter numbers 26/36, pages 263/269/277) and
# the chapter opening "Historical Perspectives" (the stray "G" is dropped).
_CURATED_LOCATOR_FIXES: dict[str, str] = {
    "2G How to Write for the Public 170": "26 How to Write for the Public 170",
    "3G How to Prepare a Curriculum Vitae, Cover Letter, and Personal Statement 237":
        "36 How to Prepare a Curriculum Vitae, Cover Letter, and Personal Statement 237",
    "How to Provide Peer Review 2G3": "How to Provide Peer Review 263",
    "How to Edit Your Own Work 2G9": "How to Edit Your Own Work 269",
    "How to Seek a Scientific-Communication Career 27G":
        "How to Seek a Scientific-Communication Career 277",
    "Historical Perspectives G": "Historical Perspectives",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rebuild a book knowledge base with PDF-verified text."
    )
    parser.add_argument("--db", required=True, type=Path, help="target SQLite database")
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help='semicolon-separated key=value spec: title=...;id=urn:...;docx=path;pdf=path',
    )
    parser.add_argument("--min-coverage", type=float, default=0.6,
                        help="below this, a unit is reported as unaligned")
    parser.add_argument("--adopt-coverage", type=float, default=0.9,
                        help="adopt the PDF text only when coverage and head/tail alignment meet this bar")
    parser.add_argument("--pdftotext-path", help="explicit pdftotext executable")
    parser.add_argument("--max-chars", type=int, default=1800)
    parser.add_argument("--overlap", type=int, default=180)
    parser.add_argument("--report", type=Path, help="write the full alignment report here")
    parser.add_argument("--dry-run", action="store_true", help="align and report without writing the database")
    return parser


def main(argv: list[str] | None = None) -> int:
    kb._configure_utf8_stdio()
    args = _build_parser().parse_args(argv)
    if not (0.0 < args.min_coverage <= 1.0):
        print("error: --min-coverage must be in (0, 1]", file=sys.stderr)
        return 2
    if not (0.0 < args.adopt_coverage <= 1.0):
        print("error: --adopt-coverage must be in (0, 1]", file=sys.stderr)
        return 2
    full_summaries = []
    for spec in args.source:
        try:
            fields = _parse_source_spec(spec)
            summary = build_source(
                args.db,
                fields,
                min_coverage=args.min_coverage,
                adopt_coverage=args.adopt_coverage,
                pdftotext_path=args.pdftotext_path,
                dry_run=args.dry_run,
                max_chars=args.max_chars,
                overlap=args.overlap,
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        full_summaries.append(summary)
        flagged = [
            r for r in summary["records"]
            if r["status"] == "kept_docx"
            and r.get("artifact")
        ]
        low_coverage = [
            r for r in summary["records"]
            if r.get("coverage") is not None and r["coverage"] < 0.8
            and not r.get("artifact")
        ]
        print(f"[{summary['title']}] units={summary['units_total']} "
              f"artifacts={summary['units_with_artifacts']} "
              f"repaired={summary['units_repaired_from_pdf']} "
              f"verified={summary['units_verified_from_pdf']} "
              f"kept_docx={summary['units_kept_from_docx']} "
              f"unrepaired_artifacts={summary['unrepaired_artifact_units']} "
              f"headers_removed={summary['headers_removed']} "
              f"min_cov={summary['min_coverage']} mean_cov={round(summary['mean_coverage'] or 0, 4)}")
        for r in flagged[:40]:
            print(f"   UNREPAIRED artifact: {r['locator'][:60]} "
                  f"cov={r.get('coverage')} {r.get('note', '')}")
        for r in low_coverage[:20]:
            print(f"   low-coverage kept: {r['locator'][:60]} cov={r.get('coverage')}")
    if args.report:
        with args.report.open("w", encoding="utf-8") as stream:
            json.dump(full_summaries, stream, ensure_ascii=False, indent=2)
        print(f"report written: {args.report}")
    compact = [{k: v for k, v in s.items() if k != "records"} for s in full_summaries]
    print(json.dumps({"sources": compact}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
