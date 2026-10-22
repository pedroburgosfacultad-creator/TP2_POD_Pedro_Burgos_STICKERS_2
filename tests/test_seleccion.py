import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
from src.seleccion import preparar_photoroom


class PruebasSeleccion(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.origen = self.raiz / 'originales'
        self.origen.mkdir()
        self.nombre = 'diseño & especial.jpg'
        Image.new('RGB', (30, 40), 'red').save(self.origen / self.nombre)
        self.seleccion = self.raiz / 'seleccion.json'

    def guardar(self, nombres):
        self.seleccion.write_text(json.dumps({'version': 1, 'carpeta': str(self.origen),
                                             'archivos': nombres}), encoding='utf-8')

    def test_copia_exacta_sin_duplicados_y_destino_nuevo(self):
        self.guardar([self.nombre, self.nombre])
        original = (self.origen / self.nombre).read_bytes()
        destino, copiados, errores = preparar_photoroom(self.seleccion, self.raiz / 'outputs')
        self.assertEqual(copiados, [self.nombre])
        self.assertFalse(errores)
        self.assertEqual((destino / self.nombre).read_bytes(), original)
        self.assertEqual((self.origen / self.nombre).read_bytes(), original)
        otra, _, _ = preparar_photoroom(self.seleccion, self.raiz / 'outputs')
        self.assertNotEqual(destino, otra)

    def test_faltante_no_impide_copiar_el_resto(self):
        self.guardar(['movido.png', self.nombre])
        _, copiados, errores = preparar_photoroom(self.seleccion, self.raiz / 'outputs')
        self.assertEqual(copiados, [self.nombre])
        self.assertEqual(errores[0][0], 'movido.png')

    def test_seleccion_invalida_no_crea_salida(self):
        for nombres in ([], ['../fuera.png'], ['C:\\fuera.png'], ['secreto.txt'], [123]):
            with self.subTest(nombres=nombres):
                self.guardar(nombres)
                with self.assertRaises(ValueError):
                    preparar_photoroom(self.seleccion, self.raiz / 'outputs')
                self.assertFalse((self.raiz / 'outputs').exists())
        self.seleccion.write_text('no es JSON')
        with self.assertRaises(ValueError):
            preparar_photoroom(self.seleccion, self.raiz / 'outputs')

    def test_flujo_menu_y_html(self):
        proyecto = Path(__file__).resolve().parents[1]
        comando = [sys.executable, 'src/main.py', '--salida', str(self.raiz / 'outputs')]
        informe = subprocess.run(comando + [str(self.origen), '--etapa', 'inicial'],
                                 cwd=proyecto, capture_output=True, text=True)
        self.assertEqual(informe.returncode, 0, informe.stderr)
        html = next((self.raiz / 'outputs').glob('*/informe.html')).read_text(encoding='utf-8')
        self.assertIn('value="diseño &amp; especial.jpg"', html)
        self.assertIn('Descargar selección', html)
        self.assertNotIn('@@ORIGEN@@', html)
        self.guardar([self.nombre])
        resultado = subprocess.run(comando, input=f'3\n"{self.seleccion}"\n',
                                   cwd=proyecto, capture_output=True, text=True)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        copias = list((self.raiz / 'outputs').glob('seleccion_photoroom_*/*.jpg'))
        self.assertEqual(len(copias), 1)
        self.assertEqual(copias[0].read_bytes(), (self.origen / self.nombre).read_bytes())
