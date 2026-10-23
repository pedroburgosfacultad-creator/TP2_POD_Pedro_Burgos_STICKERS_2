# Pruebas del proyecto

Desde la raíz del proyecto, con Pillow instalado:

```powershell
python -m unittest discover -s tests -v
```

Con el entorno virtual documentado en el README raíz:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

La suite actual contiene **52 pruebas**. Utiliza unittest y crea imágenes/archivos
pequeños en carpetas temporales que se eliminan al terminar. No usa imágenes privadas,
Internet, PhotoRoom ni un navegador real. Algunas pruebas simulan respuestas del menú
y otras ejecutan el programa como un proceso independiente.

| Archivo | Comportamiento verificado |
|---|---|
| test_lectura.py | Dimensiones, conservación del original, PNG dañado o con contenido JPEG, formatos incompatibles, rutas y subcarpetas |
| test_evaluacion.py | Fórmula PPI, cambio de tamaño, umbrales, márgenes, alpha, paleta, validaciones, estadísticas y CSV |
| test_etapas.py | JPEG en inicial/final, separación de criterios, orientación EXIF, menú configurable y limitación ante desenfoque |
| test_galeria.py | Miniaturas, escape de texto HTML, ausencia de imágenes y fallo de miniatura |
| test_guiado.py | Rutas entre comillas, decimales con coma, respuestas, apertura simulada y cancelación por fin de entrada |
| test_seleccion.py | Copias exactas, no duplicar nombres, carpetas nuevas, faltantes, JSON inválido y flujo HTML/menú |
| test_descargas.py | Nombres numerados, orden por fecha, selección por número, ruta alternativa y conservación del JSON |
| test_formatos.py | PDF y archivo sin extensión registrados en terminal, CSV y HTML en ambas etapas |
| test_fuentes.py | Contrato abstracto, equivalencia carpeta/JSON en ambas etapas, selección parcial, duplicados, faltantes y menú/CLI sin copia |
| test_tamanos.py | Límites inclusivos 0,1 y 56 cm, rechazo de extremos, reintentos del menú y rechazo por comando sin crear salidas |

Los resultados esperados se calculan con ejemplos conocidos; por ejemplo, 500 px
a 4 cm producen 317,5 PPI. Otra prueba verifica que una imagen nítida y su copia
desenfocada con iguales dimensiones obtienen igual resolución: documenta una limitación,
no demuestra capacidad de detectar nitidez.

## Interpretación y límites

`OK` significa que pasaron los casos implementados, no que el programa carezca de
errores en todas las situaciones. Los mensajes de validación impresos durante las
pruebas son esperados: se introducen respuestas incorrectas para probar reintentos.
Los archivos rechazados producen salida 1 sin impedir que se generen informes;
los argumentos inválidos producen 2 y la cancelación produce 130.

Las pruebas HTML comprueban contenido y archivos generados; no ejecutan JavaScript
en un navegador ni garantizan su apariencia. La apertura del navegador está simulada.
No son pruebas de rendimiento de la colección completa ni de todas las variantes
posibles de PNG/JPEG. Tampoco certifican calidad visual. 

## Comprobación manual

1. Analizar una carpeta pequeña con JPEG, PNG y un PDF; verificar los tres estados
   y que el PDF quede como no procesado. Repetir en etapa final.
2. Probar tamaños 0,1 y 56, y comprobar que 0,01 y 57 se rechacen.
3. Abrir el HTML; probar búsqueda, filtros y selección. Una selección oculta por
   filtros debe seguir contando; limpiar filtros no debe borrarla.
4. Descargar el JSON; elegirlo en la opción 3 y comprobar las copias y el JSON archivado.
5. En una muestra descartable, mover un original después del análisis y comprobar
   que se informe como faltante sin detener las otras copias.
6. Cancelar una pregunta con Ctrl+C y comprobar que no se inició el procesamiento.

No usar miniaturas para decidir nitidez: revisar los originales. Mantener el código
de pruebas sincronizado con las reglas; no debilitar una prueba solo para obtener OK.
