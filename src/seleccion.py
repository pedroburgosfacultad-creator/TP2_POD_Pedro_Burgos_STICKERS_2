"""Copia a una carpeta nueva los originales elegidos en el informe HTML."""
from datetime import datetime
from pathlib import Path
import shutil

if __package__:
    from .fuentes import leer_seleccion
else:
    from fuentes import leer_seleccion


def preparar_photoroom(archivo_seleccion, directorio):
    """Devuelve destino, nombres copiados y errores; nunca mueve los originales."""
    origen, nombres, contenido = leer_seleccion(archivo_seleccion)
    destino = Path(directorio).resolve() / datetime.now().strftime("seleccion_photoroom_%Y%m%d_%H%M%S_%f")
    destino.mkdir(parents=True, exist_ok=False)
    # Conserva exactamente la selección recibida, incluso si falta algún original.
    (destino / "seleccion_photoroom.json").write_bytes(contenido)
    copiados, errores = [], []
    # Conserva el orden y evita copiar dos veces el mismo nombre.
    for nombre in dict.fromkeys(nombres):
        fuente = origen / nombre
        try:
            if fuente.is_symlink() or fuente.resolve().parent != origen:
                raise ValueError("El archivo apunta fuera de la carpeta original.")
            if not fuente.is_file():
                raise ValueError("El original no existe o fue movido.")
            # Modo exclusivo: tampoco se sobrescriben colisiones de nombres.
            with fuente.open("rb") as entrada, (destino / nombre).open("xb") as salida:
                try:
                    shutil.copyfileobj(entrada, salida)
                except OSError:
                    salida.close()
                    (destino / nombre).unlink(missing_ok=True)
                    raise
            copiados.append(nombre)
        except (OSError, ValueError) as error:
            errores.append((nombre, str(error)))
    return destino, copiados, errores


def mostrar_preparacion(archivo_seleccion, directorio):
    """Copia la selección para PhotoRoom, informa en la terminal y devuelve el código de salida."""
    
    destino, copiados, errores = preparar_photoroom(archivo_seleccion, directorio)
    print(f"Originales copiados: {len(copiados)}")
    for nombre, error in errores:
        print(f"NO COPIADO | {nombre} | {error}")
    print(f"Carpeta para PhotoRoom: {destino}")
    print(f"Selección guardada: {destino / 'seleccion_photoroom.json'}")
    print("No se convierten formatos ni se eliminan fondos. Los originales permanecen intactos.")
    return 1 if errores else 0
