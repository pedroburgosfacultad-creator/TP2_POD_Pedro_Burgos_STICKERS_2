from pathlib import Path

import argparse
import sys

from seleccion import mostrar_preparacion
from lectura import analizar_fuente
from fuentes import FuenteCarpeta, FuenteSeleccionJSON
from guiado import configurar_guiado, abrir_informe
from galeria import crear_galeria
from evaluacion import evaluar_imagen, resumir_resultados, validar_parametros
from informes import guardar_informes, texto_resumen


def main():
    parser = argparse.ArgumentParser(description="Evalúa resolución y transparencia de stickers PNG/JPEG.")
    parser.add_argument("carpeta", nargs="?", type=Path,
                        help="Carpeta de PNG/JPEG; si se omite, inicia el modo guiado")
    parser.add_argument("--lado-cm", type=float, default=4,
                        help="Lado mayor en cm: de 0.1 a 56 (predeterminado: 4); imagen completa en inicial, contenido visible en final")
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
    parser.add_argument("--seleccion", type=Path, help="JSON descargado del HTML para copiar originales a PhotoRoom")
    parser.add_argument("--analizar-seleccion", type=Path, help="JSON de selección para reanalizar los originales sin copiarlos")
    argumentos = parser.parse_args()
    if sum(valor is not None for valor in (argumentos.seleccion, argumentos.carpeta, argumentos.analizar_seleccion)) > 1:
        parser.error("Elegí solo una entrada: carpeta, --analizar-seleccion o --seleccion.")
    abrir_al_terminar = False
    try:
        if argumentos.seleccion is not None:
            return mostrar_preparacion(argumentos.seleccion, argumentos.salida)
        validar_parametros(argumentos.lado_cm, argumentos.ppi, argumentos.umbral_parcial)
        if argumentos.carpeta is None and argumentos.analizar_seleccion is None:
            config = configurar_guiado(
                argumentos.lado_cm, argumentos.ppi, argumentos.umbral_parcial,
                not argumentos.permitir_opacas, argumentos.etapa or "inicial")
            if "seleccion" in config:
                return mostrar_preparacion(config["seleccion"], argumentos.salida)
            abrir_al_terminar = config.pop("abrir")
            for clave, valor in config.items():
                setattr(argumentos, clave, valor)
        argumentos.etapa = argumentos.etapa or ("inicial" if argumentos.analizar_seleccion else "final")
        validar_parametros(argumentos.lado_cm, argumentos.ppi, argumentos.umbral_parcial)
        fuente = (FuenteSeleccionJSON(argumentos.analizar_seleccion) if argumentos.analizar_seleccion
                  else FuenteCarpeta(argumentos.carpeta))
        print(f"Analizando fuente: {fuente.ruta.resolve()}")
        imagenes, errores = analizar_fuente(fuente, argumentos.etapa)
        resultados = [
            evaluar_imagen(imagen, argumentos.lado_cm, argumentos.ppi,
                           argumentos.umbral_parcial, not argumentos.permitir_opacas, argumentos.etapa)
            for imagen in imagenes
        ]
        resumen = resumir_resultados(resultados, errores)
        texto = texto_resumen(resumen, argumentos.lado_cm, argumentos.ppi,
                              argumentos.umbral_parcial, not argumentos.permitir_opacas,
                              fuente.ruta, argumentos.etapa)
        destino = guardar_informes(resultados, errores, argumentos.salida)
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
    print(f"Galería visual: {galeria}")
    for nota in notas:
        print(f"AVISO: {nota}", file=sys.stderr)
    if abrir_al_terminar:
        abrir_informe(galeria)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
