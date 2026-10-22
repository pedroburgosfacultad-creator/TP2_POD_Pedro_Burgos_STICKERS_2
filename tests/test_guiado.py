import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from src.guiado import pedir_carpeta, pedir_tamano, pedir_apertura, abrir_informe


class PruebasGuiado(unittest.TestCase):
    def test_tamano_reintentos_coma_y_default(self):
        with patch("builtins.input", side_effect=["nan", "0", "-2", "abc", "4,5"]):
            self.assertEqual(pedir_tamano(4), 4.5)
        with patch("builtins.input", return_value=""):
            self.assertEqual(pedir_tamano(4), 4)

    def test_carpeta_con_comillas_y_espacios(self):
        with tempfile.TemporaryDirectory(prefix="stickers prueba ") as carpeta:
            with patch("builtins.input", side_effect=["", str(Path(carpeta)/"no_existe"), f'"{carpeta}"']):
                self.assertEqual(pedir_carpeta(), Path(carpeta))

    def test_respuestas_apertura(self):
        with patch("builtins.input", side_effect=["quizás", "sí"]):
            self.assertTrue(pedir_apertura())
        with patch("builtins.input", return_value=""):
            self.assertFalse(pedir_apertura())

    def test_apertura_sin_lanzar_navegador_real(self):
        with patch("src.guiado.webbrowser.open", return_value=True) as abrir:
            self.assertTrue(abrir_informe(Path("informe con espacios.html")))
            self.assertTrue(abrir.call_args.args[0].startswith("file:"))
        with patch("src.guiado.webbrowser.open", side_effect=OSError("fallo")):
            self.assertFalse(abrir_informe("informe.html"))

    def test_ejecucion_guiada_y_cancelacion_por_fin_de_entrada(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            with Image.new("RGBA", (100, 100), (255, 0, 0, 255)) as imagen:
                imagen.save(raiz / "ejemplo.png")
            comando = [sys.executable, "src/main.py", "--salida", str(raiz / "salida")]
            proyecto = Path(__file__).resolve().parents[1]
            resultado = subprocess.run(comando, cwd=proyecto, input=f'1\n"{raiz}"\n4,5\n\nn\n',
                                       text=True, capture_output=True)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            informes = list((raiz / "salida").glob("*/informe.html"))
            self.assertEqual(len(informes), 1)
            self.assertIn("4.5 cm", informes[0].read_text(encoding="utf-8"))
            cancelado = subprocess.run(comando, cwd=proyecto, input="", text=True, capture_output=True)
            self.assertEqual(cancelado.returncode, 130)
            self.assertNotIn("Traceback", cancelado.stderr)
            self.assertEqual(len(list((raiz / "salida").glob("*/informe.html"))), 1)

