import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from src.evaluacion import validar_parametros, evaluar_imagen
from src.guiado import pedir_tamano
from src.lectura import ImagenSticker


class PruebasTamanos(unittest.TestCase):
    def test_extremos_inclusivos_en_ambas_etapas(self):
        imagen = ImagenSticker('ejemplo.png', 500, 500, [0] * 255 + [250000], (0, 0, 500, 500))
        for lado in (0.1, 4, 56):
            for etapa in ('inicial', 'final'):
                with self.subTest(lado=lado, etapa=etapa):
                    resultado = evaluar_imagen(imagen, lado_cm=lado, etapa=etapa)
                    self.assertTrue(math.isfinite(resultado['resolucion_ppi']))
                    self.assertAlmostEqual(resultado['resolucion_ppi'], 500 * 2.54 / lado)

    def test_rechaza_fuera_del_rango(self):
        for lado in (5e-324, 0.099, 0, -1, 56.001, 57, 1e308, float('inf'), float('nan')):
            with self.subTest(lado=lado):
                with self.assertRaisesRegex(ValueError, '0.1 y 56'):
                    validar_parametros(lado, 300, 20)

    def test_menu_repregunta_y_admite_coma(self):
        with patch('builtins.input', side_effect=['57', '0,01', '56']):
            self.assertEqual(pedir_tamano(4), 56)
        with patch('builtins.input', return_value='0,1'):
            self.assertEqual(pedir_tamano(4), 0.1)

    def test_cli_rechaza_antes_de_crear_salidas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            for etapa in ('inicial', 'final'):
                for lado in ('57', '5e-324'):
                    resultado = subprocess.run(
                        [sys.executable, 'src/main.py', str(raiz), '--lado-cm', lado,
                         '--etapa', etapa, '--salida', str(raiz / 'outputs')],
                        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
                    self.assertEqual(resultado.returncode, 2, resultado.stderr)
                    self.assertIn('0.1 y 56', resultado.stderr)
                    self.assertFalse((raiz / 'outputs').exists())
