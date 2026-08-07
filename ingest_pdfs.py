import datetime
import json
import psycopg
import pymupdf4llm
from utils.utils import create_connection
import os
from embedder import Embedder

def read_pdf_to_json(pdf_path: str) -> dict:
  return pymupdf4llm.to_json(pdf_path)

def remove_tables_from_chunk(chunk: dict) -> dict:
  boxes     = chunk["page_boxes"]
  new_chunk = chunk.copy()
  for box in boxes:
    if box['class'] == 'table':
      # remove the text from chunk['text'] that is within the box
      start, end = box["pos"]
      new_chunk['text'] = new_chunk['text'][:start] + new_chunk['text'][end:]
  return new_chunk

def clean_chunk(chunk: dict) -> dict:
  new_chunk = remove_tables_from_chunk(chunk)
  new_chunk['metadata'] = {
    'file_path': chunk['metadata']['file_path'],
    'page_number': chunk['metadata']['page_number'],
    'page_count': chunk['metadata']['page_count']
  }
  new_chunk.pop('page_boxes', None)
  new_chunk.pop('toc_items', None)
  return new_chunk

def append_metadata_to_chunk(chunk: dict, year: int, url: str, chunk_id: int) -> dict:
  new_chunk = chunk.copy()
  new_chunk['metadata'].update({'year': year, 'url': url, 'chunk_id': chunk_id})
  return new_chunk  

def read_pdf_to_chunks(pdf_path: str, year: int, url: str) -> list[dict]:
  for chunk_id, chunk in enumerate(pymupdf4llm.to_markdown(pdf_path, page_chunks=True)):
    cleaned_chunk = clean_chunk(chunk)
    cleaned_chunk = append_metadata_to_chunk(cleaned_chunk, year, url, chunk_id)
    yield cleaned_chunk


MIN_CHUNK_CHARS = 100

def insert_chunk(
  connection: psycopg.Connection,
  *,
  year: int,
  section: str,
  source_url: str,
  text: str,
  embedding: list[float],
) -> None:
  connection.execute(
    """
    INSERT INTO knowledge_base_chunks
      (ingested_date, report_year, section, source_url, text, embedding)
    VALUES (%s, %s, %s, %s, %s, %s)
    """,
    (datetime.datetime.now(), year, section, source_url, text, embedding),
  )

def ingest_pdf(connection: psycopg.Connection, pdf_path: str, year: int, url: str) -> None:
  chunks = list(read_pdf_to_chunks(pdf_path, year, url))
  connection.execute(
    "DELETE FROM knowledge_base_chunks WHERE report_year = %s",
    (year,),
  )
  embedder = Embedder()
  for chunk in chunks:
    text = chunk["text"].strip()
    if len(text) < MIN_CHUNK_CHARS:
      continue
    meta = chunk["metadata"]
    insert_chunk(
      connection,
      year=meta["year"],
      section=f"page_{meta['page_number']}",
      source_url=meta["url"],
      text=text,
      embedding=embedder.encode(text).tolist(),
    )

  stub_text = f"{year} COMPLIANCE MONITORING RESULTS — use compliance tool"
  insert_chunk(
    connection,
    year=year,
    section="compliance_monitoring_results",
    source_url=url,
    text=stub_text,
    embedding=embedder.encode(stub_text).tolist(),
  )
  connection.commit()

if __name__ == "__main__":
  connection = create_connection()
  # read SOURCE.txt and ingest each pdf
  with open("data/raw/abcwua/SOURCE.txt", "r") as f:
    for line in f:
      if line.startswith("-"):
        pdf_name, url = line.strip().removeprefix("- ").split(" ← ", 1)
        full_pdf_path = os.path.join("data/raw/abcwua", pdf_name)
        year = int(pdf_name.removesuffix(".pdf").rsplit("-", 1)[-1])
        ingest_pdf(connection, full_pdf_path, year, url)
  connection.close()