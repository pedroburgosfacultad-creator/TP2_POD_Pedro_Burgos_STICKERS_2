import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from src.guiado import buscar_selecciones, pedir_seleccion
from src.seleccion import preparar_photoroom


class PruebasDescargas(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)

    def crear(self, nombre, fecha=100):
        ruta = self.raiz / nombre
        ruta.write_text('{}', encoding='utf-8')
        os.utime(ruta, (fecha, fecha))
        return ruta

    def test_filtra_nombres_y_ordena_recientes(self):
        viejo = self.crear('seleccion_photoroom.json', 100)
        nuevo = self.crear('seleccion_photoroom (2).json', 200)
        self.crear('otros.json')
        self.crear('seleccion_photoroom.json.crdownload')
        self.assertEqual([r for r, _ in buscar_selecciones(self.raiz)], [nuevo, viejo])

    def test_elegir_numero_con_reintentos(self):
        ruta = self.crear('seleccion_photoroom (1).json')
        with patch('src.guiado.carpeta_descargas', return_value=self.raiz), \
             patch('builtins.input', side_effect=['99', '', '1']):
            self.assertEqual(pedir_seleccion(), ruta)

    def test_ruta_manual_si_descargas_no_existe(self):
        ruta = self.crear('otro nombre.json')
        with patch('src.guiado.carpeta_descargas', return_value=self.raiz / 'ausente'), \
             patch('builtins.input', return_value=f'"{ruta}"'):
            self.assertEqual(pedir_seleccion(), ruta)

    def test_archiva_json_exacto_y_conserva_descarga_con_faltantes(self):
        origen = self.raiz / 'imagenes'
        origen.mkdir()
        (origen / 'uno.jpg').write_bytes(b'contenido de prueba para copia')
        ruta = self.raiz / 'seleccion_photoroom (1).json'
        contenido = json.dumps({'version': 1, 'carpeta': str(origen),
                                'archivos': ['uno.jpg', 'faltante.png']}).encode('utf-8-sig')
        ruta.write_bytes(contenido)
        destino, copiados, errores = preparar_photoroom(ruta, self.raiz / 'outputs')
        self.assertEqual((destino / 'seleccion_photoroom.json').read_bytes(), contenido)
        self.assertEqual(ruta.read_bytes(), contenido)
        self.assertEqual(copiados, ['uno.jpg'])
        self.assertEqual(len(errores), 1)
