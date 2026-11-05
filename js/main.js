/* Clase js, menú móvil, tema del encabezado y año del pie */
(function () {
  "use strict";
  document.documentElement.classList.add("js");

  function inicio() {
    var cabecera = document.querySelector(".site-header");
    var boton = document.querySelector(".menu-toggle");
    var menu = document.getElementById("menu-principal");

    var anio = document.getElementById("anio");
    if (anio) anio.textContent = new Date().getFullYear();

    // Menú móvil
    function abrir(si) {
      if (!boton || !menu) return;
      boton.setAttribute("aria-expanded", si ? "true" : "false");
      menu.classList.toggle("is-open", si);
    }
    if (boton && menu) {
      boton.addEventListener("click", function () {
        abrir(boton.getAttribute("aria-expanded") !== "true");
      });
      menu.addEventListener("click", function (e) {
        if (e.target.closest("a")) abrir(false);
      });
      // Al pasar al diseño de escritorio el menú vuelve a su estado cerrado
      if (window.matchMedia) {
        var escritorio = window.matchMedia("(min-width: 1020px)");
        var alCambiar = function (e) { if (e.matches) abrir(false); };
        if (escritorio.addEventListener) escritorio.addEventListener("change", alCambiar);
        else if (escritorio.addListener) escritorio.addListener(alCambiar);
      }
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && boton.getAttribute("aria-expanded") === "true") {
          abrir(false);
          boton.focus();
        }
      });
    }

    if (!cabecera) return;

    // Fondo del encabezado una vez que se desplaza la página
    function alDesplazar() { cabecera.classList.toggle("is-scrolled", window.scrollY > 8); }
    window.addEventListener("scroll", alDesplazar, { passive: true });
    alDesplazar();

    // Tema: la sección que cruza la franja inferior del encabezado decide el color
    var secciones = document.querySelectorAll("[data-theme]");
    if (!("IntersectionObserver" in window) || !secciones.length) return;
    var observador = null;
    function observar() {
      if (observador) observador.disconnect();
      // Franja de 1 px en el borde inferior del encabezado
      var alto = cabecera.offsetHeight;
      var superior = Math.max(0, alto - 1);
      var inferior = Math.max(0, window.innerHeight - alto);
      observador = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (en) {
          if (en.isIntersecting) {
            cabecera.classList.toggle("is-light", en.target.getAttribute("data-theme") === "light");
          }
        });
      }, { rootMargin: "-" + superior + "px 0px -" + inferior + "px 0px", threshold: 0 });
      secciones.forEach(function (s) { observador.observe(s); });
    }
    observar();
    var temporizador = null;
    window.addEventListener("resize", function () {
      clearTimeout(temporizador);
      temporizador = setTimeout(observar, 150);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicio);
  else inicio();
})();
