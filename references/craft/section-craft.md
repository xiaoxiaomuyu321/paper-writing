# Section craft — distilled from the books

How to actually write each section of a journal paper, condensed from Gastel & Day 8e (2016),
with Turabian 7e (2003) where it adds. Each rule carries **book anchors** (KB locator); query
`scripts/paper_kb.py query "<keywords>" --source "How to Write and Publish"` for original passages
and worked examples. Anchors: HTW = Gastel & Day 8e · Tur = Turabian 7e.

## Cross-section principles

- **Organization beats literary skill.** "A scientific paper is not literature" — preparation has
  less to do with literary skill than with organization; spend revision effort on structure
  (section roles, paragraph logic, data placement) before polishing sentences.
  *(HTW — ORGANIZATION OF A SCIENTIFIC PAPER)*
- **The hourglass shape:** broad → narrow → broad. "In the introduction, you invited readers
  into your research venue; in the discussion, you usher them out" — the introduction funnels
  in, the discussion (inverted funnel) runs back out. Use it as a coherence check for the front
  and back ends of the paper. *(HTW — SHAPE OF A SCIENTIFIC PAPER; COMPONENTS OF THE
  DISCUSSION)*
- **IMRaD as four questions** — draft answers first, sections second: "What question (problem)
  was studied? The answer is the introduction. How was the problem studied? The methods. What
  were the findings? The results. What do these findings mean? The discussion."
  *(HTW — THE IMRAD STORY)*
- **One-presentation rule for data:** "Present the data in the text, or in a table, or in a
  figure. Never present the same data in more than one way." Keep a data ledger: every number/
  curve has exactly one home. *(HTW — WHEN TO USE TABLES)*
- **Sections are a pair system:** the introduction poses the questions, the discussion answers
  them; Methods subheadings mirror Results subheadings; **conclusions are stated three times —
  in the abstract, the introduction, and the discussion** — deliberately, as a signal of
  importance; draft the conclusion once and reuse it compressed at each spot.
  *(HTW — COMPONENTS OF THE DISCUSSION; HEADINGS; DEFINITION)*
- **No suspense anywhere in the front matter:** "Do not keep the reader in suspense… We want to
  know from the start that the butler did it." The first paragraphs decide whether readers read,
  skim, or skip. *(HTW — REASONS FOR THE GUIDELINES; IMPORTANCE OF INTRODUCTORY PARAGRAPHS)*
- **Match the target journal's living style:** before drafting, pull 3–5 comparable recent papers
  from the target journal and note how they handle each contested choice (subheadings, tense,
  figure placement, supplement practice); instructions state rules, recent issues reveal the
  style. *(HTW — HEADINGS; USING INSTRUCTIONS TO AUTHORS)*
- **Write for the reviewer, in past/present per the epistemic tense rules** (see
  `language-craft.md` §3): Methods and Results past; statistical statements and presentation
  ("Table 4 shows…") present. *(HTW — TENSE IN SCIENTIFIC WRITING)*
- **Start writing while the work is in progress** — everything is fresh, and the writing itself
  exposes inconsistencies in the results; with coauthors, write while they are still available to
  consult. Keep drafting momentum by marking unknowns in boldface/comments instead of stopping
  to look them up. *(HTW — DOING THE WRITING)*

## Title

- **A good title is "the fewest possible words that adequately describe the contents of the
  paper."** It "will be read by thousands of people" (journal, databases, search engines) while
  few read the whole paper, and "an improperly titled paper may be virtually lost and never
  reach its intended audience." *(HTW — IMPORTANCE OF THE TITLE)*
- **A title is a label, not a sentence** — "normally is not a sentence," so "the order of the
  words becomes even more important." Most title grammar errors are faulty word order — read it
  aloud and check what each modifier attaches to ("Mechanism of Suppression of Nontransmissible
  Pneumonia Induced in Mice by Newcastle Disease Virus," not the version where the mice were
  induced). Watch the dangling participle "using" — "the most common dangling participle in
  scientific writing" ("…from Monkeys Using Complement-Fixation Techniques").
  *(HTW — THE TITLE AS A LABEL; IMPORTANCE OF SYNTAX)*
- **Specific, not general:** "Action of Antibiotics on Bacteria" is a good title in form but
  essentially meaningless — name the actual agents/organisms (genus, species, strain if needed);
  define vague relationship words: "Action of Streptomycin on M. tuberculosis" → "Inhibition of
  Growth of M. tuberculosis by Streptomycin." Check that each word has the form its meaning
  requires ("for Biologists" vs "for Biology"). *(HTW — NEED FOR SPECIFIC TITLES; MORE ABOUT
  TITLE FORMAT)*
- **Clarity over wit:** "need not, and generally should not, be clever. It must, however, be
  clear" — the book's example keeps "Association between Diuretic Use and Cardiovascular
  Mortality" and rejects "Dying to Pee." Default away from **assertive sentence titles**
  (present-tense conclusion titles): they are "improper and imprudent," "boldly state a
  conclusion that is then stated more tentatively," and "trivialize a scientific report by
  reducing it to a one-liner" — only when the journal allows them and you've weighed the risk.
  *(HTW — IMPORTANCE OF THE TITLE; THE TITLE AS A LABEL)*
- **The index test (searchability):** "How would I look for this kind of information in an
  index?" — "hydrochloric acid," not "HCl"; no abbreviations, chemical formulas, proprietary
  names, or jargon in titles; the title terms "should be those that highlight the significant
  content of the paper" for machine indexing (MEDLINE, Chemical Abstracts).
  *(HTW — ABBREVIATIONS AND JARGON; THE TITLE AS A LABEL)*
- **Length: delete waste, keep enough.** Too short fails to say what kind of study
  ("Studies on Brucella" — taxonomic, genetic, or medical?); much more often titles are too long
  and "often less meaningful than short ones" ("that certainly sounds like a poor title;
  perhaps it would make a good abstract"). First edit pass: cut "Studies on / Investigations on
  / Observations on" openers and a leading A/An/The — "useless for indexing purposes."
  *(HTW — LENGTH OF THE TITLE)*
- **Prohibited forms:** numbered series titles ("…Studies on Bacteria. IV. Cell Wall of…") —
  each paper must "present the results of an independent, cohesive study" (redundancy,
  scheduling problems, unintelligible indexes); question-phrased titles ("probably should not be
  used"); hanging (general: specific) titles only when the front term genuinely helps and the
  journal favors the form. Suggest a compliant running title on the title page.
  *(HTW — MORE ABOUT TITLE FORMAT; THE TITLE AS A LABEL)*
- **Write it last, but plan it first:** keep a provisional title from day one (with the outline
  and audience baseline), then finalize after the argument's center of gravity is settled.
  *(HTW — GUIDELINES; Tur — Write Your Title Last)*

## Abstract

- **The abstract is a miniature of the paper** — "a miniature version of the paper," summarizing
  each main part in the same order (introduction → methods → results → discussion). Its job: let
  a reader who hasn't seen the paper "quickly and accurately identify the basic content… and
  decide whether they need to read the document in its entirety."
  *(HTW — DEFINITION)*
- **Four required elements** — use as a drafting checklist: (1) principal objectives and scope,
  (2) methods employed, (3) results summarized, (4) principal conclusions stated.
  *(HTW — DEFINITION)*
- **Two types, different jobs:** the **informative** abstract (the standard for primary-journal
  research papers) is "designed to condense the paper" and can "supplant the need to read the
  full paper"; the **indicative** (descriptive) abstract "indicate[s] the subjects dealt with in
  a paper, much like a table of contents" — reserve it for reviews, conference reports, and
  government reports, and **not** as a heading abstract for research papers.
  *(HTW — TYPES OF ABSTRACTS)*
- **Shape of a good informative abstract** (the book's worked Figure 9.1, ~250 words): purpose
  sentence → gap → design/methods → key data → "These findings suggest that…" implication — "the
  order of information parallels that in a typical scientific paper." The model of maximal
  condensation: Berry et al.'s "Probably not." abstract — "this one answers the question that
  the research addressed." Check that yours does the same, in the plainest words.
  *(HTW — Effects of Scientific-Writing Training…; ECONOMY OF WORDS)*
- **Hard rules:** never exceed the journal's limit (commonly 250 words) — single paragraph
  unless the journal requires a structured one (Background/Objective/Methods/Results/Conclusion);
  **past tense** ("it refers to work done"); **self-contained** — "it will be published by
  itself": no bibliographic, figure, or table references; **no literature citations** (rare
  exception: modification of a previously published method); no obscure abbreviations —
  "unless a long term is used several times within an abstract, do not abbreviate the term";
  **never any information or conclusion not stated in the paper.**
  *(HTW — DEFINITION; TYPES OF ABSTRACTS; TENSE IN SCIENTIFIC WRITING)*
- **Economy is a science:** the most common fault is "the inclusion of extraneous detail";
  "If you can tell your story in 100 words, do not use 200" — examine every word, delete the
  rest. "The use of clear, significant words will impress the editors and reviewers… abstruse,
  verbose constructions might well contribute to a check in the 'reject' box."
  *(HTW — ECONOMY OF WORDS)*
- **It is read first:** the abstract is almost always the first part of the manuscript read in
  review — "If you cannot make a good impression in your abstract, your cause may be lost"; "a
  poor abstract is a harbinger of woes to come." *(HTW — ECONOMY OF WORDS)*
- **Write the paper before the abstract** "if at all possible" — it is a late-stage
  condensation of the finished paper. Then run the consistency audit: "Is the content of the
  abstract consistent with that of the body of the piece? Is the terminology consistent
  throughout?" *(HTW — TYPES OF ABSTRACTS; ITEMS TO NOTICE: 8 Cs)*
- **Abstract ≠ summary:** a journal abstract "usually summariz[es] each major section of the
  paper"; a summary "is usually a summary of conclusions." Don't write a conclusions-only block
  where a section-by-section abstract is expected. *(HTW — Glossary)*
- **Anticipate the add-ons:** some journals ask for key messages, a nontechnical summary, or an
  implications statement — "you may be asked to provide, in essence, an abstract of your
  abstract." Meeting abstracts gate participation — "participation sometimes being determined on
  the basis of submitted abstracts" — give them the same discipline. *(HTW — AKIN TO ABSTRACTS;
  ECONOMY OF WORDS)*
- **Front-matter self-audit (run before submission):** Does the title accurately and concisely
  indicate the content? Does the abstract accurately reflect the paper's content, at a suitable
  length? Does the introduction provide sufficient context, make clear the gap the research was
  intended to fill, and indicate the hypotheses or research questions? (And later: does the
  discussion answer the hypotheses "posed in the introduction"?)
  *(HTW — Specialized Checklist)*

## Keywords

The 8th edition has **no dedicated keywords/index-terms section** — the book treats the title as
the retrieval handle (index test, machine-indexing suitability, no abbreviations). When a
journal asks for index terms, apply the same searcher's-eye test: the terms a reader would
actually search for, spelled out, in the field's controlled vocabulary where the field
provides one. *(HTW — ABBREVIATIONS AND JARGON; THE TITLE AS A LABEL)*

## Introduction

- **Three jobs:** orient (sufficient background to understand and evaluate the results
  "without needing to refer to previous publications"), justify (the rationale for the study),
  and declare — "Above all, you should state briefly and clearly your purpose in writing the
  paper." *(HTW — GUIDELINES)*
- **The five-beat structure** (one idea per beat, in order): (1) the nature and scope of the
  problem, with all possible clarity, including why the subject area is important; (2) a
  **brief and selective** literature review that orients the reader and **identifies the gap**
  the research addresses; (3) the objective — "hypotheses or research questions" in many
  disciplines, or wording such as "in order to determine"; (4) the method of the investigation
  (and, if necessary, why that method); (5) in some disciplines/journals, the principal results
  and conclusions. *(HTW — GUIDELINES; EXCEPTIONS)*
- **Funnel shape:** "moving from broad and general to narrow and specific" so the introduction
  "comfortably funnel[s] readers into reading about the details of your research." Mark the
  narrowing with transitional words (also/first/then/however) where a real relation exists.
  *(HTW — GUIDELINES; ITEMS TO NOTICE: 8 Cs)*
- **The cardinal rule is the problem definition:** "If the problem is not stated in a reasonable,
  understandable way, readers will have no interest in your solution." Put in a **hook** —
  "Why did you choose that subject, and why is it important?" — like journalism.
  *(HTW — REASONS FOR THE GUIDELINES)*
- **No suspense:** front-load the payoff — state what the work found or aims to find; beginning
  authors "make the mistake of holding back their more important findings until late in the
  paper." The introduction "provides a road map from problem to solution" — "a bit of
  redundancy with the abstract is often desirable." *(HTW — REASONS FOR THE GUIDELINES)*
- **Tense:** "Much of the introduction should be written in present tense because you are
  referring primarily to your problem and the established knowledge relating to it at the start
  of your work" (past for your own completed work). Model sentences: "Streptomycin is an
  antibiotic produced by Streptomyces griseus (13)… The effect of streptomycin on S. everycolor
  is reported in this paper." *(HTW — GUIDELINES; TENSE IN SCIENTIFIC WRITING)*
- **Citation discipline:** "Choose references carefully to provide the most important background
  information" — orient, don't show off. Cite a previously published preliminary note/abstract
  of the work with its citation; mention closely related or forthcoming papers, "customarily at
  or near the end," to keep the literature tidy. *(HTW — CITATIONS AND ABBREVIATIONS)*
- **Define specialized terms and abbreviations here** — the paper may be read by people outside
  your narrow specialty (the book's exhibit: a law judge who called a lawyer a "gonococcus"
  because in law GC means general counsel). *(HTW — CITATIONS AND ABBREVIATIONS)*
- **Field and journal conventions take precedence:** some disciplines favor an extensive
  literature review (even a separate related-work section — ILMRaD); check the journal's
  instructions and the introductions of analogous recent papers before finalizing.
  *(HTW — EXCEPTIONS)*
- **Plan before writing:** provisional title + outline + the audience's baseline knowledge
  (which terms need definition) — otherwise "you might go writing off in six directions at
  once." *(HTW — GUIDELINES)*
- **Worked shape (the book's Figure 10.1, ~300 words, three paragraphs):** (1) broad context
  with a striking statistic; (2) narrowing to the exact gap, including a contrasting study
  ("relatively little information exists regarding…"); (3) "To help address these gaps, we
  compared outcomes in…" + design + outcome measures. Model the paragraph roles, not the words.
  *(HTW — Introduction to an Imacinary Paper)*

## Methods

- **The governing test is replicability:** "Enough information must be given so that the
  experiments could be reproduced by a competent colleague." Write for the reviewer who will
  judge validity, not the reader who will skip the section. Open with the design (describe — and
  if necessary defend — it), then procedural detail. *(HTW — PURPOSE OF THE SECTION; CORRECT
  FORM AND GRAMMAR)*
- **Group related methods over strict chronology** — an assay goes with other assays even if
  performed later; organize by procedure family, not calendar. *(HTW — METHODS)*
- **No results in Methods.** Sweep for sentences reporting outcomes ("the temperature was chosen
  because it worked") and move them to Results or delete. *(HTW — CORRECT FORM AND GRAMMAR)*
- **Passive voice is legitimate in Methods** — "although what was done must be specified, who did
  it is often irrelevant"; keep first person for judgments and choices. *(HTW — CORRECT FORM AND
  GRAMMAR)*
- **Colleague replication test:** hand the finished manuscript to someone not involved and ask
  whether they can follow the methodology; every point where they must guess is an omission
  (distillation temperature, undefined starting material). *(HTW — CORRECT FORM AND GRAMMAR)*
- **Cookbook precision:** answer every "how" and "how much" — "If a reaction mixture was heated,
  give the temperature." Audit each step for a missing temperature, time, concentration, or
  condition. *(HTW — MEASUREMENTS AND ANALYSIS)*
- **Cite established methods, re-describe novel ones.** Familiarity tiers: new/unpublished → all
  detail; published → reference; well-known → reference only; unfamiliar or hard-to-access →
  few words + reference; when alternatives exist, name your method briefly and cite it
  ("cells were broken by ultrasonic treatment as previously described (9)").
  *(HTW — NEED FOR REFERENCES)*
- **Materials: exact specifications, quantities, sources** (city/country or preparation method);
  organisms by genus/species/strain with source and relevant characteristics. Prefer generic
  names; use a trade name (capitalized, ®/™ usually omitted) only when product identity affects
  results. Human subjects: selection criteria + informed-consent statement; human/animal work:
  committee approval. *(HTW — MATERIALS)*
- **Statistics: emphasize the data, not the statistics.** "Ordinary statistical methods
  generally should be used without comment; advanced or unusual methods may require a literature
  citation." Don't justify a t-test; name software at the end of Methods only where field custom
  requires. *(HTW — MEASUREMENTS AND ANALYSIS)*
- **Grammar matters extra in Methods** — exact and specific items, "precise use of English is a
  must": reread for dangling modifiers, missing commas, ambiguous referents (the "Employing a
  straight platinum wire rabbit, sheep and human blood agar plates were inoculated" pattern).
  *(HTW — CORRECT FORM AND GRAMMAR)*
- **Relocate one-off methods:** a protocol used in only one experiment can move to Results, or
  (if the journal allows) into a table footnote or figure legend; keep strain/reagent tables for
  multi-strain work; flow charts and apparatus diagrams are legitimate vehicles.
  *(HTW — TABLES AND FIGURES)*
- **Draft Methods while memory is fresh** — keep a running methods file; write protocol
  paragraphs right after each procedure, integrate later. *(HTW — WHEN TO WRITE THE THESIS)*

## Results

- **Two ingredients:** (1) an overall description of the experiments — the big picture without
  repeating method detail — then (2) the data, in past tense. Do NOT open by describing methods
  you forgot to include in Materials & Methods; go back and fix Methods.
  *(HTW — CONTENT OF THE RESULTS)*
- **Select, don't collect.** "The fool collects facts; the wise man selects them." Present
  representative data, not "endlessly repetitive data"; state replication ("in three independent
  experiments") instead of printing every replicate; for each datum ask "does this change what
  the reader concludes?" — if not, cut or supplement it. *(HTW — CONTENT OF THE RESULTS)*
- **Short and sweet, crystal clear** — Results is often the shortest section though the most
  important: the earlier sections explain why/how, the discussion explains meaning, so the
  results "must be presented with crystal clarity." *(HTW — STRIVE FOR CLARITY; CONTENT OF THE
  RESULTS)*
- **Few numbers in prose, systematic data in tables/graphs:** one or a few determinations are
  stated descriptively in text; anything repeated or tabular goes to a table/graph; variables
  that don't affect the reaction need not be tabulated. *(HTW — HOW TO HANDLE NUMBERS)*
- **State the negative results** — "It is often good insurance to state what you did not find
  under the conditions of your experiments" ("No effect of X was observed under these
  conditions"), rather than silent omission. *(HTW — HOW TO HANDLE NUMBERS)*
- **Don't restate figures and tables in prose** — the most common Results fault is repeating in
  words what the figure already shows; "even worse is the actual presentation, in the text, of
  all or many of the data shown in the tables or figures." For each sentence, check whether the
  cited visual carries it; if so, keep only the finding. *(HTW — AVOID REDUNDANCY)*
- **Cite visuals parenthetically, findings first:** not "It is clearly shown in Table 1 that
  X" but "X (Table 1)" — briefer, more readable, attention on the finding.
  *(HTW — AVOID REDUNDANCY)*
- **Only significant figures** — nonsignificant figures "create a false sense of precision" and
  hinder comparison; omit bookkeeping data (lab numbers, simple calculations, no-variation
  columns). *(HTW — WHEN TO USE TABLES)*
- **Kill low-information tables:** a table full of zeros, 100s, or plus/minus signs; "whenever a
  table (or columns) can be readily put into words, do it"; a word-list table "has no place in a
  paper — a copy editor will kill it." *(HTW — WHEN TO USE TABLES)*
- **Meaningful statistics only** — the cautionary tale: "33 1/3% of the mice… were cured; 33 1/3%
  remained moribund; the third mouse got away." With tiny n, report raw counts directly.
  Model comparison sentence: "The difference between the failure rates — 14 percent (5 of 35)
  for nocillin and 26 percent (9 of 34) for potassium penicillin V — was not significant
  (P = 0.21)": finding + raw counts + verdict + exact p, one sentence, non-significance stated
  plainly. *(HTW — HOW TO HANDLE NUMBERS; WHEN TO USE TABLES)*
- **Worked target shape** (the book's model paragraph): condition tested → effect with table
  reference → the single most important quantitative fact in plain prose: "Growth of S.
  everycolor was inhibited by streptomycin at all concentrations tested (Table 2) and at all pH
  levels (Table 3). Maximum inhibition occurred at pH 8.2." *(HTW — TENSE IN SCIENTIFIC
  WRITING)*
- **Logical order, appropriate detail, appropriate statistics** — the self-edit triad; sequence
  Results to mirror the question sequence and Methods subheadings. Keep pronoun antecedents
  explicit (especially "it"). *(HTW — Specialized Checklist; AVOID REDUNDANCY)*
- **Route extras to supplementary material** — most commonly additional results data, tables,
  figures; check the journal's rules and analogous papers before inflating the section.
  *(HTW — A SUPPLEMENT ON SUPPLEMENTARY MATERIAL ONLINE)*
- **Other people's results do not belong in your Results** — present them, with citations, in
  the Discussion when they confirm or contrast with yours. *(HTW — TIPS ON WRITING)*

## Discussion

- **The section that sinks papers:** "many papers are rejected by journal editors because of a
  faulty discussion, even though the data of the paper might be both valid and interesting" —
  and a muddled interpretation can obscure the data's true meaning, also a rejection. Budget
  real time for it. *(HTW — DISCUSSION AND VERBIAGE)*
- **Discuss, do not recapitulate:** "in a good discussion, you discuss — you do not
  recapitulate — the results." Delete or compress every sentence that restates a result without
  adding interpretation, comparison, or meaning. *(HTW — COMPONENTS OF THE DISCUSSION)*
- **Inverted-funnel structure:** where the introduction funnels general → specific, the
  discussion runs back out: first restate the main findings → relate them to previous research
  → note implications and applications → identify unanswered questions suited to future
  research. *(HTW — COMPONENTS OF THE DISCUSSION)*
- **Answer what the introduction asked** — list the introduction's questions before drafting;
  give each an explicit answer; failure to address the initial questions "commonly afflicts
  discussions." *(HTW — COMPONENTS OF THE DISCUSSION)*
- **The seven components:** present the principles, relationships, and generalizations shown by
  the results · point out exceptions and lack of correlation, define unsettled points · relate to
  previously published work (agree or contrast — when contrasting, state what differs:
  conditions, system, measure) · theoretical implications · practical applications · conclusions
  stated as clearly as possible, each with its evidence summarized · strengths and limitations
  disclosed. *(HTW — COMPONENTS OF THE DISCUSSION; NOTING STRENGTHS AND LIMITATIONS)*
- **Never fudge data that don't fit** — "Never take the high-risk alternative of trying to cover
  up or fudge data that do not quite fit"; one sentence naming the outlier ("X did not affect Y,
  which remains unexplained") beats quiet omission. *(HTW — COMPONENTS OF THE DISCUSSION)*
- **Purpose = relationships among observed facts** (the flea whose legs were removed one by one
  until it "could no longer hear"): every interpretive claim traces to an observed relationship
  in your data or a cited comparison, not to a general story. *(HTW — FACTUAL RELATIONSHIPS)*
- **No squid technique:** when the author is doubtful about facts or reasoning, they "retreat
  behind a protective cloud of ink" — cut the hedging fog. Avoid "It was found in the present
  investigation that…"; "If you mean 'I found that…' or 'We conclude that…,' say so." First
  person is the cure for many long, hard-to-follow discussions. *(HTW — DISCUSSION AND VERBIAGE)*
- **Don't be shy about implications** — "discuss the theoretical implications of your work, as
  well as any possible practical applications." *(HTW — COMPONENTS OF THE DISCUSSION)*
- **Name substantial strengths** (superior technique, large sample, long follow-up) — it helps
  readers judge definitiveness and shows editors/referees the work is publishable;
  **self-disclose limitations** and their likely impact on the conclusions — hiding them runs
  counter to science's openness, and astute reviewers will find them anyway.
  *(HTW — NOTING STRENGTHS AND LIMITATIONS)*
- **Bounded claims, simple words:** "the best you can do is shine a spotlight on one area of the
  truth" — extrapolating beyond the data "may appear foolish" and casts doubt on the
  data-supported conclusions too. "The simplest statements evoke the most wisdom; verbose
  language and fancy technical words are used to convey shallow thought."
  *(HTW — DEFINING SCIENTIFIC TRUTH)*
- **End with the significance, with a fitting climax:** the discussion should end with a short
  summary regarding the significance of the work (the reader must not finish asking "So what?");
  "good writing, like good music, has a fitting climax — many a paper… ends in a swampy delta."
  Make the last sentence a confident, complete statement of significance; never end mid-hedge,
  on a list, or on a trailing qualification. *(HTW — SIGNIFICANCE OF THE PAPER)*
- **Turing's warrant discipline in interpretation:** connect each reason to the conclusion with
  an explicit general principle, and support with evidence, not logic alone.
  *(Tur — Establish the Relevance of Your Reasons)*

## Conclusion (where the book locates it)

Book 1 has no dedicated conclusion chapter — the conclusion lives at the end of the Discussion:

- **Default to a strong closing inside the Discussion**; add a separate "Conclusion" section only
  if the journal's format calls for one. *(HTW — SIGNIFICANCE OF THE PAPER)*
- **A standalone conclusion carries no new data** — only restatement of the main conclusions,
  their significance, and implications/next steps. *(HTW — DEFINING SCIENTIFIC TRUTH;
  COMPONENTS OF THE DISCUSSION)*
- **Keep the three statements of conclusion consistent** (abstract, introduction, discussion) —
  draft the conclusion sentence once, reuse it with tightening, check together at the end.
  *(HTW — DEFINITION)*
- A journal "Summary" block is conclusions-only: no methods recap, no results enumeration.
  *(HTW — Glossary)*

## References and acknowledgments

- **List only significant published references** — prune "citation wallpaper" and habit
  citations; keep unpublished material (personal communications, abstracts, theses) out of the
  numbered list — parenthetical in text or footnote; accepted-but-unpublished → "in press /
  forthcoming." *(HTW — RULES TO FOLLOW)*
- **Verify every reference against the original** — "There are far more mistakes in the
  references section of a paper than anywhere else"; check before submission and again at
  proofs. Cross-check both directions: every text citation is listed, and every listed reference
  is cited. *(HTW — RULES TO FOLLOW)*
- **Citation accuracy is a credibility asset:** reviewers are often the people you cite —
  inaccuracies or misrepresentations make them question whether you are a careful researcher.
  Reread the cited passage before citing; confirm it says what you attribute.
  *(HTW — ONE MORE REASON TO CITE CAREFULLY)*
- **Place each citation where it applies** — attach the marker to the specific clause it
  supports; when one sentence draws on multiple sources, recast so each claim carries its own
  marker. No "handwaving references": "If a reference is worth citing, the reader should be
  told why" — pair every citation with a clause stating what the work contributes.
  *(HTW — CITATIONS IN THE TEXT)*
- **Describe gaps neutrally:** "Smith (2015) did not study…" is fine; "totally overlooked,"
  "ignored," "failed to" are not. *(HTW — CITATIONS IN THE TEXT)*
- **System mechanics:** name-and-year — names always for 1–2 authors; 3 authors listed in full
  once, then "first et al."; same-year works get 2015a/2015b. Numbered systems — feature the
  author or date *inside the sentence* when it matters ("was discovered by Heymans (13)"),
  keep the number as anchor. Journal-title abbreviations follow ANSI rules ("ology" words
  abbreviate at the l; one-word titles never abbreviated). Maintain a full reference database
  (titles, pages) even when the journal uses a short form — "It is easy to edit out
  information; it is indeed laborious to track down 20 or so references." Add late references as
  suffixed numbers (16a) rather than renumbering. *(HTW — Name and Year System; Alphabet-Number
  System; JOURNAL ABBREVIATIONS; REFERENCE STYLES; ADDITION OF REFERENCES)*
- **Citation software doesn't remove the checking duty** — "Electronic gremlins sometimes
  lurk"; if you entered a wrong reference, the wrong reference appears. Verify every rendered
  entry. *(HTW — ELECTRONIC AIDS TO CITATION; Tur — A Word on Citation Software)*
- **Acknowledgments:** significant technical help (assistance, discussion, equipment, reagents —
  list by contribution) + outside financial assistance (funder, grant number per requirements).
  Get each person's permission and show them the proposed wording first — an inappropriate
  thankyou "can be worse than none at all"; be very specific about any non-author's idea or
  interpretation (a broad thanks can imply endorsement they must then defend); "I thank John
  Jones" — the word "wish" implies the thanks is withheld.
  *(HTW — INGREDIENTS OF THE ACKNOWLEDGMENTS; BEING COURTEOUS)*

## Figures, tables, and statistical language

- **Vehicle decision:** trends/shapes → graph; exact values or "numbers that sit there with no
  exciting trend" → table; sparse data or a single meaningful value → one sentence
  ("Maximum yield was obtained at pH 8.1."). Try stating the result in one sentence first; if
  the sentence carries everything, cut the figure. "Attempts to dress up scientific data are
  usually doomed to failure." The book's A/B test: the same tuberculosis data as Table 17.1 vs
  Fig. 17.2 — in the figure "the synergistic action of the two-drug combination is immediately
  apparent." *(HTW — WHEN TO USE GRAPHS; WHEN NOT TO USE GRAPHS; WHEN TO USE TABLES)*
- **Titles/legends like paper titles:** concise, one clause, not split into sentences;
  "Effect of streptomycin, isoniazid, and streptomycin plus isoniazid on Mycobacterium
  tuberculosis." Legends normally on a separate page (journal production splits them); check
  the journal's current placement rule. *(HTW — TITLES, FOOTNOTES, AND ABBREVIATIONS; SYMBOLS
  AND LEGENDS)*
- **Self-contained visuals:** design graphs and tables to be understandable without the text —
  meaningful group designations, not "Group 1/Group 2" (use "High-Dose Group," "REM Sleep
  Group"); test each on a colleague who hasn't read the paper. Mention every visual in the text
  as soon as the reader needs it, in numerical order. *(HTW — A FEW MORE TIPS ON GRAPHS;
  ADDITIONAL TIPS ON TABLES; FOLLOWING THE JOURNAL'S INSTRUCTIONS)*
- **Abbreviations in tables:** journals permit shorthand in tables that wouldn't be allowed in
  text; define them once (front-load in Table 1; later tables: "Abbreviations as in Table
  1"); capitalize when opening a column heading; no periods (except "no."). Avoid exponents in
  table headings — journals use positive and negative exponents to mean the same thing; state
  the convention in words in a footnote. *(HTW — TITLES, FOOTNOTES, AND ABBREVIATIONS;
  EXPONENTS IN TABLE HEADINGS)*
- **Consistent format across a series:** analogous tables list the same groups/variables in the
  same order in each; lock one canonical order and reuse it verbatim. Three horizontal rules, no
  vertical rules (booktabs-style), unless the journal's examples differ. Footnotes supplement
  (data provenance, coding, derivation) — they don't restate methods.
  *(HTW — ADDITIONAL TIPS ON TABLES; HOW TO ARRANGE TABULAR MATERIAL)*
- **Honesty in figures:** "do not adapt the scales on the axes to make your findings seem more
  striking than they are"; zero baselines except rare justified cases; make any scale break
  obvious; **do not substitute the standard error for the standard deviation** when SD is the
  appropriate spread — SE "might make the data seem more consistent than it is"; state which is
  plotted in the legend. *(HTW — A FEW MORE TIPS ON GRAPHS)*
- **Symbol discipline:** only standard widely-available symbols (open/closed circles, triangles,
  squares; open circle → open triangle → open square → closed circle for successive curves);
  "if you need more symbols, you probably have too many curves for one graph, and you should
  consider dividing it into two." Don't mix line types and symbol types.
  *(HTW — SYMBOLS AND LEGENDS)*
- **Simple figures, legible at final size:** "The most common disaster in illustrating is to
  include too much information in one figure"; choose lettering for the reduced published
  column width, not the screen; stack related panels above/below rather than side by side in
  multi-column journals. *(HTW — HOW TO PREPARE GRAPHS)*
- **Statistical language (the book's coverage):** present tense for statistical statements and
  their implications ("These values are significantly greater…") even when the observations are
  past; report comparisons as finding + raw counts + verdict + exact p in one sentence (see
  Results above); "meaningful statistics" at every sample size; significant figures only. The
  books give no systematic p-value/CI/effect-size doctrine — apply the target journal's current
  reporting conventions (and the relevant reporting guideline) for those.
  *(HTW — TENSE IN SCIENTIFIC WRITING; HOW TO HANDLE NUMBERS; WHEN TO USE TABLES)*

## Thesis/dissertation sections

For long student works, Turabian's argument-building craft (research question, claim, working
hypothesis, planning, drafting, revision) is the deep layer — see `argument-craft.md`. The
section contracts for thesis front/back matter and institutional submission are in
`../thesis-and-dissertation.md`.
