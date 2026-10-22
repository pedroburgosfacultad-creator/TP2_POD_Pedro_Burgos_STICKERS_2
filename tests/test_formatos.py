import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image


class PruebasFormatos(unittest.TestCase):
    def test_pdf_y_sin_extension_se_informan_en_ambas_etapas(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            origen = raiz / 'entrada'
            origen.mkdir()
            Image.new('RGB', (600, 600)).save(origen / 'valido.png')
            (origen / 'documento.PDF').write_bytes(b'%PDF-prueba')
            (origen / 'sin_extension').write_bytes(b'prueba')
            (origen / 'subcarpeta').mkdir()
            (origen / 'subcarpeta/oculto.pdf').write_bytes(b'prueba')
            for etapa in ('inicial', 'final'):
                with self.subTest(etapa=etapa):
                    salida = raiz / etapa
                    resultado = subprocess.run(
                        [sys.executable, 'src/main.py', str(origen), '--etapa', etapa,
                         '--salida', str(salida)], capture_output=True, text=True,
                        cwd=Path(__file__).resolve().parents[1])
                    self.assertEqual(resultado.returncode, 1, resultado.stderr)
                    self.assertIn('documento.PDF', resultado.stderr)
                    self.assertIn('Formato no compatible', resultado.stderr)
                    reporte = next(salida.glob('*/informe.csv'))
                    with reporte.open(encoding='utf-8-sig', newline='') as archivo:
                        filas = list(csv.DictReader(archivo, delimiter=';'))
                    self.assertEqual(len(filas), 3)
                    rechazados = [f for f in filas if f['estado'] == 'ERROR_LECTURA']
                    self.assertEqual(len(rechazados), 2)
                    self.assertTrue(all(f['resolucion_ppi'] == '' for f in rechazados))
                    html = reporte.with_name('informe.html').read_text(encoding='utf-8')
                    self.assertIn('documento.PDF', html)
                    self.assertIn('Formato no compatible', html)
                    self.assertIn('No procesado', html)
                    self.assertEqual(html.count('class="seleccionar"'), 1)
            self.assertEqual((origen / 'documento.PDF').read_bytes(), b'%PDF-prueba')
