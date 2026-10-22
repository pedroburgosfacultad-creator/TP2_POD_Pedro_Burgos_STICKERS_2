# RELEVO — Modo: Crítica

## Objetivo

Realizar una revisión crítica del proyecto existente, comparar su implementación con alternativas más simples y corregir errores demostrables sin rehacerlo innecesariamente.

El usuario es estudiante de primer año de Licenciatura en Ciencia de Datos y desarrolla un TP2 de Programación Orientada a Datos. El proyecto también debe servir a su microemprendimiento de stickers.

Prioridades:
1. Cumplir la consigna y poder defender personalmente el código.
2. Mantener una implementación pequeña, comprensible y verificable.
3. Obtener utilidad real para revisar y organizar imágenes.
4. Evitar nuevas funciones o dependencias sin necesidad concreta.

## Entregable

- Hallazgos ordenados por gravedad, con archivo, función y evidencia.
- Separación entre errores, limitaciones deliberadas y mejoras opcionales.
- Evaluación de coherencia, complejidad, redundancias y cobertura de pruebas.
- Contraste con los siete puntos de la consigna.
- Correcciones mínimas justificadas y pruebas pertinentes, si se dispone del repositorio editable.
- Explicación breve en español accesible de qué cambia y por qué.
- Documentación actualizada si cambian comportamiento, comandos o resultados.

No considerar las auditorías anteriores como autoridad: contrastarlas con el código vigente. No afirmar que el programa está libre de errores solo porque pasan los tests.

## Estado actual

Proyecto activo: `C:\tps\tp2_explo`.

Repositorio: https://github.com/pedroburgosfacultad-creator/TP2_POD_Pedro_Burgos_STICKERS_2.git

Última comprobación al preparar el relevo en la conversación:
- HEAD local: `673e0be`.
- Mensaje: “Habilitación de selección de stickers - Guardado en subcarpetas - Abstracción de fuentes”.
- `git status --short` mostraba únicamente `?? docs/defensa_visual/`.
- Esa carpeta no se inspeccionó: no sobrescribirla ni asumir que es descartable.
- No se verificó si el nuevo HEAD está publicado en GitHub.
- Las afirmaciones anteriores de que todas las modificaciones seguían sin commit quedaron desactualizadas.
- Este archivo de relevo se agrega después de aquella comprobación; verificar nuevamente el estado de Git.

Ocho módulos:

| Archivo | Responsabilidad |
|---|---|
| src/main.py | Coordinación, argumentos y códigos de salida |
| src/guiado.py | Menú, preguntas, selección de JSON de Descargas y apertura del HTML |
| src/fuentes.py | Abstracción de fuentes y validación compartida del JSON |
| src/lectura.py | Lectura, validación y clase ImagenSticker |
| src/evaluacion.py | Límites, cálculo PPI, transparencia y estadísticas |
| src/informes.py | CSV y resumen textual utilizado por terminal/HTML |
| src/galeria.py | Miniaturas y HTML/CSS/JavaScript |
| src/seleccion.py | Copia de originales y JSON para PhotoRoom |

Hay diez archivos `test_*.py`. La última ejecución, después de integrar las fuentes, pasó **52 pruebas**. No se volvieron a ejecutar durante la preparación de este relevo.

Flujo vigente:

```text
FuenteCarpeta o FuenteSeleccionJSON
→ cargar(): lista de rutas
→ analizar_fuente(): lectura y errores por archivo
→ evaluar_imagen()
→ resumir_resultados()
→ CSV + HTML + resumen en terminal
```

Abstracción implementada:
- FuenteImagenes hereda de ABC y exige cargar().
- FuenteCarpeta enumera archivos del primer nivel.
- FuenteSeleccionJSON lee nombres de una selección y devuelve sus rutas.
- Ambas se utilizan realmente en el procesamiento.
- leer_seleccion() comparte validación entre reanálisis y copia para PhotoRoom.
- analizar_carpeta() permanece como atajo compatible para llamadas existentes.

Menú:
1. Revisión inicial de PNG/JPG/JPEG.
2. Revisión final de PNG preparados.
3. Preparar carpeta para PhotoRoom desde un JSON.
4. Volver a analizar una selección JSON, con etapa y parámetros nuevos.

```powershell
python src/main.py
python src/main.py "C:\ruta\imagenes" --etapa inicial --lado-cm 4 --ppi 300
python src/main.py --analizar-seleccion "C:\ruta\seleccion_photoroom.json" --lado-cm 6 --etapa inicial
python src/main.py --seleccion "C:\ruta\seleccion_photoroom.json"
python -m unittest discover -s tests -v
```

Por comando, una carpeta sin --etapa usa final; --analizar-seleccion usa inicial. El menú propone inicial.

## Decisiones aprobadas

- Trabajar con imágenes reales, no inventar contabilidad.
- Procesar PNG y JPEG en recepción, PNG en revisión final.
- No detectar automáticamente nitidez en esta versión.
- CANDIDATO no significa calidad garantizada ni fondo fácil de eliminar.
- Lado mayor máximo de 56 cm, indicado por el usuario.
- Mínimo actual de 0,1 cm, propuesto por la IA como criterio práctico y documentado. No consta una elección independiente del usuario de ese mínimo.
- Referencia predeterminada: 300 PPI. Umbral parcial predeterminado: 20 %.
- Configurar referencias y aviso por imágenes opacas.
- No modificar originales.
- Crear HTML y CSV; eliminar la generación de TXT. Conservar el resumen en terminal y HTML.
- Selección manual en HTML y descarga de JSON.
- Copiar originales a una carpeta nueva de outputs para PhotoRoom; no convertirlos ni quitar fondos.
- Buscar selecciones en Descargas y permitir elegir por número o indicar otra ruta.
- Archivar una copia exacta del JSON junto a las imágenes copiadas.
- Avisar también sobre PDF y otros formatos incompatibles.
- Mantener input() y Ctrl+C: se implementó Esc, pero el usuario pidió revertirlo por complejidad excesiva. No reintroducir un editor de teclado.
- Implementar una abstracción útil mediante carpeta y selección JSON, con reanálisis de los archivos seleccionados.
- No crear correspondencia artificial de un test por módulo: las pruebas se agrupan por comportamiento.

## Restricciones

- Herramientas gratuitas, procesamiento local y sin APIs pagas.
- Única dependencia externa del programa: Pillow==12.3.0.
- Entorno probado previamente: Python 3.14.7 en Windows.
- No añadir frameworks, servidores, agentes, bibliotecas o clases solo para aparentar sofisticación.
- No eliminar funciones sin verificar referencias y consecuencias.
- No perder historial Git, archivos del usuario ni cambios ajenos.
- No hacer commit, push o publicación sin autorización correspondiente.
- Usar muestras pequeñas para pruebas manuales; evitar reprocesar innecesariamente más de 700 stickers.
- No incluir automáticamente imágenes privadas en Git ni en el relevo.
- Comprobar los permisos efectivos del entorno receptor antes de editar.

Existe una copia antigua en `C:\Users\Usuario\Documents\ChatGPT\STICKERS\TP2_POD_Pedro_Burgos_STICKERS\proyecto`. **NO es el proyecto activo. No implementar cambios allí.**

## Fuentes y archivos

Este paquete incorpora requisitos y contexto, pero **NO contiene todo el código**. Una ruta local no concede acceso a otra IA.

Si no tenés acceso al proyecto, solicitar un ZIP o adjuntos con:
- src/ completo: indispensable para revisar implementación.
- tests/ completo: indispensable para verificar y comprender las pruebas.
- README.md, data/README.md y tests/README.md.
- requirements.txt y .gitignore.
- docs/INFORME_FINAL.md.
- consigna_TP2.pdf.

No hacen falta .venv, cachés, outputs ni cientos de imágenes para la primera revisión. Para reproducir problemas visuales, pedir después una muestra mínima autorizada. Los adjuntos no se transfieren automáticamente con este Markdown.

PDF original: `C:\Users\Usuario\Downloads\consigna_TP2.pdf`.

Contenido esencial de la consigna:
1. Definir problema, usuario, pregunta, resultado y alcance.
2. Documentar fuente, responsable, licencia/condiciones, fecha, unidad de análisis y variables. Referencia: al menos 50 observaciones y tres variables; justificar menos. Proporcionar muestra o procedimiento reproducible.
3. Flujo reproducible: leer, inspeccionar/validar, limpiar/transformar, analizar y comunicar. La versión escrita pide entrada CSV y JSON.
4. Funciones claras, clase significativa, abstracción común de fuentes con dos implementaciones, regex pertinente y errores comprensibles. La versión escrita propone fuentes CSV/JSON y exige que la jerarquía sea útil.
5. Pruebas: caso normal, inválido/límite y propiedad relevante.
6. Git/GitHub: al menos cinco commits significativos, .gitignore adecuado, revisión de cambios y acceso docente.
7. README completo, comandos exactos, organización, ejemplo de resultado, limpieza, interpretación y limitaciones. Entrega por enlace e identificación del commit o etiqueta. Defensa individual.

**Aclaración expresa del usuario:** el profesor autorizó cambiar los datos de entrada por imágenes, PERO solo autorizó cambiar los datos; no exceptuó la abstracción de fuentes.

Se implementaron FuenteCarpeta y FuenteSeleccionJSON. No afirmar que son literalmente fuentes CSV/JSON ni que su aceptación docente está confirmada.

Reglas relevantes:
- Inicial: PPI sobre la imagen completa.
- Final: PPI sobre la caja con alpha > 0.
- resolucion_ppi = max(ancho_evaluado_px, alto_evaluado_px) × 2.54 / lado_cm.
- Transparencia total = cantidad alpha 0 / píxeles totales × 100.
- Parcial = cantidad alpha 1..254 / píxeles visibles × 100.
- Sin contenido visible: resolución vacía y advertencia.
- Porcentajes de advertencias calculados sobre imágenes leídas.
- Archivo incompatible: ERROR_LECTURA en CSV, “No procesado” en HTML, motivo explícito y mediciones vacías.

JSON de selección:

```json
{
  "version": 1,
  "carpeta": "C:\\ruta\\imagenes",
  "archivos": ["uno.jpg", "dos.png"]
}
```

No contiene imágenes ni parámetros anteriores. Los nombres repetidos se procesan una sola vez. Reanalizar vuelve a leer los originales.

Salidas:

```text
outputs/analisis_FECHA_HORA/informe.csv
outputs/analisis_FECHA_HORA/informe.html
outputs/analisis_FECHA_HORA/miniaturas/
outputs/seleccion_photoroom_FECHA_HORA/
```

La última carpeta incluye originales copiados y seleccion_photoroom.json.

El informe final contiene una auditoría anterior y una nota posterior sobre fuentes. Sus huellas, cifras de módulos y algunos pendientes históricos NO describen necesariamente el estado actual. Revisar y consolidar antes de usarlo como constancia definitiva.

## Trabajo pendiente

1. Obtener el código y PDF si no están accesibles.
2. Verificar HEAD, estado de Git y alcance de archivos no versionados.
3. Leer implementación y ejecutar las pruebas sin modificar datos personales.
4. Revisar independientemente la abstracción: contrato, uso real, errores, equivalencia y ausencia de duplicación.
5. Contrastar requisitos académicos y funcionamiento, sin confundirlos.
6. Reproducir hallazgos antes de calificarlos como errores.
7. Corregir defectos con cambios mínimos; mantener las decisiones aprobadas.
8. Revisar coherencia de README e informe final después de cualquier corrección.
9. Presentar diferencias, evidencia y pendientes de entrega.

## Riesgos abiertos

Hallazgos anteriores que requieren verificación independiente:
- El CSV no guarda umbral parcial ni opción de advertir por opacidad; el resumen HTML sí.
- Búsqueda HTML: Python usa casefold() y JavaScript minúsculas; ciertos nombres Unicode pueden no coincidir.
- El JSON conserva nombres/ruta, pero no identificador del informe, fecha ni decisión manual.
- Si un original cambia después de analizarse, se copia/reanaliza su versión actual.
- El JSON archivado registra lo solicitado, no garantiza que todas las copias se completaron.
- Puede haber salidas parciales tras una interrupción o fallo de escritura.
- Coherencia entre lectura de enlaces simbólicos, ruta de origen del HTML y rechazo de enlaces durante la copia.
- No se ha acreditado la referencia académica de 50 observaciones mediante una evidencia final reproducible/publicable.
- No está confirmada por la cátedra la equivalencia de carpeta/selección JSON con la adaptación del punto 4.
- La disponibilidad del repositorio para la cuenta docente y la versión remota vigente están por verificar.
- El aspecto y las descargas del HTML requieren pruebas reales de navegador; pruebas simuladas no las sustituyen.
- Nitidez, impresión física y calidad comercial quedan fuera de las garantías del programa.
- El límite numérico extremo que producía PPI infinito fue corregido con el rango 0,1..56 cm; verificar que siga controlado.

## Siguiente acción exacta

Inspeccioná `C:\tps\tp2_explo` con `git status` y `git log`, leé src/fuentes.py, src/lectura.py, src/main.py y la consigna completa, y ejecutá `python -m unittest discover -s tests -v` antes de proponer cambios. Si no tenés acceso a esos archivos, solicitá primero el ZIP del proyecto y consigna_TP2.pdf; no evalúes el código como si lo hubieras leído basándote únicamente en este resumen.
