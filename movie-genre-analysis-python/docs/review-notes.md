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
