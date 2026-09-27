/* SPEC-027 PWA — install cache shell + fetch: cache-first nav, network-first API */
const CACHE = "swiss-p-map-v2";
const SHELL = ["/de", "/en", "/fr", "/it", "/manifest.json", "/icon-192.png", "/icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL).catch(() => undefined)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  const isApi = url.pathname.startsWith("/api/");
  const isNav = e.request.mode === "navigate" || (e.request.headers.get("accept") || "").includes("text/html");

  if (isApi) {
    // network-first for API
    e.respondWith(
      fetch(e.request)
        .then((r) => {
          const copy = r.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
          return r;
        })
        .catch(() => caches.match(e.request).then((r) => r || Response.error())),
    );
    return;
  }

  if (isNav) {
    // cache-first for navigations/shell
    e.respondWith(
      caches.match(e.request).then((cached) => {
        const fetched = fetch(e.request)
          .then((r) => {
            const copy = r.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copy));
            return r;
          })
          .catch(() => cached || caches.match("/de"));
        return cached || fetched;
      }),
    );
    return;
  }

  // other GET (assets): stale-while-revalidate
  e.respondWith(
    caches.match(e.request).then((cached) => {
      const fetched = fetch(e.request)
        .then((r) => {
          const copy = r.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
          return r;
        })
        .catch(() => cached);
      return cached || fetched;
    }),
  );
});

self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : { title: "Swiss P Map", body: "Neue Meldung" };
  event.waitUntil(self.registration.showNotification(data.title, { body: data.body, data: data.url || "/de" }));
});
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data || "/de"));
});
