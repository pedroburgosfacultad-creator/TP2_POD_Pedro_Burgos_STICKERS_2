from pathlib import Path

import argparse
import sys

from lectura import analizar_carpeta
from evaluacion import evaluar_imagen, resumir_resultados, validar_parametros
from informes import guardar_informes, texto_resumen


def main():
    parser = argparse.ArgumentParser(description="Evalúa resolución y transparencia de PNG.")
    parser.add_argument("carpeta", type=Path, help="Carpeta que contiene los stickers")
    parser.add_argument("--lado-cm", type=float, default=4,
                        help="Lado mayor del diseño visible en cm (predeterminado: 4)")
    parser.add_argument("--ppi", type=float, default=300,
                        help="Referencia mínima de píxeles por pulgada (300)")
    parser.add_argument("--umbral-parcial", type=float, default=20,
                        help="Porcentaje de píxeles visibles semitransparentes que activa aviso (20)")
    parser.add_argument("--permitir-opacas", action="store_true",
                        help="No advertir por ausencia de transparencia")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).resolve().parents[1] / "outputs",
                        help="Carpeta para los informes (predeterminado: outputs en la raíz del proyecto)")
    argumentos = parser.parse_args()
    try:
        validar_parametros(argumentos.lado_cm, argumentos.ppi, argumentos.umbral_parcial)
        imagenes, errores = analizar_carpeta(argumentos.carpeta)
        resultados = [
            evaluar_imagen(imagen, argumentos.lado_cm, argumentos.ppi,
                           argumentos.umbral_parcial, not argumentos.permitir_opacas)
            for imagen in imagenes
        ]
        resumen = resumir_resultados(resultados, errores)
        texto = texto_resumen(resumen, argumentos.lado_cm, argumentos.ppi,
                              argumentos.umbral_parcial, not argumentos.permitir_opacas,
                              argumentos.carpeta)
        destino = guardar_informes(resultados, errores, texto, argumentos.salida)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    for imagen, resultado in zip(imagenes, resultados):
        ppi = resultado["resolucion_ppi"]
        resolucion = f"{ppi:.1f} PPI" if ppi is not None else "sin contenido visible"
        motivos = ", ".join(resultado["advertencias"]) or "sin advertencias"
        print(f"{resultado['estado']} | {imagen.ruta.name} | "
              f"{imagen.ancho_px} x {imagen.alto_px} px | {resolucion} | {motivos}")
    for ruta, motivo in errores:
        print(f"ERROR | {ruta.name} | {motivo}", file=sys.stderr)

    print("\n" + texto)
    print(f"Informe por archivo: {destino / 'informe.csv'}")
    print(f"Resumen: {destino / 'resumen.txt'}")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
