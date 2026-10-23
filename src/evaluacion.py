"""Evaluación técnica según la etapa del proceso; no certifica nitidez."""
import math


LADO_MIN_CM = 0.1
LADO_MAX_CM = 56


def validar_lado(lado_cm):
    """Rechaza lados no finitos o fuera del rango de 0,1 a 56 cm (ambos inclusive)."""
    if not math.isfinite(lado_cm) or not LADO_MIN_CM <= lado_cm <= LADO_MAX_CM:
        raise ValueError(f"El lado mayor debe estar entre {LADO_MIN_CM:g} y {LADO_MAX_CM:g} cm, inclusive.")


def validar_parametros(lado_cm, ppi_minimos, umbral_parcial):
    """Valida lado, referencia PPI (positiva y finita) y umbral parcial (0 a 100). Lanza ValueError con un mensaje comprensible si alguno no es válido."""
    validar_lado(lado_cm)
    if not math.isfinite(ppi_minimos) or ppi_minimos <= 0:
        raise ValueError("La referencia PPI debe ser positiva y finita.")
    if not math.isfinite(umbral_parcial) or not 0 <= umbral_parcial <= 100:
        raise ValueError("El umbral de transparencia parcial debe estar entre 0 y 100.")


def evaluar_imagen(imagen, lado_cm=4, ppi_minimos=300,
                   umbral_parcial=20, exigir_transparencia=True, etapa="final"):
    """Evalúa una ImagenSticker y devuelve un diccionario con una fila del informe.
    En la etapa inicial calcula el PPI sobre la imagen completa; en la final, sobre
    el rectángulo con alpha > 0, y además revisa opacidad y semitransparencia.
    Las advertencias se acumulan en 'advertencias' y determinan el 'estado'.
    Lanza ValueError si los parámetros o la etapa no son válidos.
    """
    validar_parametros(lado_cm, ppi_minimos, umbral_parcial)
    if etapa not in ("inicial", "final"):
        raise ValueError("La etapa debe ser inicial o final.")
    ancho_visible, alto_visible = imagen.dimensiones_visibles()
    if etapa == "inicial":
        ancho, alto = imagen.ancho_px, imagen.alto_px
        transparentes, parciales = None, None
        tipo = "no_evaluada"
        base = "imagen_completa"
        observacion = ("Nitidez no evaluada. Capturas ampliadas, márgenes y varios diseños "
                       "pueden sobreestimar la resolución útil del sticker.")
    else:
        ancho, alto = ancho_visible, alto_visible
        transparentes, parciales = imagen.porcentajes_alpha()
        tipo = "con_transparencia"
        base = "rectangulo_visible"
        observacion = "Sin advertencias no garantiza calidad ni aprobación para imprimir."
    advertencias = []
    ppi = ancho_cm = alto_cm = None
    if not ancho_visible or not alto_visible:
        tipo = "completamente_transparente"
        advertencias.append("SIN_CONTENIDO_VISIBLE")
    else:
        ppi = max(ancho, alto) * 2.54 / lado_cm
        ancho_cm = lado_cm * ancho / max(ancho, alto)
        alto_cm = lado_cm * alto / max(ancho, alto)
        if ppi < ppi_minimos:
            advertencias.append("RESOLUCION_INFERIOR_A_REFERENCIA")
        if etapa == "final":
            if imagen.formato != "PNG":
                advertencias.append("FORMATO_NO_PREPARADO")
            if imagen.histograma_alpha[255] == imagen.ancho_px * imagen.alto_px:
                tipo = "opaca"
                if exigir_transparencia:
                    advertencias.append("SIN_TRANSPARENCIA")
            if parciales > umbral_parcial:
                advertencias.append("ALTA_PROPORCION_SEMITRANSPARENTE")
    estado = "REVISAR" if advertencias else (
        "CANDIDATO" if etapa == "inicial" else "SIN_ADVERTENCIAS")
    return {
        "archivo": imagen.ruta.name, "formato": imagen.formato,
        "etapa": etapa, "base_resolucion": base,
        "ancho_px": imagen.ancho_px, "alto_px": imagen.alto_px,
        "ancho_visible_px": ancho_visible, "alto_visible_px": alto_visible,
        "ancho_evaluado_px": ancho, "alto_evaluado_px": alto,
        "lado_mayor_cm": lado_cm, "ancho_impresion_cm": ancho_cm,
        "alto_impresion_cm": alto_cm, "resolucion_ppi": ppi,
        "referencia_ppi": ppi_minimos, "tipo_transparencia": tipo,
        "transparentes_pct_lienzo": transparentes,
        "semitransparentes_pct_visibles": parciales,
        "estado": estado, "advertencias": advertencias,
        "observaciones": observacion, "error": "",
    }


def resumir_resultados(resultados, errores):
    """Cuenta imágenes leídas, errores, estados y motivos de advertencia."""
    leidos = len(resultados)
    revisar = sum(r["estado"] == "REVISAR" for r in resultados)
    candidatos = sum(r["estado"] == "CANDIDATO" for r in resultados)
    sin = sum(r["estado"] == "SIN_ADVERTENCIAS" for r in resultados)
    motivos = {}
    for resultado in resultados:
        for motivo in resultado["advertencias"]:
            motivos[motivo] = motivos.get(motivo, 0) + 1
    return {
        "encontrados": leidos + len(errores), "leidos": leidos,
        "errores": len(errores), "revisar": revisar,
        "sin_advertencias": sin, "candidatos": candidatos,
        "revisar_pct_leidos": 100 * revisar / leidos if leidos else None,
        "motivos": motivos,
    }

