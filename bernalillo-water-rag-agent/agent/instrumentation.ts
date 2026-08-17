// agent/instrumentation.ts
import { defineInstrumentation } from "eve/instrumentation";
import { registerOTel } from "@vercel/otel";
import {
  isOpenInferenceSpan,
  OpenInferenceSimpleSpanProcessor,
} from "@arizeai/openinference-vercel";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";

export default defineInstrumentation({
  setup: ({ agentName }) => {
    // Route to the project named by ARIZE_PROJECT_NAME (falling back to the agent
    // name), matching the ARIZE_PROJECT_NAME convention used across the Arize docs.
    const projectName = process.env.ARIZE_PROJECT_NAME ?? agentName;
    return registerOTel({
      serviceName: projectName,
      attributes: { model_id: projectName },
      spanProcessors: [
        new OpenInferenceSimpleSpanProcessor({
          exporter: new OTLPTraceExporter({
            url: "https://otlp.arize.com/v1/traces",
            headers: {
              "arize-space-id": process.env.ARIZE_SPACE_ID ?? "",
              "arize-api-key": process.env.ARIZE_API_KEY ?? "",
            },
          }),
          spanFilter: isOpenInferenceSpan,
          reparentOrphanedSpans: true,
        }),
      ],
    });
  },
});