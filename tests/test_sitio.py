import json
import re
import unittest

from html_util import RAIZ, find_all, parse_index

SECCIONES = [("inicio", "dark"), ("nosotros", "light"), ("servicios", "light"),
             ("fabricantes", "light"), ("clientes", "light"), ("contacto", "dark")]


class TestSitio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = parse_index()

    def todos(self, pred):
        return find_all(self.raiz, pred)

    def test_secciones(self):
        secs = self.todos(lambda e: e.tag == "section" and "id" in e.attrs)
        self.assertEqual([(s.attrs["id"], s.attrs.get("data-theme")) for s in secs], SECCIONES)

    def test_un_h1_y_jerarquia(self):
        hs = self.todos(lambda e: re.fullmatch(r"h[1-6]", e.tag))
        self.assertEqual(len([h for h in hs if h.tag == "h1"]), 1)
        previo = 0
        for h in hs:
            nivel = int(h.tag[1])
            self.assertLessEqual(nivel, previo + 1, f"salto de nivel en {h.full_text()!r}")
            previo = nivel

    def test_assets_existen(self):
        for e in self.todos(lambda e: "src" in e.attrs or "href" in e.attrs):
            for k in ("src", "href"):
                v = e.attrs.get(k, "")
                if not v or v.startswith(("http", "mailto", "tel", "#")):
                    continue
                ruta = RAIZ / v.split("?")[0].split("#")[0]
                self.assertTrue(ruta.exists(), f"no existe {v}")

    def test_imagenes(self):
        for img in self.todos(lambda e: e.tag == "img"):
            for a in ("alt", "width", "height"):
                self.assertIn(a, img.attrs, f"img {img.attrs} sin {a}")

    def test_i18n_paridad(self):
        crudo = (RAIZ / "js" / "i18n-en.js").read_text(encoding="utf-8").strip()
        crudo = re.sub(r"^window\.IKONECT_EN\s*=\s*", "", crudo).rstrip(";").strip()
        dic = set(json.loads(crudo))
        claves = set()
        for e in self.todos(lambda e: "data-i18n" in e.attrs):
            claves.add(e.attrs["data-i18n"])
        for e in self.todos(lambda e: "data-i18n-attr" in e.attrs):
            for par in e.attrs["data-i18n-attr"].split(";"):
                if par.strip():
                    claves.add(par.split(":", 1)[1].strip())
        self.assertEqual(claves - dic, set(), "claves sin traducción")
        self.assertEqual(dic - claves, set(), "claves de más en el diccionario")

    def test_enlaces_externos(self):
        for a in self.todos(lambda e: e.tag == "a" and e.attrs.get("href", "").startswith("http")):
            if "ikonect.com.co" in a.attrs["href"] and "tickects" not in a.attrs["href"]:
                continue
            self.assertEqual(a.attrs.get("target"), "_blank", a.attrs["href"])
            self.assertIn("noopener", a.attrs.get("rel", ""), a.attrs["href"])

    def test_whatsapp_flotante(self):
        wa = self.todos(lambda e: e.tag == "a" and "wa-float" in e.attrs.get("class", "").split())
        self.assertEqual(len(wa), 1)
        self.assertTrue(wa[0].attrs["href"].startswith("https://wa.me/"))
        self.assertTrue(wa[0].attrs.get("aria-label"))
        self.assertIn("aria-label", wa[0].attrs.get("data-i18n-attr", ""))

    def test_idioma_toggle(self):
        b = self.todos(lambda e: e.tag == "button" and "data-lang-toggle" in e.attrs)
        self.assertEqual(len(b), 1)
        self.assertTrue(b[0].attrs.get("aria-label"))

    def test_sin_mayusculas_ni_flechas(self):
        self.assertNotIn("→", self.raiz.full_text())
        for css in (RAIZ / "css").glob("*.css"):
            txt = css.read_text(encoding="utf-8")
            self.assertNotRegex(txt, r"text-transform:\s*uppercase", css.name)
            self.assertNotIn("→", txt)

    def seccion(self, ident):
        secs = self.todos(lambda e: e.tag == "section" and e.attrs.get("id") == ident)
        self.assertEqual(len(secs), 1, f"falta #{ident}")
        return secs[0]

    def test_portada(self):
        inicio = self.seccion("inicio")
        h1 = find_all(inicio, lambda e: e.tag == "h1")
        self.assertEqual(len(h1), 1)
        self.assertEqual(" ".join(h1[0].full_text().split()),
                         "Conectamos tu empresa, del cable al access point")
        cta = find_all(inicio, lambda e: e.tag == "a"
                       and "btn--cta" in e.attrs.get("class", "").split())
        self.assertTrue(cta, "falta a.btn--cta en #inicio")
        self.assertEqual(cta[0].attrs.get("href"), "#contacto")
        self.assertEqual(cta[0].full_text().strip(), "Contáctanos")
        ghost = find_all(inicio, lambda e: e.tag == "a"
                         and "btn--ghost" in e.attrs.get("class", "").split())
        self.assertTrue(ghost, "falta el botón secundario en #inicio")
        self.assertEqual(ghost[0].attrs.get("href"), "#servicios")
        self.assertEqual(ghost[0].full_text().strip(), "Ver servicios")
        sub = find_all(inicio, lambda e: e.tag == "p")
        self.assertTrue(sub, "falta el subtítulo de la portada")
        self.assertIn("Canal autorizado Ruckus e integrador Systimax", sub[0].full_text())
        self.assertTrue(sub[0].attrs.get("data-i18n"), "subtítulo sin data-i18n")
        arcos = find_all(inicio, lambda e: e.tag == "svg"
                         and "arcos" in e.attrs.get("class", "").split())
        self.assertEqual(len(arcos), 1, "falta svg.arcos")
        self.assertEqual(arcos[0].attrs.get("aria-hidden"), "true")
        paths = find_all(arcos[0], lambda e: e.tag == "path")
        self.assertEqual(len(paths), 3)
        for p in paths:
            self.assertEqual(p.attrs.get("pathlength"), "1")

    def test_arcos_animacion(self):
        css = (RAIZ / "css" / "portada.css").read_text(encoding="utf-8")
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        # Toda regla que anima o esconde el trazo depende de .js; sin JavaScript las curvas se ven completas
        for sel, cuerpo in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            if "stroke-dashoffset: 1" in cuerpo or "animation: arcos-" in cuerpo:
                self.assertIn(".js", sel, f"animación de curvas sin .js en {sel.strip()!r}")
        self.assertRegex(css, r"\.js\s+\.arcos__arco\s*\{[^}]*animation:")
        bloque = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\}\s*\}", css, re.S)
        self.assertTrue(bloque, "falta el bloque prefers-reduced-motion en portada.css")
        self.assertIn(".arcos__arco", bloque.group(1))

    def test_nav_indicador(self):
        ind = self.todos(lambda e: "site-nav__indicador" in e.attrs.get("class", "").split())
        self.assertEqual(len(ind), 1, "falta el indicador de sección activa")
        self.assertEqual(ind[0].attrs.get("aria-hidden"), "true")
        self.assertTrue((RAIZ / "js" / "nav-activo.js").exists())

    def test_medios_animacion(self):
        css = (RAIZ / "css" / "portada.css").read_text(encoding="utf-8")
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        reglas = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
        anima = [(sel, c) for sel, c in reglas if re.search(r"animation:\s*medio-", c)]
        self.assertTrue(anima, "el diagrama de medios no tiene animación")
        for sel, _ in anima + [(sel, c) for sel, c in reglas
                               if ".medio" in sel and "stroke-dashoffset: 1" in c]:
            for parte in sel.split(","):
                self.assertIn(".js", parte, f"animación del diagrama sin .js en {parte.strip()!r}")
        bloques = re.findall(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\}\s*\}", css, re.S)
        self.assertTrue(any(".medio" in b and "animation: none" in b for b in bloques),
                        "falta el reduced-motion del diagrama de medios")

    def test_nosotros(self):
        nos = self.seccion("nosotros")
        self.assertTrue(find_all(nos, lambda e: e.tag == "h2"), "falta h2 en #nosotros")
        texto = " ".join(nos.full_text().split())
        for frase in ("cableado estructurado", "fibra óptica", "inalámbricas"):
            self.assertIn(frase, texto)

    CAPAS = ["wifi", "cableado", "firewall", "licencias", "equipos", "soporte"]
    TITULOS = ["Redes inalámbricas", "Cableado estructurado", "Seguridad perimetral",
               "Licenciamiento Ruckus", "Equipos de cómputo", "Mantenimiento y soporte"]

    def servicios(self):
        sec = self.seccion("servicios")
        listas = find_all(sec, lambda e: e.tag == "ol"
                          and "servicios-lista" in e.attrs.get("class", "").split())
        self.assertEqual(len(listas), 1, "falta ol.servicios-lista")
        return find_all(listas[0], lambda e: e.tag == "li"
                        and "servicio" in e.attrs.get("class", "").split())

    def test_servicios_estructura(self):
        items = self.servicios()
        self.assertEqual([li.attrs.get("data-capa") for li in items], self.CAPAS)
        titulos = [" ".join(find_all(li, lambda e: e.tag == "h3")[0].full_text().split())
                   for li in items]
        self.assertEqual(titulos, self.TITULOS)
        for li in items:
            self.assertTrue(find_all(li, lambda e: e.tag == "p"), f"{li.attrs} sin párrafo")
        plano = self.todos(lambda e: e.tag == "svg" and e.attrs.get("id") == "plano")
        self.assertEqual(len(plano), 1, "falta svg#plano")
        self.assertIn("plano", plano[0].attrs.get("class", "").split())
        self.assertEqual(plano[0].attrs.get("viewbox"), "0 0 400 300")
        capas = find_all(plano[0], lambda e: e.tag == "g"
                         and "capa" in e.attrs.get("class", "").split())
        self.assertEqual(sorted(g.attrs.get("data-capa") for g in capas), sorted(self.CAPAS))
        for zona in ("Sala de juntas", "Gerencia", "Área abierta", "Centro de datos"):
            textos = find_all(plano[0], lambda e: e.tag == "text" and e.full_text().strip() == zona)
            self.assertEqual(len(textos), 1, f"falta la zona {zona!r}")
            self.assertTrue(textos[0].attrs.get("data-i18n"), f"{zona!r} sin data-i18n")

    def test_servicios_teclado(self):
        for li in self.servicios():
            h3 = find_all(li, lambda e: e.tag == "h3"
                          and "servicio__titulo" in e.attrs.get("class", "").split())
            self.assertEqual(len(h3), 1, f"{li.attrs} sin h3.servicio__titulo")
            # El botón va dentro del título (un encabezado no puede ir dentro de un botón)
            b = find_all(h3[0], lambda e: e.tag == "button"
                         and "servicio__activar" in e.attrs.get("class", "").split())
            self.assertEqual(len(b), 1, f"{li.attrs}: el h3 no contiene button.servicio__activar")
            self.assertEqual(b[0].attrs.get("aria-controls"), "plano")
            self.assertIn(b[0].attrs.get("aria-pressed"), ("true", "false"))
            self.assertEqual(b[0].attrs.get("type"), "button")
            self.assertFalse(find_all(b[0], lambda e: re.fullmatch(r"h[1-6]", e.tag)),
                             "no puede haber encabezados dentro del botón")
            # data-i18n en un span interno, para que la traducción no borre el ícono
            self.assertNotIn("data-i18n", b[0].attrs)
            self.assertTrue(find_all(b[0], lambda e: e.tag == "span" and "data-i18n" in e.attrs))

    def test_servicios_tickets(self):
        soporte = [li for li in self.servicios() if li.attrs.get("data-capa") == "soporte"]
        self.assertEqual(len(soporte), 1)
        enlaces = find_all(soporte[0], lambda e: e.tag == "a"
                           and e.attrs.get("href") == "https://www.ikonect.com.co/tickects/")
        self.assertEqual(len(enlaces), 1, "falta el enlace a la mesa de ayuda en soporte")
        aviso = find_all(enlaces[0], lambda e: "sr-only" in e.attrs.get("class", "").split()
                         and e.attrs.get("data-i18n"))
        self.assertEqual(len(aviso), 1, "el enlace debe avisar que abre una pestaña nueva")

    ESCENARIOS = [("empresa", "Empresa"), ("hotel", "Hotel"), ("educacion", "Educación")]

    def test_escenarios(self):
        sec = self.seccion("servicios")
        grupos = find_all(sec, lambda e: e.attrs.get("role") == "group"
                          and "plano-escenarios" in e.attrs.get("class", "").split())
        self.assertEqual(len(grupos), 1, "falta div.plano-escenarios[role=group]")
        self.assertTrue(grupos[0].attrs.get("aria-label"), "el grupo necesita aria-label")
        # Va dentro del bloque fijo del plano, para que siga a la vista al desplazarse
        bloque = find_all(sec, lambda e: "servicios__plano" in e.attrs.get("class", "").split())
        self.assertTrue(find_all(bloque[0], lambda e: e is grupos[0]), "el selector va dentro de .servicios__plano")
        # Grupo de botones conmutables (como los servicios): sin semántica de pestañas
        self.assertFalse(find_all(grupos[0], lambda e: e.attrs.get("role") in ("tab", "tablist")
                                  or "aria-selected" in e.attrs or "aria-controls" in e.attrs))
        botones = find_all(grupos[0], lambda e: e.tag == "button")
        self.assertEqual([(b.attrs.get("data-escenario"), " ".join(b.full_text().split())) for b in botones],
                         self.ESCENARIOS)
        for b in botones:
            self.assertEqual(b.attrs.get("type"), "button")
        self.assertEqual([b.attrs.get("aria-pressed") for b in botones], ["true", "false", "false"])
        self.assertEqual([b.attrs.get("tabindex") for b in botones], ["0", "-1", "-1"])

        plano = self.todos(lambda e: e.tag == "svg" and e.attrs.get("id") == "plano")[0]
        self.assertEqual(plano.attrs.get("data-escenario"), "empresa")
        validos = {e for e, _ in self.ESCENARIOS}
        for el in find_all(plano, lambda e: "data-solo" in e.attrs):
            self.assertIn(el.attrs["data-solo"], validos, f"data-solo desconocido en {el}")
        zonas = find_all(plano, lambda e: e.tag == "text"
                         and "plano__zona" in e.attrs.get("class", "").split())
        for esc, _ in self.ESCENARIOS:
            propias = [z for z in zonas if z.attrs.get("data-solo") == esc]
            comunes = [z for z in zonas if "data-solo" not in z.attrs]
            self.assertGreaterEqual(len(propias), 3, f"{esc}: faltan zonas propias")
            self.assertGreaterEqual(len(propias) + len(comunes), 4, f"{esc}: menos de 4 zonas")
            for z in propias:
                self.assertTrue(z.attrs.get("data-i18n"), f"zona sin data-i18n en {esc}")
        # Una sola capa por servicio; las variantes de cada escenario van dentro con data-solo
        capas = find_all(plano, lambda e: e.tag == "g" and "capa" in e.attrs.get("class", "").split())
        self.assertEqual(sorted(g.attrs.get("data-capa") for g in capas), sorted(self.CAPAS))
        for g in capas:
            self.assertNotIn("data-solo", g.attrs, "una capa no puede ser exclusiva de un escenario")
        self.assertTrue((RAIZ / "js" / "escenarios.js").exists(), "falta js/escenarios.js")
        js = (RAIZ / "js" / "escenarios.js").read_text(encoding="utf-8")
        for clave in ("ArrowRight", "ArrowLeft", "Home", "End", "aria-pressed", "tabindex", "data-escenario"):
            self.assertIn(clave, js)
        css = re.sub(r"/\*.*?\*/", "", (RAIZ / "css" / "servicios.css").read_text(encoding="utf-8"), flags=re.S)
        for esc, _ in self.ESCENARIOS:
            self.assertRegex(css, r'\.plano\[data-escenario="%s"\]\s*\[data-solo\]:not\(\[data-solo="%s"\]\)' % (esc, esc))
        self.assertRegex(css, r"html:not\(\.js\)\s*\.plano-escenarios\s*\{[^}]*display:\s*none")

    def test_servicios_intro_sin_js(self):
        intro = self.todos(lambda e: "servicios__intro" in e.attrs.get("class", "").split())[0]
        solo = find_all(intro, lambda e: "solo-js" in e.attrs.get("class", "").split())
        self.assertEqual(len(solo), 1, "la invitación a elegir espacio solo aplica con JavaScript")
        self.assertIn("Elige el tipo de espacio", solo[0].full_text())
        self.assertTrue(solo[0].attrs.get("data-i18n"))
        resto = [c for c in intro.children if c is not solo[0] and c.attrs.get("data-i18n")]
        self.assertEqual(len(resto), 1, "falta la frase que se lee sola")
        self.assertNotIn("Elige", resto[0].full_text())
        css = re.sub(r"/\*.*?\*/", "", (RAIZ / "css" / "servicios.css").read_text(encoding="utf-8"), flags=re.S)
        self.assertRegex(css, r"html:not\(\.js\)\s*\.solo-js\s*\{[^}]*display:\s*none")
        # La altura del selector se deriva de sus medidas, no es un número suelto
        self.assertNotRegex(css, r"--escenarios-h:\s*\d+px\s*;")

    def test_iconos_phosphor(self):
        txt = (RAIZ / "index.html").read_text(encoding="utf-8")
        self.assertTrue("Phosphor Icons (MIT)" in txt, "falta la nota de licencia de Phosphor")
        simbolos = set(re.findall(r'<symbol id="(ph-[\w-]+)"', txt))
        usados = set(re.findall(r'<use[^>]*href="#(ph-[\w-]+)"', txt))
        self.assertTrue(usados, "no se usa ningún ícono del sprite")
        self.assertEqual(usados - simbolos, set(), "íconos usados sin símbolo")
        self.assertEqual(simbolos - usados, set(), "símbolos que no se usan")
        for li in self.servicios():
            icono = find_all(li, lambda e: e.tag == "svg"
                             and "servicio__icono" in e.attrs.get("class", "").split())
            self.assertEqual(len(icono), 1)
            self.assertEqual(icono[0].attrs.get("aria-hidden"), "true")
            self.assertTrue(find_all(icono[0], lambda e: e.tag == "use"
                                     and e.attrs.get("href", "").startswith("#ph-")))

    def test_servicios_movimiento(self):
        css = (RAIZ / "css" / "servicios.css").read_text(encoding="utf-8")
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        # Las capas solo se apagan con JavaScript; sin él el plano muestra todo
        for sel, cuerpo in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            if re.search(r"opacity:\s*\.08", cuerpo):
                for parte in sel.split(","):
                    self.assertIn(".js", parte, f"capa apagada sin .js en {parte.strip()!r}")
        bloques = re.findall(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\}\s*\}", css, re.S)
        self.assertTrue(any(".anillo" in b and "animation: none" in b for b in bloques),
                        "los anillos Wi‑Fi deben detenerse con movimiento reducido")
        js = (RAIZ / "js" / "servicios.js").read_text(encoding="utf-8")
        self.assertIn('rootMargin: "-45% 0px -45% 0px"', js)
        self.assertIn("aria-pressed", js)
        self.assertIn("data-activa", js)

    def test_reglas_globales(self):
        for css in (RAIZ / "css").glob("*.css"):
            txt = css.read_text(encoding="utf-8")
            if css.name == "base.css":
                txt = re.sub(r":root\s*\{[^}]*\}", "", txt, count=1)
            self.assertNotRegex(txt, r"#[0-9a-fA-F]{3,8}(?![\w-])", f"hex directo en {css.name}")
        visible = self.raiz.full_text()
        self.assertNotIn("·", visible)
        self.assertNotIn("ingeniero", visible.lower())


if __name__ == "__main__":
    unittest.main()
