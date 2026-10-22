"""Pruebas con imágenes artificiales en carpetas temporales."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
from src.lectura import analizar_carpeta, buscar_png, leer_png


class PruebasLectura(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.carpeta = Path(temporal.name)

    def crear_png(self, nombre="sticker.png"):
        ruta = self.carpeta / nombre
        with Image.new("RGBA", (40, 25), (255, 0, 0, 255)) as imagen:
            imagen.save(ruta, format="PNG")
        return ruta

    def test_dimensiones_y_original_intacto(self):
        ruta = self.crear_png()
        original = ruta.read_bytes()
        sticker = leer_png(ruta)
        self.assertEqual((sticker.ancho_px, sticker.alto_px), (40, 25))
        self.assertEqual(ruta.read_bytes(), original)

    def test_lote_mixto_continua_y_contabiliza_todos(self):
        self.crear_png("valido.PNG")
        (self.carpeta / "danado.png").write_bytes(b"no es una imagen")
        (self.carpeta / "notas.txt").write_text("ignorar", encoding="utf-8")
        imagenes, errores = analizar_carpeta(self.carpeta)
        self.assertEqual(len(imagenes), 1)
        self.assertEqual(len(errores), 2)
        self.assertEqual(len(buscar_png(self.carpeta)), 2)
        self.assertIn("Formato no compatible", errores[1][1])
        self.assertEqual(errores[0][0].name, "danado.png")

    def test_jpeg_disfrazado_de_png(self):
        ruta = self.carpeta / "falso.png"
        with Image.new("RGB", (20, 20)) as imagen:
            imagen.save(ruta, format="JPEG")
        with self.assertRaisesRegex(ValueError, "contenido no es PNG"):
            leer_png(ruta)

    def test_png_truncado(self):
        ruta = self.crear_png()
        ruta.write_bytes(ruta.read_bytes()[:45])
        imagenes, errores = analizar_carpeta(self.carpeta)
        self.assertEqual(imagenes, [])
        self.assertEqual(len(errores), 1)

    def test_carpeta_vacia(self):
        self.assertEqual(analizar_carpeta(self.carpeta), ([], []))

    def test_carpeta_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            analizar_carpeta(self.carpeta / "inexistente")

    def test_ruta_es_archivo(self):
        with self.assertRaises(NotADirectoryError):
            analizar_carpeta(self.crear_png())

    def test_no_recorre_subcarpetas(self):
        (self.carpeta / "sub").mkdir()
        self.crear_png("sub/oculto.png")
        self.assertEqual(buscar_png(self.carpeta), [])

    def test_comando_documentado(self):
        self.crear_png()
        resultado = subprocess.run(
            [sys.executable, "src/main.py", str(self.carpeta),
             "--salida", str(self.carpeta / "salidas")],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("40 x 25 px", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
