# Chicago citation: choosing and applying a system

Use this when the target venue, discipline, or advisor prescribes Chicago style (or "Turabian" style). The bundled Turabian dataset (Book 2, `--source "A Manual for Writers"`) holds the full examples for every source type; this file fixes the decisions and the basic patterns.

## Step 1 — choose the system

- **Notes-bibliography** (footnote/endnote + bibliography): common in humanities and some social sciences.
- **Parenthetical citations–reference list** (author-date): common in most social sciences and in the natural and physical sciences that use Chicago.

Determine the required system from the venue, department guide, or advisor; if unspecified, default to the discipline norm. Never mix the two systems in one document.

## Step 2 — keep the basic patterns

Notes-bibliography:

- First footnote, book: Author's First Name Middle Name, *Title of book*, page (City: Publisher, Year).
- Short form afterward: Author's Last Name, page.
- Bibliography entry, book: Author's Last Name, Author's First Name. Year. *Title: Subtitle*. City: Publisher.
- First footnote, journal article: Author's First Name, "Article Title," *Journal* volume, no. (Year): page.
- Bibliography entry, article: Author's Last Name, Author's First Name. Year. "Article Title." *Journal* volume, no.: pages.

Parenthetical (author-date):

- In text: (Last Name Year) or (Last Name Year, page).
- Reference list, book: Author's Last Name, Author's First Name. Year. *Title of book: Subtitle*. City: Publisher.
- Reference list, journal article: Author's Last Name, Author's First Name. Year. "Article Title." *Journal* volume, no.: pages.

Element order for every reference-list entry: author, date, title, then other facts of publication. In reference lists, separate most elements with periods; in parenthetical citations, no punctuation between author and date, comma before a page number. Capitalize most titles in sentence style; capitalize journal/magazine/newspaper names in headline style.

## Step 3 — follow the citation rules

- Give the full citation on first use; use the short form (or bare parenthetical) on later references to the same work.
- Cite the source you actually consulted; when one source is quoted through another, cite the original and say "quoted in" only when the original is inaccessible.
- Electronic sources need URL and access date where the venue requires it; verify the current electronic-citation rules before relying on the 2007 examples, because web publishing practices have changed substantially since.
- Keep citation form, spelling, and punctuation identical for the same source everywhere (notes, bibliography, reference list, in-text).
- For each cited source, verify the metadata (authors, title, venue, year, volume/pages, DOI) against the original record, as in the general citation-integrity rules; the book supplies form, not verification.

## What to query for

- Any unusual source type (datasets, software, public documents, theses, unpublished works, social media, visual/performing arts): `query "books journal articles public documents" --source "A Manual for Writers" --limit 8` or the specific type name.
- Short forms, one-source-quoted-in-another, citation software cautions: `query "short forms notes bibliography" --source "A Manual for Writers"`.
- Reference-list ordering and formatting: `query "reference lists capitalization" --source "A Manual for Writers"`.
