// Hangarin Service Worker
const CACHE_NAME = 'hangarin-cache-v1';
const URLS_TO_CACHE = [
    '/',
    '/account/login/',
    '/static/css/custom.css',
    '/static/css/ready.css',
    '/static/css/bootstrap.min.css',
    '/static/img/profile_default.jpg',
];

// Install: cache essential files
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

// Fetch: try cache first, then network
self.addEventListener('fetch', function (event) {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request).then(function (response) {
            return response || fetch(event.request).then(function (networkResponse) {
                return caches.open(CACHE_NAME).then(function (cache) {
                    cache.put(event.request, networkResponse.clone());
                    return networkResponse;
                });
            });
        }).catch(function () {
            // Offline fallback could go here
        })
    );
});