"""Compliance-table tool: structured lookup over compliance_results.

Citation shape (seam): contaminant | value + units | report year | publisher | table/row key | source URL
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import psycopg
from psycopg.rows import dict_row

from utils.utils import ContaminantValueType, create_connection

PUBLISHER = "ABCWUA"


@dataclass(frozen=True)
class ComplianceCitation:
    """Represents a citation from the compliance database.

    Attributes:
        contaminant: The name of the contaminant.
        value: The value(s) of the citation.
        units: The units of the citation.
        report_year: The year the citation was reported.
        publisher: The publisher of the citation.
        row_id: The row ID of the citation.
        source_url: The URL of the source of the citation.
    """

    contaminant: str
    value: dict[str, Any]
    units: str | None
    report_year: int
    publisher: str
    row_id: int
    source_url: str | None


@dataclass(frozen=True)
class YearSQL:
    sql: str
    params: list[int]


def _display_value(
    row: dict[str, Any], value_type: ContaminantValueType | None
) -> dict[str, Any]:
    """Determine the display value for a given row and value type.

    Args:
        row: A dictionary representing a row from the compliance database.
        value_type: The type of value to extract from the row.

    Returns:
        The display value for the given row and value type.
        If no value is passed or 1 value is not found, returns all available values.
    """
    if value_type is None or row.get(value_type.value) is None:
        return {
            value_type.value: row.get(value_type.value)
            for value_type in list(ContaminantValueType)
            if row.get(value_type.value) is not None
        }
    return {value_type.value: row.get(value_type.value)}


def _citation_from_row(
    row: dict[str, Any], value_type: ContaminantValueType | None
) -> ComplianceCitation:
    """Converts a row from the compliance database into a ComplianceCitation.

    Args:
        row: A dictionary representing a row from the compliance database.
        value_type: The type of value to extract from the row.

    Returns:
        A ComplianceCitation object.
    """
    return ComplianceCitation(
        contaminant=row["contaminant_name"],
        value=_display_value(row, value_type),
        units=row.get("units"),
        report_year=row["report_year"],
        publisher=PUBLISHER,
        row_id=row["id"],
        source_url=row.get("source_url"),
    )


# sample_year_range values look like "2015-2017" / "2019-2020"
_SAMPLE_RANGE_RE = r"^\d{4}-\d{4}$"


def _sample_range_bounds_sql(alias: str = "sample_year_range") -> tuple[str, str]:
    """SQL exprs for start/end year parsed from ``YYYY-YYYY`` (else NULL)."""
    start = f"""
        CASE
            WHEN {alias} ~ '{_SAMPLE_RANGE_RE}'
            THEN split_part({alias}, '-', 1)::int
        END
    """
    end = f"""
        CASE
            WHEN {alias} ~ '{_SAMPLE_RANGE_RE}'
            THEN split_part({alias}, '-', 2)::int
        END
    """
    return start, end


def _validate_inclusive_range(start: int, end: int, label: str) -> None:
    if start > end:
        raise ValueError(f"{label} start ({start}) > end ({end})")


def _year_clause(
    *,
    report_year: int | None,
    report_year_range: tuple[int, int] | None,
    sample_year: int | None,
    sample_year_range: tuple[int, int] | None,
) -> YearSQL | None:
    """Build SQL year predicate. Exactly one year arg must be set."""
    modes = {
        "report_year": report_year,
        "report_year_range": report_year_range,
        "sample_year": sample_year,
        "sample_year_range": sample_year_range,
    }
    set_modes = [name for name, value in modes.items() if value is not None]
    if len(set_modes) != 1:
        # raise ValueError(
        #     "Pass exactly one of report_year, report_year_range, "
        #     "sample_year, or sample_year_range"
        # )
        return None

    if report_year is not None:
        return YearSQL("report_year = %s", [report_year])

    if report_year_range is not None:
        start, end = report_year_range
        _validate_inclusive_range(start, end, "report_year_range")
        return YearSQL("report_year BETWEEN %s AND %s", [start, end])

    range_start_sql, range_end_sql = _sample_range_bounds_sql()
    # sample_* filters: match sample_year column OR overlapping sample_year_range text
    if sample_year is not None:
        return YearSQL(
            f"""
            (
                sample_year = %s
                OR (
                    ({range_start_sql}) <= %s
                    AND ({range_end_sql}) >= %s
                )
            )
        """,
            [sample_year, sample_year, sample_year],
        )

    start, end = sample_year_range  # type: ignore[misc]
    _validate_inclusive_range(start, end, "sample_year_range")
    return YearSQL(
        f"""
        (
            sample_year BETWEEN %s AND %s
            OR (
                ({range_start_sql}) <= %s
                AND ({range_end_sql}) >= %s
            )
        )
    """,
        [start, end, end, start],
    )


def lookup_compliance(
    contaminant: str,
    *,
    report_year: int | None = None,
    report_year_range: tuple[int, int] | None = None,
    sample_year: int | None = None,
    sample_year_range: tuple[int, int] | None = None,
    connection: psycopg.Connection | None = None,
    value_type: ContaminantValueType | None = None,
) -> dict[str, Any]:
    """Look up COMPLIANCE MONITORING RESULTS rows by contaminant and year(s).

    Pass exactly one year filter:

    - ``report_year`` / ``report_year_range`` — filter on CCR ``report_year`` only
    - ``sample_year`` / ``sample_year_range`` — filter on ``sample_year`` or
      ``sample_year_range`` (``YYYY-YYYY`` text, inclusive overlap) only

    Contaminant matches ``contaminant_name`` or ``contaminant_code`` (case-insensitive).

    Value type passing a ``ContaminantValueType`` enum value. or None to return all value types.

    Returns ``{"rows": [...], "citations": [...]}``. Empty lists if no hit
    (caller / cite-or-refuse flow should refuse or hedge).
    """
    owns_connection = connection is None
    if owns_connection:
        connection = create_connection()
        if connection is None:
            raise RuntimeError("Could not connect to Postgres")

    try:
        year_clause = _year_clause(
            report_year=report_year,
            report_year_range=report_year_range,
            sample_year=sample_year,
            sample_year_range=sample_year_range,
        )
        year_sql = f" AND {year_clause.sql}" if year_clause else ""

        sql = f"""
            SELECT *
            FROM compliance_results
            WHERE (
                contaminant_name ILIKE %s
                OR contaminant_code ILIKE %s
            )
              {year_sql}
            ORDER BY report_year ASC, contaminant_name ASC, id ASC
        """
        params = [contaminant.strip(), contaminant.strip()] + (
            year_clause.params if year_clause else []
        )

        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, params)
            rows = list(cursor.fetchall())

        citations = [_citation_from_row(row, value_type=value_type) for row in rows]
        return {
            "rows": rows,
            "citations": [asdict(c) for c in citations],
        }
    finally:
        if owns_connection and connection is not None:
            connection.close()


def main() -> None:

    # arsenic via report year range
    arsenic = lookup_compliance("arsenic", report_year_range=(2020, 2025))
    print(f"arsenic report 2020–2025: {len(arsenic['rows'])} rows")
    for cite in arsenic["citations"]:
        print(f"  {cite} " f"(row_id={cite['row_id']})")

    # nitrate via report year and value type = AVG_SYSTEM
    nitrate = lookup_compliance(
        "nitrate", report_year=2024, value_type=ContaminantValueType.AVG_SYSTEM
    )
    print(f"nitrate report 2024: {len(nitrate['rows'])} rows")
    for cite in nitrate["citations"]:
        print(
            f"  {cite['report_year']}: {cite['value']} {cite['units']} "
            f"(row_id={cite['row_id']})"
        )

    # crypto via sample year and value type = AVG_SYSTEM
    crypto = lookup_compliance(
        "Cryptosporidium", sample_year=2016, value_type=ContaminantValueType.AVG_SYSTEM
    )
    print(f"Cryptosporidium sample covering 2016: {len(crypto['rows'])} rows")
    for row in crypto["citations"]:
        print(
            f"  report={row['report_year']}: {row['value']} {row['units']}  "
            f"row_id={row['row_id']}"
        )

    # lead via report year range
    lead = lookup_compliance("lead", report_year_range=(2020, 2022))
    print(f"lead report 2010–2020: {len(lead['rows'])} rows")
    for cite in lead["citations"]:
        print(
            f"  {cite['report_year']}: {cite['value']} {cite['units']} "
            f"(row_id={cite['row_id']})"
        )


if __name__ == "__main__":
    main()
