from contextlib import nullcontext

from PIL import Image
import os
import time
import multiprocessing

def convertir_a_gris(ruta_imagen):
    try:
        imagen = Image.open(ruta_imagen)
        imagen_gris = imagen.convert('L') # 'L' representa escala de grises
        nombre_archivo, extension = os.path.splitext(ruta_imagen)
        ruta_gris = nombre_archivo + "_gris" + extension
        imagen_gris.save(ruta_gris)
        print(f"Imagen convertida: {ruta_imagen} -> {ruta_gris}")
    except FileNotFoundError:
        print(f"Error: No se encontró la imagen {ruta_imagen}")
    except Exception as e:
        print(f"Error al procesar {ruta_imagen}: {e}")

def procesar_imagenes_secuencial(lista_imagenes):
    for ruta_imagen in lista_imagenes:
        convertir_a_gris(ruta_imagen)

def procesar_imagenes_parcial(lista_parcial, q):
    for ruta in lista_parcial:
        convertir_a_gris(ruta)
    q.put(len(lista_parcial))  # Retornar cuántas imágenes se procesaron

def limpiar_imagenes_grises(directorio):
    eliminadas = 0
    for f in os.listdir(directorio):
        if "_gris" in f:  # Identificar las imágenes procesadas
            os.remove(os.path.join(directorio, f))
            eliminadas += 1

if __name__ == '__main__':
    directorio_imagenes = r"C:\Users\Galaxiumy\Pictures\Prueba" # Reemplaza con el nombre de tu directorio
    lista_imagenes = [os.path.join(directorio_imagenes, f) for f in
                  os.listdir(directorio_imagenes) if os.path.isfile(os.path.join(directorio_imagenes, f))]

    inicio = time.time()
    procesar_imagenes_secuencial(lista_imagenes)
    fin = time.time()
    print(f"\n Tiempo total de procesamiento secuencial: {fin - inicio:.6f} segundos")
    print()
    limpiar_imagenes_grises(directorio_imagenes)

    num_procesos = multiprocessing.cpu_count()
    tamaño_parcial = len(lista_imagenes) // num_procesos
    procesos = []
    resultados = multiprocessing.Queue()

    inicio = time.time()

    for i in range(num_procesos):
        inicio_idx = i * tamaño_parcial
        fin_idx = (i + 1) * tamaño_parcial if i != num_procesos - 1 else len(lista_imagenes)
        chunk = lista_imagenes[inicio_idx:fin_idx]
        p = multiprocessing.Process(target=procesar_imagenes_parcial, args=(chunk, resultados))
        procesos.append(p)
        p.start()

    # Esperar a que terminen
    for p in procesos:
        p.join()

    # Recolectar resultados
    total_procesadas = 0
    while not resultados.empty():
        total_procesadas += resultados.get()

    fin = time.time()
    print(f"\n Tiempo total de procesamiento paralelo: {fin - inicio:.6f} segundos")
    limpiar_imagenes_grises(directorio_imagenes)