# CC5213 - TAREA 2 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# Fecha: 08 de mayo de 2025
# Alumno: [Patricio Espinoza Acuña]

import sys
import os
import util as util
import numpy as np
import scipy


# Audios R: Originales (duración de 5 a 40 segundos)
# Audios Q: Emisoras (pueden contener multiples veces un audio R) (contiene de 20 a 40 canciones R)

def tarea2_parte2(carpeta_descriptores_radio_Q, carpeta_descritores_canciones_R, carpeta_salida_ventanas_similares):
    if not os.path.isdir(carpeta_descriptores_radio_Q):
        print("ERROR: no existe carpeta {}".format(carpeta_descriptores_radio_Q))
        sys.exit(1)
    elif not os.path.isdir(carpeta_descritores_canciones_R):
        print("ERROR: no existe carpeta {}".format(carpeta_descritores_canciones_R))
        sys.exit(1)
    elif os.path.exists(carpeta_salida_ventanas_similares):
        print("ERROR: ya existe {}".format(carpeta_salida_ventanas_similares))
        sys.exit(1)
    #
    # Implementar la tarea con los siguientes pasos:
    #
    #  1-leer descriptores de Q y R: datos en carpeta_descriptores_radio_Q y carpeta_descritores_canciones_R
    #     esas carpetas fueron creadas por tarea2_parte1
    #     puede servir la funcion util.leer_objeto() que está definida en util.py
    carpetas = [carpeta_descritores_canciones_R, carpeta_descriptores_radio_Q]
    nombres = ["R", "Q"]
    descriptores_Q = ventanas_Q = descriptores_R = ventanas_R = None

    for nombre, carpeta in zip(nombres, carpetas):
        descriptores, ventanas = util.load_descriptors_and_windows(carpeta)

        if nombre == "R":
            descriptores_R, ventanas_R = descriptores, ventanas
        elif nombre == "Q":
            descriptores_Q, ventanas_Q = descriptores, ventanas
  
    Q_windows_list = [item for sub in ventanas_Q for item in (sub if isinstance(sub, list) else [sub])]
    R_windows_list = [item for sub in ventanas_R for item in (sub if isinstance(sub, list) else [sub])]

    Q_descriptors_matrix = np.vstack(descriptores_Q) if descriptores_Q else np.array([])
    R_descriptors_matrix = np.vstack(descriptores_R) if descriptores_R else np.array([])
    #  2-para cada descriptor de Q localizar el más cercano en R
    #     se puede usar cdist como en la tarea 1
    matriz_distancias = scipy.spatial.distance.cdist(Q_descriptors_matrix, R_descriptors_matrix, metric='cityblock')

    # Obtener la posición del más cercano por fila
    posicion_min = np.argmin(matriz_distancias, axis=1)

    #  3-crear la carpeta carpeta_salida_ventanas_similares
    #     guardar un archivo que asocie cada ventana de Q con su ventana más parecida en R
    #     tambien guardar el nombre del archivo y los tiempos de inicio y fin que representa cada ventana de Q y R
    #     puede servir la funcion util.guardar_objeto() que está definida en util.py
    os.makedirs(carpeta_salida_ventanas_similares)
    resultados_txt = os.path.join(carpeta_salida_ventanas_similares, "ventanas_similares.txt")

    # Estructura para guardar como objeto si quieres usar util.guardar_objeto
    asociaciones = []

    with open(resultados_txt, 'w') as archivo:
        for i in range(len(Q_windows_list)):
            window_Q = Q_windows_list[i]
            window_R = R_windows_list[posicion_min[i]]
            
            diff = window_R.segundos_desde - window_Q.segundos_desde
            
            asociaciones.append({
                "ventana_Q": window_Q,
                "ventana_R": window_R,
                "diferencia_segundos": diff
            })

    # Guardar objeto .pickle con util.guardar_objeto (opcional)
    util.guardar_objeto(asociaciones, carpeta_salida_ventanas_similares, "asociaciones_Q_R.pickle")
    print(f"✓ Se han guardado las asociaciones en {resultados_txt} y en 'asociaciones_Q_R.pickle'.")

# inicio de la tarea
if len(sys.argv) != 4:
    print(
        "Uso: {} [carpeta_descriptores_radio_Q] [carpeta_descritores_canciones_R] [carpeta_salida_ventanas_similares]".format(
            sys.argv[0]))
    sys.exit(1)

# lee los parametros de entrada
carpeta_descriptores_radio_Q = sys.argv[1]
carpeta_descritores_canciones_R = sys.argv[2]
carpeta_salida_ventanas_similares = sys.argv[3]

# llamar a la tarea
tarea2_parte2(carpeta_descriptores_radio_Q, carpeta_descritores_canciones_R, carpeta_salida_ventanas_similares)
