const CACHE_NAME = '2fa-pub-cache-v8';
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/google-extractor',
  '/qr-generator',
  '/steam',
  '/vault',
  '/cli',
  '/manifest.json',
  '/assets/tailwind.css',
  '/assets/fonts/fonts.css',
  '/assets/vendor/lucide.min.js',
  '/assets/vendor/jsQR.min.js',
  '/assets/vendor/qrcode.min.js',
  '/assets/icon-64.png',
  '/assets/icon-180.png',
  '/assets/icon-192.png',
  '/assets/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      Promise.all(PRECACHE_ASSETS.map((url) => cache.add(url).catch(() => undefined)))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Do not intercept analytics, ads, or Cloudflare trace endpoints
  if (
    url.pathname === '/cdn-cgi/trace' ||
    (url.origin !== self.location.origin &&
      (url.hostname.includes('google-analytics.com') ||
       url.hostname.includes('googletagmanager.com') ||
       url.hostname.includes('googlesyndication.com') ||
       url.hostname.includes('doubleclick.net') ||
       url.hostname.includes('adtrafficquality.google') ||
       url.hostname.includes('cloudflareinsights.com')))
  ) {
    return;
  }

  // Navigations: network-first so site updates land immediately; cache is the offline fallback.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy)).catch(() => undefined);
          return response;
        })
        .catch(() => caches.match(request).then((cached) => cached || caches.match('/index.html')))
    );
    return;
  }

  // Same-origin static assets: stale-while-revalidate — serve the cached copy
  // instantly, refresh the cache from the network in the background so new
  // deploys propagate on the next visit without cache-version bumps.
  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy)).catch(() => undefined);
          }
          return response;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
