# Digitized corpus: Koskenniemi & Parpola 1979, *Corpus of Texts in the Indus Script*

Machine-read from the scanned Helda reprint (`../indus_corpus_1979.pdf`),
pages [19]–[77] (PDF pp. 20–78): the sign list and the basic corpus.
The two sorted lists (PDF pp. 79–176) were not processed.

## Files

| File | Content |
|---|---|
| `corpus_inscriptions.tsv` | one row per inscription (4066) |
| `corpus_signs_long.tsv` | one row per sign occurrence (18381) |
| `sign_list.tsv` | the 687 sign-list entries (401 ranks): sign, 1965 variant code, underlined flag, position |
| `proofsheets/pXXX_colN.png` | for every list line: the scan, the recognized signs re-plotted beneath, labels; low-confidence signs boxed |
| `pipeline/` | the Python scripts used (paths inside point to a temporary working directory) |

## Conventions

- **Sign numbers** are the *rank numbers* of the 1979 sign list (upper number in the list).
  `variant_code` is the 1965 code (lower number), which also identifies the graphic variant.
- **Reading order** is right to left (as in the script): the first token in `text` is the rightmost sign.
- `/` = boundary (a blank in the plotted line, i.e. line/side boundary per §6.5, or a wrap to the next list line).
- `*` after a sign = underlined in the corpus (uncertain reading, §6.6).
- Auxiliary signs are ordinary ranks: 395 hatched "?", 396 hatched box, 397–399 narrow hatchings, 400 empty box, 401 uninscribed seal (≡).
- `type_code`, `lines_code` (blank = one line; 2, 3, 6, 7, 9), `icon_code` are the lower code line of the code group (§6.3–6.5).

## Quality

- Inscription numbers were checked for strictly increasing order; 38 misreads were repaired from
  the sequence (`number_corrected=1`), the doubtful ones verified visually.
- Signs were matched against templates cut from the sign list (same plotter font). Median match
  distance 0.035; 26 tokens remain with distance > 0.3 (`low_confidence`, boxed in proof sheets).
- Visual spot checks of several pages showed the readings correct, but the result has not been
  proofread in full. The proof sheets are designed for that.
- Known weak spots: underline detection (needs ≥30 % dash coverage under a sign); boundary
  threshold (gap > 115 px); signs that are absent from the sign list in the exact plotted form.
