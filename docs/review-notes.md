# Methodology review

- The original high-rating query used `vote_average.nunique()`. That counts distinct score values, not movies. The revised query uses stable movie IDs and supplies eligible-movie denominators.
- Title-only counting can merge distinct movies with the same title. The source ID is unique after exact-row deduplication.
- Multi-genre memberships overlap. A genre pie chart can obscure that denominator, so counts are shown with bars.
- Nonpositive budget/revenue records are excluded from financial comparisons under an explicit data-quality policy. The eligible sample is 3,854 movies; do not extrapolate it to all movies.
- Reported revenue minus budget is not accounting net profit. Other costs, distribution shares, and inflation adjustments are absent from the calculation.
- Correlations use the un-exploded movie table. Genre expansion would otherwise overweight multi-genre titles.
- High-rating comparisons use at least 50 votes and score >=8. These are analyst-selected thresholds, not validated universal standards.
- Current findings are descriptive, not proof of causes or an investment strategy.

Validation: all code cells ran against the supplied data in order; nbformat validation passed. Native Jupyter launch is blocked by socket permissions in the execution environment, not by a notebook error. Run the notebook locally for native-kernel confirmation.

## GitHub publication review — 2026-10-25

Published input, code, notebook, and output blobs matched the reviewed package. Removed the redundant outer project directory so the root README and run instructions agree. Added a business summary, clarified third-party data licensing, and changed the standalone script to resolve paths relative to its file. Standalone scripts were rerun; native notebook-kernel validation was pending at that stage and is now completed below.

## Native Jupyter validation completed — 2026-10-25

[Successful GitHub Actions run](https://github.com/sharankumarsrathod12345/movie-genre-analysis-python/actions/runs/40205401956) at commit `3fe210fcde151661b587a1bbcfac308053ce5044`.

Executed 7 code cells in a fresh Python 3.12.15 kernel after clearing saved outputs and execution counts. All 5 aggregate CSV files reconciled to the repository baselines using numerical tolerances (rtol=1e-9, atol=1e-10). Source hashes and notebook structure passed. The earlier local socket restriction is superseded by this successful hosted run. See `native-validation.json` for the package versions and file list.
