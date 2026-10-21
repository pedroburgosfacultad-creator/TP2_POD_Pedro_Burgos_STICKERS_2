from pathlib import Path

import argparse
import sys

from lectura import analizar_carpeta


def main():
    parser = argparse.ArgumentParser(description="Lee PNG e informa sus dimensiones.")
    parser.add_argument("carpeta", type=Path, help="Carpeta que contiene los stickers")
    argumentos = parser.parse_args()
    try:
        imagenes, errores = analizar_carpeta(argumentos.carpeta)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    for imagen in imagenes:
        print(imagen.resumen())
    for ruta, motivo in errores:
        print(f"ERROR | {ruta.name} | {motivo}", file=sys.stderr)

    encontrados = len(imagenes) + len(errores)
    print(f"\nPNG encontrados: {encontrados}")
    print(f"Leídos correctamente: {len(imagenes)}")
    print(f"Con errores: {len(errores)}")
    if encontrados == 0:
        print("No se encontraron archivos con extensión .png en esta carpeta.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())

