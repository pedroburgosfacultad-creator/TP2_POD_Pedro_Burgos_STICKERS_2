import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
from src.fuentes import FuenteImagenes, FuenteCarpeta, FuenteSeleccionJSON
from src.lectura import analizar_fuente
from src.evaluacion import evaluar_imagen


class PruebasFuentes(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.carpeta = self.raiz / 'imagenes'
        self.carpeta.mkdir()
        Image.new('RGB', (500, 500), 'red').save(self.carpeta / 'uno.jpg')
        Image.new('RGBA', (200, 200), (0, 0, 255, 128)).save(self.carpeta / 'dos.png')
        self.json = self.raiz / 'seleccion.json'
        self.guardar(['dos.png', 'uno.jpg'])

    def guardar(self, nombres):
        self.json.write_text(json.dumps({'version': 1, 'carpeta': str(self.carpeta),
                                         'archivos': nombres}), encoding='utf-8')

    def test_contrato_abstracto(self):
        with self.assertRaises(TypeError):
            FuenteImagenes(self.carpeta)

    def test_equivalencia_de_ambas_fuentes_en_ambas_etapas(self):
        for etapa in ('inicial', 'final'):
            salidas = []
            for fuente in (FuenteCarpeta(self.carpeta), FuenteSeleccionJSON(self.json)):
                imagenes, errores = analizar_fuente(fuente, etapa)
                resultados = sorted([evaluar_imagen(i, etapa=etapa) for i in imagenes], key=lambda r:r['archivo'])
                salidas.append((resultados, sorted((p.name, e) for p,e in errores)))
            self.assertEqual(salidas[0], salidas[1])

    def test_solo_seleccionados_sin_duplicar_y_faltantes_visibles(self):
        self.guardar(['uno.jpg', 'uno.jpg', 'movido.png'])
        imagenes, errores = analizar_fuente(FuenteSeleccionJSON(self.json), 'inicial')
        self.assertEqual([i.ruta.name for i in imagenes], ['uno.jpg'])
        self.assertEqual([p.name for p,e in errores], ['movido.png'])

    def test_json_invalido_se_rechaza(self):
        self.guardar(['../fuera.jpg'])
        with self.assertRaises(ValueError):
            FuenteSeleccionJSON(self.json).cargar()
        self.json.write_text('no es JSON')
        with self.assertRaises(ValueError):
            FuenteSeleccionJSON(self.json).cargar()

    def test_menu_y_cli_reanalizan_sin_copiar(self):
        self.guardar(['uno.jpg'])
        comando = [sys.executable, 'src/main.py', '--salida', str(self.raiz / 'outputs')]
        proyecto = Path(__file__).resolve().parents[1]
        guiado = subprocess.run(comando, cwd=proyecto, input=f'4\n"{self.json}"\n1\n6\n\nn\n',
                                capture_output=True, text=True)
        self.assertEqual(guiado.returncode, 0, guiado.stderr)
        directo = subprocess.run(comando + ['--analizar-seleccion', str(self.json), '--lado-cm', '6'],
                                 cwd=proyecto, capture_output=True, text=True)
        self.assertEqual(directo.returncode, 0, directo.stderr)
        reportes = list((self.raiz / 'outputs').glob('*/informe.csv'))
        self.assertEqual(len(reportes), 2)
        for reporte in reportes:
            with reporte.open(encoding='utf-8-sig', newline='') as f:
                filas = list(csv.DictReader(f, delimiter=';'))
            self.assertEqual(len(filas), 1)
            self.assertEqual(filas[0]['archivo'], 'uno.jpg')
            self.assertEqual(filas[0]['etapa'], 'inicial')
            self.assertEqual(filas[0]['estado'], 'REVISAR')
        self.assertFalse(list((self.raiz/'outputs').glob('seleccion_photoroom_*')))
