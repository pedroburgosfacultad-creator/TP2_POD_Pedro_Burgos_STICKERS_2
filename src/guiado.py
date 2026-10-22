"""Preguntas para configurar las dos etapas sin memorizar argumentos."""
from pathlib import Path
import math
import webbrowser


def pedir_carpeta():
    while True:
        texto = input("Carpeta de imágenes (pegá su ruta): ").strip()
        if len(texto) >= 2 and texto[0] == texto[-1] and texto[0] in ("'", '"'):
            texto = texto[1:-1]
        if texto:
            ruta = Path(texto).expanduser()
            if ruta.is_dir():
                return ruta
        print("Ingresá una ruta de carpeta existente.")


def pedir_numero(pregunta, predeterminado, porcentaje=False):
    while True:
        texto = input(f"{pregunta} [{predeterminado:g}]: ").strip()
        try:
            valor = float(texto.replace(",", ".")) if texto else predeterminado
            valido = 0 <= valor <= 100 if porcentaje else valor > 0
            if math.isfinite(valor) and valido:
                return valor
        except ValueError:
            pass
        print("Ingresá un número entre 0 y 100." if porcentaje else
              "Ingresá un número positivo, por ejemplo 4 o 4,5.")


def pedir_tamano(predeterminado):
    return pedir_numero("Lado mayor a imprimir en cm", predeterminado)


def pedir_si_no(pregunta, predeterminado=False):
    while True:
        respuesta = input(f"{pregunta} [{'S/n' if predeterminado else 's/N'}]: ").strip().lower()
        if not respuesta:
            return predeterminado
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Respondé s para sí o n para no.")


def pedir_apertura():
    return pedir_si_no("¿Abrir el HTML en tu navegador al terminar?")


def pedir_etapa(predeterminada="inicial"):
    print("1. Revisión inicial: imágenes recibidas (JPEG y PNG).")
    print("2. Revisión final: archivos preparados (PNG).")
    while True:
        valor = input(f"Etapa [{'1' if predeterminada == 'inicial' else '2'}]: ").strip().lower()
        if not valor:
            return predeterminada
        if valor in ("1", "inicial"):
            return "inicial"
        if valor in ("2", "final"):
            return "final"
        print("Elegí 1 o 2.")


def configurar_guiado(lado_cm, ppi, umbral_parcial, exigir_transparencia, etapa="inicial"):
    print("\nREVISIÓN DE STICKERS · Modo guiado")
    print("Los originales no se modifican. Podés cancelar con Ctrl+C.")
    etapa = pedir_etapa(etapa)
    carpeta = pedir_carpeta()
    print("El tamaño corresponde a la imagen completa, incluidos márgenes y fondos."
          if etapa == "inicial" else
          "El tamaño corresponde al rectángulo visible, sin márgenes transparentes.")
    lado_cm = pedir_tamano(lado_cm)
    ppi = pedir_numero("Referencia mínima de resolución (PPI)", ppi)
    if etapa == "final":
        umbral_parcial = pedir_numero("Umbral de semitransparencia (%)",
                                     umbral_parcial, porcentaje=True)
        exigir_transparencia = pedir_si_no("¿Advertir por imágenes opacas?", exigir_transparencia)
    else:
        print("La transparencia no se evalúa en esta etapa.")
        print("PPI alto NO demuestra nitidez. Capturas ampliadas requieren revisión visual.")
    abrir = pedir_apertura()
    return {"carpeta": carpeta, "lado_cm": lado_cm, "ppi": ppi,
            "umbral_parcial": umbral_parcial, "permitir_opacas": not exigir_transparencia,
            "etapa": etapa, "abrir": abrir}


def abrir_informe(ruta):
    try:
        abierto = webbrowser.open(Path(ruta).resolve().as_uri())
    except (OSError, webbrowser.Error):
        abierto = False
    if not abierto:
        print(f"No se pudo solicitar la apertura del navegador. Abrí este archivo manualmente: {ruta}")
    return abierto

