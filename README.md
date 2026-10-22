# Revisión técnica de imágenes para stickers

Autor: Pedro Burgos. Trabajo Práctico 2 de Programación Orientada a Datos.

## Problema y alcance

El microemprendimiento recibe imágenes que deben revisarse antes de preparar stickers.
El programa responde: **¿Qué archivos presentan advertencias de resolución o
transparencia al tamaño previsto, y qué problemas aparecen con más frecuencia?**

Se analizan imágenes locales, se generan mediciones y estadísticas, y se presenta
una galería para tomar decisiones manuales. No se necesitan registros contables.
Según la aclaración docente comunicada por el alumno, se permiten imágenes como
entrada; el CSV es una salida del análisis, no un requisito artificial de entrada.

Hay dos etapas:

| Etapa | Archivos admitidos | Base del cálculo | Resultado sin advertencias |
|---|---|---|---|
| Inicial: recepción | PNG, JPG, JPEG estáticos | Imagen completa, incluidos fondos y márgenes | CANDIDATO, sujeto a revisión visual |
| Final: archivos preparados | PNG estáticos | Rectángulo que contiene los píxeles visibles | SIN_ADVERTENCIAS, no aprobación de impresión |

El programa no detecta nitidez, no convierte imágenes ni quita fondos. Convertir
JPEG a PNG no recupera detalle. Una captura ampliada puede superar la referencia
PPI y seguir borrosa. La elección para PhotoRoom siempre corresponde al usuario.

## Instalación y ejecución

Proyecto activo: `C:\tps\tp2_explo`.
Repositorio: https://github.com/pedroburgosfacultad-creator/TP2_POD_Pedro_Burgos_STICKERS_2

Versión probada: Python 3.14. Dependencia: Pillow 12.3.0, fijada en requirements.txt.
Desde la raíz del proyecto, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

Si el Python activo ya tiene Pillow instalado:

```powershell
python src/main.py
```

El menú ofrece revisión inicial, revisión final y preparación para PhotoRoom.
Las preguntas aceptan rutas entre comillas y decimales con coma o punto. Enter
mantiene el valor indicado; Ctrl+C cancela. La lectura sigue usando `input()`.
No hay servidor, APIs, agentes ni servicios pagos. Tras instalar Pillow, el
análisis y la preparación de carpetas funcionan sin Internet.

## Parámetros y tamaño físico

El **lado mayor permitido es de 0,1 a 56 cm, inclusive**, con 4 cm por defecto.
56 cm corresponde a la plantilla máxima indicada por el usuario. El mínimo de
0,1 cm (1 mm) es un criterio práctico del proyecto para evitar valores absurdamente
pequeños; no es una norma de impresión. Se conserva la proporción: no se exige
que ambos lados midan lo indicado. El programa no distribuye diseños en una plantilla.

| Parámetro | Uso |
|---|---|
| `carpeta` | Carpeta de entrada; si se omite, abre el menú |
| `--etapa inicial` / `--etapa final` | Modo de evaluación; con carpeta explícita se usa final por defecto; el menú propone inicial |
| `--lado-cm` | Lado mayor entre 0.1 y 56; por comando se usa punto decimal |
| `--ppi` | Referencia positiva y finita; 300 por defecto |
| `--umbral-parcial` | Porcentaje de semitransparencia entre 0 y 100; 20 por defecto; aplica a etapa final |
| `--permitir-opacas` | Desactiva el aviso por ausencia de transparencia en etapa final |
| `--salida` | Directorio de resultados; por defecto outputs en la raíz del proyecto |
| `--seleccion` | JSON descargado del HTML para preparar la carpeta de PhotoRoom; no se combina con carpeta de análisis |
| `--analizar-seleccion` | JSON descargado del HTML para volver a analizar los originales seleccionados, sin copiarlos; inicial por defecto; no se combina con carpeta ni `--seleccion` |

```powershell
python src/main.py "data/muestra_jpeg_y_png" --etapa inicial --lado-cm 4 --ppi 300
python src/main.py "C:\ruta\a\png_preparados" --etapa final --lado-cm 6 --umbral-parcial 25
python src/main.py --seleccion "C:\ruta\seleccion_photoroom.json"
```

En el menú, un tamaño fuera del rango provoca una nueva pregunta. Por comando,
se informa el error sin crear resultados. NaN, infinito y tamaños fuera de rango
se rechazan también al llamar directamente a la función de evaluación.

## Lectura y evaluación

Solo se enumeran archivos del primer nivel; no se recorren subcarpetas. Las
extensiones se reconocen sin distinguir mayúsculas. Pillow comprueba el formato
real, verifica y decodifica la imagen. Se respeta la orientación EXIF.
Los originales nunca se guardan modificados.

PDF, TXT, WEBP y otros formatos quedan registrados como no procesados, sin abrirlos.
También se rechazan imágenes dañadas, PNG animados y tamaños que exceden la
protección de Pillow. Un JPEG en etapa final recibe una explicación para usar la
etapa inicial. Un rechazo no detiene el análisis de los otros archivos.

Para la resolución se usa:

```text
lado_evaluado_px = máximo(ancho_evaluado_px, alto_evaluado_px)
resolucion_ppi = lado_evaluado_px × 2.54 / lado_cm
ancho_impresion_cm = lado_cm × ancho_evaluado_px / lado_evaluado_px
alto_impresion_cm = lado_cm × alto_evaluado_px / lado_evaluado_px
```

PPI significa píxeles por pulgada; no es el DPI mecánico de una impresora ni el
valor de una etiqueta guardada en la imagen. Un lado de 500 px produce 317,5 PPI
a 4 cm y 158,75 PPI a 8 cm. La referencia debe acordarse con el proveedor.

El canal alpha vale 0 para transparencia total, 255 para opacidad y 1 a 254 para
transparencia parcial. El rectángulo visible abarca todos los píxeles con alpha > 0.
Se interpreta también transparencia de paleta y PNG con tRNS.

| Advertencia | Condición |
|---|---|
| SIN_CONTENIDO_VISIBLE | No hay píxeles visibles; resolución y medidas de impresión quedan vacías |
| RESOLUCION_INFERIOR_A_REFERENCIA | PPI menor que la referencia, antes de redondear |
| SIN_TRANSPARENCIA | Todos los píxeles son opacos y está activado el aviso; solo final |
| ALTA_PROPORCION_SEMITRANSPARENTE | El porcentaje parcial supera el umbral; igual al umbral no advierte; solo final |

La transparencia total se divide por todos los píxeles; la parcial, por los visibles.
En una imagen completamente transparente, el porcentaje parcial final es 0 por
convención, acompañado de SIN_CONTENIDO_VISIBLE. En inicial, los porcentajes de
transparencia no se evalúan y quedan vacíos.

Los totales distinguen candidatos/sin advertencias, imágenes para revisar y archivos
no procesados. Los porcentajes de advertencias usan únicamente imágenes leídas.
Los motivos pueden superponerse; sin imágenes evaluadas el porcentaje es «no aplica».

## Resultados y galería

Cada ejecución crea una carpeta distinta y muestra su ruta en la terminal:

```text
outputs/analisis_FECHA_HORA/
    informe.html
    informe.csv
    miniaturas/
```

Abrir informe.html con doble clic. Incluye miniaturas de hasta 240 px, indicadores,
filtros por estado/motivo, búsqueda y el resumen con parámetros y limitaciones.
El HTML recibe los resultados en memoria; no lee el CSV para construirse.
Las miniaturas no reemplazan la revisión del original a tamaño completo.
Si una miniatura falla, se conserva la tarjeta y se informa el problema.

El CSV es una tabla por archivo para Excel, LibreOffice o futuros análisis.
Usa UTF-8 con BOM, punto y coma como separador y punto decimal, con hasta cuatro
decimales. El diccionario está en [data/README.md](data/README.md).
No se genera TXT; el resumen se conserva en la terminal y en el HTML.
El CSV solo no conserva el umbral parcial y la opción de opacidad: mantener el
HTML de la misma ejecución para conocer todos los parámetros.

Un archivo rechazado tiene estado ERROR_LECTURA en CSV y «No procesado» en HTML,
con explicación y mediciones vacías. Ese estado no implica necesariamente daño.
Los archivos no procesados no tienen casilla para PhotoRoom.

Agregar imágenes requiere ejecutar nuevamente el análisis. Para compartir el informe,
conservar toda la carpeta de ejecución, incluyendo miniaturas y CSV. Las rutas
locales del HTML/JSON no se adaptan automáticamente a otra computadora.

## Preparar una selección para PhotoRoom

1. Marcar las casillas de las imágenes elegidas en el HTML.
2. Pulsar «Descargar selección». El navegador guarda seleccion_photoroom.json.
3. Ejecutar el programa y elegir la opción 3.
4. Elegir un JSON por número en la lista de Descargas, ordenada desde el más reciente,
   o pegar su ruta si el navegador lo guardó en otra carpeta.
5. Usar las imágenes de la carpeta que muestra la terminal en PhotoRoom manualmente.

```text
outputs/seleccion_photoroom_FECHA_HORA/
    seleccion_photoroom.json
    sticker_01.jpg
    sticker_02.png
```

Se copian los originales y una copia exacta del JSON. No se mueven ni convierten.
Descargas conserva su archivo. Cada preparación crea otra carpeta: repetirla ocupa
espacio adicional. La búsqueda admite los sufijos numerados del navegador y consulta
la ubicación de Descargas de Windows; una carpeta personalizada del navegador puede
requerir indicar la ruta manualmente.

Los filtros mantienen la selección, incluso cuando ocultan tarjetas. «Quitar selección»
la borra; «Limpiar filtros» no. Cerrar o recargar el HTML pierde la selección no descargada.
No seleccionar no significa rechazar. Seleccionar no significa que ya se procesó.

Si falta un original, se informa NO COPIADO y se continúa con los demás. El JSON
archivado registra lo solicitado, no acredita que todas las copias se completaron.
Si un original cambió, se copia su versión actual: generar otro informe tras modificarlo.
La copia rechaza nombres que salen de la carpeta de origen y enlaces simbólicos.

## Organización y pruebas

| Módulo | Responsabilidad |
|---|---|
| src/main.py | Argumentos, coordinación, presentación en terminal y códigos de salida |
| src/guiado.py | Preguntas, búsqueda de selecciones y apertura del HTML |
| src/fuentes.py | Contrato FuenteImagenes, fuentes de carpeta/selección y validación compartida del JSON |
| src/lectura.py | Enumeración, lectura PNG/JPEG y clase ImagenSticker |
| src/evaluacion.py | Rango físico, reglas, mediciones y estadísticas |
| src/informes.py | CSV y texto del resumen compartido por terminal y HTML |
| src/galeria.py | Miniaturas, HTML, filtros y descarga de selección en JavaScript |
| src/seleccion.py | Validación del JSON y copia para PhotoRoom |

```powershell
python -m unittest discover -s tests -v
```

El alcance de las pruebas y su interpretación están en [tests/README.md](tests/README.md).
No necesitan imágenes privadas ni Internet. Códigos de salida: 0 si no hubo rechazos
(puede haber advertencias), 1 si algún archivo fue rechazado/no copiado, 2 por error
de parámetros, carpeta, selección o escritura, y 130 por cancelación. Si se interrumpe
una operación empezada o falla la escritura, pueden quedar salidas parciales.

## Límites, GitHub y entrega

No se certifican nitidez, color, recorte ni facilidad de eliminar fondos. Márgenes,
varios diseños o píxeles aislados pueden sobreestimar la resolución útil. La
semitransparencia puede ser intencional; su umbral es una heurística configurable.
No se eliminan duplicados ni se hace seguimiento de ventas o pedidos.

Las salidas, entornos y muestras privadas están excluidos de Git. No agregar nuevas
imágenes sin comprobar sus permisos de distribución. El código, requirements.txt,
documentación y pruebas permiten reproducir el funcionamiento sin esas muestras.

Antes de entregar, contrastar la implementación con la consigna, justificar la adaptación
del requisito de abstracción de fuentes mediante carpeta y selección JSON, preparar una muestra
compartible y documentar la revisión visual. Esta documentación describe lo implementado;
no sustituye la verificación académica, la evidencia de trabajo ni la defensa individual.

Para la defensa, explicar la diferencia entre etapas, PPI y nitidez, alpha, denominadores
de los porcentajes, errores por archivo y decisión manual. El caso de una imagen borrosa
con muchos píxeles es una limitación del método, no una garantía de calidad.


## Auditoría final y ejemplo comprobado

La [auditoría final](docs/INFORME_FINAL.md) contrasta el código con los siete pasos
de la consigna y detalla evidencia, limitaciones, proyección y pendientes de entrega.

El 22/10/2026 se verificaron 52 pruebas y el flujo completo con la muestra local
mixta, que ahora incluye un PDF: 13 archivos en total. A 4 cm y 300 PPI, la etapa
inicial produjo 10 candidatos, 2 imágenes para revisar y 1 archivo no procesado.
El 16,67 % corresponde a las 2 imágenes con advertencias entre las 12 leídas;
no mide calidad real ni representa la colección completa. En final se leyó el PNG
(con dos advertencias) y se rechazaron los 11 JPEG y el PDF por formato de etapa.

Para entregar, identificar el commit definitivo con `git rev-parse HEAD` después
de confirmar y publicar los últimos cambios. El enlace solo no identifica la versión.
El alumno confirmó que el docente solo autorizó cambiar los datos de entrada.
El requisito de abstracción común de fuentes se implementó con FuenteCarpeta y
FuenteSeleccionJSON. La adaptación al dominio de imágenes debe explicarse en la defensa.
También debe acreditarse la referencia de 50 observaciones o justificarse menos,
y garantizar datos de demostración autorizados y accesibles para la cátedra.


## Reanalizar una selección: abstracción de fuentes

La opción **4** del menú permite elegir un JSON de Descargas (o pegar su ruta),
elegir revisión inicial/final y definir tamaño y parámetros nuevos. Genera otro
HTML y CSV solo para los originales seleccionados; no copia imágenes a PhotoRoom.
La opción **3** conserva esa función de copia.

```powershell
python src/main.py --analizar-seleccion "C:\ruta\seleccion_photoroom.json" --lado-cm 6 --etapa inicial
```

FuenteImagenes es una clase abstracta: exige cargar(), que devuelve una lista de
rutas. FuenteCarpeta enumera archivos; FuenteSeleccionJSON lee la lista seleccionada.
analizar_fuente() usa el mismo contrato sin distinguir el tipo concreto de fuente.
Después se comparten lectura, evaluación, resumen y reportes. ImagenSticker sigue
representando cada imagen, no la fuente. No hay reglas PPI duplicadas.

Los nombres repetidos en el JSON se procesan una sola vez; no se eliminan archivos
distintos que tengan contenido idéntico. Si una imagen falta, se registra el error
y se continúa. Si el JSON está mal formado o su carpeta original no existe, la
fuente se rechaza antes de crear informes. El resumen identifica el JSON de entrada.
El JSON no guarda los parámetros del análisis: se eligen de nuevo.
Por comando, --analizar-seleccion propone inicial; la carpeta conserva final por defecto.
No se combinan carpeta, --seleccion y --analizar-seleccion en el mismo comando.
