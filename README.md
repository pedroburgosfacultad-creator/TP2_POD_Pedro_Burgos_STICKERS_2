# Revisión técnica de imágenes para stickers

Autor: Pedro Andrés Burgos. TP2 - POD - 1er año LCD
GitHub: pedroburgosfacultad-creator
Licencia: 
Link Repositorio: https://github.com/pedroburgosfacultad-creator/TP2_POD_Pedro_Burgos_STICKERS_2

> Todos los comandos de este README se ejecutan desde la **raíz del proyecto**, la
> carpeta que contiene `src/` y `tests/`.


## Problema y alcance

El microemprendimiento recibe imágenes que deben revisarse antes de prepararlas como stickers. Se necesita saber cuáles de estas imágenes presentan problemas de resolución o
transparencia previo a obtener el sticker final. 

Se analizan imágenes locales, se generan mediciones y estadísticas, obtenemos información y en base a esto se presenta una galería para tomar decisiones manuales (imagen apta/no apta para transformar en sticker).

La pregunta que guía el analisis es ¿Qué archivos presentan advertencias de resolución o
transparencia al tamaño previsto?

El resultado que producirá el programa es información sobre el estado de las imagenes y la posibilidad de una selección y separación de estas dependiendo de la intención del usuario.
El resultado es utilizado para facilitar el manejo de las imagene hacia la conversión a sticker o hacia la necesidad de ser manipuladas. De esta forma se le da un orden y se ahorra la revisión manual de cada una de las imágenes. Por otro lado entrega información obtenida de los procesos, lo que permite tener un registro estos. 

El alcance de esta primera versión permite lo ya mencionado anteriormente. El programa no detecta nitidez, no convierte imágenes ni quita fondos. Convertir JPEG a PNG no recupera detalle. No descarga automáticamente las imagenes proporcionadas por el cliente Entre otras posibles futuras versiones e implementaciones. El proyecto fue llevado hasta un punto conveniente no solamente para lograr cumplir con las consignas del trabajo sin exagerar en complejidad sino también hasta donde no se requiriera un margen de gasto económico en APIs, algoritmos u otras herramientas pagas.  



## Instalación y ejecución


Repositorio: https://github.com/pedroburgosfacultad-creator/TP2_POD_Pedro_Burgos_STICKERS_2

Versión probada: Python 3.14. Dependencia: Pillow 12.3.0, fijada en requirements.txt.
Desde la raíz del proyecto, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

Si el Python activo ya tiene Pillow instalado, para iniciar el programa desde la terminal:

```powershell
python src/main.py
```

El menú ofrece revisión inicial, revisión final y preparación para PhotoRoom*.
Las preguntas aceptan rutas entre comillas y decimales con coma o punto. Enter
mantiene el valor indicado; Ctrl+C cancela. La lectura usa `input()`.
No hay servidor, APIs, agentes ni servicios pagos. Tras instalar Pillow, el
análisis y la preparación de carpetas funcionan sin Internet.

** Photoroom es la pagina web donde el usuario realiza la conversión de las imagenes .jpeg a .png 

## Contexto de uso
El menu que se despliega al incializar la ejecución tiene 4 posibles opciones. En un flujo normal partiendo del inicio donde recibimos y ya tenemos descargado en nuestro dispositivo las imagenes proporcionadas por el cliente que desea como stickers, se sigue la siguiente secuencia de pasos óptima:

1. "Revisión inicial": el código analiza las imagenes crudas como las recibimos del cliente y nos permite ajustar los parámetros de los futuros stickers (medida de un lado y PPI*). El resultado es un análisis técnico de las imágenes, interpretaciones y límites a tener en cuenta y el despliegue de un html donde vemos esta información mejor estructurada y la posibilidad de seleccionar aquellos stickers que deseamos separar. Recibe cualquier tipo de archivo, apunta a .png, .jpeg, .jpg. el resto queda como "no procesado". 

2. "Preparar carpeta para photoroom": el código crea una carpeta aislada donde se encuentran las imágenes que seleccionamos listas para pasar a stickers. No obligatoriamente deben ser imagenes listas para este fin, podemos usar esta misma herramienta para crear una carpeta con imagenes seleccionadas que requieran una revisión. 

3. "Revisión Final": el código realiza un proceso similar al de la revisión inicial pero explicitamente con las imagenes ya hechas formato sticker (.png) y realiza un análisis sobre estos para corroborar su correcto uso. Procesa explicitamente .png. 

4. "Volver a analizar JSON": no es de uso constante pero nos permite poder analizar una selección de stickers y no tener que volver a hacerlo con el conjunto entero de imagenes que nos proporcionó el cliente. 

** PPI: Pixel per Inch


## Parámetros y tamaño físico

El **lado mayor del sticker permitido es de 0,1 a 56 cm, inclusive**, con 4 cm por defecto.
56 cm corresponde a la plantilla máxima posible. El mínimo de
0,1 cm (1 mm) es un criterio práctico del proyecto para evitar valores absurdamente
pequeños; no es una norma de impresión. Se conserva la proporción: no se exige
que ambos lados midan lo indicado. El programa no distribuye diseños en una plantilla.

| Parámetro |   Uso |   Significado/Ejemplo |
|---|---|---|
| `--carpeta` | Carpeta de entrada; si se omite, abre el menú | Carpeta con imagenes/stickers
| `--etapa inicial` / `--etapa final` | Modo de evaluación; con carpeta explícita se usa final por defecto; el menú propone inicial | Proceso que queremos realizar
| `--lado-cm` | Lado mayor entre 0.1 y 56; por comando se usa punto decimal | Medida de uno de los lados del sticker
| `--ppi` | Referencia positiva y finita; 300 por defecto | PPI
| `--umbral-parcial` | Porcentaje de semitransparencia entre 0 y 100; 20 por defecto; aplica a etapa final | Umbral de cantidad de pixeles semitransparentes en un sticker/imagen
| `--permitir-opacas` | Desactiva el aviso por ausencia de transparencia en etapa final | A veces algunos stickers no requieren eliminar fondo y son completamente opacos. Ejemplo: sticker rectangular
| `--salida` | Directorio de resultados; por defecto outputs en la raíz del proyecto | outputs
| `--seleccion` | JSON descargado del HTML para preparar la carpeta de PhotoRoom; no se combina con carpeta de análisis | Imagenes que hayamos seleccionado. Se guardan sus rutas en un archivo JSON
| `--analizar-seleccion` | JSON descargado del HTML para volver a analizar los originales seleccionados, sin copiarlos; inicial por defecto; no se combina con carpeta ni `--seleccion` | Analisis de una selección particular

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
Los motivos pueden superponerse; sin imágenes evaluadas el porcentaje es "no aplica".

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
conservar toda la carpeta de ejecución, incluyendo miniaturas y CSV. 

Uso en otra computadora: el programa puede ejecutarse siguiendo las instrucciones de instalación y generando nuevos informes. Los archivos que contienen referencias a rutas locales, especialmente los JSON de selección, dependen de la ubicación de las imágenes originales y no se trasladan automáticamente entre equipos.

## Preparar una selección para PhotoRoom

1. Marcar las casillas de las imágenes elegidas en el HTML.
2. Pulsar "Descargar selección". El navegador guarda seleccion_photoroom.json.
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

Los filtros mantienen la selección, incluso cuando ocultan tarjetas. "Quitar selección"
la borra; "Limpiar filtros" no. Cerrar o recargar el HTML pierde la selección no descargada.
No seleccionar no significa rechazar. Seleccionar no significa que ya se procesó.

Si falta un original, se informa NO COPIADO y se continúa con los demás. El JSON
archivado registra lo solicitado, no acredita que todas las copias se completaron.
Si un original cambió, se copia su versión actual: generar otro informe tras modificarlo.
La copia rechaza nombres que salen de la carpeta de origen y enlaces simbólicos.

## Diseño del código

El flujo es una cadena de pasos, cada uno con una sola responsabilidad:

```text
fuente (FuenteCarpeta o FuenteSeleccionJSON) -> cargar(): lista de rutas
  -> analizar_fuente(): lectura y validación; un error por archivo, sin detener el lote
  -> evaluar_imagen(): reglas de resolución y transparencia
  -> resumir_resultados(): conteos y motivos
  -> informe.csv + informe.html + resumen en la terminal
```

Clase `ImagenSticker` (src/lectura.py): representa una imagen ya leída y validada.
Guarda sus medidas, no sus píxeles: ruta, formato, ancho y alto en píxeles, el
histograma del canal alpha y la caja que contiene los píxeles visibles. Sus métodos
son `dimensiones_visibles()`, que devuelve el tamaño del contenido sin márgenes
transparentes, y `porcentajes_alpha()`, que calcula la transparencia total y parcial.
Con eso las reglas de evaluación no necesitan volver a abrir la imagen.

Abstracción de fuentes (src/fuentes.py): `FuenteImagenes` es una clase abstracta
que obliga a implementar `cargar()`, que devuelve una lista de rutas.
`FuenteCarpeta` enumera los archivos del primer nivel de una carpeta y
`FuenteSeleccionJSON` devuelve los archivos elegidos en el JSON descargado del HTML.
`analizar_fuente()` trabaja con cualquiera de las dos sin distinguirlas, por lo que
lectura, evaluación e informes son idénticos para ambas. Una prueba verifica que ambas
fuentes dan resultados equivalentes en las dos etapas.

Evaluación como función pura (src/evaluacion.py): `evaluar_imagen()` recibe una
`ImagenSticker` y los parámetros, y devuelve un diccionario con una fila del informe.
No lee ni escribe archivos, por lo que se prueba con datos conocidos
(por ejemplo, 500 px a 4 cm son 317,5 PPI).

Validaciones y errores: los parámetros se validan antes de crear salidas
(`validar_parametros`). El JSON de selección se valida en `leer_seleccion`. Un archivo
ilegible no detiene el análisis: se registra con un mensaje comprensible como
ERROR_LECTURA. Los errores de entrada terminan con código de salida 2.


## Organización y pruebas
Desde la raíz del proyecto:

```powershell
python -m unittest discover -s tests -v
```

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
. Códigos de salida: 0 si no hubo rechazos
(puede haber advertencias), 1 si algún archivo fue rechazado/no copiado, 2 por error
de parámetros, carpeta, selección o escritura, y 130 por cancelación. Si se interrumpe
una operación empezada o falla la escritura, pueden quedar salidas parciales.

## Auditoría final y ejemplo comprobado

El 22/10/2026 se verificaron 47 pruebas y el flujo completo con la muestra local mixta, que ahora incluye un PDF: 13 archivos en total. A 4 cm y 300 PPI, la etapa inicial produjo 10 candidatos, 2 imágenes para revisar y 1 archivo no procesado. El 16,67 % corresponde a las 2 imágenes con advertencias entre las 12 leídas; no mide calidad real ni representa la colección completa. En final se leyó el PNG (con dos advertencias) y se rechazaron los 11 JPEG y el PDF por formato de etapa.

## Límites y GitHub

No se certifican nitidez, color, recorte ni facilidad de eliminar fondos. Márgenes,
varios diseños o píxeles aislados pueden sobreestimar la resolución útil. La
semitransparencia puede ser intencional; su umbral es un valor ajustable.
No se eliminan duplicados ni se hace seguimiento de ventas o pedidos.

Las salidas, entornos y muestras privadas están excluidos de Git. No agregar nuevas
imágenes sin comprobar sus permisos de distribución. El código, requirements.txt,
documentación y pruebas permiten reproducir el funcionamiento sin esas muestras.


