// Offline support: keeps the page, its data tables and Chart.js available
// without a connection. Sheet data itself is cached by the page in localStorage.
const CACHE = "archery-tracker-v1";
const SHELL = ["./", "agb-data.js", "manifest.webmanifest", "icon-192.png", "icon-512.png"];
const CDN = ["https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.js"];

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (c) {
    // The CDN copy is a bonus: if it can't be fetched now it is cached on first use.
    return c.addAll(SHELL).then(function () { return Promise.all(CDN.map(function (u) { return c.add(u).catch(function () {}); })); });
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (event) {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;
  if (!sameOrigin && url.hostname !== "cdn.jsdelivr.net") return; // Google Sheets, analytics: network only

  if (req.mode === "navigate") {
    // Page: fresh when online, cached copy when not.
    event.respondWith(fetch(req).then(function (res) {
      const copy = res.clone();
      caches.open(CACHE).then(function (c) { c.put("./", copy); });
      return res;
    }).catch(function () {
      return caches.match("./");
    }));
    return;
  }
  // Everything else: cached copy straight away, refreshed in the background.
  event.respondWith(caches.match(req).then(function (hit) {
    const net = fetch(req).then(function (res) {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, copy); }); }
      return res;
    });
    return hit || net;
  }));
});
