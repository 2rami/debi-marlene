export default function Loading() {
  return (
    <div className="min-h-screen bg-discord-darkest flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-4 border-discord-dark" />
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-debi-primary animate-spin" />
        </div>
        <span className="text-discord-muted">Loading...</span>
      </div>
    </div>
  )
}
