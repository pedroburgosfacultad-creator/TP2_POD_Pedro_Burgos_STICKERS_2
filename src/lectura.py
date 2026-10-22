"""Lectura de PNG y JPEG sin modificar las imágenes originales."""

from pathlib import Path
import re
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

if __package__:
    from .fuentes import FuenteCarpeta, buscar_archivos
else:
    from fuentes import FuenteCarpeta, buscar_archivos



class ImagenSticker:
    """Dimensiones del lienzo de un sticker leído correctamente."""

    def __init__(self, ruta, ancho_px, alto_px, histograma_alpha, caja_visible, formato="PNG"):
        self.formato = formato
        self.ruta = Path(ruta)
        self.ancho_px = ancho_px
        self.alto_px = alto_px
        self.histograma_alpha = histograma_alpha
        self.caja_visible = caja_visible

    def dimensiones_visibles(self):
        """Rectángulo que contiene todos los píxeles con alpha mayor que cero."""
        if self.caja_visible is None:
            return 0, 0
        izquierda, arriba, derecha, abajo = self.caja_visible
        return derecha - izquierda, abajo - arriba

    def porcentajes_alpha(self):
        """Transparencia total sobre el lienzo y parcial sobre píxeles visibles."""
        total = self.ancho_px * self.alto_px
        transparentes = self.histograma_alpha[0]
        parciales = sum(self.histograma_alpha[1:255])
        visibles = total - transparentes
        return (100 * transparentes / total,
                100 * parciales / visibles if visibles else 0)

def leer_imagen(ruta):
    """Comprueba formato e integridad y obtiene dimensiones en píxeles."""
    ruta = Path(ruta)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(ruta) as imagen:
                esperado = "PNG" if ruta.suffix.lower() == ".png" else "JPEG"
                formato = imagen.format
                if formato != esperado:
                    raise ValueError(f"El contenido no es {esperado}, aunque tenga esa extensión.")
                if getattr(imagen, "n_frames", 1) > 1:
                    raise ValueError("Los PNG animados no se admiten en esta versión.")
                imagen.verify()
            # verify() requiere reabrir para decodificar los píxeles.
            with Image.open(ruta) as imagen:
                imagen.load()
                imagen = ImageOps.exif_transpose(imagen)
                ancho, alto = imagen.size
                # RGBA también interpreta transparencia de paleta y PNG RGB con tRNS.
                # Esta conversión ocurre en memoria y nunca se guarda sobre el original.
                with imagen.convert("RGBA") as rgba:
                    with rgba.getchannel("A") as alpha:
                        histograma = alpha.histogram()
                        caja = alpha.getbbox()
                return ImagenSticker(ruta, ancho, alto, histograma, caja, formato)
    except UnidentifiedImageError as error:
        raise ValueError("Imagen no reconocida; puede estar dañada o vacía.") from error
    except (Image.DecompressionBombWarning, Image.DecompressionBombError) as error:
        raise ValueError("La imagen supera el límite de seguridad de Pillow.") from error
    except (OSError, SyntaxError) as error:
        raise ValueError(f"No se pudo leer el archivo: {error}") from error


def analizar_carpeta(carpeta, etapa="final"):
    """Atajo compatible con el análisis original por carpeta."""
    return analizar_fuente(FuenteCarpeta(carpeta), etapa)


def analizar_fuente(fuente, etapa="final"):
    """Separa imágenes válidas y errores sin detener todo el lote."""
    if etapa not in ("inicial", "final"):
        raise ValueError("La etapa debe ser inicial o final.")
    imagenes = []
    errores = []
    for ruta in fuente.cargar():
        try:
            if not re.search(r"\.(png|jpe?g)\Z", ruta.name, re.IGNORECASE):
                extension = ruta.suffix or "sin extensión"
                admitidos = "PNG, JPG y JPEG" if etapa == "inicial" else "PNG"
                raise ValueError(f"Formato no compatible ({extension}). "
                                 f"La revisión {etapa} admite {admitidos}. No se abrió el archivo.")
            if etapa == "final" and ruta.suffix.lower() != ".png":
                raise ValueError("La revisión final requiere PNG. Para JPEG usá la etapa inicial.")
            imagenes.append(leer_imagen(ruta))
        except ValueError as error:
            errores.append((ruta, str(error)))
    return imagenes, errores
