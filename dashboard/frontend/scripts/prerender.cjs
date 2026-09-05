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
  '/', '/landing', '/commands', '/docs', '/bot-guide', '/terms', '/privacy', '/about',
  '/guide/faq', '/guide/eternal-return', '/guide/tier-season', '/guide/characters',
  '/guide/tts', '/guide/music', '/guide/welcome', '/guide/credits',
  '/guide/record', '/guide/stats', '/guide/quiz', '/guide/server-setup',
]

// 광고 도메인. 프리렌더 시점에 자동광고가 돌면 그 결과(빈 슬롯 + aswift iframe)가
// page.content() 에 그대로 굳어 정적 HTML 에 박힌다. 굳은 슬롯은 data-adsbygoogle-status="done"
// 이라 실사용자 브라우저의 adsbygoogle.js 가 처리 대상에서 건너뛰고, 광고가 영영 안 채워진다.
// 게다가 그 슬롯의 광고 요청 url 파라미터에 빌드 머신 주소(localhost:4178)가 박혀 나간다.
const AD_HOSTS = /googlesyndication\.com|doubleclick\.net|googletagservices\.com/

const ORIGIN = 'https://debimarlene.com'

// 같은 문서가 /guide/tts 와 /guide/tts/ 두 주소로 열린다(서버가 308 로 이어 준다).
// canonical 이 없으면 구글이 어느 쪽을 정본으로 삼을지 스스로 고르고, 그 판단이
// 갈리면 색인 가치가 두 주소로 쪼개진다. 정규형(끝 슬래시)을 못박는다.
//
// '/' 는 캐릭터 선택 인트로다 — 2.2초 카운트업 뒤 /landing 으로 넘어가는 관문이라
// 본문이 142자뿐이다. 그래서 정본을 /landing/ 으로 넘긴다. 크롤러에게 다른 화면을
// 보여주는 것이 아니라, 실제 목적지를 알려 주는 것이다.
const canonicalFor = (route) =>
  route === '/' ? `${ORIGIN}/landing/` : `${ORIGIN}${route}/`

const AD_LEFTOVERS =
  'ins.adsbygoogle, iframe[id^="aswift_"], iframe[id^="google_ads_iframe"], ' +
  'div[id^="google_ads_iframe"], .google-auto-placed, [data-google-query-id]'

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
        // 테마는 localStorage 없으면 prefers-color-scheme 을 따른다. 고정하지 않으면
        // 빌드한 사람의 맥 설정이 정적 HTML 의 <html class="dark"> 로 굳어 전 사용자 첫 화면에 샌다.
        await page.emulateMediaFeatures([
          { name: 'prefers-color-scheme', value: 'light' },
        ])
        await page.setRequestInterception(true)
        page.on('request', (req) => {
          if (AD_HOSTS.test(req.url())) req.abort().catch(() => {})
          else req.continue().catch(() => {})
        })
        await page.goto(`http://localhost:${PORT}${route}`, {
          waitUntil: 'networkidle0',
          timeout: 30000,
        })
        await sleep(400) // 애니메이션/레이지 콘텐츠 안정화
        await page.evaluate((sel) => {
          document.querySelectorAll(sel).forEach((el) => el.remove())
        }, AD_LEFTOVERS)
        await page.evaluate((href) => {
          document.querySelectorAll('link[rel="canonical"]').forEach((el) => el.remove())
          const link = document.createElement('link')
          link.rel = 'canonical'
          link.href = href
          document.head.appendChild(link)
        }, canonicalFor(route))
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
