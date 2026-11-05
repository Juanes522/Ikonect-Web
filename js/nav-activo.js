/* Navegación: marca el enlace de la sección visible (aria-current) y desliza el indicador del menú de escritorio */
(function () {
  "use strict";
  function inicio() {
    var nav = document.getElementById("menu-principal");
    var indicador = nav && nav.querySelector(".site-nav__indicador");
    var enlaces = nav ? Array.prototype.slice.call(nav.querySelectorAll(".site-nav__lista a[href^='#']")) : [];
    if (!nav || !enlaces.length || !("IntersectionObserver" in window)) return;

    var porId = {};
    enlaces.forEach(function (a) { porId[a.getAttribute("href").slice(1)] = a; });
    var secciones = ["inicio"].concat(Object.keys(porId))
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    var activo = null;

    // Solo transform y opacity: el indicador mide 100 px y se escala al ancho del enlace
    function ubicar(instantaneo) {
      if (!indicador) return;
      if (!activo || !activo.offsetWidth) { indicador.classList.remove("is-visible"); return; }
      var base = nav.getBoundingClientRect();
      var caja = activo.getBoundingClientRect();
      var aparece = !indicador.classList.contains("is-visible");
      if (aparece || instantaneo) indicador.classList.add("sin-transicion");
      indicador.style.transform = "translateX(" + (caja.left - base.left) + "px) scaleX(" + (caja.width / 100) + ")";
      if (aparece || instantaneo) {
        void indicador.offsetWidth; // aplica la posición antes de devolver la transición
        indicador.classList.remove("sin-transicion");
      }
      indicador.classList.add("is-visible");
    }

    function activar(id) {
      var nuevo = porId[id] || null;
      if (nuevo === activo) return;
      enlaces.forEach(function (a) {
        if (a === nuevo) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
      activo = nuevo;
      ubicar(false);
    }

    // La sección que cruza la línea media de la pantalla es la activa
    var ultimoEnlace = enlaces[enlaces.length - 1].getAttribute("href").slice(1);
    var porLinea = "inicio";
    function alFinal() {
      var raiz = document.documentElement;
      return window.innerHeight + window.scrollY >= raiz.scrollHeight - 4;
    }
    // La última sección puede no llegar nunca a la línea media: al final de la página queda activa
    function decidir() { activar(alFinal() ? ultimoEnlace : porLinea); }
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) { if (en.isIntersecting) porLinea = en.target.id; });
      decidir();
    }, { rootMargin: "-50% 0px -50% 0px", threshold: 0 });
    secciones.forEach(function (s) { observador.observe(s); });
    var pendiente = false;
    window.addEventListener("scroll", function () {
      if (pendiente) return;
      pendiente = true;
      window.requestAnimationFrame(function () { pendiente = false; decidir(); });
    }, { passive: true });

    var temporizador = null;
    window.addEventListener("resize", function () {
      clearTimeout(temporizador);
      temporizador = setTimeout(function () { ubicar(true); }, 150);
    });
    // Los textos en inglés y la fuente definitiva cambian el ancho de los enlaces
    document.addEventListener("ikonect:lang", function () { ubicar(true); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ubicar(true); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicio);
  else inicio();
})();
