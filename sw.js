// 원어 성경 서비스 워커: 인터넷 없이도 앱이 열리도록 파일을 기기에 보관합니다.
// 앱 화면(index.html 등)을 고친 뒤에는 VERSION 숫자를 올려 주세요. 그래야 설치된 앱도 새 화면으로 바뀝니다.
// 성경 데이터(data/books, krv, search)를 다시 만들었을 때는 DATA_CACHE 숫자를 올려 주세요(index.html의 DATA_CACHE도 같이).
const VERSION = 'v7';
const CORE_CACHE = 'ob-core-' + VERSION;
const DATA_CACHE = 'ob-data-v1';
const CORE = [
  './', 'index.html', 'manifest.json', 'fonts/fonts.css',
  'fonts/gentium-400-greek.woff2', 'fonts/gentium-400-greek-ext.woff2', 'fonts/gentium-400-latin.woff2', 'fonts/gentium-400-latin-ext.woff2',
  'fonts/gentium-400i-greek.woff2', 'fonts/gentium-400i-greek-ext.woff2', 'fonts/gentium-400i-latin.woff2', 'fonts/gentium-400i-latin-ext.woff2',
  'fonts/gentium-700-greek.woff2', 'fonts/gentium-700-greek-ext.woff2', 'fonts/gentium-700-latin.woff2', 'fonts/gentium-700-latin-ext.woff2',
  'fonts/noto-400-hebrew.woff2', 'fonts/noto-400-latin.woff2', 'fonts/noto-600-hebrew.woff2', 'fonts/noto-600-latin.woff2',
  'fonts/plexkr-400.woff2', 'fonts/plexkr-500.woff2', 'fonts/plexkr-600.woff2',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png',
  'data/pt.json', 'data/glx.json', 'data/hlx.json'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CORE_CACHE).then(c => c.addAll(CORE.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys
    .filter(k => k.startsWith('ob-') && k !== CORE_CACHE && k !== DATA_CACHE)
    .map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // 성경 책, 한국어 성경, 검색 자료: 저장된 것이 있으면 바로 쓰고, 없으면 받아서 저장
  if (/\/data\/(books|krv|search)\//.test(url.pathname)) {
    e.respondWith(caches.open(DATA_CACHE).then(async c => {
      const hit = await c.match(req, { ignoreSearch: true });
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) c.put(req, res.clone());
      return res;
    }));
    return;
  }

  // 앱 화면과 앱 설명 파일(manifest): 인터넷이 되면 최신 파일, 안 되면 저장된 파일
  if (req.mode === 'navigate' || url.pathname.endsWith('/manifest.json')) {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CORE_CACHE).then(c => c.put(req.mode === 'navigate' ? 'index.html' : 'manifest.json', copy)); }
      return res;
    }).catch(() => caches.match(req.mode === 'navigate' ? 'index.html' : 'manifest.json', { cacheName: CORE_CACHE })));
    return;
  }

  // 나머지(글꼴, 사전, 아이콘): 저장된 것을 먼저
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => hit || fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CORE_CACHE).then(c => c.put(req, copy)); }
    return res;
  })));
});
