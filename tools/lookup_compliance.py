"""Compliance-table tool: structured lookup over compliance_results.

Citation shape (seam): contaminant | value + units | report year | publisher | table/row key | source URL
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import psycopg
from psycopg.rows import dict_row

from utils.utils import create_connection

PUBLISHER = "ABCWUA"


@dataclass(frozen=True)
class ComplianceCitation:
    contaminant: str
    value: float | None
    units: str | None
    report_year: int
    publisher: str
    row_id: int
    source_url: str | None


def _display_value(row: dict[str, Any]) -> float | None:
    """Prefer the headline number a CCR answer usually cites."""
    for key in ("avg_system", "max_detected", "ninetieth_percentile", "max_lraa"):
        if row.get(key) is not None:
            return row[key]
    return None


def _citation_from_row(row: dict[str, Any]) -> ComplianceCitation:
    return ComplianceCitation(
        contaminant=row["contaminant_name"],
        value=_display_value(row),
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
    params: dict[str, Any],
) -> str:
    """Build SQL year predicate. Exactly one year arg must be set."""
    modes = {
        "report_year": report_year,
        "report_year_range": report_year_range,
        "sample_year": sample_year,
        "sample_year_range": sample_year_range,
    }
    set_modes = [name for name, value in modes.items() if value is not None]
    if len(set_modes) != 1:
        raise ValueError(
            "Pass exactly one of report_year, report_year_range, "
            "sample_year, or sample_year_range"
        )

    if report_year is not None:
        params["report_year"] = report_year
        return "report_year = %(report_year)s"

    if report_year_range is not None:
        start, end = report_year_range
        _validate_inclusive_range(start, end, "report_year_range")
        params["report_year_start"] = start
        params["report_year_end"] = end
        return "report_year BETWEEN %(report_year_start)s AND %(report_year_end)s"

    range_start_sql, range_end_sql = _sample_range_bounds_sql()
    # sample_* filters: match sample_year column OR overlapping sample_year_range text
    if sample_year is not None:
        params["sample_year"] = sample_year
        return f"""
            (
                sample_year = %(sample_year)s
                OR (
                    ({range_start_sql}) <= %(sample_year)s
                    AND ({range_end_sql}) >= %(sample_year)s
                )
            )
        """

    start, end = sample_year_range  # type: ignore[misc]
    _validate_inclusive_range(start, end, "sample_year_range")
    params["sample_year_start"] = start
    params["sample_year_end"] = end
    return f"""
        (
            sample_year BETWEEN %(sample_year_start)s AND %(sample_year_end)s
            OR (
                ({range_start_sql}) <= %(sample_year_end)s
                AND ({range_end_sql}) >= %(sample_year_start)s
            )
        )
    """


def lookup_compliance(
    contaminant: str,
    *,
    report_year: int | None = None,
    report_year_range: tuple[int, int] | None = None,
    sample_year: int | None = None,
    sample_year_range: tuple[int, int] | None = None,
    connection: psycopg.Connection | None = None,
) -> dict[str, Any]:
    """Look up COMPLIANCE MONITORING RESULTS rows by contaminant and year(s).

    Pass exactly one year filter:

    - ``report_year`` / ``report_year_range`` — filter on CCR ``report_year`` only
    - ``sample_year`` / ``sample_year_range`` — filter on ``sample_year`` or
      ``sample_year_range`` (``YYYY-YYYY`` text, inclusive overlap) only

    Contaminant matches ``contaminant_name`` or ``contaminant_code`` (case-insensitive).

    Returns ``{"rows": [...], "citations": [...]}``. Empty lists if no hit
    (caller / cite-or-refuse flow should refuse or hedge).
    """
    owns_connection = connection is None
    if owns_connection:
        connection = create_connection()
        if connection is None:
            raise RuntimeError("Could not connect to Postgres")

    try:
        params: dict[str, Any] = {"contaminant": contaminant.strip()}
        year_clause = _year_clause(
            report_year=report_year,
            report_year_range=report_year_range,
            sample_year=sample_year,
            sample_year_range=sample_year_range,
            params=params,
        )

        sql = f"""
            SELECT *
            FROM compliance_results
            WHERE (
                contaminant_name ILIKE %(contaminant)s
                OR contaminant_code ILIKE %(contaminant)s
            )
              AND {year_clause}
            ORDER BY report_year ASC, contaminant_name ASC, id ASC
        """

        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, params)
            rows = list(cursor.fetchall())

        citations = [_citation_from_row(row) for row in rows]
        return {
            "rows": rows,
            "citations": [asdict(c) for c in citations],
        }
    finally:
        if owns_connection and connection is not None:
            connection.close()


def main() -> None:
    """Smoke: arsenic/nitrate via report year; crypto via sample year."""
    arsenic = lookup_compliance("arsenic", report_year_range=(2020, 2025))
    print(f"arsenic report 2020–2025: {len(arsenic['rows'])} rows")
    for cite in arsenic["citations"]:
        print(
            f"  {cite['report_year']}: {cite['value']} {cite['units']} "
            f"(row_id={cite['row_id']})"
        )

    nitrate = lookup_compliance("nitrate", report_year=2024)
    print(f"nitrate report 2024: {len(nitrate['rows'])} rows")
    for cite in nitrate["citations"]:
        print(
            f"  {cite['report_year']}: {cite['value']} {cite['units']} "
            f"(row_id={cite['row_id']})"
        )

    crypto = lookup_compliance("Cryptosporidium", sample_year=2016)
    print(f"Cryptosporidium sample covering 2016: {len(crypto['rows'])} rows")
    for row in crypto["rows"]:
        print(
            f"  report={row['report_year']} sample_range={row['sample_year_range']} "
            f"row_id={row['id']}"
        )


if __name__ == "__main__":
    main()
