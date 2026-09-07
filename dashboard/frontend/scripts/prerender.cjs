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

// 프리렌더 전에는 모든 라우트가 index.html 의 <title> 하나를 공유했다. 검색 결과에 전 페이지가
// "Debi Marlene Dashboard" 로 뜨고, 제목·설명이 같으니 구글은 서로 다른 문서를 같은 문서로 본다
// (2026-09-06 서치콘솔: /guide/faq/ 와 /guide/eternal-return/ 이 "사용자가 선택한 표준이 없는
// 중복 페이지"로 색인 제외). SPA 라 라우터가 문서 메타를 바꿔 주지 않으므로 여기서 박는다.
const BRAND = 'Debi & Marlene'
const withBrand = (t) => (t.includes('Marlene') ? t : `${t} · ${BRAND}`)

const LANDING_META = {
  title: 'Debi & Marlene · 이터널 리턴 전적 검색 디스코드 봇',
  description:
    '이터널 리턴 전적 검색, TTS 음성 읽기, 음악 재생과 퀴즈, 환영 카드까지 — 디스코드 서버 운영에 필요한 기능을 하나로 묶은 봇입니다.',
}

// 루트는 canonical 을 /landing/ 으로 넘기므로 메타도 같은 것을 쓴다. 구글이 표준을 뒤집어
// 루트를 골라도(2026-09-06 실제로 그랬다) 검색 결과 문구는 랜딩의 것이 뜬다.
const META = {
  '/': LANDING_META,
  '/landing': LANDING_META,
  '/commands': {
    title: '명령어 목록',
    description:
      '전적 검색, 캐릭터 통계, TTS, 음악, 퀴즈, 서버 설정까지 Debi & Marlene 봇의 모든 명령어를 한곳에 모았습니다. 클릭 한 번으로 복사해 바로 쓰세요.',
  },
  '/docs': {
    title: '사용 설명서',
    description:
      '봇 초대부터 대시보드 사용법, 음성과 TTS, 음악 재생, 문의까지 Debi & Marlene 을 시작하는 데 필요한 안내를 모았습니다.',
  },
  '/about': {
    title: 'Debi & Marlene 소개',
    description:
      '이터널 리턴을 즐기는 한국 디스코드 커뮤니티를 위해 만든 다기능 봇입니다. 전적 검색, 음성 읽기, 음악, 음악 퀴즈, 환영 카드를 하나의 봇으로 묶었습니다.',
  },
  '/bot-guide': {
    title: 'Intent 요청 안내',
    description:
      'Debi & Marlene 봇이 사용하는 Discord Privileged Gateway Intents 세 가지와, 개발자 포털 승인 심사 항목에 대한 답변을 정리했습니다.',
  },
  '/guide/faq': {
    title: '자주 묻는 질문',
    description:
      '봇 초대, 이터널 리턴 전적 검색, TTS 음성, 음악, 크레딧까지 처음 쓰는 분들이 가장 많이 묻는 질문을 모았습니다.',
  },
  '/guide/eternal-return': {
    title: '이터널 리턴 전적 검색 가이드',
    description:
      '/전적 명령어 하나로 디스코드를 떠나지 않고 시즌 MMR, 평균 순위, 모스트 캐릭터, 최근 경기를 한눈에 확인하는 방법을 정리했습니다.',
  },
  '/guide/record': {
    title: '전적 검색 결과 읽는 법',
    description:
      '/전적 화면에 뜨는 MMR, 평균 순위, 승률, 모스트 캐릭터가 각각 무엇을 뜻하는지 숫자 하나씩 짚어 설명합니다.',
  },
  '/guide/stats': {
    title: '캐릭터 통계 보는 법',
    description:
      '/통계 로 지금 잘 나가는 실험체를 승률과 픽률로 확인하는 법. 승률만 보고 픽을 고르면 왜 자주 실패하는지도 함께 다룹니다.',
  },
  '/guide/tier-season': {
    title: '티어와 시즌 가이드',
    description:
      '이터널 리턴 랭크의 MMR 과 티어 구간, 시즌이 끝나는 시점, 막바지에 티어를 굳히는 방법을 봇 명령어와 함께 정리했습니다.',
  },
  '/guide/characters': {
    title: '캐릭터 통계 활용 가이드',
    description:
      '시즌마다 바뀌는 메타를 /통계 로 읽는 법. 픽률과 승률을 함께 봐야 하는 이유와 실전에서 캐릭터를 고르는 기준을 설명합니다.',
  },
  '/guide/tts': {
    title: 'TTS 음성 가이드',
    description:
      '채팅에 쓴 글을 데비 또는 마를렌의 목소리로 읽어 주는 TTS 사용법. 음성 채널로 봇을 부르는 법부터 목소리 바꾸기까지 안내합니다.',
  },
  '/guide/music': {
    title: '음악과 퀴즈 가이드',
    description:
      '/음악 으로 YouTube 곡을 재생하는 법, 재생이 안 될 때 확인할 것, 친구들과 즐기는 음악 퀴즈 진행법을 담았습니다.',
  },
  '/guide/quiz': {
    title: '퀴즈로 서버 사람들과 놀기',
    description:
      '노래 맞히기, 이터널 리턴 지식 겨루기, 직접 문제 내기까지 /퀴즈 로 서버 사람들과 함께 즐기는 미니게임을 안내합니다.',
  },
  '/guide/welcome': {
    title: '환영 메시지와 서버 설정 가이드',
    description:
      '커스텀 환영 이미지 카드, 자동 역할 부여, YouTube 채널 알림을 /설정 명령어와 대시보드에서 관리하는 방법을 정리했습니다.',
  },
  '/guide/credits': {
    title: '크레딧과 AI 대화 가이드',
    description:
      'AI 대화와 TTS 를 움직이는 크레딧이 무엇인지, 출석과 충전으로 모으는 법, 어디에 얼마나 쓰이는지 한 페이지에 정리했습니다.',
  },
  '/guide/server-setup': {
    title: '서버 관리자를 위한 설정 안내',
    description:
      '봇을 초대한 다음 무엇부터 만져야 하는지 — 명령을 받을 채널과 알림 보낼 곳을 정하는 방법을 관리자 관점에서 안내합니다.',
  },
  '/terms': {
    title: '이용약관',
    description:
      'Debi & Marlene 봇과 debimarlene.com 대시보드 이용에 관한 약관입니다.',
  },
  '/privacy': {
    title: '개인정보처리방침',
    description:
      'Debi & Marlene 봇과 대시보드가 수집하는 정보의 항목, 이용 목적, 보관과 파기 절차를 안내합니다.',
  },
}

const metaFor = (route) => {
  const m = META[route] || LANDING_META
  return { title: withBrand(m.title), description: m.description }
}

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
        await page.evaluate((m) => {
          const put = (sel, attr, key, value) => {
            let el = document.head.querySelector(sel)
            if (!el) {
              el = document.createElement('meta')
              el.setAttribute(attr, key)
              document.head.appendChild(el)
            }
            el.setAttribute('content', value)
          }
          document.title = m.title
          put('meta[name="description"]', 'name', 'description', m.description)
          put('meta[property="og:title"]', 'property', 'og:title', m.title)
          put('meta[property="og:description"]', 'property', 'og:description', m.description)
          put('meta[property="og:url"]', 'property', 'og:url', m.canonical)
          put('meta[name="twitter:title"]', 'name', 'twitter:title', m.title)
          put('meta[name="twitter:description"]', 'name', 'twitter:description', m.description)
          document.querySelectorAll('link[rel="canonical"]').forEach((el) => el.remove())
          const link = document.createElement('link')
          link.rel = 'canonical'
          link.href = m.canonical
          document.head.appendChild(link)
        }, { ...metaFor(route), canonical: canonicalFor(route) })
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
