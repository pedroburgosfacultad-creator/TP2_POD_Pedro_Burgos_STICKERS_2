"""Fuentes intercambiables de rutas para el mismo análisis de imágenes."""
from abc import ABC, abstractmethod
from pathlib import Path
import json


class FuenteImagenes(ABC):
    """Contrato: cargar devuelve rutas, sin evaluar ni copiar imágenes."""

    def __init__(self, ruta):
        self.ruta = Path(ruta)

    @abstractmethod
    def cargar(self):
        """Devuelve una lista de Path; una fuente inválida produce una excepción."""
        pass


class FuenteCarpeta(FuenteImagenes):
    """Fuente que lista los archivos del primer nivel de una carpeta."""
    def cargar(self):
        return buscar_archivos(self.ruta)


class FuenteSeleccionJSON(FuenteImagenes):
    """Fuente que lista los archivos elegidos en un JSON descargado del informe HTML."""
    def cargar(self):
        """Devuelve las rutas de los nombres seleccionados, sin repetir y en su orden."""
        origen, nombres, _ = leer_seleccion(self.ruta)
        return [origen / nombre for nombre in dict.fromkeys(nombres)]


def buscar_archivos(carpeta):
    """Busca archivos del primer nivel y los ordena por nombre."""
    carpeta = Path(carpeta)
    if not carpeta.exists():
        raise FileNotFoundError(f"La carpeta no existe: {carpeta}")
    if not carpeta.is_dir():
        raise NotADirectoryError(f"La ruta no corresponde a una carpeta: {carpeta}")
    archivos = []
    for ruta in carpeta.iterdir():
        if ruta.is_file():
            archivos.append(ruta)
    return sorted(archivos, key=lambda ruta: (ruta.name.casefold(), ruta.name))


def leer_seleccion(archivo_seleccion):
    """Valida el JSON compartido por reanálisis y copia para PhotoRoom."""
    try:
        contenido = Path(archivo_seleccion).read_bytes()
        datos = json.loads(contenido.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("La selección no es un JSON válido descargado del informe.") from error
    if not isinstance(datos, dict) or datos.get("version") != 1:
        raise ValueError("Formato de selección no reconocido.")
    carpeta = datos.get("carpeta")
    nombres = datos.get("archivos")
    if not isinstance(carpeta, str) or not Path(carpeta).is_absolute():
        raise ValueError("La selección debe indicar una carpeta de origen absoluta.")
    if not isinstance(nombres, list) or not nombres:
        raise ValueError("La selección no contiene archivos.")
    for nombre in nombres:
        if (not isinstance(nombre, str) or not nombre or
                any(c in nombre for c in '/\\:\x00') or
                Path(nombre).suffix.lower() not in (".png", ".jpg", ".jpeg")):
            raise ValueError("La selección contiene un nombre de imagen inválido.")
    origen = Path(carpeta).resolve()
    if not origen.is_dir():
        raise ValueError(f"La carpeta original ya no está disponible: {origen}")
    return origen, nombres, contenido
