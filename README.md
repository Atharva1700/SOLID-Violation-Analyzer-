# SOLID Violation Analyzer (prototype)

Static checks on Python source using only the standard-library `ast` module. It computes
cyclomatic complexity, method length and LCOM, and flags three SOLID heuristics: SRP, OCP and
ISP. It is evaluated on a seeded synthetic corpus of 40 modules. The corpus is generated and has
ground-truth labels, so the numbers describe that corpus only.

## Results against the stated targets

| Target | Result | Evidence |
|---|---|---|
| 0.85+ precision | **1.00** module-level (16 TP, 0 FP) | `results/evaluation.json` |
| 0.80+ recall | **0.84** module-level (16 of 19 planted) | `results/evaluation.json` |
| 40 modules within 5 s | **0.05 s** for all 40 | `results/evaluation.json` |

Per principle (module level): SRP precision 1.00 / recall 0.73 (8 of 11), OCP 1.00 / 1.00, ISP
1.00 / 1.00.

## What the misses are, and what they are not

- **All three misses are SRP violations hidden by a shared logger.** Two method clusters use
  disjoint state, but both also append to `self._log`. LCOM then counts every pair as related,
  so the class is not flagged. This is a real limit of LCOM, and the analyzer reports it as a
  miss rather than working around it.
- **No false positives on the hard confounders:** a bridged class (two groups joined by one
  method), a five-method protocol (below the threshold of six), and a two-type `isinstance` check
  (below three). Those were added on purpose to test the thresholds.

## Honest limits

- **The corpus is synthetic and templated.** It does not show how the analyzer does on real
  code. The 0.85 / 0.80 bars were met on this corpus, not on production code.
- **The evaluation is not held out.** The first corpus was all clean templates and scored
  perfectly. The hard confounders were added afterwards, and the analyzer's stateless-interface
  rule was changed after the first results (see below). So the numbers are fitted to this
  corpus.
- **A rule change made after first results.** The first version flagged every Protocol as SRP,
  because a class with no instance state has LCOM equal to the number of method pairs. The fix was
  to skip SRP for classes with no instance attributes and for Protocol/ABC classes. This is a
  correctness fix, not a tuned threshold.
- **Thresholds are fixed by hand** (`THRESHOLDS` in `solid_check/analyzer.py`): LCOM ≥ 3 with at
  least 4 methods; at least 3 `isinstance` calls in one function; a Protocol or ABC with at least 6
  methods. They were not tuned against the labels, but they were chosen without any real code to
  test them on.
- **LSP and DIP are not detected.** They need type information this analysis does not have.
- **Module-level scoring.** A module counts as correct if its flags match its planted labels,
  so two classes in one module cannot be scored separately.
- **CI not run.** `.github/workflows/solid.yml` was written and not executed.

## Run it

```
pip install pytest pandas
python corpus/generate.py          # regenerates the seeded corpus and labels
python -m pytest -q tests          # 8 analyzer tests
python evaluate.py                 # writes results/evaluation.json
```

## Files

- `solid_check/analyzer.py`: metrics and flags
- `corpus/generate.py`, `corpus/labels.json`, `corpus/mod_*.py`: seeded corpus and labels
- `evaluate.py`: pandas evaluation (precision, recall, timing)
- `tests/test_analyzer.py`: metric and flag tests
- `results/evaluation.json`
- `.github/workflows/solid.yml` (not run)
