# Informe final de estado y auditoría del TP2

> **Actualización posterior: abstracción implementada.** El cuerpo de esta auditoría
> y sus huellas corresponden al estado anterior a la adaptación de fuentes.
> El pendiente de implementación del punto 4 queda sustituido por FuenteImagenes
> (abstracta), FuenteCarpeta y FuenteSeleccionJSON, utilizadas por analizar_fuente().
> La opción 4 reanaliza selecciones; la opción 3 conserva la copia para PhotoRoom.
> La validación del JSON se comparte entre ambas operaciones. La suite actual
> tiene 52 pruebas, incluida equivalencia de resultados entre fuentes en ambas etapas.
> Las cifras de líneas y huellas históricas de este informe no identifican esta nueva
> versión. Sigue pendiente publicar el commit definitivo y justificar los datos y
> la adaptación del requisito escrito a imágenes ante la cátedra. No se afirma
> implementar fuentes CSV/JSON equivalentes: las fuentes son carpeta/selección JSON.


**Proyecto:** Revisión técnica de imágenes para stickers.  
**Autor del proyecto:** Pedro Burgos.  
**Fecha de auditoría:** 22 de octubre de 2026.  
**Carpeta auditada:** `C:\tps\tp2_explo`.  
**Repositorio:** https://github.com/pedroburgosfacultad-creator/TP2_POD_Pedro_Burgos_STICKERS_2  
**Referencia académica:** consigna_TP2.pdf, cuatro páginas, compartida por el alumno.  
**Naturaleza del documento:** revisión técnica asistida; no es una certificación de la cátedra ni sustituye la defensa individual.

## 1. Dictamen

El programa es funcional para el alcance acordado: inspeccionar imágenes, calcular
resolución para un tamaño físico, evaluar transparencia en PNG preparados, comunicar
advertencias y copiar una selección manual para PhotoRoom. La arquitectura es
comprensible y la complejidad es razonable para las funciones elegidas.

La suite de **47 pruebas pasó sin fallos**. Se verificó adicionalmente el flujo
completo con la muestra local y copias temporales. No se detectaron fallos que
bloqueen el uso habitual de ese flujo. Esto no demuestra ausencia total de errores.

**El cierre técnico no equivale todavía a cumplimiento académico completo.**
Hay asuntos que deben resolverse o acreditarse antes de presentar el TP:

1. Confirmar la adaptación del requisito de abstracción de fuentes del punto 4.
2. Acreditar al menos 50 observaciones o justificar una muestra menor, y asegurar
   que la cátedra pueda obtener los datos de demostración de forma autorizada.
3. Confirmar y publicar los cambios finales; entregar el enlace y el identificador
   del commit evaluado, y verificar el acceso de la cátedra.

La autorización docente comunicada por el alumno permite imágenes en lugar de
CSV/JSON como entrada. En una aclaración posterior, el alumno confirmó expresamente
que el profesor solo autorizó cambiar los datos. Por tanto, el requisito de
abstracción común de fuentes sigue vigente y no está implementado. No se incorporó una jerarquía artificial solo para aparentar cumplimiento.

## 2. Qué quedó aplicado y qué se completó en esta revisión

| Cambio acordado | Estado comprobado |
|---|---|
| Lado mayor de hasta 56 cm | Implementado; rango inclusivo 0,1 a 56 cm |
| Evitar valores absurdamente pequeños | Implementado; mínimo 0,1 cm propuesto como criterio práctico, no norma industrial |
| Validar por menú y comandos | Implementado; el menú repregunta y el comando falla antes de crear salidas |
| Documentación principal, de datos y pruebas | Reescrita y sincronizada con la versión actual |
| Limpieza de código obsoleto | Retirados resumen() de ImagenSticker y auxiliares antiguos buscar_imagenes(), buscar_png(), leer_png() |
| Conservar lectura PNG/JPEG | leer_imagen() y buscar_archivos() reemplazan los auxiliares; pruebas actualizadas |
| Cancelación con Esc | Revertida por decisión del usuario; se conserva input() y Ctrl+C |
| Generación de TXT | Eliminada; resumen en terminal y HTML |
| Archivos incompatibles | Informados en terminal, CSV y HTML sin detener el lote |
| Selección para PhotoRoom | Implementada, incluida búsqueda en Descargas y copia exacta del JSON |
| Corrección pendiente de formato Markdown | Corregida la barra vertical que rompía una celda del diccionario de datos |

Se conservaron las validaciones utilizadas por las funciones independientes y las
funciones pequeñas que sí coordinan el menú. No se sustituyeron por código más
compacto pero difícil de explicar. No se agregaron dependencias de ejecución al TP.

## 3. Características y arquitectura

El flujo es: enumerar archivos, leer y validar, transformar en memoria, evaluar,
resumir y exportar. La transformación incluye orientación EXIF, conversión RGBA,
histograma alpha y rectángulo visible; no incluye modificar los originales.

| Módulo | Responsabilidad y evaluación |
|---|---|
| main.py | Coordina CLI/menú, resultados y códigos de salida; no concentra las reglas |
| guiado.py | Entrada con reintentos, búsqueda de JSON y apertura del informe; la parte Windows de Descargas tiene respaldo de ruta manual |
| lectura.py | Enumera, valida y obtiene mediciones; ImagenSticker agrupa atributos y métodos del dominio |
| evaluacion.py | Reglas numéricas, límites y estadísticas; funciones verificables con datos conocidos |
| informes.py | CSV y resumen textual compartido; el texto no se guarda en un TXT separado |
| galeria.py | Miniaturas y plantilla HTML/CSS/JavaScript; concentra la mayor complejidad visual |
| seleccion.py | Valida la selección y copia los originales a una carpeta nueva |

Hay siete módulos y aproximadamente **822 líneas físicas en src**, incluyendo
comentarios, espacios y la plantilla HTML/CSS/JavaScript. El número de líneas no es
una medida de calidad. No se observó otra ampliación desproporcionada como la del
editor de teclado que se retiró al revertir Esc.

La ordenación de n archivos cuesta aproximadamente O(n log n). Lectura, alpha y
miniaturas dependen sobre todo del total de píxeles; no hay un algoritmo que compare
cada imagen con todas las demás. Se conservan mediciones por archivo, no una colección
completa de imágenes decodificadas en memoria. Una imagen individual grande puede,
sin embargo, consumir bastante memoria. No se hizo una medición de rendimiento del
lote completo de más de 700 imágenes en esta auditoría.

Entorno comprobado: Python 3.14.7 y Pillow 12.3.0. Pillow es la única dependencia
externa del programa. Las herramientas usadas para leer la consigna durante la
auditoría se instalaron fuera del proyecto y no forman parte de requirements.txt.

## 4. Evidencia de verificación

### 4.1 Suite automatizada

Comando desde la raíz:

```powershell
python -m unittest discover -s tests -q
```

Resultado observado: `Ran 47 tests ... OK`.

Se cubren casos normales, dañados, extensiones falsas, formatos incompatibles,
carpetas vacías/inexistentes, alpha, paletas, orientación, cálculo PPI, límites
físicos, estadísticas, CSV, generación HTML, menú, selección y conservación de originales.
El mínimo y máximo se prueban en ambas etapas. También se rechazan 5e-324, 0,099,
56,001, negativos, infinito y NaN. Véase [tests/README.md](../tests/README.md).

Se comprobó la sintaxis de todos los módulos de src y tests. Las pruebas del
navegador de la suite son simuladas; no abren un navegador real.

### 4.2 Ejecución independiente con datos locales

Muestra auditada: data/muestra_jpeg_y_png, 13 archivos presentes: 11 JPEG, un PNG y
un PDF. Condiciones: lado mayor 4 cm, referencia 300 PPI, umbral parcial 20 % y aviso
de opacidad activado en etapa final. Se usaron destinos temporales para no acumular
informes de auditoría en outputs.

| Etapa | Encontrados | Leídos | Candidatos | Para revisar | No procesados |
|---|---:|---:|---:|---:|---:|
| Inicial | 13 | 12 | 10 | 2 | 1 |
| Final | 13 | 1 | 0 | 1 | 12 |

En inicial, el PDF queda rechazado y las dos advertencias son por resolución inferior
a la referencia: 2/12 = 16,67 %. En final, los 11 JPEG y el PDF no se procesan; el PNG
presenta resolución baja y opacidad. Dos motivos no significan dos imágenes distintas.
Estas cifras corresponden a una muestra de prueba, no a la colección ni a ventas.

Se verificaron la cantidad de filas CSV y tarjetas HTML, la ausencia de TXT y la
creación de miniaturas sin avisos. Se copiaron dos originales mediante una selección
JSON: los bytes de las copias y del JSON archivado coincidieron con sus fuentes.
Los SHA-256 de los 13 originales permanecieron iguales después de la revisión.

### 4.3 JavaScript y límites de la comprobación

El JavaScript extraído del HTML actual pasó una comprobación con DOM simulado:
seleccionar, ocultar una selección mediante un filtro, descargar el JSON, limpiar
filtros sin perder selección y quitar la selección. No equivale a una prueba visual
en todos los navegadores ni verifica su ubicación real de Descargas.

No se auditó PhotoRoom, la impresión física, la calidad comercial ni todos los
archivos potencialmente malformados. Tampoco se midió cobertura porcentual de tests.

## 5. Contraste con los siete pasos de la consigna

| Paso | Evidencia | Evaluación |
|---|---|---|
| 1. Problema y alcance (p. 1) | README identifica negocio, usuario, pregunta, resultados y exclusiones | Cubierto; la aprobación del tema propio corresponde a la cátedra |
| 2. Datos y procedencia (p. 2) | data/README documenta unidad, variables, fuente propia, muestras y restricciones | Parcial: faltan datos compartibles/reproducibles para terceros y evidencia de 50 observaciones o justificación menor; no se inventó licencia |
| 3. Flujo reproducible (p. 2) | Comando, validación, transformaciones, rechazos, CSV, HTML y pruebas | Funcional; entrada por imágenes según autorización docente relatada. El código no lee CSV como fuente analítica |
| 4. Conceptos (p. 2) | Funciones, clase significativa, listas/diccionarios, regex y manejo de errores | Parcial: falta implementar la abstracción común con dos fuentes concretas; el alumno confirmó que no se exceptuó este requisito |
| 5. Verificación (p. 3) | 47 pruebas con casos normales, inválidos y propiedades de resultados | Cubierto para el alcance técnico probado, sin afirmar perfección |
| 6. Git/GitHub (p. 3) | 10 commits locales, cambios significativos, .gitignore y remoto consultado | Historial suficiente en cantidad; cambios recientes sin publicar y acceso docente aún por verificar |
| 7. Documentar/entregar/defender (p. 3) | Tres README, informe final, comandos, resultados y estructura equivalente | Documentación preparada; faltan identificar/publicar versión final y realizar defensa |

### Aclaración fundamental sobre fuentes

Exportar CSV no equivale a leer una fuente CSV. Leer el JSON de una selección tampoco
equivale a implementar dos fuentes analíticas con una interfaz común. Tener una clase
ImagenSticker y usar Pillow no reemplaza ese requisito de diseño.

La consigna pide que la jerarquía sea útil, no formal. El requisito se mantiene:
se debe diseñar e implementar una interfaz común con dos fuentes concretas.
La autorización para imágenes no elimina esa obligación. La elección de las dos
fuentes debe justificarse en el dominio y, si hay dudas sobre su equivalencia con
la consigna escrita, validarse con la cátedra antes de dar por cumplido el punto 4.

### Regex y limpieza, para la defensa

La expresión `\\.(png|jpe?g)\\Z` en notación de texto representa el patrón de extensión
usado en lectura (en el código se escribe `r"\.(png|jpe?g)\Z"`). Reconoce PNG/JPG/JPEG
al final del nombre sin distinguir mayúsculas. No certifica el contenido: Pillow lo
comprueba después. La búsqueda de selecciones usa otra regex para los nombres JSON
y las copias numeradas del navegador.

La limpieza consiste en rechazar entradas inválidas con registro, normalizar la
orientación y obtener medidas comparables en memoria. No se eliminan duplicados;
cada archivo cuenta. Los valores no aplicables quedan vacíos y los porcentajes usan
denominadores explícitos. No se inventan valores para imágenes ilegibles.

## 6. Hallazgos y límites aún vigentes

| Prioridad | Hallazgo | Consecuencia y tratamiento |
|---|---|---|
| Alta para entrega | Abstracción de fuentes requerida pero no implementada | El punto 4 sigue incompleto; implementar una adaptación útil y justificarla |
| Alta para entrega | Datos privados y referencia de 50 observaciones sin evidencia final publicada | No basta con afirmar que existen más de 700 imágenes; documentar ejecución autorizada o justificar menos y ofrecer muestra/procedimiento reproducible |
| Alta para entrega | Cambios locales no incluidos en el remoto | La cátedra no recibiría la versión auditada si se entrega el enlace actual sin commit/push |
| Media | El CSV omite umbral parcial y opción de opacidad | Conservar el HTML correspondiente para interpretar todos los parámetros; posible mejora pequeña futura |
| Baja, reproducible | casefold() en Python y minúsculas en JavaScript no son equivalentes | Una búsqueda con ciertos caracteres, por ejemplo Straße, puede no encontrar el nombre; no afecta los cálculos |
| Limitación funcional | Píxeles suficientes no equivalen a nitidez | CANDIDATO requiere revisión humana; las capturas ampliadas son un caso conocido |
| Limitación funcional | El JSON no identifica informe, fecha ni revisión manual | No usarlo como registro completo de calidad o productividad |
| Limitación operativa | El original puede cambiar después de analizarse | La copia usa su contenido actual; regenerar el informe tras modificaciones |
| Limitación operativa | Interrupción o error de escritura puede dejar salidas parciales | Revisar mensajes y repetir; no se promete una operación transaccional |

La detección de opacidad no juzga si el diseño debe tener fondo. El rectángulo visible
puede ampliarse por píxeles aislados. La transparencia parcial puede ser válida. Las
miniaturas reducidas no son una prueba fiable de detalle de impresión.

Un caso técnico adicional poco habitual es analizar enlaces simbólicos a archivos:
la lectura puede seguirlos, mientras la copia los rechaza; además, la ruta de origen
del HTML se deriva de la primera imagen resuelta. Utilizar archivos ordinarios del
mismo directorio para este flujo. No se verificó compatibilidad con ese escenario.

Los defectos menores ya conocidos no se ocultaron ni se marcaron como corregidos.
No se agregaron funciones ajenas al alcance para cerrar artificialmente la auditoría.

## 7. Entrega y defensa: acciones concretas

El punto 7 admite una estructura equivalente: los nombres fuentes.py/pipeline.py
son ejemplos, no obligan a renombrar módulos. Lo que sí importa es implementar y
explicar las responsabilidades y requisitos.

Antes de entregar:

1. Resolver los pendientes académicos de fuentes y datos; registrar la aclaración
   docente con sus términos reales, sin afirmar una excepción que no existe.
2. Revisar los cambios y ejecutar la suite desde un entorno con requirements.txt.
3. Confirmar los archivos de código, tests, README e informe; no incluir imágenes
   restringidas, outputs, cachés ni entornos. Revisar con `git status` y `git diff`.
4. Hacer commit y push desde VS Code o Git. Obtener `git rev-parse HEAD` después
   del commit definitivo y consignarlo en la entrega por EVA junto al enlace.
5. Comprobar acceso al repositorio desde la cuenta prevista para la evaluación.
   El remoto respondió durante la auditoría, pero eso no prueba acceso de la cátedra.

Guion sugerido de demostración breve:

- Presentar problema, usuario y pregunta; explicar que no es un detector de nitidez.
- Analizar una muestra pequeña inicial y mostrar un candidato, un aviso y un PDF rechazado.
- Explicar una cuenta PPI y el cambio de criterio de transparencia en etapa final.
- Seleccionar un archivo, descargar el JSON y preparar la carpeta para PhotoRoom.
- Mostrar una prueba significativa y su propiedad, y recorrer commits de cambios reales.

Preparar respuestas sobre alpha, PPI frente a DPI, métodos de ImagenSticker,
validaciones, regex frente a formato real, códigos de salida, duplicados y CSV/JSON.
La consigna también contempla preguntas del TP1 para quienes deban recuperar esa
exposición; solo corresponde si aplica a la situación académica del alumno.

## 8. Proyección del proyecto

La versión actual sirve como base de inspección y organización de archivos. Una
evolución razonable sería añadir fecha/identificador de informe y revisión manual
para comparar decisiones humanas con reglas, después estudiar métricas locales de
nitidez con ejemplos etiquetados. Estas métricas necesitarían validación y no
resolverían por sí solas el recorte del sticker dentro de una captura.

Ventas, precios, pedidos, tiempos de retoque y rentabilidad requieren nuevos datos.
No pueden deducirse del tamaño de imagen. APIs, automatización de PhotoRoom,
eliminación de fondos, bases de datos y aprendizaje automático quedan fuera de
esta versión. No se requieren para demostrar el análisis implementado.

## 9. Identificación de la versión auditada

HEAD local y HEAD remoto observados al inicio:
`fcee67258538825ccb56b4f0fff9448949a4d27b`.

Ese commit todavía no incluye los últimos cambios locales de rango físico,
limpieza, README, test_tamanos.py ni este informe. La versión auditada es el árbol
de trabajo local sobre esa base, no únicamente ese commit. No se creó ni publicó
un commit en esta auditoría. La identificación académica definitiva será el hash
del commit posterior que incluya estos cambios.

La tabla de huellas al final identifica los módulos realmente comprobados. Si
se modifica el código después, repetir las pruebas y actualizar esta constancia.

## 10. Conclusión

Se puede continuar usando y probando la versión técnica actual. Las funciones
principales están implementadas, los límites físicos se respetan y la limpieza
no dejó referencias rotas en las pruebas. La documentación distingue medición,
interpretación y limitaciones.

**No se certifica que el TP esté listo para aprobar sin resolver los pendientes
académicos y de entrega listados.** Este informe deja constancia del estado real,
la evidencia obtenida y las condiciones necesarias para cerrar la entrega.


## Anexo: huellas SHA-256 de los módulos auditados

| Módulo | SHA-256 |
|---|---|
| evaluacion.py | `a52e8b1677272158d67f82b5660a601b7093404834063278f45712c862ea7bad` |
| galeria.py | `0b52074b3f2bbf128632754ba535a313767638ec7f031f4a3e3ff9fc788e8d65` |
| guiado.py | `f7a90ee491f334dfbd56c1c29bda8a0a875be1ab59264d6986f4cb52b3657737` |
| informes.py | `f884dddc9f94aa2cb7bddf6c5fbeedc3c7abeb3845fbdc67479df196da7cf533` |
| lectura.py | `15adb0e342f43ef817a0492aa0400f0757f546cb1deb95ad6f541c1919f87bc9` |
| main.py | `fbb83242a17959cdf9025ff8f9b3e6bbe2d09622951d1f4556225a9399b983f0` |
| seleccion.py | `dff73029e35ffb8611e62f38f3b1677a3c2d9aa7d599103aece1599fb46d4e42` |
