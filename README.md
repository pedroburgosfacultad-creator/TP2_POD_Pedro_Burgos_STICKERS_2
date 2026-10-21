# Análisis técnico de imágenes para stickers

Autor: Pedro Burgos. Trabajo Práctico 2 de Programación Orientada a Datos.

El proyecto busca identificar imágenes que requieren revisión antes de imprimir
stickers. Su usuario es el responsable del microemprendimiento.

## Etapa actual

Lee PNG estáticos de una carpeta, comprueba su formato e integridad y obtiene el
ancho y alto del lienzo en píxeles. Informa errores individuales y continúa con
los demás archivos. No modifica los originales ni recorre subcarpetas.

Las medidas incluyen márgenes transparentes. Esta etapa todavía no evalúa
transparencia, resolución efectiva ni aptitud para impresión. Rechaza PNG animados
e imágenes que superan la protección de tamaño de Pillow.

## Estructura

- `data/README.md`: procedencia, variables y condiciones de uso.
- `src/main.py`: argumentos y presentación de resultados.
- `src/lectura.py`: búsqueda, lectura y clase `ImagenSticker`.
- `tests/test_lectura.py`: pruebas con imágenes artificiales temporales.
- `requirements.txt`: dependencias de Python

## Uso

Desde la carpeta `proyecto`, con Python 3.14 (versión utilizada para las pruebas),
ejecutar en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py "C:\ruta\a\stickers"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Si el Python activo ya tiene las dependencias:

```powershell
python src/main.py "C:\ruta\a\stickers"
python -m unittest discover -s tests -v
```

Ejemplo ilustrativo, no obtenido de la colección real:

```text
OK | ejemplo.png | 40 x 25 px

PNG encontrados: 1
Leídos correctamente: 1
Con errores: 0
```

## Validaciones y errores

La expresión regular `\.png\Z` selecciona extensiones sin distinguir mayúsculas.
Pillow verifica además el formato real, la integridad y la decodificación. Los
archivos rechazados conservan su ruta y motivo. No se reparan ni se borran.
No se eliminan duplicados: cada archivo es una observación.

Los errores se escriben en la salida de errores. Códigos de salida: 0 sin errores,
1 con archivos rechazados y 2 con carpeta o argumentos inválidos. Una carpeta sin
PNG devuelve 0 con un aviso explícito; no significa que se analizaron imágenes.

Pillow permite leer imágenes; unittest está incluido en Python. No se necesitan
APIs ni Internet después de instalar las dependencias.

## Pendientes

La pregunta final será qué archivos requieren revisión según resolución y
transparencia al tamaño previsto. Quedan pendientes esos indicadores, informes,
abstracción de fuentes y documentación de resultados. Según la aclaración docente
comunicada por el alumno, se permiten imágenes sin exigir lectura CSV/JSON.
