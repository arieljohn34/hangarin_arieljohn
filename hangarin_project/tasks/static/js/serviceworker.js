// Hangarin Service Worker
const CACHE_NAME = 'hangarin-cache-v2';  // ← bumped so old cache is discarded

// ONLY static assets — never HTML pages, never anything with a CSRF token
const URLS_TO_CACHE = [
    '/static/css/custom.css',
    '/static/css/ready.css',
    '/static/css/bootstrap.min.css',
    '/static/js/core/jquery.3.2.1.min.js',
    '/static/js/core/bootstrap.min.js',
    '/static/img/profile_default.jpg',
    '/static/img/hangarin_icon-192x192.png',
    '/static/img/hangarin_icon-512x512.png',
];

// Install: cache static assets only
self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(URLS_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// Activate: delete old caches
self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys.filter(function (key) {
                    return key !== CACHE_NAME;
                }).map(function (key) {
                    return caches.delete(key);
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch: only cache static assets, NEVER HTML navigations
self.addEventListener('fetch', function (event) {
    const req = event.request;

    // 1. Only handle GET requests
    if (req.method !== 'GET') return;

    // 2. NEVER cache navigation requests (HTML pages) — always hit the network
    if (req.mode === 'navigate') return;

    // 3. Only cache same-origin static assets
    const url = new URL(req.url);
    if (url.origin !== self.location.origin) return;
    if (!/\.(css|js|png|jpe?g|gif|svg|woff2?|ttf|eot|ico)$/i.test(url.pathname)) return;

    event.respondWith(
        caches.match(req).then(function (cached) {
            if (cached) return cached;
            return fetch(req).then(function (networkResponse) {
                // Only cache successful responses
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                    return networkResponse;
                }
                const clone = networkResponse.clone();
                caches.open(CACHE_NAME).then(function (cache) {
                    cache.put(req, clone);
                });
                return networkResponse;
            });
        })
    );
});