import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  base: "./",
  define: {
    "import.meta.env.VITE_API_BASE_URL": JSON.stringify("http://127.0.0.1:11238/api/v1"),
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-router-dom"],
          vendor: ["@tanstack/react-query", "zustand"],
        },
      },
    },
  },
  server: {
    allowedHosts: ["goliath"],
    port: 10842,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      "/api": {
        target: "http://127.0.0.1:10843",
        changeOrigin: true,
      },
    },
  },
});
