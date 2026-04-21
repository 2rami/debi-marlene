const envValue = import.meta.env.VITE_DISCORD_CLIENT_ID

export const DISCORD_CLIENT_ID =
  envValue && envValue !== 'undefined' ? envValue : '1393529860793831489'
