import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import type { ViteDevServer } from "vite";

function securityHeadersPlugin() {
  return {
    name: "security-headers",
    configureServer(server: ViteDevServer) {
      server.middlewares.use((_req: any, res: any, next: any) => {
        res.setHeader("X-Content-Type-Options", "nosniff");
        res.setHeader("X-Frame-Options", "DENY");
        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [securityHeadersPlugin(), react()],
  server: {
    port: 5173,
    host: "127.0.0.1",
  },
});
