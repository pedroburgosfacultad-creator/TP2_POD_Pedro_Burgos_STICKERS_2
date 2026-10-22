"""Galería HTML local: miniaturas pequeñas y filtros sin Internet."""
from html import escape
from pathlib import Path
from PIL import Image, ImageOps

ETIQUETAS = {
    "RESOLUCION_INFERIOR_A_REFERENCIA": "Resolución baja",
    "SIN_TRANSPARENCIA": "Imagen opaca",
    "ALTA_PROPORCION_SEMITRANSPARENTE": "Semitransparencia alta",
    "SIN_CONTENIDO_VISIBLE": "Sin contenido visible",
}
ESTADOS = {"REVISAR": "Para revisar", "SIN_ADVERTENCIAS": "Sin advertencias",
           "ERROR_LECTURA": "Error de lectura", "CANDIDATO": "Candidato · revisar nitidez"}


def crear_galeria(imagenes, resultados, errores, resumen, texto, destino, etapa="final"):
    """Crea HTML y miniaturas de hasta 240 px. No guarda cambios en los originales."""
    destino = Path(destino)
    miniaturas = destino / "miniaturas"
    miniaturas.mkdir(exist_ok=True)
    rutas = {imagen.ruta.name: imagen.ruta for imagen in imagenes}
    tarjetas = []
    notas = []
    filas = list(resultados) + [
        {"archivo": ruta.name, "estado": "ERROR_LECTURA", "advertencias": [], "error": motivo}
        for ruta, motivo in errores
    ]
    orden = {"REVISAR": 0, "ERROR_LECTURA": 1, "SIN_ADVERTENCIAS": 2, "CANDIDATO": 2}
    filas.sort(key=lambda fila: (orden[fila["estado"]], fila["archivo"].casefold()))
    for numero, fila in enumerate(filas):
        nombre = fila["archivo"]
        estado = fila["estado"]
        motivos = fila["advertencias"]
        vista = '<span class="sin-vista">Sin vista previa</span>'
        if estado != "ERROR_LECTURA":
            try:
                with Image.open(rutas[nombre]) as original:
                    with ImageOps.exif_transpose(original).convert("RGBA") as miniatura:
                        miniatura.thumbnail((240, 240), Image.Resampling.LANCZOS)
                        archivo_miniatura = f"{numero:04d}.png"
                        miniatura.save(miniaturas / archivo_miniatura)
                vista = (f'<img loading="lazy" src="miniaturas/{archivo_miniatura}" '
                         f'alt="{escape(nombre, quote=True)}">')
            except (OSError, ValueError) as error:
                notas.append(f"No se pudo crear miniatura de {nombre}: {error}")
        etiquetas = "".join(f'<li>{escape(ETIQUETAS.get(m, m))}</li>' for m in motivos)
        if estado == "ERROR_LECTURA":
            detalle = f'<p class="error-texto">{escape(fila["error"])}</p>'
        else:
            ppi = fila["resolucion_ppi"]
            resolucion = f"{ppi:.1f}" if ppi is not None else "—"
            inicial = etapa == "inicial"
            dimensiones = (f'{fila["ancho_evaluado_px"]} × {fila["alto_evaluado_px"]}')
            etiqueta = "píxeles de la imagen completa" if inicial else "píxeles visibles"
            alpha = ("Nitidez no evaluada · transparencia no evaluada" if inicial else
                     f'Semitransparentes: {fila["semitransparentes_pct_visibles"]:.1f}% de los visibles')
            detalle = (
                f'<div class="medidas"><div><strong>{resolucion}</strong><span>PPI efectivos</span></div>'
                f'<div><strong>{dimensiones}</strong>'
                f'<span>{etiqueta}</span></div></div>'
                f'<p class="alpha">{alpha}</p>'
            )
        seleccion = (f'<label class="elegir"><input type="checkbox" class="seleccionar" '
                     f'value="{escape(nombre, quote=True)}"> Seleccionar para PhotoRoom</label>'
                     if estado != "ERROR_LECTURA" else "")
        tarjetas.append(
            f'<article class="tarjeta" data-nombre="{escape(nombre.casefold(), quote=True)}" '
            f'data-estado="{estado}" data-motivos="{escape(" ".join(motivos), quote=True)}">'
            f'<div class="vista">{vista}</div><div class="contenido">'
            f'<span class="estado {estado}">{ESTADOS[estado]}</span>'
            f'<h3 title="{escape(nombre, quote=True)}">{escape(nombre)}</h3>{detalle}'
            f'<ul class="motivos">{etiquetas}</ul>{seleccion}</div></article>'
        )
    opciones = "".join(f'<option value="{codigo}">{escape(etiqueta)}</option>'
                       for codigo, etiqueta in ETIQUETAS.items())
    barras = ""
    for codigo, cantidad in sorted(resumen["motivos"].items()):
        porcentaje = 100 * cantidad / resumen["leidos"] if resumen["leidos"] else 0
        barras += (f'<div class="barra"><span>{escape(ETIQUETAS.get(codigo, codigo))}</span>'
                   f'<strong>{cantidad}</strong><div class="pista"><i style="width:{porcentaje:.2f}%"></i></div></div>')
    if not barras:
        barras = '<p>No se activaron advertencias en las imágenes evaluadas.</p>'
    config = ""
    if resultados:
        primero = resultados[0]
        config = f'{primero["lado_mayor_cm"]:g} cm · referencia {primero["referencia_ppi"]:g} PPI'
    else:
        config = "Sin imágenes evaluables · consultá los parámetros del resumen"
    html = PLANTILLA
    cambios = {
        "@@CONFIG@@": escape(config),
        "@@ORIGEN@@": escape(str(imagenes[0].ruta.resolve().parent) if imagenes else "", quote=True),
        "@@ETAPA@@": "Recepción inicial" if etapa == "inicial" else "Revisión final",
        "@@BASE@@": ("Tamaño aplicado a la imagen completa. Candidato solo indica suficientes píxeles; no verifica nitidez, márgenes ni facilidad de quitar el fondo."
                     if etapa == "inicial" else "El tamaño corresponde al lado mayor del diseño visible."),
        "@@POSITIVOS@@": "Candidatos" if etapa == "inicial" else "Sin advertencias",
        "@@TOTAL@@": str(resumen["encontrados"]),
        "@@REVISAR@@": str(resumen["revisar"]),
        "@@SIN@@": str(resumen["candidatos"] if etapa == "inicial" else resumen["sin_advertencias"]),
        "@@ERRORES@@": str(resumen["errores"]),
        "@@BARRAS@@": barras, "@@OPCIONES@@": opciones,
        "@@TARJETAS@@": "\n".join(tarjetas),
        "@@RESUMEN@@": escape(texto),
        "@@NOTAS@@": escape("\n".join(notas)),
    }
    # Una sola sustitución evita reinterpretar contenido de nombres de archivo.
    import re
    html = re.sub(r"@@[A-Z]+@@", lambda m: cambios[m.group(0)], html)
    ruta = destino / "informe.html"
    ruta.write_text(html, encoding="utf-8")
    return ruta, notas


PLANTILLA = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Stickers · Revisión de colección</title>
<style>
:root{--ink:#192a32;--muted:#53656e;--teal:#166c63;--paper:#f5f4ef}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,sans-serif}
header{background:#193c42;color:#fff;padding:36px max(24px,calc((100vw - 1200px)/2))}
.eyebrow{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#bddbd4}
h1{font-size:clamp(28px,4vw,44px);letter-spacing:-1.5px;margin:8px 0}header p{color:#d2e3e0}
nav{display:flex;gap:12px;flex-wrap:wrap}nav a{color:white;border:1px solid #7b9d9e;border-radius:8px;padding:8px 14px;text-decoration:none}
main{max-width:1248px;margin:auto;padding:28px 24px 60px}.indicadores{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.indicador,.panel{background:white;border:1px solid #dce1dc;border-radius:14px;padding:20px}
.indicador strong{display:block;font-size:34px;line-height:1.3}.indicador span{color:var(--muted)}.indicador.aviso{background:#fff5df}
.contexto{display:grid;grid-template-columns:1fr;gap:18px;margin:20px 0 28px}
h2{font-size:20px;margin:0 0 12px}.panel p{margin:8px 0;color:var(--muted)}
.barra{display:grid;grid-template-columns:1fr auto;gap:4px;margin:12px 0}.pista{grid-column:1/-1;background:#eef1ee;height:7px;border-radius:5px;overflow:hidden}.pista i{display:block;background:#c48b26;height:100%}
.filtros{display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:12px;align-items:end}
label{display:block;font-size:13px;font-weight:600}input,select,button{font:inherit;border:1px solid #b4c2bf;border-radius:8px;background:white;padding:10px;min-height:44px;width:100%;color:var(--ink)}button{cursor:pointer}
input:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible{outline:3px solid #24a38d;outline-offset:3px}
.cuenta{color:var(--muted);margin:16px 0}.galeria{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}
.tarjeta{border:1px solid #dce1dc;border-radius:14px;overflow:hidden;background:white}.tarjeta[hidden]{display:none}
.vista{height:210px;display:flex;align-items:center;justify-content:center;padding:16px;background-color:#fff;background-image:conic-gradient(#e5e9e5 25%,transparent 0 50%,#e5e9e5 0 75%,transparent 0);background-size:20px 20px}
.vista img{max-width:100%;max-height:100%;object-fit:contain}.sin-vista{background:#fff;padding:8px 12px;border-radius:8px;color:#53656e}
.contenido{padding:16px}.estado{font-size:11px;font-weight:700;padding:4px 8px;border-radius:5px;display:inline-block}
.REVISAR{background:#fff0c7;color:#744a00}.SIN_ADVERTENCIAS,.CANDIDATO{background:#dff2e9;color:#185b43}.ERROR_LECTURA{background:#fce1dc;color:#942e21}
h3{font-size:14px;line-height:1.4;overflow-wrap:anywhere;margin:12px 0}
.medidas{display:flex;justify-content:space-between;gap:8px;border-top:1px solid #e5e9e5;padding-top:12px}.medidas strong{display:block;font-size:17px}.medidas span,.alpha{font-size:11px;color:var(--muted)}
.motivos{font-size:12px;padding-left:17px;color:#744a00}.error-texto{font-size:13px;overflow-wrap:anywhere}
.elegir{display:flex;align-items:center;gap:8px;margin-top:12px}.elegir input{width:20px;min-height:20px;height:20px}.seleccion-panel{margin:20px 0}.seleccion-panel button{width:auto;margin:4px}button:disabled{opacity:.5;cursor:default}
.vacio{padding:32px;background:white;border-radius:12px;text-align:center}
details{margin-top:28px;background:white;border-radius:12px;padding:18px}summary{cursor:pointer;font-weight:600}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 system-ui,sans-serif}
footer{margin-top:24px;color:var(--muted);font-size:12px}
@media(max-width:1000px){.galeria{grid-template-columns:repeat(3,minmax(0,1fr))}.filtros{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.galeria,.indicadores{grid-template-columns:repeat(2,minmax(0,1fr))}.contexto{grid-template-columns:1fr}.vista{height:180px}}
@media(max-width:440px){.galeria,.filtros{grid-template-columns:1fr}main{padding:20px 16px}.indicador{padding:14px}}
</style></head><body>
<header><div class="eyebrow">Laboratorio de stickers · TP2</div><h1>Revisión de Stickers</h1>
<p>@@ETAPA@@ · @@CONFIG@@ · @@BASE@@</p>
<nav aria-label="Informes"><a href="informe.csv" download>Descargar CSV</a></nav></header>
<main><section class="indicadores" aria-label="Resultados de esta ejecución">
<div class="indicador"><strong>@@TOTAL@@</strong><span>Archivos encontrados</span></div>
<div class="indicador aviso"><strong>@@REVISAR@@</strong><span>Para revisar</span></div>
<div class="indicador"><strong>@@SIN@@</strong><span>@@POSITIVOS@@</span></div>
<div class="indicador"><strong>@@ERRORES@@</strong><span>Errores de lectura</span></div></section>
<section class="contexto"><div class="panel"><h2>¿Qué merece una mirada?</h2>@@BARRAS@@
<p>Un archivo puede tener varios motivos. Las barras expresan proporciones sobre imágenes leídas.</p></div>
</section>
<section class="panel seleccion-panel" aria-label="Selección para PhotoRoom" data-origen="@@ORIGEN@@" id="seleccion-panel">
<h2>Preparar para PhotoRoom</h2>
<p>Marcá las imágenes que querés preparar. Descargá la selección y luego ejecutá el programa: opción 3 del menú.</p>
<p>Se copiarán los originales. Los archivos no seleccionados permanecen en su carpeta. Los filtros no borran tu selección; al recargar la página se pierde.</p>
<p id="seleccion-cuenta" role="status" aria-live="polite">0 seleccionados</p>
<button type="button" id="descargar-seleccion" disabled>Descargar selección</button>
<button type="button" id="vaciar-seleccion">Quitar selección</button>
</section>
<h2>Galería de revisión</h2>
<div class="filtros"><label>Buscar archivo<input id="buscar" type="search" placeholder="Nombre del sticker…"></label>
<label>Estado<select id="estado"><option value="">Todos los estados</option><option value="REVISAR">Para revisar</option><option value="CANDIDATO">Candidatos</option><option value="SIN_ADVERTENCIAS">Sin advertencias</option><option value="ERROR_LECTURA">Error de lectura</option></select></label>
<label>Motivo<select id="motivo"><option value="">Todos los motivos</option>@@OPCIONES@@</select></label>
<button id="limpiar" type="button">Limpiar filtros</button></div>
<p id="cuenta" class="cuenta" role="status" aria-live="polite">@@TOTAL@@ archivos en esta ejecución · primero los que necesitan revisión.</p>
<noscript><p>JavaScript está desactivado: se muestran todas las tarjetas sin filtros.</p></noscript>
<section class="galeria" aria-label="Stickers">@@TARJETAS@@</section>
<p id="vacio" class="vacio" hidden>No hay archivos que coincidan con estos filtros.</p>
<details><summary>Parámetros completos, interpretación y limitaciones</summary><pre>@@RESUMEN@@</pre><pre>@@NOTAS@@</pre></details>
<footer>Informe local · No modifica los originales · Para compartir la galería, conservá también la carpeta miniaturas.</footer>
</main><script>
const buscar=document.querySelector('#buscar'),estado=document.querySelector('#estado'),motivo=document.querySelector('#motivo');
const tarjetas=[...document.querySelectorAll('.tarjeta')];
function filtrar(){const texto=buscar.value.toLocaleLowerCase('es').trim();let visibles=0;
for(const tarjeta of tarjetas){const coincide=tarjeta.dataset.nombre.includes(texto)&&(!estado.value||tarjeta.dataset.estado===estado.value)&&(!motivo.value||tarjeta.dataset.motivos.split(' ').includes(motivo.value));tarjeta.hidden=!coincide;if(coincide)visibles++;}
document.querySelector('#cuenta').textContent=visibles+' de '+tarjetas.length+' archivos mostrados';
document.querySelector('#vacio').hidden=visibles!==0;}
buscar.addEventListener('input',filtrar);estado.addEventListener('change',filtrar);motivo.addEventListener('change',filtrar);
document.querySelector('#limpiar').addEventListener('click',()=>{buscar.value='';estado.value='';motivo.value='';filtrar();});filtrar();
const casillas=[...document.querySelectorAll('.seleccionar')];
const descargar=document.querySelector('#descargar-seleccion');
function seleccionados(){return casillas.filter(c=>c.checked).map(c=>c.value);}
function actualizarSeleccion(){const cantidad=seleccionados().length;
document.querySelector('#seleccion-cuenta').textContent=cantidad+' seleccionados (incluye los ocultos por filtros)';
descargar.disabled=cantidad===0;}
casillas.forEach(c=>c.addEventListener('change',actualizarSeleccion));
document.querySelector('#vaciar-seleccion').addEventListener('click',()=>{casillas.forEach(c=>c.checked=false);actualizarSeleccion();});
descargar.addEventListener('click',()=>{
const archivos=seleccionados();if(!archivos.length)return;
const datos={version:1,carpeta:document.querySelector('#seleccion-panel').dataset.origen,archivos};
const blob=new Blob([JSON.stringify(datos,null,2)],{type:'application/json;charset=utf-8'});
const url=URL.createObjectURL(blob),enlace=document.createElement('a');
enlace.href=url;enlace.download='seleccion_photoroom.json';document.body.appendChild(enlace);enlace.click();enlace.remove();
setTimeout(()=>URL.revokeObjectURL(url),1000);
});
actualizarSeleccion();
</script></body></html>
"""
