from typing import NamedTuple

import psycopg
from pgvector.psycopg import register_vector

from embedder import Embedder
from utils.utils import create_connection


class SearchHit(NamedTuple):
    id: int
    report_year: int
    section: str
    source_url: str
    text: str
    distance: float

class FusedHit(NamedTuple):
    hit: SearchHit
    rrf_score: float
    vector_rank: int | None  # 0-based; None if not in vector list
    fts_rank: int | None  # 0-based; None if not in FTS list
class Retrieval:
    def __init__(self, embedder: Embedder, connection: psycopg.Connection):
        self.embedder = embedder
        self.connection = connection
        register_vector(connection)

    def pgvector_search(self, query: str, num_results: int = 5) -> list[SearchHit]:
        query_vector = self.embedder.encode(query)
        rows = self.connection.execute(
            """
            SELECT
              id,
              report_year,
              section,
              source_url,
              text,
              embedding <=> %s AS distance
            FROM knowledge_base_chunks
            ORDER BY distance
            LIMIT %s
            """,
            (query_vector, num_results),
        ).fetchall()
        return [SearchHit(*row) for row in rows]

    def pg_full_text_search(self, query: str, num_results: int = 5) -> list[SearchHit]:
        rows = self.connection.execute(
            """
            SELECT
              id,
              report_year,
              section,
              source_url,
              text,
              ts_rank(tsv, plainto_tsquery('english', %s)) AS rank
            FROM knowledge_base_chunks
            WHERE tsv @@ plainto_tsquery('english', %s)
            ORDER BY rank DESC
            LIMIT %s
            """,
            (query, query, num_results),
        ).fetchall()
        return [SearchHit(*row) for row in rows]

    def pg_full_text_search_soft_match(self, query: str, num_results: int = 5) -> list[SearchHit]:
        """
        Soft keyword search (minsearch-like): match if *any* query term appears.
        plainto_tsquery builds AND (&); we flip to OR (|) so long NL questions still hit.
        """
        rows = self.connection.execute(
            """
            SELECT
              id,
              report_year,
              section,
              source_url,
              text,
              ts_rank(tsv, query) AS rank
            FROM knowledge_base_chunks,
                 to_tsquery(
                   'english',
                   replace(plainto_tsquery('english', %s)::text, ' & ', ' | ')
                 ) AS query
            WHERE tsv @@ query
            ORDER BY rank DESC
            LIMIT %s
            """,
            (query, num_results),
        ).fetchall()
        return [SearchHit(*row) for row in rows]


    def rrf(
        self,
        vector: list[SearchHit],
        fts: list[SearchHit],
        k: int = 60,
        num_results: int = 5,
    ) -> list[FusedHit]:
        """
        AI assisted RRF implementation -- cleaner than hand written new_rrf
        """
        scores: dict[int, float] = {}
        hits: dict[int, SearchHit] = {}
        vector_rank: dict[int, int] = {}
        fts_rank: dict[int, int] = {}

        for rank, hit in enumerate(vector):
            scores[hit.id] = scores.get(hit.id, 0.0) + 1.0 / (k + rank)
            hits[hit.id] = hit
            vector_rank[hit.id] = rank

        for rank, hit in enumerate(fts):
            scores[hit.id] = scores.get(hit.id, 0.0) + 1.0 / (k + rank)
            hits[hit.id] = hit
            fts_rank[hit.id] = rank

        ranked_ids = sorted(scores, key=scores.get, reverse=True)
        return [
            FusedHit(
                hit=hits[i],
                rrf_score=scores[i],
                vector_rank=vector_rank.get(i),
                fts_rank=fts_rank.get(i),
            )
            for i in ranked_ids[:num_results]
        ]


    def new_rrf(
      self,
      vectorHits: list[SearchHit], 
      textHits: list[SearchHit],
      num_results: int = 5
    ) -> list[FusedHit]:
      """
      My own RRF implementation -- not as clean as the AI assisted version
      """
      scores = {}
      fused_hits = []

      for i, vecHit in enumerate(vectorHits):
        score = 1 / (60 + i)
        scores[vecHit.id] = {"hit": vecHit, "score": score, "vector_rank": i, "fts_rank": None}

      for i, textHit in enumerate(textHits):
        score = 1 / (60 + i)
        if textHit.id in scores:
          scores[textHit.id]["score"] += score
          scores[textHit.id]["fts_rank"] = i
        else:
          scores[textHit.id] = {"hit": textHit, "score": score, "vector_rank": None, "fts_rank": i}
      
      for id, score in scores.items():
        fused_hits.append(FusedHit(hit=score["hit"], rrf_score=score["score"], vector_rank=score["vector_rank"], fts_rank=score["fts_rank"]))
      return sorted(fused_hits, key=lambda x: x.rrf_score, reverse=True)[:num_results]


def main():
    embedder = Embedder()
    connection = create_connection()
    retrieval = Retrieval(embedder, connection)
    query = "According to the ABCWUA water quality report, is there arsenic in Albuquerque drinking water"
    results_vec = retrieval.pgvector_search(query, num_results=20)
    results_fts = retrieval.pg_full_text_search(
        "arsenic Albuquerque drinking water", num_results=20
    )

    # fused = retrieval.new_rrf(results_vec, results_fts, 5)
    # print("--- RRF results ---")
    # for i, f in enumerate(fused):
    #     print(
    #         f"#{i} id={f.hit.id} section={f.hit.section} "
    #         f"vector_rank={f.vector_rank} "
    #         f"fts_rank={f.fts_rank} rrf={f.rrf_score:.5f}"
    #     )
    #     print(f"    {f.hit.text[:120]!r}...")

    # fused = retrieval.rrf(results_vec, results_fts, num_results=5)
    # print("--- RRF results ---")
    # for i, f in enumerate(fused):
    #     print(
    #         f"#{i} id={f.hit.id} section={f.hit.section} "
    #         f"vector_rank={f.vector_rank} "
    #         f"fts_rank={f.fts_rank} rrf={f.rrf_score:.5f}"
    #     )
    #     print(f"    {f.hit.text[:120]!r}...")

    results_soft = retrieval.pg_full_text_search_soft_match(query, num_results=20)
    print("--- Soft match results ---")
    for i, f in enumerate(results_soft):
        print(
            f"#{i} id={f.id} section={f.section} "
            f"rank={f.distance}"
        )
        print(f"    {f.text}...")


if __name__ == "__main__":
    main()
