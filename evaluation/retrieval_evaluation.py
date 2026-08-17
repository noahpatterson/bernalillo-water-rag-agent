"""Retrieval metrics against the search ground-truth CSV.

Each ground-truth row is a question plus the knowledge_base_chunks.id that
should answer it. Hit rate is the share of questions whose labeled chunk
appears anywhere in the top-k list. MRR is the mean of 1/rank of that chunk.
"""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm

from embedder import Embedder
from tools.retrieval import FusedHit, Retrieval, SearchHit
from utils.utils import (
    DEFAULT_GROUND_TRUTH,
    GroundTruthQuery,
    get_connection,
    load_ground_truth,
)

DEFAULT_EMBEDDER_PATH = "models/Xenova/all-MiniLM-L6-v2"
DEFAULT_RESULTS_CSV = Path("evaluation/retrieval_evaluation_results.csv")
SINGLE_SEARCH_METHODS = (
    "pgvector_search",
    "pg_full_text_search",
    "pg_full_text_search_soft_match",
)


def hit_id(result: SearchHit | FusedHit) -> int:
    """Return the knowledge-base chunk id from a vector/FTS or fused hit."""
    return result.hit.id if isinstance(result, FusedHit) else result.id


def compute_relevance(
    query: GroundTruthQuery,
    search_fn: Callable,
    report_year: int | None = None,
) -> list[int]:
    """Score one ground-truth query against a ranked search result list.

    Compares the labeled chunk id to each hit. 1 if the hit is that chunk, else 0.

    Args:
        query: Ground-truth row with ``question`` and ``document``.
        search_fn: Retrieval method that takes ``query=`` and optionally
            ``report_year=``.
        report_year: Optional CCR year filter. Passed only if ``search_fn``
            accepts it.

    Returns:
        Binary relevance list, one entry per ranked hit.
    """
    doc_id = query["document"]
    kwargs: dict[str, str | int | None] = {"query": query["question"]}
    if "report_year" in search_fn.__code__.co_varnames:
        kwargs["report_year"] = report_year
    results = search_fn(**kwargs)
    return [int(hit_id(r) == doc_id) for r in results]


def compute_relevance_total(
    ground_truth: list[GroundTruthQuery],
    search_fn: Callable,
    report_year: int | None = None,
) -> list[list[int]]:
    """Score every ground-truth query with ``compute_relevance``.

    Args:
        ground_truth: Ground-truth rows with ``question`` and ``document``.
        search_fn: Retrieval method that takes ``query=`` and optionally
            ``report_year=``.
        report_year: Optional CCR year filter.

    Returns:
        One binary relevance list per query.
    """
    relevance_total = []
    for q in tqdm(ground_truth):
        relevance_total.append(compute_relevance(q, search_fn, report_year))
    return relevance_total


def hit_rate(relevance_total: list[list[int]]) -> float:
    """Share of queries with at least one relevant hit in the ranked list."""
    return sum(1 for r in relevance_total if any(r)) / len(relevance_total)


def reciprocal_rank(line: list[int]) -> float:
    """1 / rank of the first relevant hit, or 0 if none are relevant."""
    for rank, relevance in enumerate(line):
        if relevance:
            return 1 / (rank + 1)
    return 0


def mrr(relevance_total: list[list[int]]) -> float:
    """Mean reciprocal rank across all ground-truth queries."""
    return sum(reciprocal_rank(line) for line in relevance_total) / len(relevance_total)


def evaluate(
    queries: list[GroundTruthQuery],
    search_method: str = "pgvector_search",
    report_year: int | None = None,
    embedder_path: str = DEFAULT_EMBEDDER_PATH,
    embedder: Embedder | None = None,
) -> dict[str, float]:
    """Run one Retrieval method over the ground truth and return hit rate and MRR.

    Args:
        queries: Ground-truth rows with ``question`` and ``document``.
        search_method: Name of a ``Retrieval`` method, e.g. ``pgvector_search``.
        report_year: Optional CCR year filter.
        embedder_path: Local MiniLM directory used by ``Embedder``.
        embedder: Optional shared embedder so a full run does not reload the model.

    Returns:
        ``{"hit_rate": ..., "mrr": ...}``.
    """
    if embedder is None:
        embedder = Embedder(path=embedder_path)
    with get_connection() as connection:
        search = Retrieval(embedder, connection)
        search_fn = getattr(search, search_method)
        relevance_total = compute_relevance_total(queries, search_fn, report_year)

    return {
        "hit_rate": hit_rate(relevance_total),
        "mrr": mrr(relevance_total),
    }


def compute_relevance_rrf(
    q: GroundTruthQuery,
    search: Retrieval,
    report_year: int = 2025,
    fts_method: str = "pg_full_text_search_soft_match",
    rrf_method: str = "rrf",
    search_k: int = 20,
    num_results: int = 5,
) -> list[int]:
    """Score one query with vector + FTS fused by reciprocal rank fusion.

    Pulls ``search_k`` hits from each list (year-filtered), fuses to
    ``num_results``, then marks the labeled chunk as relevant.

    Args:
        q: Ground-truth row with ``question`` and ``document``.
        search: Live ``Retrieval`` bound to an open connection.
        report_year: CCR year applied to both candidate lists.
        fts_method: ``Retrieval`` FTS method name.
        rrf_method: ``Retrieval`` fusion method name (``rrf`` or ``new_rrf``).
        search_k: Hits to retrieve from each list before fusion.
        num_results: Fused list size to score.

    Returns:
        Binary relevance list over the fused ranking.
    """
    doc_id = q["document"]
    search_kwargs = {
        "query": q["question"],
        "num_results": search_k,
        "report_year": report_year,
    }

    vector_hits = search.pgvector_search(**search_kwargs)
    fts_hits = getattr(search, fts_method)(**search_kwargs)
    if any(h.report_year != report_year for h in vector_hits + fts_hits):
        raise ValueError("search results included a year other than report_year")

    fused = getattr(search, rrf_method)(vector_hits, fts_hits, num_results=num_results)
    return [int(r.hit.id == doc_id) for r in fused]


def compute_relevance_total_rrf(
    queries: list[GroundTruthQuery],
    search: Retrieval,
    report_year: int = 2025,
    fts_method: str = "pg_full_text_search_soft_match",
    rrf_method: str = "rrf",
    search_k: int = 20,
    num_results: int = 5,
) -> list[list[int]]:
    """Score every ground-truth query with ``compute_relevance_rrf``.

    Args:
        queries: Ground-truth rows with ``question`` and ``document``.
        search: Live ``Retrieval`` bound to an open connection.
        report_year: CCR year applied to both candidate lists.
        fts_method: ``Retrieval`` FTS method name.
        rrf_method: ``Retrieval`` fusion method name.
        search_k: Hits to retrieve from each list before fusion.
        num_results: Fused list size to score.

    Returns:
        One binary relevance list per query.
    """
    relevance_total = []
    for q in tqdm(queries):
        relevance_total.append(
            compute_relevance_rrf(
                q,
                search,
                report_year,
                fts_method=fts_method,
                rrf_method=rrf_method,
                search_k=search_k,
                num_results=num_results,
            )
        )
    return relevance_total


def evaluate_rrf(
    queries: list[GroundTruthQuery],
    report_year: int = 2025,
    fts_method: str = "pg_full_text_search_soft_match",
    rrf_method: str = "rrf",
    search_k: int = 20,
    num_results: int = 5,
    embedder_path: str = DEFAULT_EMBEDDER_PATH,
    embedder: Embedder | None = None,
) -> dict[str, float]:
    """Run year-filtered RRF over the ground truth and return hit rate and MRR.

    Args:
        queries: Ground-truth rows with ``question`` and ``document``.
        report_year: CCR year applied to both candidate lists.
        fts_method: ``Retrieval`` FTS method name.
        rrf_method: ``Retrieval`` fusion method name.
        search_k: Hits to retrieve from each list before fusion.
        num_results: Fused list size to score.
        embedder_path: Local MiniLM directory used by ``Embedder``.
        embedder: Optional shared embedder so a full run does not reload the model.

    Returns:
        ``{"hit_rate": ..., "mrr": ...}``.
    """
    if embedder is None:
        embedder = Embedder(path=embedder_path)
    with get_connection() as connection:
        search = Retrieval(embedder, connection)
        relevance_total = compute_relevance_total_rrf(
            queries,
            search,
            report_year,
            fts_method=fts_method,
            rrf_method=rrf_method,
            search_k=search_k,
            num_results=num_results,
        )

    return {
        "hit_rate": hit_rate(relevance_total),
        "mrr": mrr(relevance_total),
    }


def save_results(
    rows: list[dict[str, str | float | int | None]],
    path: Path = DEFAULT_RESULTS_CSV,
) -> Path:
    """Append evaluation rows to CSV. ``run_date`` is the run key."""
    new_df = pd.DataFrame(rows)
    if path.exists():
        existing = pd.read_csv(path)
        out = pd.concat([existing, new_df], ignore_index=True)
    else:
        out = new_df
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    return path


def main(
    report_year: int = 2025,
    results_path: Path = DEFAULT_RESULTS_CSV,
    ground_truth_path: Path = DEFAULT_GROUND_TRUTH,
    embedder_path: str = DEFAULT_EMBEDDER_PATH,
) -> Path:
    """Run all search methods and save one CSV row per method, keyed by run date."""
    run_date = datetime.now().astimezone().isoformat(timespec="seconds")
    queries = load_ground_truth(ground_truth_path)
    embedder = Embedder(path=embedder_path)
    rows: list[dict[str, str | float | int | None]] = []

    for method in SINGLE_SEARCH_METHODS:
        print(f"evaluating {method}...")
        metrics = evaluate(
            queries,
            search_method=method,
            report_year=report_year,
            embedder=embedder,
        )
        rows.append(
            {
                "run_date": run_date,
                "method": method,
                "report_year": report_year,
                **metrics,
            }
        )
        print(f"  {metrics}")

    print("evaluating rrf...")
    rrf_metrics = evaluate_rrf(
        queries,
        report_year=report_year,
        embedder=embedder,
    )
    rows.append(
        {
            "run_date": run_date,
            "method": "rrf",
            "report_year": report_year,
            **rrf_metrics,
        }
    )
    print(f"  {rrf_metrics}")

    saved = save_results(rows, results_path)
    print(f"saved {len(rows)} rows to {saved} (run_date={run_date})")
    return saved


if __name__ == "__main__":
    main()
