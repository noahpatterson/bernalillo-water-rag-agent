import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from embedder import Embedder
from tools.retrieval import FusedHit, Retrieval
from tools.lookup_compliance import lookup_compliance
from tools.lookup_contaminant_info import contaminant_info
from utils.utils import ContaminantValueType, create_connection

load_dotenv()

embedder = Embedder(
    execution_provider=os.getenv("ONNX_EXECUTION_PROVIDER", "CPUExecutionProvider"),
)
connection = create_connection()

class LookupComplianceParams(BaseModel):
    contaminant: str
    report_year: int | None = Field(default=None, ge=2020, le=2025)
    report_year_range: tuple[int, int] | None = None
    sample_year: int | None = Field(default=None, ge=2020, le=2025)
    sample_year_range: tuple[int, int] | None = None
    value_type: ContaminantValueType | None = None

app = FastAPI()

@app.get(
    "/lookup_compliance",
    operation_id="lookup_compliance",
    summary=(
        "lookup_compliance: measured contaminant levels, MCL, compliance "
        "monitoring results, arsenic nitrate lead copper by report year"
    ),
)
async def run_lookup_compliance(request: Annotated[LookupComplianceParams, Query()]):
    result = lookup_compliance(
        connection=connection,
        **request.model_dump(exclude_none=True),
    )
    return result

@app.get(
    "/lookup_contaminant_info",
    operation_id="lookup_contaminant_info",
    summary=(
        "lookup_contaminant_info: contaminant information, EPA standards, "
        "what a contaminant is, units, health effects"
    ),
)
def run_lookup_contaminant_info(contaminant: str):
    result = contaminant_info(
        connection=connection,
        contaminant=contaminant,
    )
    return result

@app.get(
    "/search",
    operation_id="search",
    summary=(
        "search: Albuquerque water quality reports, CCR PDFs, source water, "
        "treatment, narrative FAQ, customer water quality report"
    ),
    response_model=list[FusedHit],
)
def run_search(query: str) -> list[FusedHit]:
    retrieval = Retrieval(embedder=embedder, connection=connection)
    results_vec = retrieval.pgvector_search(query, num_results=20)
    results_soft_fts = retrieval.pg_full_text_search_soft_match(query, num_results=20)
    results = retrieval.new_rrf(results_vec, results_soft_fts, num_results=5)
    return results

@app.get("/health", operation_id="health_check")
def health_check():
  return {"status": "healthy"}
