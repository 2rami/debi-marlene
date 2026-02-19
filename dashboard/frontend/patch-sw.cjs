// SW 빌드 후 NavigationRoute에 /api/ denylist 주입
const fs = require('fs')
const path = require('path')

const swPath = path.resolve(__dirname, 'dist/sw.js')

try {
  let sw = fs.readFileSync(swPath, 'utf-8')
  const before = 'new e.NavigationRoute(e.createHandlerBoundToURL("index.html"))'
  const after = 'new e.NavigationRoute(e.createHandlerBoundToURL("index.html"),{denylist:[/^\\/api\\//]})'

  if (sw.includes(before)) {
    sw = sw.replace(before, after)
    fs.writeFileSync(swPath, sw)
    console.log('SW patched: added /api/ denylist to NavigationRoute')
  } else {
    console.log('SW patch: NavigationRoute pattern not found, skipping')
  }
} catch (e) {
  console.error('SW patch failed:', e.message)
}
