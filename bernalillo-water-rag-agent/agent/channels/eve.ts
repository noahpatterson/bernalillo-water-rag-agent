import { eveChannel } from "eve/channels/eve";
import { localDev, none, placeholderAuth, vercelOidc } from "eve/channels/auth";

// Compose sets EVE_ALLOW_ANONYMOUS=1 so the production Next.js image can
// serve the chat without a real identity provider. Host `pnpm dev` still
// uses localDev() and does not need this flag.
const allowAnonymous = process.env.EVE_ALLOW_ANONYMOUS === "1";

export default eveChannel({
  auth: [
    // Lets the eve TUI and your Vercel deployments reach the deployed agent.
    vercelOidc(),
    // Open on localhost for `eve dev` and the REPL; ignored in production.
    localDev(),
    // This placeholder will not allow browser requests in production.
    // Replace it with your app's auth provider, like Auth.js or Clerk,
    // or use none() for a public demo.
    allowAnonymous ? none() : placeholderAuth(),
  ],
});
