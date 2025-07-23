# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# Fecha: 27 de marzo de 2025
# Alumno: Patricio Espinoza A.

import sys
import os
import util as util

import scipy.spatial
import pandas as pd
from scipy.spatial import distance
import numpy as np


def tarea1_parte2(dir_input_imagenes_Q, dir_input_descriptores_R, file_output_resultados):
    if not os.path.isdir(dir_input_imagenes_Q):
        print("ERROR: no existe directorio {}".format(dir_input_imagenes_Q))
        sys.exit(1)
    elif not os.path.isdir(dir_input_descriptores_R):
        print("ERROR: no existe directorio {} (¿terminó bien tarea1-parte1.py?)".format(dir_input_descriptores_R))
        sys.exit(1)
    elif os.path.exists(file_output_resultados):
        print("ERROR: ya existe archivo {}".format(file_output_resultados))
        sys.exit(1)
    # Implementar la fase online

    # 1-calcular descriptores de Q para imágenes en dir_input_imagenes_Q
    # ver codigo de ejemplo publicado en el curso
    imagenes_Q = util.listar_archivos_con_extension(dir_input_imagenes_Q, ".jpg")
    print("Número de imágenes Q: {}".format(len(imagenes_Q)))

    # Calcula los descriptores para cada imagen en Q
    descriptores_Q = {}
    for nombre_imagen_q in imagenes_Q:
        descriptor_q = util.concat_features(nombre_imagen_q, dir_input_imagenes_Q)
        descriptores_Q[nombre_imagen_q] = descriptor_q

    nombres_imagenes_Q = list(descriptores_Q.keys())
    matriz_descriptores_Q = None
    num_fila = 0
    
    for nombre_imagen in nombres_imagenes_Q:
        descriptor_imagen = descriptores_Q[nombre_imagen]
        
        if matriz_descriptores_Q is None:
            # Crear la matriz en base al primer descriptor
            matriz_descriptores_Q = np.zeros((len(nombres_imagenes_Q), len(descriptor_imagen)), dtype=np.float32)
        
        matriz_descriptores_Q[num_fila] = descriptor_imagen
        num_fila += 1

    # 2-leer descriptores de R guardados en dir_input_descriptores_R
    # puede servir la funcion util.leer_objeto() que está definida en util.py
    descriptores_R = util.leer_objeto(dir_input_descriptores_R, "descriptores_R.pkl")

    # descriptores_R a matriz
    nombres_imagenes_R = list(descriptores_R.keys())
    matriz_descriptores_R = None
    num_fila = 0

    for nombre_imagen in nombres_imagenes_R:
        descriptor_imagen = descriptores_R[nombre_imagen]
        
        if matriz_descriptores_R is None:
            # Crear la matriz una sola vez, usando la forma del primer descriptor
            matriz_descriptores_R = np.zeros((len(nombres_imagenes_R), len(descriptor_imagen)), dtype=np.float32)
        
        # Copiar el descriptor a la fila correspondiente
        matriz_descriptores_R[num_fila] = descriptor_imagen
        num_fila += 1

    # 3-para cada descriptor q localizar el mas cercano en R
    matriz_distancias = distance.cdist(matriz_descriptores_Q, matriz_descriptores_R, metric='cityblock') 

    resultados = []

    for i, nombre_q in enumerate(nombres_imagenes_Q):
        idx_r_mas_cercano = np.argmin(matriz_distancias[i])
        nombre_r_mas_cercano = nombres_imagenes_R[idx_r_mas_cercano]
        min_distancia = matriz_distancias[i, idx_r_mas_cercano]
        resultados.append([nombre_q, nombre_r_mas_cercano, min_distancia])


    # 4-escribir en el archivo file_output_resultados un archivo con tres columnas separado por \t:
    # columna 1: imagen_q
    # columna 2: imagen_r
    # columna 3: distancia
    # Puede servir la funcion util.escribir_lista_de_columnas_en_archivo() que está definida util.py
    util.escribir_lista_de_columnas_en_archivo(resultados, file_output_resultados)


# inicio de la tarea
if len(sys.argv) < 4:
    print("Uso: {}  dir_input_imagenes_Q  dir_input_descriptores_R  file_output_resultados".format(sys.argv[0]))
    sys.exit(1)

# lee los parametros de entrada
dir_input_imagenes_Q = sys.argv[1]
dir_input_descriptores_R = sys.argv[2]
file_output_resultados = sys.argv[3]

# ejecuta la tarea
tarea1_parte2(dir_input_imagenes_Q, dir_input_descriptores_R, file_output_resultados)
