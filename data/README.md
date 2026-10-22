# Datos de entrada, salidas y significado de las variables

## Procedencia y unidad de análisis

Fuente: imágenes PNG/JPEG utilizadas por Pedro Burgos en su microemprendimiento.
No se usan datos contables ni se requieren ventas simuladas. La unidad de análisis
es un archivo estático evaluado en una etapa y a un tamaño físico determinado.
Reanalizarlo a otro tamaño no representa una venta ni un nuevo diseño.

Las imágenes pueden estar en cualquier carpeta accesible. Solo se enumeran archivos
del primer nivel; los formatos no admitidos también se registran como no procesados.
No se eliminan duplicados. Las imágenes y miniaturas se procesan sin modificar originales.

Las muestras locales `muestra_visual/` y `muestra_jpeg_y_png/` están ignoradas por Git.
La segunda fue aportada por el usuario con 11 JPEG y 1 PNG. La muestra visual contiene
casos reales seleccionados por advertencia y casos artificiales vacío/dañado; consultar
su README local para la selección. No son muestras representativas del negocio.
Las pruebas de tests generan datos artificiales temporales y no dependen de ellas.

Pertenecer a la colección no implica licencia de redistribución. Revisar los permisos
antes de compartir imágenes, miniaturas o informes. Los informes y selecciones incluyen
nombres y rutas locales. Una muestra publicable debe indicar procedencia, criterio de
selección, cantidad y condiciones de uso.

## Diccionario de informe.csv

Cada fila corresponde a un archivo evaluado: todos los archivos de la carpeta de
entrada o, al reanalizar una selección JSON, solo los nombres incluidos en ella.
El CSV se genera en outputs, no dentro de data. Formato: UTF-8 con BOM,
separador `;`, punto decimal y hasta cuatro decimales. Los vacíos representan
datos no disponibles/no aplicables, no ceros.

| Campo | Significado |
|---|---|
| archivo | Nombre con extensión |
| formato | PNG o JPEG verificado por contenido; vacío en archivos rechazados |
| etapa | inicial o final; vacío en archivos rechazados |
| base_resolucion | imagen_completa en inicial; rectangulo_visible en final |
| ancho_px, alto_px | Dimensiones de la imagen, respetando orientación EXIF |
| ancho_visible_px, alto_visible_px | Caja que contiene todos los píxeles con alpha > 0 |
| ancho_evaluado_px, alto_evaluado_px | Dimensiones utilizadas para calcular PPI según la etapa |
| lado_mayor_cm | Tamaño físico solicitado: de 0,1 a 56 cm, inclusive |
| ancho_impresion_cm, alto_impresion_cm | Medidas físicas conservando proporciones; vacías sin contenido visible |
| resolucion_ppi | max(ancho_evaluado_px, alto_evaluado_px) × 2.54 / lado_mayor_cm; vacío sin contenido visible |
| referencia_ppi | Referencia positiva, 300 por defecto |
| tipo_transparencia | opaca, con_transparencia, completamente_transparente o no_evaluada |
| transparentes_pct_lienzo | Píxeles con alpha 0 / píxeles totales × 100; solo final |
| semitransparentes_pct_visibles | Píxeles con alpha 1..254 / píxeles visibles × 100; solo final |
| estado | CANDIDATO, REVISAR, SIN_ADVERTENCIAS o ERROR_LECTURA |
| advertencias | Motivos separados por una barra vertical; pueden coexistir |
| observaciones | Limitaciones de interpretación de los resultados |
| error | Motivo del rechazo; puede ser formato incompatible o fallo de lectura |

En inicial, la transparencia no se evalúa: los porcentajes quedan vacíos, aunque
la ausencia total de contenido sí genera aviso. En final, una imagen vacía tiene
100 % de transparencia total, 0 % parcial por convención y resolución vacía.

CANDIDATO solo indica que no se activaron advertencias de la etapa inicial.
SIN_ADVERTENCIAS corresponde a la final. Ninguno certifica calidad de impresión.
ERROR_LECTURA aparece como «No procesado» en HTML y no implica necesariamente daño.
Las filas rechazadas tienen mediciones vacías. Los porcentajes globales de advertencias
se calculan únicamente sobre imágenes leídas; las reglas se describen en el README raíz.

El CSV no guarda el umbral parcial ni la opción de advertir por opacidad. Conservar
el HTML correspondiente, cuyo resumen registra esos parámetros y la carpeta de origen.
No combinar ejecuciones como si fueran archivos distintos sin identificar los diseños
y las condiciones de cada evaluación.

## Selección para PhotoRoom

El HTML descarga un JSON con esta estructura:

```json
{
  "version": 1,
  "carpeta": "C:\\ruta\\a\\imagenes",
  "archivos": ["sticker_01.jpg", "sticker_02.png"]
}
```

`version` identifica el formato; `carpeta` es la ruta absoluta de origen;
`archivos` contiene los nombres elegidos, no las imágenes ni mediciones.
No registra fecha de selección, identificador de informe, motivos manuales ni
confirmación de trabajo terminado. No seleccionar no equivale a rechazar.

Python conserva una copia exacta del JSON junto a las imágenes copiadas en
outputs/seleccion_photoroom_FECHA_HORA. Si falta un archivo, el JSON mantiene su
nombre y la terminal informa el fallo. Por eso es un registro de intención,
no una constancia de que todo se copió. No convertir sus selecciones en métricas
de calidad o productividad sin agregar datos de revisión manual y seguimiento.


## Constancia de revisión de datos

Fecha de inspección local: 22/10/2026. No se dispone de una fecha de obtención
individual ni licencia de redistribución acreditada para cada imagen del negocio;
no se las presume abiertas. La muestra mixta contenía, al auditarla, 12 imágenes
(11 JPEG y un PNG) y un PDF agregado para comprobar el rechazo de formatos.
La referencia de 50 observaciones del punto 2 de la consigna requiere documentar
una ejecución sobre datos autorizados o justificar un tamaño menor. Los casos
temporales de los tests verifican software, no sustituyen automáticamente esa evidencia.
Antes de entregar, acordar una muestra compartible o un procedimiento reproducible
de generación/obtención. El resultado local se documenta en el informe final.


El mismo JSON ahora sirve como fuente del reanálisis (opción 4). No incorpora las
mediciones anteriores: se vuelven a leer los originales y se eligen parámetros
nuevos. Nombres repetidos en la selección se procesan una vez. Esto no es una
deduplicación de la colección por contenido. El CSV tiene el mismo esquema que
al analizar una carpeta y el resumen HTML registra la ruta del JSON utilizado.
