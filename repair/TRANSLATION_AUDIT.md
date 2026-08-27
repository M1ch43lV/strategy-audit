# Translation audit

Scope: files that differ from their respective Git `HEAD`, not untouched
author files elsewhere in the downloaded corpus.

## Audit framework

- `strategy-audit/tools/translation_repair.py` reconstructs each translated
  Python file from `HEAD` and replaces only Python comment and string tokens.
- It rejects Cyrillic output, missing protected tokens and any change to the
  normalized Python AST.
- DeepSeek V4 Flash was used for the batch translation and semantic review;
  ambiguous protocol terms were normalized manually (`PASS`, `FAIL`, `NA`,
  `SKIP`, `FOUND`, `TIMEOUT`).

## Verified changes

| Scope | Result |
|---|---|
| 26 audit Python files | 858 unique Russian token bodies translated; normalized AST unchanged; no Cyrillic or `XXXX` remains |
| 5 copied strategy files (`BBRSITV.py`, `SMA_BBRSI.py`) | normalized AST equals each nested repository's `HEAD`; no Cyrillic or `XXXX` remains |
| `markdregan.../tests/conftest.py` | corrupted comment repaired; normalized AST unchanged |
| `BTC_scores.csv` | exactly 15 of 1,827 lines changed; 15 Russian headlines translated; no Cyrillic or `XXXX` remains |

The CSV translation is not merely cosmetic: headline text is model input.
Results produced from the translated CSV must therefore record that data
localization occurred.

## Checks

- `translation_repair.py --check`: 26 files validated, zero Russian remnants.
- `freeze_guard.py --selftest`: 8/8.
- `verify_ledger.py --selftest`: 7/7.
- The five strategy files and `conftest.py` compile to the same normalized AST
  as their author versions.

The three `MelvynClark_Freqtrade-Strategy` changes (`numpy.lib.math` to the
standard-library `math`) are compatibility repairs, not translations. The two
large repositories with staged deletions are also unrelated to translation and
remain unresolved intentionally.
