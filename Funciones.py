import time
import multiprocessing

""""""""""""""""""""""""""
"""ALGORITMO SECUENCIAL"""
""""""""""""""""""""""""""

def procesar_texto_secuencial(ruta_entrada, ruta_salida):
    """Procesa el archivo de texto secuencialmente."""
    try:
        with open(ruta_entrada, 'r') as f_in, open(ruta_salida, 'w') as f_out:
            for linea in f_in:
                linea_limpia = linea.strip()
                linea_mayusculas = linea_limpia.upper()
                f_out.write(linea_mayusculas + '\n')
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")

""""""""""""""""""""""""""
"""ALGORITMO   PARALELO"""
""""""""""""""""""""""""""

def leer_lineas(ruta_entrada, cola_salida, tamaño_bloque=10000):
    #Lee el archivo en subdivisiones y los envia a la cola
    with open(ruta_entrada, 'r') as f:
        while True:
            lineas = [f.readline() for _ in range(tamaño_bloque)]
            lineas = [l for l in lineas if l]
            if not lineas:
                break
            cola_salida.put(lineas)
    cola_salida.put(None)

def limpiar_lineas(bloque):
    return [linea.strip() for linea in bloque]

def convertir_mayusculas(bloque):
    return [linea.upper() for linea in bloque]

def limpiar_y_convertir(cola_entrada, cola_salida):
    while True:
        bloque = cola_entrada.get()
        if bloque is None:
            cola_salida.put(None)
            break
        bloque = limpiar_lineas(bloque)
        bloque = convertir_mayusculas(bloque)
        cola_salida.put(bloque)

def escribir_lineas(ruta_salida, cola_entrada):
    with open(ruta_salida, 'w') as f:
        while True:
            bloque = cola_entrada.get()
            if bloque is None:
                break
            for linea in bloque:
                f.write(linea + '\n')

def procesar_texto_pipeline(ruta_entrada, ruta_salida):
    cola1 = multiprocessing.Queue()
    cola2 = multiprocessing.Queue()

    # Procesos del pipeline
    p1 = multiprocessing.Process(target=leer_lineas, args=(ruta_entrada, cola1))
    p2 = multiprocessing.Process(target=limpiar_y_convertir, args=(cola1, cola2))
    p3 = multiprocessing.Process(target=escribir_lineas, args=(ruta_salida, cola2))

    inicio = time.time()
    for p in [p1, p2, p3]:
        p.start()
    for p in [p1, p2, p3]:
        p.join()
    fin = time.time()

    print(f"Tiempo total de procesamiento paralelo: {fin - inicio:.6f} segundos")

if __name__ == '__main__':
    ruta_entrada = "prueba.txt"
    ruta_salida_secuencial = "texto_salida_secuencial.txt"
    ruta_salida_pipeline = "texto_salida_pipeline.txt"

    # Secuencial
    inicio = time.time()
    procesar_texto_secuencial(ruta_entrada, ruta_salida_secuencial)
    fin = time.time()
    print(f"Tiempo total de procesamiento secuencial: {fin - inicio:.6f} segundos")
    print(f"Archivo procesado secuencialmente guardado en {ruta_salida_secuencial}\n")

    # Paralelo
    procesar_texto_pipeline(ruta_entrada, ruta_salida_pipeline)
    print(f"Archivo procesado en pipeline guardado en {ruta_salida_pipeline}")