// 공개 라우트를 puppeteer 로 정적 HTML 프리렌더.
// SPA(빈 #root)라 크롤러가 본문을 못 읽는 문제 해결 — AdSense "low value content" 거절 대응.
// nginx try_files $uri $uri/ /index.html + index index.html 이라 dist/{route}/index.html 이
// 있으면 nginx 가 자동 서빙한다 (nginx 수정 불필요).
//
// 빌드 실패를 막기 위해 어떤 단계가 실패해도 exit 0 (프리렌더는 부가 작업).
const { spawn } = require('child_process')
const fs = require('fs')
const path = require('path')

const DIST = path.resolve(__dirname, '..', 'dist')
const PORT = 4178
// portfolio/* (채용 전용·광고 차단), 로그인·결제·동적 데이터 경로는 제외.
const ROUTES = [
  '/', '/landing', '/commands', '/docs', '/bot-guide', '/terms', '/about',
  '/guide/faq', '/guide/eternal-return', '/guide/tier-season', '/guide/characters',
  '/guide/tts', '/guide/music', '/guide/welcome', '/guide/credits',
]

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

;(async () => {
  let puppeteer
  try {
    puppeteer = require('puppeteer')
  } catch {
    console.log('[prerender] puppeteer 미설치 — 건너뜀 (빌드 계속)')
    return
  }
  if (!fs.existsSync(DIST)) {
    console.log('[prerender] dist 없음 — 건너뜀')
    return
  }

  const preview = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], {
    cwd: path.resolve(__dirname, '..'),
    stdio: 'ignore',
  })

  await sleep(3500) // preview 서버 기동 대기

  let browser
  try {
    browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] })
    for (const route of ROUTES) {
      const page = await browser.newPage()
      try {
        await page.goto(`http://localhost:${PORT}${route}`, {
          waitUntil: 'networkidle0',
          timeout: 30000,
        })
        await sleep(400) // 애니메이션/레이지 콘텐츠 안정화
        const html = await page.content()
        const outPath =
          route === '/'
            ? path.join(DIST, 'index.html')
            : path.join(DIST, route, 'index.html')
        fs.mkdirSync(path.dirname(outPath), { recursive: true })
        fs.writeFileSync(outPath, html, 'utf-8')
        console.log(`[prerender] ${route} -> ${path.relative(DIST, outPath)}`)
      } catch (e) {
        console.log(`[prerender] ${route} 실패: ${e.message}`)
      } finally {
        await page.close()
      }
    }
  } catch (e) {
    console.log(`[prerender] 브라우저 실패: ${e.message}`)
  } finally {
    if (browser) await browser.close()
    preview.kill()
  }
})()
