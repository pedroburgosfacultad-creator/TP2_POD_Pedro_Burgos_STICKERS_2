# Análisis técnico de imágenes para stickers

Autor: Pedro Burgos. Trabajo Práctico 2 de Programación Orientada a Datos.

## Problema, usuario y pregunta

El responsable del microemprendimiento necesita identificar archivos que requieren
revisión antes de componer una impresión. ¿Qué imágenes presentan advertencias
de resolución o transparencia al tamaño de impresión previsto, y qué problemas
aparecen con mayor frecuencia?

La entrada es una carpeta local de PNG estáticos. No se modifica ningún original
ni se recorren subcarpetas. La salida es un informe CSV por archivo y un resumen
de las reglas, cantidades y limitaciones.

## Instalación

Desde la carpeta `C:\tps\tp2_explo`, en PowerShell, con Python 3.14 (versión probada):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py "C:\ruta\a\stickers" --lado-cm 4 --ppi 300
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Si el Python activo ya tiene las dependencias:

```powershell
python src/main.py "C:\ruta\a\stickers" --lado-cm 4 --ppi 300
python -m unittest discover -s tests -v
```

Pillow lee las imágenes; las demás bibliotecas pertenecen a Python. El análisis
funciona sin Internet, APIs ni servicios de IA una vez instaladas las dependencias.

## Parámetros

- `carpeta`: ruta de entrada obligatoria.
- `--lado-cm`: longitud del lado mayor del rectángulo visible, 4 cm por defecto.
  Se conserva la proporción; NO significa que ambos lados deban medir 4 cm.
- `--ppi`: referencia mínima de resolución, 300 PPI por defecto. Es una referencia
  del proyecto que debe confirmarse con el proveedor, no una certificación.
- `--umbral-parcial`: porcentaje de píxeles visibles semitransparentes por encima
  del cual se advierte; 20 por defecto. Es una heurística exploratoria configurable,
  no un estándar de impresión validado. El valor exacto igual al umbral no advierte.
- `--permitir-opacas`: desactiva únicamente la advertencia por falta de transparencia.
- `--salida`: carpeta para resultados. Por defecto es `outputs` dentro de
  la raíz del proyecto, independientemente de dónde se ejecute el comando.

Ejemplo de comparación de tamaños (cada ejecución conserva sus propios informes):

```powershell
python src/main.py "C:\ruta\a\stickers" --lado-cm 4
python src/main.py "C:\ruta\a\stickers" --lado-cm 6
```

## Dónde ver los resultados

La terminal muestra cada evaluación y al final las rutas completas de los informes.
Cada ejecución crea una subcarpeta nueva, por ejemplo:

```text
outputs/analisis_FECHA_HORA/
    informe.csv
    resumen.txt
```

Abrir `resumen.txt` en VS Code para leer la conclusión de la colección.
Abrir o importar `informe.csv` en una planilla para filtrar por `estado` o
`advertencias`. El CSV usa UTF-8 con BOM, separador punto y coma y punto decimal.
Si la planilla no reconoce los números, elegir punto como separador decimal al importar.
Los resultados locales están excluidos de Git: no se suben automáticamente a GitHub.

El CSV incluye todos los archivos encontrados: los ilegibles aparecen como
`ERROR_LECTURA`, con motivo y mediciones vacías. El resumen incluye parámetros
y carpeta de origen. No publicar estos reportes sin revisar su contenido.

## Reglas y cálculos

El alpha indica opacidad: 0 es transparente, 255 opaco y 1 a 254 parcialmente
transparente. La lectura RGBA interpreta también transparencia de PNG de paleta
y transparencia definida mediante tRNS.

Se obtiene la caja rectangular que contiene todos los píxeles con alpha > 0.
Solo se calcula esa caja: no se recorta ni reescribe el archivo. Si sus medidas son
ancho_visible y alto_visible:

```text
lado_visible_px = máximo(ancho_visible, alto_visible)
resolucion_ppi = lado_visible_px × 2.54 / lado_cm
ancho_impresion_cm = lado_cm × ancho_visible / lado_visible_px
alto_impresion_cm = lado_cm × alto_visible / lado_visible_px
```

PPI significa píxeles por pulgada de la imagen impresa; no es la resolución
mecánica DPI de una impresora. Se calcula desde píxeles y centímetros, no desde
una etiqueta DPI guardada en el archivo.

Ejemplo didáctico: un diseño visible de 500 × 500 px mide 317.5 PPI al imprimirlo
a 4 cm y 158.75 PPI a 8 cm. Aumentar el tamaño físico reduce su resolución efectiva.

| Advertencia | Regla |
|---|---|
| SIN_CONTENIDO_VISIBLE | Todos los píxeles son transparentes; no hay resolución calculable |
| RESOLUCION_INFERIOR_A_REFERENCIA | PPI calculado menor a la referencia, sin redondear para decidir |
| SIN_TRANSPARENCIA | Todos los píxeles son opacos y no se indicó permitir opacas |
| ALTA_PROPORCION_SEMITRANSPARENTE | Píxeles con alpha 1..254 / píxeles con alpha > 0 supera el umbral |

`REVISAR` indica al menos una advertencia; `SIN_ADVERTENCIAS` significa que
no se activaron estas reglas. NO significa aprobación para imprimir.
Los motivos pueden superponerse: su suma puede superar la cantidad de imágenes.

El porcentaje de transparencia total se calcula sobre el lienzo completo.
El porcentaje de semitransparencia se calcula sobre los píxeles visibles.
Para una imagen vacía este último se exporta como 0 por convención, junto con
SIN_CONTENIDO_VISIBLE y sin resolución. No significa que tenga contenido opaco.

## Validaciones y límites

La expresión regular `\.png\Z` selecciona extensiones sin distinguir mayúsculas.
Pillow verifica el formato real, integridad y decodificación. Rechazamos archivos
ilegibles, PNG animados e imágenes que superan su protección de tamaño.
No hay reparación automática ni eliminación de duplicados: cada archivo cuenta.

No se evalúan nitidez, fidelidad del diseño, recorte correcto, color ni requisitos
del proveedor. Unas dimensiones grandes no garantizan detalle real.
Los bordes suavizados pueden tener transparencia parcial válida; no se los considera
defectuosos por existir. El umbral requiere validación visual con ejemplos del negocio.
Píxeles aislados casi transparentes pueden ampliar la caja visible y sobreestimar
la resolución útil. Una imagen opaca puede ser un diseño legítimo.

Las mismas imágenes y parámetros producen las mismas mediciones; cambian las
carpetas de salida por ejecución. El CSV redondea a cuatro decimales solo al exportar.
El resumen separa errores de lectura de imágenes evaluadas. Sin imágenes leídas,
el porcentaje para revisar es «no aplica», no 0 %.

Códigos de salida: 0 sin errores de lectura (puede haber advertencias), 1 con archivos
rechazados, 2 con argumentos/carpetas inválidos o fallo al escribir los informes.
Una carpeta sin PNG genera informes vacíos y un aviso explícito.

## Organización

- `src/main.py`: argumentos y coordinación.
- `src/lectura.py`: búsqueda, lectura y clase ImagenSticker con mediciones.
- `src/evaluacion.py`: parámetros, reglas y resumen.
- `src/informes.py`: exportación CSV y texto.
- `tests/`: pruebas ejecutables con imágenes artificiales temporales.
- `data/README.md`: procedencia, variables y condiciones de uso.

## Estado académico

Según la aclaración docente comunicada por el alumno, se permiten imágenes como
entrada sin exigir lectura CSV/JSON. El CSV aquí es un resultado, no una fuente.
Todavía debe resolverse la adaptación del requisito de abstracción de fuentes.
Quedan pendientes la revisión visual de advertencias, selección de una muestra
compartible, documentación final de resultados y preparación de la defensa.

## Galería HTML local

Cada ejecución genera también informe.html y miniaturas/ dentro de su carpeta
de outputs. Abrir informe.html con doble clic en el navegador. No requiere un
servidor, Internet ni dependencias nuevas. CSV y TXT se conservan.

La galería muestra indicadores, motivos, tarjetas con miniaturas (hasta 240 px),
búsqueda por nombre y filtros por estado y advertencia. Las cifras generales
corresponden a la ejecución completa; el contador de tarjetas responde a los filtros.
Las miniaturas son vistas reducidas, no certifican detalles de impresión.
Si falla una miniatura, la tarjeta conserva sus mediciones y se informa el problema.

Para probar con la muestra local pequeña, desde la raíz del proyecto:

~~~powershell
python src/main.py "data/muestra_visual" --lado-cm 4 --ppi 300
~~~

La muestra contiene casos reales seleccionados por advertencia y dos artificiales
identificados, uno vacío y otro dañado. El dañado produce código de salida 1
intencionalmente; los informes igualmente se generan. No extrapolar sus porcentajes
a la colección completa. Su README registra la selección.
La muestra y las salidas están ignoradas por Git. Las pruebas automatizadas generan
sus propias imágenes y no dependen de esa muestra.

Para compartir la galería, copiar toda la carpeta de esa ejecución, incluyendo
miniaturas, CSV y TXT. Revisar permisos de las imágenes antes de publicarla.
El módulo src/galeria.py presenta resultados; no cambia las reglas de evaluación.

## Modo guiado para stickers nuevos

Desde C:\tps\tp2_explo, ejecutar:

~~~powershell
python src/main.py
~~~

El programa pregunta la carpeta de PNG, el lado mayor de impresión y si se desea
abrir el HTML al terminar. Se puede pegar la ruta entre comillas y escribir
decimales con coma o punto. Enter mantiene el tamaño predeterminado de 4 cm;
en la pregunta de apertura, Enter significa no. Ctrl+C cancela.

Los originales pueden estar en cualquier carpeta accesible. No se suben a Internet.
No se recorren subcarpetas. Cada ejecución crea informes nuevos dentro de outputs.
El HTML es un resultado estático: agregar archivos requiere volver a ejecutar.

Los comandos con carpeta y parámetros siguen funcionando sin preguntas.
En modo guiado también se pueden configurar referencias previamente:
python src/main.py --ppi 300 --umbral-parcial 20
Las pruebas de apertura usan simulaciones y no lanzan el navegador real.
