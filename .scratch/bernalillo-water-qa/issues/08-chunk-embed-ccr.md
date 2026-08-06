# Decide CCR chunking and embeddings

Type: grilling
Status: resolved
Blocked by: 03
Claimed by: wayfinder session

## Question

How will we chunk and embed CCR knowledge-base text (narrative around treatment, monitoring, definitions, FAQs—excluding or specially handling the compliance tables)—chunk boundaries, size/overlap, embedding model/API—so retrieval fixtures can label relevant chunk IDs and hybrid (pgvector + FTS) stays coherent?

## Answer

**PDF → text:** **`pymupdf` (fitz)** for page/layout-aware extraction before chunking. GuardDog flagged `pymupdf` 1.28.0 `repository_integrity_mismatch` on **`./COPYING` only** (license text vs GitHub)—accepted as heuristic noise; pin a version and re-scan; revisit if non-license files differ. Compliance **table** extract may refine this in [Decide COMPLIANCE MONITORING RESULTS extract and table schema](10-compliance-table-schema.md).

**Chunking:** Section-aware on CCR headings / major blocks (source water, treatment, monitoring, definitions, FAQ). Oversized sections → ~**400–800 tokens** with ~**10–15% overlap**. Metadata per chunk: `report_year`, `section`, `source_url`, stable chunk id.

**Compliance tables in KB:** **Strip table bodies** from embeddings (tool owns exact numbers). Keep a **one-line stub chunk per year** (“{year} COMPLIANCE MONITORING RESULTS — use compliance tool”).

**Embeddings:** Free local MiniLM via Zoomcamp ONNX path — download once to `models/Xenova/all-MiniLM-L6-v2/`, run with **onnxruntime + tokenizers** (course `Embedder`). **`vector(384)`** in pgvector. Same encode path for ingest and query. `models/` gitignored.
