"""Exportación de resultados: CSV por archivo y resumen legible."""
import csv
from datetime import datetime
from pathlib import Path

CAMPOS = [
    "archivo", "ancho_px", "alto_px", "ancho_visible_px", "alto_visible_px",
    "lado_mayor_cm", "ancho_impresion_cm", "alto_impresion_cm",
    "resolucion_ppi", "referencia_ppi", "tipo_transparencia",
    "transparentes_pct_lienzo", "semitransparentes_pct_visibles",
    "estado", "advertencias", "error",
]


def texto_resumen(resumen, lado_cm, ppi_minimos, umbral_parcial,
                  exigir_transparencia, carpeta):
    porcentaje = resumen["revisar_pct_leidos"]
    porcentaje_texto = f"{porcentaje:.2f} %" if porcentaje is not None else "no aplica"
    lineas = [
        "ANÁLISIS TÉCNICO DE STICKERS",
        f"Carpeta de origen: {Path(carpeta).resolve()}",
        f"Lado mayor del diseño visible: {lado_cm:g} cm",
        f"Referencia de resolución: {ppi_minimos:g} PPI",
        f"Advertencia de semitransparencia: más de {umbral_parcial:g} % de píxeles visibles",
        f"Exigir transparencia: {'sí' if exigir_transparencia else 'no'}",
        "",
        f"PNG encontrados: {resumen['encontrados']}",
        f"Leídos correctamente: {resumen['leidos']}",
        f"Con errores de lectura: {resumen['errores']}",
        f"Con advertencias para revisar: {resumen['revisar']}",
        f"Sin advertencias según estas reglas: {resumen['sin_advertencias']}",
        f"Porcentaje para revisar entre los leídos: {porcentaje_texto}",
        "",
        "MOTIVOS DE ADVERTENCIA (un archivo puede tener varios):",
    ]
    for motivo, cantidad in sorted(resumen["motivos"].items()):
        lineas.append(f"- {motivo}: {cantidad}")
    if not resumen["motivos"]:
        lineas.append("- Ninguno.")
    if resumen["encontrados"] == 0:
        lineas.append("No se encontraron PNG. No hay una colección evaluada.")
    elif resumen["leidos"] == 0:
        lineas.append("No se pudo evaluar ninguna imagen: consultar los errores.")
    lineas += [
        "",
        "INTERPRETACIÓN Y LÍMITES",
        "Consultar informe.csv para identificar cada archivo y sus motivos.",
        "SIN_ADVERTENCIAS no garantiza calidad ni aprobación para imprimir.",
        "La resolución usa el rectángulo de píxeles con alpha > 0, sin recortar el original.",
        "Píxeles aislados casi transparentes pueden ampliar ese rectángulo.",
        "La semitransparencia puede ser intencional; el umbral es una heurística configurable.",
        "SIN_TRANSPARENCIA no demuestra que exista un fondo incorrecto.",
        "No se detectan desenfoque, detalles inventados, contornos defectuosos ni requisitos de la imprenta.",
        "Los registros con ERROR_LECTURA no tienen mediciones válidas.",
        "Los porcentajes y las mediciones del CSV se redondean solo al exportar.",
    ]
    return "\n".join(lineas) + "\n"


def guardar_informes(resultados, errores, texto, directorio):
    """Crea una carpeta por ejecución para conservar informes anteriores."""
    destino = Path(directorio) / datetime.now().strftime("analisis_%Y%m%d_%H%M%S_%f")
    destino.mkdir(parents=True, exist_ok=False)
    with (destino / "informe.csv").open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS, delimiter=";")
        escritor.writeheader()
        for resultado in resultados:
            fila = dict(resultado)
            fila["advertencias"] = " | ".join(fila["advertencias"])
            for campo, valor in fila.items():
                if isinstance(valor, float):
                    fila[campo] = round(valor, 4)
            escritor.writerow(fila)
        for ruta, motivo in errores:
            escritor.writerow({"archivo": ruta.name, "estado": "ERROR_LECTURA",
                               "error": motivo})
    (destino / "resumen.txt").write_text(texto, encoding="utf-8")
    return destino.resolve()

