/* Escenarios del plano (empresa, hotel, educación): grupo de botones conmutables (aria-pressed),
   como los de los servicios. Las flechas, Inicio y Fin recorren el grupo con tabindex móvil.
   Cambia data-escenario en el plano; la capa del servicio activo (data-activa) no se toca. */
(function () {
  "use strict";
  function inicio() {
    var plano = document.getElementById("plano");
    var grupo = document.querySelector(".plano-escenarios");
    if (!plano || !grupo) return;
    var botones = Array.prototype.slice.call(grupo.querySelectorAll("button[data-escenario]"));
    if (!botones.length) return;

    function elegir(boton, enfocar) {
      botones.forEach(function (b) {
        var on = b === boton;
        b.setAttribute("aria-pressed", on ? "true" : "false");
        b.setAttribute("tabindex", on ? "0" : "-1");
      });
      plano.setAttribute("data-escenario", boton.getAttribute("data-escenario"));
      if (enfocar) boton.focus({ preventScroll: true });
    }

    botones.forEach(function (boton, i) {
      boton.addEventListener("click", function () { elegir(boton, false); });
      boton.addEventListener("keydown", function (ev) {
        var destino = null;
        if (ev.key === "ArrowRight") destino = botones[(i + 1) % botones.length];
        else if (ev.key === "ArrowLeft") destino = botones[(i - 1 + botones.length) % botones.length];
        else if (ev.key === "Home") destino = botones[0];
        else if (ev.key === "End") destino = botones[botones.length - 1];
        if (!destino) return;
        ev.preventDefault();
        elegir(destino, true);
      });
    });

    // Estado inicial coherente con el HTML (el botón presionado o el primero)
    var marcado = botones.filter(function (b) { return b.getAttribute("aria-pressed") === "true"; })[0] || botones[0];
    elegir(marcado, false);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicio);
  else inicio();
})();
