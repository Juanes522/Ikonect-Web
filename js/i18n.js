/* Motor de idioma: el español vive en el HTML y el inglés en window.IKONECT_EN */
(function () {
  "use strict";
  var CLAVE = "ikonect-lang";
  var idioma = "es";
  // Español original de cada elemento, capturado la primera vez que se ve (también los que se agreguen después)
  var htmlOriginal = new WeakMap();
  var attrOriginal = new WeakMap();

  function leer() {
    try { return window.localStorage.getItem(CLAVE); } catch (e) { return null; }
  }
  function guardar(lang) {
    try { window.localStorage.setItem(CLAVE, lang); } catch (e) { /* sin almacenamiento */ }
  }

  function paresAttr(el) {
    return (el.getAttribute("data-i18n-attr") || "").split(";").map(function (p) {
      var i = p.indexOf(":");
      return i > 0 ? { attr: p.slice(0, i).trim(), clave: p.slice(i + 1).trim() } : null;
    }).filter(Boolean);
  }

  // Un data-i18n anidado dentro de otro lo resuelve el padre con su innerHTML
  function dentroDeOtro(el) {
    return !!(el.parentElement && el.parentElement.closest("[data-i18n]"));
  }

  function aplicar(lang) {
    var en = window.IKONECT_EN || {};
    var conTexto = Array.prototype.filter.call(document.querySelectorAll("[data-i18n]"), function (el) {
      return !dentroDeOtro(el);
    });
    var conAttr = document.querySelectorAll("[data-i18n-attr]");

    // Primero se captura todo lo nuevo y luego se reescribe, para no leer HTML ya traducido
    conTexto.forEach(function (el) {
      if (!htmlOriginal.has(el)) htmlOriginal.set(el, el.innerHTML);
    });
    conAttr.forEach(function (el) {
      if (!attrOriginal.has(el)) {
        var mapa = {};
        paresAttr(el).forEach(function (p) { mapa[p.attr] = el.getAttribute(p.attr); });
        attrOriginal.set(el, mapa);
      }
    });

    conTexto.forEach(function (el) {
      var clave = el.getAttribute("data-i18n");
      el.innerHTML = lang === "en" && en[clave] !== undefined ? en[clave] : htmlOriginal.get(el);
    });
    conAttr.forEach(function (el) {
      var mapa = attrOriginal.get(el);
      paresAttr(el).forEach(function (p) {
        if (!(p.attr in mapa)) mapa[p.attr] = el.getAttribute(p.attr);
        el.setAttribute(p.attr, lang === "en" && en[p.clave] !== undefined ? en[p.clave] : mapa[p.attr]);
      });
    });
    document.documentElement.lang = lang;
  }

  function setLang(lang) {
    lang = lang === "en" ? "en" : "es";
    aplicar(lang);
    idioma = lang;
    guardar(lang);
    document.dispatchEvent(new CustomEvent("ikonect:lang", { detail: { lang: lang } }));
  }

  // Reaplica el idioma actual a todo el documento (útil tras insertar nodos con data-i18n)
  function refresh() { aplicar(idioma); }

  function getLang() { return idioma; }

  window.IkonectI18n = { setLang: setLang, getLang: getLang, refresh: refresh };

  function inicio() {
    var param = new URLSearchParams(window.location.search).get("lang");
    var inicial = param === "en" || param === "es" ? param : leer();
    if (inicial === "en" || param === "es") setLang(inicial);
    var boton = document.querySelector("[data-lang-toggle]");
    if (boton) {
      boton.addEventListener("click", function () { setLang(idioma === "en" ? "es" : "en"); });
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicio);
  else inicio();
})();
