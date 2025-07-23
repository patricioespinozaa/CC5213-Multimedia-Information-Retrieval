# CC5213 - TAREA 2 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# Fecha: 08 de mayo de 2025
# Alumno: [Patricio Espinoza Acuña]

import sys
import os
import util as util

def tarea2_parte3(carpeta_ventanas_similares, archivo_salida_detecciones_txt):
    if not os.path.isdir(carpeta_ventanas_similares):
        print("ERROR: no existe carpeta {}".format(carpeta_ventanas_similares))
        sys.exit(1)
    elif os.path.exists(archivo_salida_detecciones_txt):
        print("ERROR: ya existe {}".format(archivo_salida_detecciones_txt))
        sys.exit(1)
    #
    # Implementar la tarea con los siguientes pasos:
    #
    #  1-leer el o los archivos en carpeta_ventanas_similares (fue creado por tarea2_parte2)
    #    puede servir la funcion util.leer_objeto() que está definida en util.py
    archivos = os.listdir(carpeta_ventanas_similares)
    objetos_leidos = []

    for archivo in archivos:
        if archivo.endswith(".pickle"):
            objeto = util.leer_objeto(carpeta_ventanas_similares, archivo)
            if objeto is not None:
                objetos_leidos.extend(objeto)  # cada archivo contiene muchas filas
            else:
                print(f"✗ No se pudo leer: {archivo}")
    print(f"T2. Parte 3: Se leyeron {len(objetos_leidos)} objetos de {len(archivos)} archivos en {carpeta_ventanas_similares}")

    #  2-crear un algoritmo para buscar secuencias similares entre audios
    #    ver material de la semanas 5 y 7
    #    identificar grupos de ventanas de Q y R que son similares y pertenecen a las mismas canciones con el mismo desfase
    resultados = []
    secuencia_activa = False
    fallos_limite = 6
    secuencia_actual = {
        "diferencia_tiempo": None,
        "inicio_secuencia": None,
        "fin_secuencia": None,
        "radio": None,
        "cancion": None,
        "confianza": 0,
        "fallos_actuales": 0
    }

    def iniciar_secuencia(actual, siguiente):
        return {
            "diferencia_tiempo": actual["diferencia_segundos"],
            "inicio_secuencia": actual["ventana_Q"].segundos_desde,
            "fin_secuencia": actual["ventana_Q"].segundos_hasta,
            "radio": siguiente["ventana_Q"].nombre_archivo,
            "cancion": actual["ventana_R"].nombre_archivo,
            "confianza": 1,
            "fallos_actuales": 0
        }

    def guardar_secuencia(secuencia):
        duracion = secuencia["fin_secuencia"] - secuencia["inicio_secuencia"]
        cancion = ".".join(secuencia["cancion"].split(".")[:2])
        radio = ".".join(secuencia["radio"].split(".")[:2])
        resultados.append([
            radio,
            round(secuencia["inicio_secuencia"], 2),
            cancion,
            secuencia["confianza"]
        ])


    # Ordenar por nombre y tiempo de inicio de ventana Q
    objetos_leidos.sort(key=lambda x: (x["ventana_Q"].nombre_archivo, x["ventana_Q"].segundos_desde))

    i = 0
    total = len(objetos_leidos)

    while i < total:
        actual = objetos_leidos[i]
        siguiente = objetos_leidos[i + 1] if i + 1 < total else None

        if not secuencia_activa and siguiente:
            if (actual["ventana_Q"].nombre_archivo == siguiente["ventana_Q"].nombre_archivo and
                actual["ventana_R"].nombre_archivo == siguiente["ventana_R"].nombre_archivo and
                actual["diferencia_segundos"] == siguiente["diferencia_segundos"]):
                secuencia_activa = True
                secuencia_actual = iniciar_secuencia(actual, siguiente)
            else:
                i += 1
                continue
        elif secuencia_activa:
            if (siguiente and
                actual["ventana_R"].nombre_archivo == siguiente["ventana_R"].nombre_archivo and
                actual["diferencia_segundos"] == siguiente["diferencia_segundos"]):
                secuencia_actual["fin_secuencia"] = actual["ventana_Q"].segundos_hasta
                secuencia_actual["confianza"] += 1
                secuencia_actual["fallos_actuales"] = 0
            else:
                secuencia_actual["fallos_actuales"] += 1

            if secuencia_actual["fallos_actuales"] >= fallos_limite:
                guardar_secuencia(secuencia_actual)
                secuencia_activa = False
                secuencia_actual = {
                    "diferencia_tiempo": None,
                    "inicio_secuencia": None,
                    "fin_secuencia": None,
                    "radio": None,
                    "cancion": None,
                    "confianza": 0,
                    "fallos_actuales": 0
                }

        i += 1

    if secuencia_activa:
        guardar_secuencia(secuencia_actual)

    #  3-escribir las detecciones encontradas en archivo_salida_detecciones_txt:
    #    columna 1: nombre de archivo Q (nombre de archivo en carpeta radio)
    #    columna 2: tiempo de inicio (número decimal, tiempo en segundos del inicio de la detección)
    #    columna 3: nombre de archivo R (nombre de archivo en carpeta canciones)
    #    columna 4: confianza (número decimal, mientras más alto mayor confianza que la respuesta es correcta)
    #   le puede servir la funcion util.escribir_lista_de_columnas_en_archivo() que está definida util.py
    util.escribir_lista_de_columnas_en_archivo(resultados, archivo_salida_detecciones_txt)


# inicio de la tarea
if len(sys.argv) != 3:
    print("Uso: {} [carpeta_ventanas_similares] [archivo_salida_detecciones_txt]".format(sys.argv[0]))
    sys.exit(1)

# lee los parametros de entrada
carpeta_ventanas_similares = sys.argv[1]
archivo_salida_detecciones_txt = sys.argv[2]

# llamar a la tarea
tarea2_parte3(carpeta_ventanas_similares, archivo_salida_detecciones_txt)
