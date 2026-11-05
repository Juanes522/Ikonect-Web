/* Servicios: el servicio que cruza el centro de la pantalla (o el que recibe clic o foco) enciende su capa del plano */
(function () {
  "use strict";
  function inicio() {
    var plano = document.getElementById("plano");
    var items = Array.prototype.slice.call(document.querySelectorAll(".servicios-lista .servicio"));
    if (!plano || !items.length) return;

    var activa = null;
    // Tras un clic o un foco, el desplazamiento que provoca el navegador no debe cambiar la capa elegida
    var bloqueoHasta = 0;

    function activar(capa) {
      if (!capa || capa === activa) return;
      activa = capa;
      plano.setAttribute("data-activa", capa);
      items.forEach(function (li) {
        var on = li.getAttribute("data-capa") === capa;
        li.classList.toggle("is-activo", on);
        var boton = li.querySelector(".servicio__activar");
        if (boton) boton.setAttribute("aria-pressed", on ? "true" : "false");
      });
    }

    items.forEach(function (li) {
      var boton = li.querySelector(".servicio__activar");
      if (!boton) return;
      function elegir() {
        bloqueoHasta = Date.now() + 600;
        activar(li.getAttribute("data-capa"));
      }
      boton.addEventListener("click", elegir);
      boton.addEventListener("focus", elegir);
    });

    activar("wifi");

    if (!("IntersectionObserver" in window)) return;
    var observador = new IntersectionObserver(function (entradas) {
      if (Date.now() < bloqueoHasta) return;
      entradas.forEach(function (en) {
        if (en.isIntersecting) activar(en.target.getAttribute("data-capa"));
      });
    }, { rootMargin: "-45% 0px -45% 0px", threshold: 0 });
    items.forEach(function (li) { observador.observe(li); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicio);
  else inicio();
})();
