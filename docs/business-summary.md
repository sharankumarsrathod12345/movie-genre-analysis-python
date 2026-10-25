# Business summary: movie catalogue analysis

## Decision

How can an analyst describe catalogue composition and compare ratings without misleading stakeholders through duplicate titles, overlapping genres, or missing financial data?

## Evidence

The extract contains 10,865 unique movies after one duplicate is removed. Drama has 4,760 genre memberships, Comedy 3,793, and Thriller 2,907. Because one movie can have several genres, these counts cannot be summed to count the catalogue.

Only 3,854 movies have positive reported budget and revenue. Financial summaries apply to this selected subset. Among movies with a known rating and at least 50 votes, Drama has 21 high-rated movies out of 2,057 (1.02%), while Documentary has 7 out of 87 (8.05%). The threshold is a rating of at least 8. A higher rate in a smaller sample does not establish a better investment.

## Recommended next step

For a real catalogue review, obtain current licensed metadata, dated rating snapshots, audience consumption, availability, and acquisition costs. Agree whether the decision is discovery, catalogue balance, licensing, or financial planning before choosing KPIs. Validate metadata completeness and compare like-for-like release periods and audience coverage.

Use this analysis to demonstrate data cleaning and descriptive reporting. It does not establish current audience demand, recommend film investments, or predict revenue. The data ends in 2015; financial units and source definitions still need confirmation.

## Example client handoff

For a similar scoped engagement: schema/quality checks, deduplicated entity definitions, category mapping, aggregate CSV tables, five charts, and a reproducible script/notebook. A recommendation engine, forecasting, or investment model would be a separate engagement requiring additional evidence.

## Read next

[Notebook](../notebooks/movie_genre_analysis.ipynb) · [Genre summary](../outputs/genre_summary.csv) · [Rating denominators](../outputs/high_rating_summary.csv) · [Source notes](../data/README.md)
