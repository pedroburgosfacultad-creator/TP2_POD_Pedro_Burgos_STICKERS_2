"""Pruebas de reglas y reportes con mediciones conocidas."""
import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
from src.lectura import leer_png
from src.evaluacion import evaluar_imagen, resumir_resultados, validar_parametros
from src.informes import guardar_informes, texto_resumen


class PruebasEvaluacion(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.carpeta = Path(temporal.name)

    def crear(self, modo="RGBA", medida=(500, 500), color=(255, 0, 0, 255)):
        ruta = self.carpeta / "ejemplo.png"
        with Image.new(modo, medida, color) as imagen:
            imagen.save(ruta)
        return leer_png(ruta)

    def test_resolucion_y_doble_tamano(self):
        imagen = self.crear()
        a = evaluar_imagen(imagen, 4, exigir_transparencia=False)
        b = evaluar_imagen(imagen, 8, exigir_transparencia=False)
        self.assertAlmostEqual(a["resolucion_ppi"], 317.5)
        self.assertEqual(b["resolucion_ppi"], a["resolucion_ppi"] / 2)
        self.assertEqual(a["estado"], "SIN_ADVERTENCIAS")
        self.assertIn("RESOLUCION_INFERIOR_A_REFERENCIA", b["advertencias"])

    def test_umbral_exacto_no_advierte(self):
        resultado = evaluar_imagen(self.crear(medida=(300, 150)), 2.54,
                                  exigir_transparencia=False)
        self.assertEqual(resultado["resolucion_ppi"], 300)
        self.assertEqual(resultado["advertencias"], [])

    def test_margenes_y_proporciones(self):
        ruta = self.carpeta / "margenes.png"
        with Image.new("RGBA", (500, 500), (0, 0, 0, 0)) as imagen:
            imagen.paste((255, 0, 0, 255), (100, 150, 400, 350))
            imagen.save(ruta)
        resultado = evaluar_imagen(leer_png(ruta), 4)
        self.assertEqual(resultado["ancho_visible_px"], 300)
        self.assertEqual(resultado["alto_visible_px"], 200)
        self.assertAlmostEqual(resultado["resolucion_ppi"], 190.5)
        self.assertEqual(resultado["ancho_impresion_cm"], 4)
        self.assertAlmostEqual(resultado["alto_impresion_cm"], 8 / 3)
        self.assertAlmostEqual(resultado["transparentes_pct_lienzo"], 76)

    def test_opaca_rgb_y_opcion(self):
        imagen = self.crear("RGB", color=(255, 0, 0))
        self.assertIn("SIN_TRANSPARENCIA", evaluar_imagen(imagen)["advertencias"])
        self.assertEqual(evaluar_imagen(imagen, exigir_transparencia=False)["advertencias"], [])

    def test_imagen_vacia_no_inventa_resolucion(self):
        resultado = evaluar_imagen(self.crear(color=(0, 0, 0, 0)))
        self.assertIsNone(resultado["resolucion_ppi"])
        self.assertEqual(resultado["advertencias"], ["SIN_CONTENIDO_VISIBLE"])
        self.assertEqual(resultado["transparentes_pct_lienzo"], 100)

    def test_parcial_sobre_visibles(self):
        ruta = self.carpeta / "parcial.png"
        with Image.new("RGBA", (10, 10), (0, 0, 0, 0)) as imagen:
            imagen.paste((255, 0, 0, 128), (0, 0, 5, 10))
            imagen.save(ruta)
        resultado = evaluar_imagen(leer_png(ruta))
        self.assertEqual(resultado["transparentes_pct_lienzo"], 50)
        self.assertEqual(resultado["semitransparentes_pct_visibles"], 100)
        self.assertIn("ALTA_PROPORCION_SEMITRANSPARENTE", resultado["advertencias"])

    def test_transparencia_de_paleta(self):
        ruta = self.carpeta / "paleta.png"
        with Image.new("P", (10, 10), 0) as imagen:
            imagen.putpalette([0, 0, 0, 255, 0, 0] + [0] * 762)
            imagen.putpixel((3, 4), 1)
            imagen.save(ruta, transparency=0)
        sticker = leer_png(ruta)
        self.assertEqual(sticker.dimensiones_visibles(), (1, 1))
        self.assertEqual(sticker.histograma_alpha[0], 99)

    def test_parametros_invalidos(self):
        for lado, ppi, parcial in [(0, 300, 20), (-1, 300, 20),
                                   (float("nan"), 300, 20), (4, float("inf"), 20),
                                   (4, 0, 20), (4, 300, 101), (4, 300, -1)]:
            with self.subTest(valores=(lado, ppi, parcial)):
                with self.assertRaises(ValueError):
                    validar_parametros(lado, ppi, parcial)

    def test_resumen_y_exportacion_incluyen_errores(self):
        resultados = [evaluar_imagen(self.crear())]
        errores = [(self.carpeta / "roto.png", "Archivo dañado")]
        resumen = resumir_resultados(resultados, errores)
        self.assertEqual(resumen["encontrados"], 2)
        self.assertEqual(resumen["leidos"],
                         resumen["revisar"] + resumen["sin_advertencias"])
        salida = guardar_informes(resultados, errores, self.carpeta / "salidas")
        with (salida / "informe.csv").open(encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.DictReader(archivo, delimiter=";"))
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[0]["estado"], "REVISAR")
        self.assertEqual(filas[1]["estado"], "ERROR_LECTURA")
        self.assertEqual(filas[1]["resolucion_ppi"], "")
        self.assertFalse((salida / "resumen.txt").exists())
        otra = guardar_informes(resultados, errores, self.carpeta / "salidas")
        self.assertNotEqual(salida, otra)

    def test_sin_imagenes_no_porcentaje_enganoso(self):
        resumen = resumir_resultados([], [])
        self.assertIsNone(resumen["revisar_pct_leidos"])
        self.assertIn("No se encontraron PNG",
                      texto_resumen(resumen, 4, 300, 20, True, self.carpeta))

    def test_cli_crea_reportes_y_rechaza_parametros(self):
        self.crear()
        base = [sys.executable, "src/main.py", str(self.carpeta),
                "--salida", str(self.carpeta / "salidas")]
        proyecto = Path(__file__).resolve().parents[1]
        correcto = subprocess.run(base, cwd=proyecto, capture_output=True, text=True)
        self.assertEqual(correcto.returncode, 0, correcto.stderr)
        self.assertEqual(len(list((self.carpeta / "salidas").glob("*/informe.csv"))), 1)
        invalido = subprocess.run(base + ["--lado-cm", "nan"], cwd=proyecto,
                                  capture_output=True, text=True)
        self.assertEqual(invalido.returncode, 2)
        self.assertEqual(len(list((self.carpeta / "salidas").glob("*/informe.csv"))), 1)


if __name__ == "__main__":
    unittest.main()

