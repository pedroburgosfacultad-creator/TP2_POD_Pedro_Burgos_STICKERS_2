import tempfile
import unittest
from pathlib import Path
from PIL import Image
from src.lectura import leer_imagen
from src.evaluacion import evaluar_imagen, resumir_resultados
from src.galeria import crear_galeria


class PruebasGaleria(unittest.TestCase):
    def test_miniatura_y_original_intacto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            ruta = raiz / "sticker & especial.png"
            with Image.new("RGBA", (800, 400), (255, 0, 0, 128)) as imagen:
                imagen.save(ruta)
            original = ruta.read_bytes()
            sticker = leer_imagen(ruta)
            resultados = [evaluar_imagen(sticker)]
            salida = raiz / "salida"
            salida.mkdir()
            html, notas = crear_galeria([sticker], resultados, [],
                resumir_resultados(resultados, []), "<script>alert(1)</script>", salida)
            contenido = html.read_text(encoding="utf-8")
            self.assertIn("sticker &amp; especial.png", contenido)
            self.assertIn("&lt;script&gt;", contenido)
            self.assertNotIn("<script>alert(1)</script>", contenido)
            self.assertEqual(notas, [])
            with Image.open(salida / "miniaturas/0000.png") as miniatura:
                self.assertEqual(miniatura.size, (240, 120))
                self.assertEqual(miniatura.mode, "RGBA")
            self.assertEqual(ruta.read_bytes(), original)

    def test_error_y_coleccion_vacia(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            errores = [(raiz / "roto.png", "Archivo dañado")]
            html, _ = crear_galeria([], [], errores, resumir_resultados([], errores), "", raiz)
            contenido = html.read_text(encoding="utf-8")
            self.assertIn('data-estado="ERROR_LECTURA"', contenido)
            self.assertIn("Sin vista previa", contenido)
            html, _ = crear_galeria([], [], [], resumir_resultados([], []), "", raiz)
            self.assertNotIn('<article class="tarjeta"', html.read_text(encoding="utf-8"))

    def test_fallo_miniatura_conserva_resultado(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            ruta = raiz / "original.png"
            with Image.new("RGBA", (20, 20)) as imagen:
                imagen.save(ruta)
            sticker = leer_imagen(ruta)
            resultados = [evaluar_imagen(sticker)]
            ruta.unlink()
            html, notas = crear_galeria([sticker], resultados, [],
                resumir_resultados(resultados, []), "", raiz)
            self.assertEqual(len(notas), 1)
            self.assertIn("original.png", html.read_text(encoding="utf-8"))

