"""Lectura de PNG sin modificar las imágenes originales."""

from pathlib import Path
import re
import warnings

from PIL import Image, UnidentifiedImageError


class ImagenSticker:
    """Dimensiones del lienzo de un sticker leído correctamente."""

    def __init__(self, ruta, ancho_px, alto_px):
        self.ruta = Path(ruta)
        self.ancho_px = ancho_px
        self.alto_px = alto_px

    def resumen(self):
        return f"OK | {self.ruta.name} | {self.ancho_px} x {self.alto_px} px"


def buscar_png(carpeta):
    """Busca archivos del primer nivel y los ordena por nombre."""
    carpeta = Path(carpeta)
    if not carpeta.exists():
        raise FileNotFoundError(f"La carpeta no existe: {carpeta}")
    if not carpeta.is_dir():
        raise NotADirectoryError(f"La ruta no corresponde a una carpeta: {carpeta}")
    archivos = []
    for ruta in carpeta.iterdir():
        # Valida la extensión; el contenido se verifica después con Pillow.
        if ruta.is_file() and re.search(r"\.png\Z", ruta.name, re.IGNORECASE):
            archivos.append(ruta)
    return sorted(archivos, key=lambda ruta: (ruta.name.casefold(), ruta.name))


def leer_png(ruta):
    """Comprueba formato e integridad y obtiene dimensiones en píxeles."""
    ruta = Path(ruta)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(ruta) as imagen:
                if imagen.format != "PNG":
                    raise ValueError("El contenido no es PNG, aunque tenga esa extensión.")
                if getattr(imagen, "n_frames", 1) > 1:
                    raise ValueError("Los PNG animados no se admiten en esta versión.")
                imagen.verify()
            # verify() requiere reabrir para decodificar los píxeles.
            with Image.open(ruta) as imagen:
                imagen.load()
                ancho, alto = imagen.size
                return ImagenSticker(ruta, ancho, alto)
    except UnidentifiedImageError as error:
        raise ValueError("Imagen no reconocida; puede estar dañada o vacía.") from error
    except (Image.DecompressionBombWarning, Image.DecompressionBombError) as error:
        raise ValueError("La imagen supera el límite de seguridad de Pillow.") from error
    except (OSError, SyntaxError) as error:
        raise ValueError(f"No se pudo leer el archivo: {error}") from error


def analizar_carpeta(carpeta):
    """Separa imágenes válidas y errores sin detener todo el lote."""
    imagenes = []
    errores = []
    for ruta in buscar_png(carpeta):
        try:
            imagenes.append(leer_png(ruta))
        except ValueError as error:
            errores.append((ruta, str(error)))
    return imagenes, errores
