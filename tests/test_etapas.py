import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw, ImageFilter
from src.lectura import analizar_carpeta, leer_imagen
from src.evaluacion import evaluar_imagen
from src.guiado import configurar_guiado


class PruebasEtapas(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)

    def test_jpeg_inicial_y_final_sin_omision(self):
        ruta = self.raiz / 'recibido.JPEG'
        Image.new('RGB', (600, 400), 'white').save(ruta)
        original = ruta.read_bytes()
        imagenes, errores = analizar_carpeta(self.raiz, 'inicial')
        self.assertFalse(errores)
        resultado = evaluar_imagen(imagenes[0], etapa='inicial')
        self.assertEqual(resultado['estado'], 'CANDIDATO')
        self.assertIsNone(resultado['transparentes_pct_lienzo'])
        self.assertEqual(resultado['advertencias'], [])
        imagenes, errores = analizar_carpeta(self.raiz, 'final')
        self.assertFalse(imagenes)
        self.assertEqual(len(errores), 1)
        self.assertIn('etapa inicial', errores[0][1])
        self.assertEqual(original, ruta.read_bytes())

    def test_misma_resolucion_no_significa_misma_nitidez(self):
        imagen = Image.new('RGB', (600, 600), 'white')
        dibujo = ImageDraw.Draw(imagen)
        for x in range(0, 600, 20):
            dibujo.rectangle((x, 0, x + 9, 599), fill='black')
        imagen.save(self.raiz / 'nitida.jpg')
        imagen.filter(ImageFilter.GaussianBlur(12)).save(self.raiz / 'borrosa.jpg')
        resultados = [evaluar_imagen(i, etapa='inicial')
                      for i in analizar_carpeta(self.raiz, 'inicial')[0]]
        self.assertEqual([r['estado'] for r in resultados], ['CANDIDATO'] * 2)
        self.assertEqual(resultados[0]['resolucion_ppi'], resultados[1]['resolucion_ppi'])

    def test_png_inicial_usa_lienzo_final_usa_contenido(self):
        imagen = Image.new('RGBA', (600, 600))
        imagen.paste((255, 0, 0, 255), (100, 100, 200, 200))
        ruta = self.raiz / 'margen.png'
        imagen.save(ruta)
        sticker = leer_imagen(ruta)
        self.assertEqual(evaluar_imagen(sticker, etapa='inicial')['estado'], 'CANDIDATO')
        self.assertEqual(evaluar_imagen(sticker)['estado'], 'REVISAR')

    def test_exif_orientacion(self):
        ruta = self.raiz / 'girada.jpg'
        exif = Image.Exif()
        exif[274] = 6
        Image.new('RGB', (600, 400)).save(ruta, exif=exif)
        sticker = leer_imagen(ruta)
        self.assertEqual((sticker.ancho_px, sticker.alto_px), (400, 600))

    def test_menu_final_configurable(self):
        with patch('builtins.input', side_effect=['2', str(self.raiz), '5', '240', '35', 'n', 'n']):
            config = configurar_guiado(4, 300, 20, True)
        self.assertEqual(config['etapa'], 'final')
        self.assertEqual(config['ppi'], 240)
        self.assertEqual(config['umbral_parcial'], 35)
        self.assertTrue(config['permitir_opacas'])

    def test_inicial_baja_resolucion(self):
        ruta = self.raiz / 'pequena.jpg'
        Image.new('RGB', (100, 200)).save(ruta)
        resultado = evaluar_imagen(leer_imagen(ruta), etapa='inicial')
        self.assertEqual(resultado['advertencias'], ['RESOLUCION_INFERIOR_A_REFERENCIA'])

