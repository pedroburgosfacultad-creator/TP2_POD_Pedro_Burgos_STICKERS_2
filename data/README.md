# Datos y variables

Fuente: colección local de PNG y JPEG utilizada por Pedro Burgos en su microemprendimiento.
Los originales permanecen fuera del repositorio. La carpeta se indica al ejecutar.
Responsable de la selección: Pedro Burgos. No se necesitan datos contables.

Unidad de análisis: un archivo PNG o JPEG estático evaluado a un tamaño configurado.
El mismo archivo en ejecuciones con tamaños distintos no representa un nuevo diseño.
No se eliminan copias automáticamente.

| Variable | Descripción |
|---|---|
| archivo | Nombre del archivo |
| ancho_px, alto_px | Medidas del lienzo completo |
| ancho_visible_px, alto_visible_px | Caja de píxeles con alpha > 0 |
| lado_mayor_cm | Tamaño solicitado para el lado mayor visible |
| ancho_impresion_cm, alto_impresion_cm | Dimensiones físicas conservando proporciones |
| resolucion_ppi | Píxeles por pulgada al tamaño elegido; vacío si no hay contenido |
| referencia_ppi | Umbral configurado |
| tipo_transparencia | opaca, con_transparencia o completamente_transparente |
| transparentes_pct_lienzo | Porcentaje de alpha 0 sobre todos los píxeles |
| semitransparentes_pct_visibles | Porcentaje de alpha 1..254 sobre píxeles alpha > 0 |
| estado | CANDIDATO, REVISAR, SIN_ADVERTENCIAS o ERROR_LECTURA |
| advertencias | Reglas activadas; pueden coexistir |
| error | Motivo si el archivo no se pudo leer |

Los archivos rechazados quedan registrados con mediciones vacías, no con ceros
que aparenten resultados reales. En una imagen vacía, la proporción de
semitransparencia se representa como 0 por convención y se marca SIN_CONTENIDO_VISIBLE.

La colección no es una muestra representativa de todos los diseños posibles.
Deben comprobarse procedencia y derechos de redistribución antes de publicar cada
imagen: pertenecer a la colección no implica licencia abierta. Las pruebas generan
imágenes artificiales temporales sin usar originales comerciales.

Al seleccionar una muestra publicable se documentarán fecha, cantidad, criterio y
condiciones de uso. Los reportes de ejecuciones locales quedan en outputs (ignorado
por Git). El resumen registra los parámetros y la ruta de entrada de cada ejecución.



## Variables de las etapas

- formato: PNG o JPEG verificado por contenido, no solo por extensión.
- etapa: inicial o final.
- base_resolucion: imagen_completa o rectangulo_visible.
- ancho_evaluado_px, alto_evaluado_px: dimensiones utilizadas en el cálculo PPI.
- observaciones: límites de interpretación de la clasificación.
- tipo_transparencia puede ser no_evaluada en recepción; los porcentajes vacíos
  significan no aplicable. La ausencia completa de contenido sigue generando aviso.

La muestra local muestra_jpeg_y_png fue aportada por Pedro (11 JPEG y 1 PNG).
Está excluida de Git; no se modifican sus originales. El resultado numérico inicial
no establece facilidad de eliminar fondos, ni detecta desenfoque o ampliación.
