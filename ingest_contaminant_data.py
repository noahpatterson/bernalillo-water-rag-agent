import csv
from typing import Iterable, TypeVar
import psycopg
from dataclasses import dataclass
from utils.utils import create_connection

SOURCE_URLS: dict[int, str] = {
    2025: "https://www.abcwua.org/wp-content/uploads/2026/05/ABCWUA-2025WaterQualityMailerWeb.pdf",
    2024: "https://www.abcwua.org/wp-content/uploads/2025/04/ABCWUA-2024WaterQualityMailerWeb-FINAL2.pdf",
    2023: "https://www.abcwua.org/wp-content/uploads/2024/04/ABCWUA-2023WaterQualityMailerWeb.pdf",
    2022: "https://www.abcwua.org/wp-content/uploads/2023/05/2022WaterQualityMailerWeb.pdf",
    2021: "https://www.abcwua.org/wp-content/uploads/2022/05/ABCWUA-2021WaterQualityReport_Web_FINAL.pdf",
    2020: "https://www.abcwua.org/wp-content/uploads/2021/05/ABCWUA-2021WaterQualityMailerWeb.pdf",
}

CONTAMINANT_SOURCES: dict[str, str] = {
    "arsenic": "Erosion of natural volcanic deposits",
    "Barium": "Erosion of natural deposits",
    "Chromium": "Erosion of natural deposits",
    "Fluoride": "Erosion of natural deposits",
    "Gross Alpha Particle Activity": "Erosion of natural deposits",
    "Nitrate": "Runoff from fertilizer use; leaching from septic tanks, sewage; erosion of natural deposits",
    "Radium 226 + 228": "Erosion of natural deposits",
    "Total Xylenes": "Gasoline, paint, varnishes, and industrial cleaning solvents",
    "Uranium": "Erosion of natural deposits",
    "Bromate": "By-product of drinking water disinfection",
    "Chlorine: Distribution System": "Disinfectant",
    "Chlorine: Surface Water": "Disinfectant",
    "Chlorine: Groundwater": "Disinfectant",
    "Cryptosporidium": "Human and animal fecal waste",
    "Turbidity": "Soil runoff",
    "Total Organic Carbon": "Naturally present in the environment",
    "Total Coliform": "Coliforms are bacteria that are normally present in the environment",
    "Haloacetic Acids": "By-product of chlorination",
    "Total Trihalomethanes": "By-product of chlorination",
    "Lead": "Corrosion of household plumbing",
    "Copper": "Corrosion of household plumbing",
    "E. coli": "E.coli are bacteria that are normally present in the environment",
}


@dataclass
class ComplianceResult:
    report_year: int
    contaminant_code: str | None
    contaminant_name: str
    sample_year: int | None
    sample_year_range: str | None
    units: str
    lower_detection_limit: float | None
    upper_detection_limit: float | None
    min_detected: float | None
    avg_system: float | None
    avg_sjcp: float | None
    max_detected: float
    mcl: float | None
    mclg: float | None
    source_url: str
    contaminant_source: str
    max_lraa: float | None
    num_samples_exceeding_action_level: int | None
    ninetieth_percentile: float | None
    action_level: float | None
    uses_treatment_technique: bool


NumericType = TypeVar("NumericType", int, float)


def parse_numeric_value(
    value: str | None, numeric_type: type[NumericType]
) -> NumericType | None:
    if value is None:
        return None
    if value == "":
        return None
    return numeric_type(value)


def parse_TT_values_in_numeric_column(
    value: str | None, numeric_type: type[NumericType]
) -> None:
    if value and value.casefold() == "tt":
        return None
    return parse_numeric_value(value, numeric_type)


def row_uses_treatment_technique(row: dict[str, str | None]) -> bool:
    return any((v or "").strip().casefold() == "tt" for v in row.values())


def add_source_url(value: str | None, year: int) -> str:
    if value:
        return value
    if year in SOURCE_URLS:
        return SOURCE_URLS[year]
    raise ValueError(f"Source URL not found for year {year}")


def add_contaminant_source(value: str | None) -> str:
    if value:
        return value
    if value in CONTAMINANT_SOURCES:
        return CONTAMINANT_SOURCES[value]
    return None


def parse_csv(path: str) -> Iterable[ComplianceResult]:
    with open(path, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            report_year = parse_numeric_value(row["report_year"], int)

            yield ComplianceResult(
                report_year=report_year,
                contaminant_code=row["contaminant_code"],
                contaminant_name=row["contaminant_name"],
                sample_year=parse_numeric_value(row["sample_year"], int),
                sample_year_range=row["sample_year_range"],
                units=row["units"],
                lower_detection_limit=parse_numeric_value(
                    row["lower_detection_limit"], float
                ),
                upper_detection_limit=parse_TT_values_in_numeric_column(
                    row["upper_detection_limit"], float
                ),
                min_detected=parse_TT_values_in_numeric_column(
                    row["min_detected"], float
                ),
                avg_system=parse_TT_values_in_numeric_column(row["avg_system"], float),
                avg_sjcp=parse_TT_values_in_numeric_column(row["avg_sjcp"], float),
                max_detected=parse_TT_values_in_numeric_column(
                    row["max_detected"], float
                ),
                mcl=parse_TT_values_in_numeric_column(row["mcl"], float),
                mclg=parse_TT_values_in_numeric_column(row["mclg"], float),
                source_url=add_source_url(row["source_url"], report_year),
                contaminant_source=add_contaminant_source(row["contaminant_source"]),
                max_lraa=parse_numeric_value(row["max_lraa"], float),
                num_samples_exceeding_action_level=parse_numeric_value(
                    row["num_samples_exceeding_action_level"], int
                ),
                ninetieth_percentile=parse_numeric_value(
                    row["ninetieth_percentile"], float
                ),
                action_level=parse_numeric_value(row["Action Level"], float),
                uses_treatment_technique=row_uses_treatment_technique(row),
            )


def csv_to_db(
    connection: psycopg.Connection, csv_path: str, table_name: str, columns: list[str]
):
    parsed_data = parse_csv(csv_path)

    try:
        with connection.cursor() as cursor:
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            cursor.executemany(
                insert_query,
                [
                    tuple(getattr(data, column) for column in columns)
                    for data in parsed_data
                ],
            )
        connection.commit()
        print(f"Data inserted into {table_name}")
    except psycopg.errors.UniqueViolation:
        print(f"Data already exists in {table_name}")
    except psycopg.errors.ForeignKeyViolation:
        print(f"Data already exists in {table_name}")


def main():
    connection = create_connection()
    columns = list(ComplianceResult.__annotations__)
    csv_to_db(
        connection,
        "data/processed/abcwua/CCR_Compliance_Results.csv",
        "compliance_results",
        columns,
    )
    connection.close()


if __name__ == "__main__":
    main()
