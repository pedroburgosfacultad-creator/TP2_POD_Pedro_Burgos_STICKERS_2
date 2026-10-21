"""Preguntas de terminal para ejecutar el análisis sin memorizar argumentos."""
from pathlib import Path
import math
import webbrowser


def pedir_carpeta():
    while True:
        texto = input("Carpeta de stickers (pegá su ruta): ").strip()
        if len(texto) >= 2 and texto[0] == texto[-1] and texto[0] in ("'", '"'):
            texto = texto[1:-1]
        if not texto:
            print("Ingresá una carpeta; no puede quedar vacía.")
            continue
        ruta = Path(texto).expanduser()
        if ruta.is_dir():
            return ruta
        print("No se encontró esa carpeta. Revisá la ruta y probá otra vez.")


def pedir_tamano(predeterminado):
    while True:
        texto = input(f"Lado mayor del diseño visible en cm [{predeterminado:g}]: ").strip()
        try:
            valor = float(texto.replace(",", ".")) if texto else predeterminado
            if math.isfinite(valor) and valor > 0:
                return valor
        except ValueError:
            pass
        print("Ingresá un número positivo, por ejemplo 4 o 4,5.")


def pedir_apertura():
    while True:
        respuesta = input("¿Abrir el HTML en tu navegador al terminar? [s/N]: ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("", "n", "no"):
            return False
        print("Respondé s para sí o n para no.")


def configurar_guiado(lado_cm, ppi, umbral_parcial, exigir_transparencia):
    print("\nREVISIÓN DE STICKERS · Modo guiado")
    print("Pegá la ruta de una carpeta con PNG. Los originales no se modifican.")
    print("Podés cancelar con Ctrl+C.")
    carpeta = pedir_carpeta()
    lado_cm = pedir_tamano(lado_cm)
    print(f"Referencia: {ppi:g} PPI; umbral de semitransparencia: {umbral_parcial:g} %.")
    print(f"Advertir por imágenes opacas: {'sí' if exigir_transparencia else 'no'}.")
    print("El tamaño elegido se aplica a todos los PNG de esta ejecución.")
    abrir = pedir_apertura()
    return carpeta, lado_cm, abrir


def abrir_informe(ruta):
    """Intenta abrir el informe solo cuando el usuario eligió hacerlo."""
    try:
        abierto = webbrowser.open(Path(ruta).resolve().as_uri())
    except (OSError, webbrowser.Error):
        abierto = False
    if not abierto:
        print(f"No se pudo solicitar la apertura del navegador. Abrí este archivo manualmente: {ruta}")
    return abierto

