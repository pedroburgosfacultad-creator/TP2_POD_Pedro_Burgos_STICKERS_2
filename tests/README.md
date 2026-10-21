# Pruebas

Desde la raíz del proyecto (C:\tps\tp2_explo), con las dependencias instaladas:

```powershell
python -m unittest discover -s tests -v
```

Las pruebas crean imágenes pequeñas en carpetas temporales y las eliminan al
terminar. No requieren imágenes personales ni Internet.

- Lectura: medidas, originales intactos, formato real, errores y rutas.
- Resolución: cálculo conocido, umbral exacto y reducción a la mitad al duplicar tamaño.
- Transparencia: RGB opaco, RGBA vacío/parcial, márgenes y PNG de paleta.
- Validaciones: tamaños y umbrales inválidos, NaN e infinito.
- Informes: archivos rechazados incluidos, totales coherentes, texto y CSV legibles,
  preservación de ejecuciones anteriores y comportamiento sin imágenes.
- Integración: ejecución del comando y creación efectiva de reportes.
