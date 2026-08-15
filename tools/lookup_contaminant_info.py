import psycopg
from psycopg.rows import DictRow, dict_row

from utils.utils import create_connection


def contaminant_info(
    contaminant: str,
    connection: psycopg.Connection | None = None,
) -> list[DictRow]:
    if not contaminant.strip():
        return []

    owns_connection = connection is None
    if owns_connection:
        connection = create_connection()
        if connection is None:
            raise RuntimeError("Could not connect to Postgres")

    try:
        sql = """
        SELECT
            contaminant_name,
            contaminant_code,
            units,
            contaminant_source,
            source_url
        FROM compliance_results
        WHERE (
            contaminant_name ILIKE %s
            OR contaminant_code ILIKE %s
        )
        LIMIT 1
    """
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, (contaminant.strip(), contaminant.strip()))
            rows = list(cursor.fetchall())
        return rows

    finally:
        if owns_connection and connection is not None:
            connection.close()


def __main__():
    # smoke: empty
    rows = contaminant_info("")
    print(rows)

    # smoke: known contaminant
    rows = contaminant_info("U")
    print(rows)

    # smoke: unknown contaminant
    rows = contaminant_info("Gold")
    print(rows)


if __name__ == "__main__":
    __main__()
