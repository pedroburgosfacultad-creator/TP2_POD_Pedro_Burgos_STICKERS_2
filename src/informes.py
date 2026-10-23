"""CSV por imagen y resumen legible de la etapa y reglas aplicadas."""
import csv
from datetime import datetime
from pathlib import Path

CAMPOS = [
    "archivo", "formato", "etapa", "base_resolucion", "ancho_px", "alto_px",
    "ancho_visible_px", "alto_visible_px", "ancho_evaluado_px", "alto_evaluado_px",
    "lado_mayor_cm", "ancho_impresion_cm", "alto_impresion_cm",
    "resolucion_ppi", "referencia_ppi", "tipo_transparencia",
    "transparentes_pct_lienzo", "semitransparentes_pct_visibles",
    "estado", "advertencias", "observaciones", "error",
]


def texto_resumen(resumen, lado_cm, ppi_minimos, umbral_parcial,
                  exigir_transparencia, carpeta, etapa="final"):
    """Arma el resumen textual (parámetros, conteos, motivos y límites) para terminal y HTML."""

    porcentaje = resumen["revisar_pct_leidos"]
    porcentaje_texto = f"{porcentaje:.2f} %" if porcentaje is not None else "no aplica"
    lineas = [
        "ANÁLISIS TÉCNICO DE STICKERS",
        f"Etapa: {etapa}",
        f"Fuente de entrada (carpeta o JSON): {Path(carpeta).resolve()}",
        f"Lado mayor: {lado_cm:g} cm",
        f"Base del cálculo: {'imagen completa' if etapa == 'inicial' else 'rectángulo visible'}",
        f"Referencia de resolución: {ppi_minimos:g} PPI",
    ]
    if etapa == "final":
        lineas += [f"Advertencia de semitransparencia: más de {umbral_parcial:g} % de píxeles visibles",
                   f"Exigir transparencia: {'sí' if exigir_transparencia else 'no'}"]
    else:
        lineas += ["Transparencia y opacidad: no se evalúan en la revisión inicial.",
                   "La imagen completa puede incluir márgenes, interfaz del celular y varios diseños."]
    lineas += [
        "", f"Archivos encontrados (sin subcarpetas): {resumen['encontrados']}",
        f"Leídos correctamente: {resumen['leidos']}",
        f"No procesados (formato no compatible o error de lectura): {resumen['errores']}",
        f"Con advertencias para revisar: {resumen['revisar']}",
    ]
    if etapa == "inicial":
        lineas.append(f"Candidatos a quitar fondo, sujetos a revisión visual: {resumen['candidatos']}")
    else:
        lineas.append(f"Sin advertencias según estas reglas: {resumen['sin_advertencias']}")
    lineas += [f"Porcentaje para revisar entre los leídos: {porcentaje_texto}", "",
               "MOTIVOS (un archivo puede tener varios):"]
    lineas += [f"- {motivo}: {cantidad}" for motivo, cantidad in sorted(resumen["motivos"].items())]
    if not resumen["motivos"]:
        lineas.append("- Ninguno.")
    if resumen["encontrados"] == 0:
        lineas.append("No se encontraron archivos. No hay colección evaluada.")
    elif resumen["leidos"] == 0:
        lineas.append("No se pudo evaluar ninguna imagen: consultar errores.")
    lineas += ["", "INTERPRETACIÓN Y LÍMITES",
               "Nitidez no evaluada: una captura borrosa puede tener muchos píxeles y superar la referencia.",
               "CANDIDATO significa que cumple la referencia numérica; no autoriza procesamiento automático.",
               "Si hay márgenes o varios stickers, seleccionar el diseño y volver a evaluar es más representativo.",
               "El programa no recorta, convierte ni elimina fondos en los originales.",
               "Convertir JPEG a PNG no recupera detalles ni elimina el fondo.",
               "SIN_ADVERTENCIAS no garantiza calidad para imprimir.",
               "La semitransparencia puede ser intencional; su umbral final es una heurística configurable.",
               "En modo final se aceptan PNG; los JPEG se registran como ERROR_LECTURA con explicación.",
               "Los valores vacíos del CSV indican mediciones no aplicables o no disponibles.",
               "Consultar informe.csv e informe.html para identificar cada archivo."]
    return "\n".join(lineas) + "\n"


def guardar_informes(resultados, errores, directorio):
    """Crea una carpeta nueva con informe.csv (resultados y errores) y devuelve su ruta."""
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
            escritor.writerow({"archivo": ruta.name, "estado": "ERROR_LECTURA", "error": motivo})
    return destino.resolve()

