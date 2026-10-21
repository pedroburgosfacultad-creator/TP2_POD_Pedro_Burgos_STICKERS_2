# Tests

Desde `proyecto`: `python -m unittest discover -s tests -v`.

Las pruebas crean imágenes pequeñas en carpetas temporales y las eliminan al
terminar. Verifican dimensiones, conservación del original, conteo de un lote con
errores, extensión en mayúsculas, formato incorrecto, PNG truncado, carpeta vacía
o inexistente, ruta que es archivo, exclusión de subcarpetas y el comando de uso.
No requieren imágenes personales ni Internet.
