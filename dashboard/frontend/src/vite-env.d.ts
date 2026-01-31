/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_DISCORD_CLIENT_ID: string
  readonly VITE_TOSS_CLIENT_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
