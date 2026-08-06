-- Enable pgvector for embedding columns (e.g. vector(384) MiniLM).
-- Runs only on first DB init (empty volume). On an existing volume, run manually:
--   CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS vector;
