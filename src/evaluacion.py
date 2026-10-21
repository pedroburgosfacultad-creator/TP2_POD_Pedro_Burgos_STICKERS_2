"""Reglas explícitas de resolución y transparencia, sin modificar imágenes."""
import math


def validar_parametros(lado_cm, ppi_minimos, umbral_parcial):
    if not math.isfinite(lado_cm) or lado_cm <= 0:
        raise ValueError("El lado mayor en centímetros debe ser positivo y finito.")
    if not math.isfinite(ppi_minimos) or ppi_minimos <= 0:
        raise ValueError("La referencia PPI debe ser positiva y finita.")
    if not math.isfinite(umbral_parcial) or not 0 <= umbral_parcial <= 100:
        raise ValueError("El umbral de transparencia parcial debe estar entre 0 y 100.")


def evaluar_imagen(imagen, lado_cm=4, ppi_minimos=300,
                   umbral_parcial=20, exigir_transparencia=True):
    """El tamaño pedido corresponde al lado mayor del rectángulo visible."""
    validar_parametros(lado_cm, ppi_minimos, umbral_parcial)
    ancho, alto = imagen.dimensiones_visibles()
    transparentes, parciales = imagen.porcentajes_alpha()
    advertencias = []
    ppi = None
    ancho_cm = None
    alto_cm = None

    if ancho == 0 or alto == 0:
        tipo = "completamente_transparente"
        advertencias.append("SIN_CONTENIDO_VISIBLE")
    else:
        ppi = max(ancho, alto) * 2.54 / lado_cm
        ancho_cm = lado_cm * ancho / max(ancho, alto)
        alto_cm = lado_cm * alto / max(ancho, alto)
        if ppi < ppi_minimos:
            advertencias.append("RESOLUCION_INFERIOR_A_REFERENCIA")
        if imagen.histograma_alpha[255] == imagen.ancho_px * imagen.alto_px:
            tipo = "opaca"
            if exigir_transparencia:
                advertencias.append("SIN_TRANSPARENCIA")
        else:
            tipo = "con_transparencia"
        # Una proporción alta pide revisión; no demuestra un defecto gráfico.
        if parciales > umbral_parcial:
            advertencias.append("ALTA_PROPORCION_SEMITRANSPARENTE")

    return {
        "archivo": imagen.ruta.name,
        "ancho_px": imagen.ancho_px,
        "alto_px": imagen.alto_px,
        "ancho_visible_px": ancho,
        "alto_visible_px": alto,
        "lado_mayor_cm": lado_cm,
        "ancho_impresion_cm": ancho_cm,
        "alto_impresion_cm": alto_cm,
        "resolucion_ppi": ppi,
        "referencia_ppi": ppi_minimos,
        "tipo_transparencia": tipo,
        "transparentes_pct_lienzo": transparentes,
        "semitransparentes_pct_visibles": parciales,
        "estado": "REVISAR" if advertencias else "SIN_ADVERTENCIAS",
        "advertencias": advertencias,
        "error": "",
    }


def resumir_resultados(resultados, errores):
    leidos = len(resultados)
    revisar = sum(r["estado"] == "REVISAR" for r in resultados)
    motivos = {}
    for resultado in resultados:
        for motivo in resultado["advertencias"]:
            motivos[motivo] = motivos.get(motivo, 0) + 1
    return {
        "encontrados": leidos + len(errores),
        "leidos": leidos,
        "errores": len(errores),
        "revisar": revisar,
        "sin_advertencias": leidos - revisar,
        "revisar_pct_leidos": 100 * revisar / leidos if leidos else None,
        "motivos": motivos,
    }

