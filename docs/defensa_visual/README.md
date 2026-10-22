# StickerLab · Guía para la defensa

Material de estudio local para el TP2 de Programación Orientada a Datos de Pedro Burgos.
Está separado del programa Python. No requiere cambiar requirements.txt ni usar servicios externos.

## Abrir

Abrir `../../outputs/defensa/index.html` con doble clic. Es un HTML autocontenido: funciona sin Internet y no necesita servidor ni Node para consultarlo. Se puede copiar ese único archivo a otra computadora. El progreso, notas y checklist se guardan solo en el navegador cuando su almacenamiento está disponible.

## Regenerar después de cambiar el código

Con Python y Node disponibles, desde esta carpeta:

```powershell
python snapshot.py
pnpm install --frozen-lockfile
pnpm build
pnpm start
```

La vista previa se sirve solo en http://127.0.0.1:4173. El build genera `dist/index.html` y `outputs/defensa/index.html`. El contenido fuente y el lockfile se versionan; node_modules, dist y outputs se ignoran. No se copian fotografías privadas.

## Contenido y procedencia

El explorador incluye todos los módulos, clases, funciones y métodos de `src`, con líneas y huellas SHA-256 tomadas por `snapshot.py`. Incluye código de tests, documentación, diccionario de datos, simuladores didácticos y una animación con Remotion Player. Los simuladores son traducciones didácticas del cálculo, no ejecutan Python ni certifican imágenes reales.

La matriz académica usa los siete pasos de `consigna_TP2.pdf` de Programación Orientada a Datos, páginas 1–4, consultado localmente el 22/10/2026. No se distribuye el PDF docente. `rubrica_TP2_ED.pdf` es de Exploración de Datos (R/SQLite) y no se aplica a este TP. No se inventan ponderaciones ni una nota de aprobación. La adaptación CSV/JSON a carpeta/selección JSON debe justificarse ante la cátedra.

Verificación de base: 52 pruebas Python aprobadas el 22/10/2026 sobre commit 673e0be6edc158a5c84a88f6ee62af39852d26b1. Regenerar una instantánea no vuelve a ejecutar las pruebas: la fecha del resultado es histórica. No se confirma acceso docente al remoto ni cumplimiento académico completo.

Remotion Player: https://www.remotion.dev/docs/player/player
