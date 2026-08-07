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


def main():
    embedder = Embedder()
    connection = create_connection()
    retrieval = Retrieval(embedder, connection)
    query = "According to the ABCWUA water quality report, is there arsenic in Albuquerque drinking water"
    results = retrieval.pgvector_search(query)
    print(f"--- Vector search results: {results[0] if results else None}")
    # plainto_tsquery ANDs all terms — long NL questions often match nothing
    results = retrieval.pg_full_text_search("arsenic Albuquerque drinking water")
    print(f"---Full text search results: {results[0] if results else None}")


if __name__ == "__main__":
    main()
