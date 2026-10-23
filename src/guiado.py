"""Preguntas para configurar las dos etapas sin memorizar argumentos."""
from pathlib import Path
import math
import os
import re
from datetime import datetime
import webbrowser

if __package__:
    from .evaluacion import validar_lado, LADO_MIN_CM, LADO_MAX_CM
else:
    from evaluacion import validar_lado, LADO_MIN_CM, LADO_MAX_CM


def pedir_carpeta():
    """Pregunta hasta recibir la ruta de una carpeta existente (acepta comillas)."""

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
    """Pregunta un número (con coma o punto); repite si no es finito o está fuera de rango."""

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
    """Pregunta el lado mayor en cm y repite hasta que esté dentro del rango permitido."""
    while True:
        valor = pedir_numero(f"Lado mayor a imprimir en cm ({LADO_MIN_CM:g} a {LADO_MAX_CM:g})", predeterminado)
        try:
            validar_lado(valor)
            return valor
        except ValueError as error:
            print(error)


def pedir_si_no(pregunta, predeterminado=False):
    """Pregunta sí/no; Enter devuelve el valor predeterminado."""
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
    """Pregunta si se abre el informe HTML en el navegador al terminar."""
    return pedir_si_no("¿Abrir el HTML en tu navegador al terminar?")


def pedir_etapa(predeterminada="inicial", permitir_acciones=True):
    """Muestra el menú y devuelve 'inicial', 'final', 'seleccion' o 'reanalizar'."""
    print("1. Revisión inicial: imágenes recibidas (JPEG y PNG).")
    print("2. Revisión final: archivos preparados (PNG).")
    if permitir_acciones:
        print("3. Preparar carpeta para PhotoRoom desde una selección del HTML.")
        print("4. Volver a analizar una selección JSON.")
    while True:
        valor = input(f"Etapa [{'1' if predeterminada == 'inicial' else '2'}]: ").strip().lower()
        if not valor:
            return predeterminada
        if valor in ("1", "inicial"):
            return "inicial"
        if valor in ("2", "final"):
            return "final"
        if permitir_acciones and valor == "4":
            return "reanalizar"
        if permitir_acciones and valor == "3":
            return "seleccion"
        print("Elegí 1, 2, 3 o 4." if permitir_acciones else "Elegí 1 o 2.")


def configurar_guiado(lado_cm, ppi, umbral_parcial, exigir_transparencia, etapa="inicial"):
    """Conduce el menú y devuelve un diccionario con la configuración elegida.Si se elige preparar PhotoRoom, devuelve solo {'seleccion': ruta_del_json}."""

    print("\nREVISIÓN DE STICKERS · Modo guiado")
    print("Los originales no se modifican. Podés cancelar con Ctrl+C.")
    etapa = pedir_etapa(etapa)
    if etapa == "seleccion":
        return {"seleccion": pedir_seleccion()}
    analizar_seleccion = None
    if etapa == "reanalizar":
        analizar_seleccion = pedir_seleccion()
        etapa = pedir_etapa(permitir_acciones=False)
        carpeta = None
    else:
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
    return {"carpeta": carpeta, "analizar_seleccion": analizar_seleccion, "lado_cm": lado_cm, "ppi": ppi,
            "umbral_parcial": umbral_parcial, "permitir_opacas": not exigir_transparencia,
            "etapa": etapa, "abrir": abrir}


def abrir_informe(ruta):
    """Pide al navegador abrir el HTML; si no puede, muestra la ruta para abrirlo a mano."""

    try:
        abierto = webbrowser.open(Path(ruta).resolve().as_uri())
    except (OSError, webbrowser.Error):
        abierto = False
    if not abierto:
        print(f"No se pudo solicitar la apertura del navegador. Abrí este archivo manualmente: {ruta}")
    return abierto



def carpeta_descargas():
    """Consulta Descargas de Windows; usa la ubicación habitual como respaldo."""
    if os.name == "nt":
        try:
            import winreg
            clave = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave) as registro:
                valor, _ = winreg.QueryValueEx(registro, "{374DE290-123F-4565-9164-39C4925E467B}")
            return Path(os.path.expandvars(valor))
        except OSError:
            pass
    return Path.home() / "Downloads"


def buscar_selecciones(carpeta):
    """Reconoce el nombre de descarga y sus copias numeradas por el navegador."""
    encontrados = []
    for ruta in Path(carpeta).iterdir():
        if re.fullmatch(r"seleccion_photoroom(?: \(\d+\))?\.json", ruta.name, re.IGNORECASE):
            try:
                if ruta.is_file():
                    encontrados.append((ruta, ruta.stat().st_mtime))
            except OSError:
                continue
    return sorted(encontrados, key=lambda item: (-item[1], item[0].name.casefold()))


def pedir_seleccion():
    """Lista los JSON de selección de Descargas y devuelve el elegido (por número o ruta)."""
    carpeta = carpeta_descargas()
    print(f"Buscando selecciones en: {carpeta}")
    try:
        encontrados = buscar_selecciones(carpeta)
    except OSError:
        encontrados = []
        print("No se pudo acceder a Descargas. Podés pegar la ruta del JSON.")
    for numero, (ruta, fecha) in enumerate(encontrados, start=1):
        momento = datetime.fromtimestamp(fecha).strftime("%d/%m/%Y %H:%M:%S")
        print(f"{numero}. {ruta.name} — guardado/modificado {momento}")
    if not encontrados:
        print("No se encontraron selecciones descargadas.")
    print("Elegí un número o pegá la ruta de otro JSON. Ctrl+C cancela.")
    while True:
        texto = input("Selección: ").strip()
        if texto.isdecimal():
            numero = int(texto)
            if 1 <= numero <= len(encontrados):
                ruta = encontrados[numero - 1][0]
            else:
                print("Elegí un número de la lista.")
                continue
        else:
            texto = texto.strip('"').strip("'")
            ruta = Path(texto).expanduser()
        if texto and ruta.is_file() and ruta.suffix.lower() == ".json":
            print(f"Selección elegida: {ruta}")
            return ruta
        print("Ingresá un número válido o la ruta de un archivo JSON existente.")
