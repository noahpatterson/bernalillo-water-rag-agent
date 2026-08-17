// agent/connections/knowledge.ts
import { defineOpenAPIConnection } from "eve/connections";

// Host `pnpm dev` talks to the published FastAPI port. Compose overrides this
// to http://api.localhost:8000 so Eve can use HTTP (loopback-style hostname)
// while Docker DNS routes it to the api service.
const knowledgeApiBaseUrl =
  process.env.KNOWLEDGE_API_BASE_URL ?? "http://127.0.0.1:8000";

export default defineOpenAPIConnection({
  spec: `${knowledgeApiBaseUrl}/openapi.json`,
  baseUrl: knowledgeApiBaseUrl,
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
