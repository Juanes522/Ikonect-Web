/* Fabricantes y clientes: el botón de cada marca abre y cierra su información (aria-expanded),
   y un logo que no carga deja ver el nombre (.sin-logo) */
(function () {
  "use strict";
  function inicio() {
    var marcas = Array.prototype.slice.call(document.querySelectorAll(".marca"));

    function boton(m) { return m.querySelector(".marca__abrir"); }
    function abierta(m) { return boton(m).getAttribute("aria-expanded") === "true"; }
    // La clase .abierta refleja aria-expanded para el CSS (sin depender de :has())
    function fijar(m, abrir) {
      boton(m).setAttribute("aria-expanded", abrir ? "true" : "false");
      m.classList.toggle("abierta", abrir);
      if (!abrir) m.abiertaPorFoco = false;
    }
    // Ruckus (destacada) empieza abierta y solo la cambia su propio botón
    function destacada(m) { return m.classList.contains("marca--destacada"); }
    function cerrarOtras(m) {
      marcas.forEach(function (o) { if (o !== m && !destacada(o)) fijar(o, false); });
    }
    function porTeclado(el) {
      try { return el.matches(":focus-visible"); } catch (e) { return false; }
    }
    var punteroFino = window.matchMedia ? window.matchMedia("(hover: hover) and (pointer: fine)") : { matches: false };

    marcas.forEach(function (m) {
      var b = boton(m);
      if (!b) return;
      fijar(m, abierta(m));
      b.addEventListener("click", function () {
        // Si el foco con teclado acaba de abrirla, el primer Enter/Espacio no la vuelve a cerrar
        if (m.abiertaPorFoco) { m.abiertaPorFoco = false; return; }
        var abrir = !abierta(m);
        if (abrir) cerrarOtras(m);
        fijar(m, abrir);
      });
      if (destacada(m)) return;
      // Con teclado, recibir el foco ya muestra los productos; al salir se cierra.
      // Con el dedo o el ratón, el foco no abre (lo hace el clic)
      b.addEventListener("focus", function () {
        if (!porTeclado(b)) return;
        cerrarOtras(m);
        fijar(m, true);
        m.abiertaPorFoco = true;
      });
      b.addEventListener("blur", function () { fijar(m, false); });
      // Con ratón el hover ya muestra la tarjeta: un clic no la deja fija al salir, así nunca hay dos abiertas
      m.addEventListener("mouseleave", function () {
        if (punteroFino.matches && abierta(m) && !porTeclado(b)) fijar(m, false);
      });
    });

    // Tocar o hacer clic fuera de las tarjetas cierra las pequeñas (iOS no da foco a los botones al tocarlos)
    document.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest(".marca")) return;
      marcas.forEach(function (o) { if (!destacada(o) && abierta(o)) fijar(o, false); });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var actual = document.activeElement && document.activeElement.closest && document.activeElement.closest(".marca");
      if (actual) { fijar(actual, false); return; }
      marcas.forEach(function (o) { if (!destacada(o)) fijar(o, false); });
    });

    // El logo se baja lo justo para quedar centrado sobre la información abierta (--info-h)
    function medir(m) {
      var info = m.querySelector(".marca__info");
      if (info) m.style.setProperty("--info-h", info.offsetHeight + "px");
    }
    var pequenas = marcas.filter(function (m) { return !destacada(m); });
    pequenas.forEach(medir);
    if ("ResizeObserver" in window) {
      var ro = new ResizeObserver(function (entradas) {
        entradas.forEach(function (en) { medir(en.target.closest(".marca")); });
      });
      pequenas.forEach(function (m) { ro.observe(m.querySelector(".marca__info")); });
    }

    // Respaldo: si un logo no carga, se muestra el nombre en su lugar
    Array.prototype.forEach.call(document.querySelectorAll(".marca__logo, .cliente__logo img"), function (img) {
      function fallo() {
        var c = img.closest(".marca, .cliente");
        if (c.classList.contains("sin-logo")) return;
        c.classList.add("sin-logo");
        // En las marcas el nombre es el alt del logo: se muestra como texto (y sigue nombrando al botón)
        if (img.alt) {
          var nombre = document.createElement("span");
          nombre.className = "marca__nombre";
          nombre.textContent = img.alt;
          img.parentNode.insertBefore(nombre, img);
        }
      }
      img.addEventListener("error", fallo);
      if (img.complete && img.naturalWidth === 0) fallo();
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicio);
  else inicio();
})();
