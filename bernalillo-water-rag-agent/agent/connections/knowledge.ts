// agent/connections/knowledge.ts
import { defineOpenAPIConnection } from "eve/connections";

export default defineOpenAPIConnection({
  spec: "http://127.0.0.1:8000/openapi.json",
  baseUrl: "http://127.0.0.1:8000",
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
