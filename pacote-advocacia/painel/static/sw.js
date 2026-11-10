// Guarda só a "casca" do painel (telas, estilos, imagens) para abrir rápido no celular.
// Dados de clientes (/api/...) nunca ficam guardados no aparelho.
const VERSAO = "painel-v1";
const CASCA = ["/", "/index.html", "/app.css", "/app.js", "/manifest.webmanifest",
  "/img/logo.png", "/img/monograma.png", "/img/textura.jpg", "/img/icone-192.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSAO).then((c) => c.addAll(CASCA)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSAO).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.pathname.startsWith("/api/")) return; // dados: sempre da rede
  e.respondWith(
    fetch(e.request).then((r) => {
      const copia = r.clone();
      caches.open(VERSAO).then((c) => c.put(e.request, copia));
      return r;
    }).catch(() => caches.match(e.request).then((r) => r || caches.match("/index.html")))
  );
});
