// agent/connections/knowledge.ts
import { defineOpenAPIConnection } from "eve/connections";

// Host `pnpm dev` talks to the published FastAPI port. The Docker image sets
// KNOWLEDGE_API_BASE_URL=http://api.localhost:8000 at `eve build` time because
// the bundler inlines this URL into .output.
export default defineOpenAPIConnection({
  spec: `${process.env.KNOWLEDGE_API_BASE_URL ?? "http://127.0.0.1:8000"}/openapi.json`,
  baseUrl: process.env.KNOWLEDGE_API_BASE_URL ?? "http://127.0.0.1:8000",
  description:
    "Albuquerque Water authority yearly water quality report database. Search it before answering questions about compliance requirements, contaminants, or information from the water quality reports pdfs.",
  operations: {
    allow: [
      "lookup_compliance",
      "lookup_contaminant_info",
      "search"
    ],
  },
});
