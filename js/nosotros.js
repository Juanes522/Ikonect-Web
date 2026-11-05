/* Nosotros: el diagrama de los tres medios se anima una sola vez al entrar en pantalla */
(function () {
  "use strict";
  function inicio() {
    var medios = document.querySelector(".medios");
    if (!medios) return;
    function animar() { medios.classList.add("is-animado"); }
    if (!("IntersectionObserver" in window)) { animar(); return; }
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) {
          animar();
          observador.disconnect();
        }
      });
    }, { threshold: 0.4 });
    observador.observe(medios);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicio);
  else inicio();
})();
