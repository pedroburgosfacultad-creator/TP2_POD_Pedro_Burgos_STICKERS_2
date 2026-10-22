from pathlib import Path

import argparse
import sys

from lectura import analizar_carpeta
from guiado import configurar_guiado, abrir_informe
from galeria import crear_galeria
from evaluacion import evaluar_imagen, resumir_resultados, validar_parametros
from informes import guardar_informes, texto_resumen


def main():
    parser = argparse.ArgumentParser(description="Evalúa resolución y transparencia de stickers PNG/JPEG.")
    parser.add_argument("carpeta", nargs="?", type=Path,
                        help="Carpeta de PNG/JPEG; si se omite, inicia el modo guiado")
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
    parser.add_argument("--etapa", choices=("inicial", "final"),
                        help="Inicial: recibidos PNG/JPEG; final: PNG preparados")
    argumentos = parser.parse_args()
    abrir_al_terminar = False
    try:
        validar_parametros(argumentos.lado_cm, argumentos.ppi, argumentos.umbral_parcial)
        if argumentos.carpeta is None:
            config = configurar_guiado(
                argumentos.lado_cm, argumentos.ppi, argumentos.umbral_parcial,
                not argumentos.permitir_opacas, argumentos.etapa or "inicial")
            abrir_al_terminar = config.pop("abrir")
            for clave, valor in config.items():
                setattr(argumentos, clave, valor)
        argumentos.etapa = argumentos.etapa or "final"
        validar_parametros(argumentos.lado_cm, argumentos.ppi, argumentos.umbral_parcial)
        print(f"Analizando: {argumentos.carpeta.resolve()}")
        imagenes, errores = analizar_carpeta(argumentos.carpeta, argumentos.etapa)
        resultados = [
            evaluar_imagen(imagen, argumentos.lado_cm, argumentos.ppi,
                           argumentos.umbral_parcial, not argumentos.permitir_opacas, argumentos.etapa)
            for imagen in imagenes
        ]
        resumen = resumir_resultados(resultados, errores)
        texto = texto_resumen(resumen, argumentos.lado_cm, argumentos.ppi,
                              argumentos.umbral_parcial, not argumentos.permitir_opacas,
                              argumentos.carpeta, argumentos.etapa)
        destino = guardar_informes(resultados, errores, texto, argumentos.salida)
        galeria, notas = crear_galeria(imagenes, resultados, errores, resumen, texto, destino, argumentos.etapa)
    except (KeyboardInterrupt, EOFError):
        print("\nAnálisis cancelado. Si ya había comenzado, pueden quedar salidas parciales.")
        return 130
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
    print(f"Galería visual: {galeria}")
    for nota in notas:
        print(f"AVISO: {nota}", file=sys.stderr)
    if abrir_al_terminar:
        abrir_informe(galeria)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
