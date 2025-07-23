# CC5213 - TAREA 2 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# Fecha: 08 de mayo de 2025
# Alumno: [Patricio Espinoza Acuña]

import sys
import os
import util as util
import numpy as np

# Audios R: Originales (duración de 5 a 40 segundos)
# Audios Q: Emisoras (pueden contener multiples veces un audio R) (contiene de 20 a 40 canciones R)

def tarea2_parte1(carpeta_entrada_audios, carpeta_salida_descriptores):
    if not os.path.isdir(carpeta_entrada_audios):
        print("ERROR: no existe carpeta {}".format(carpeta_entrada_audios))
        sys.exit(1)
    elif os.path.exists(carpeta_salida_descriptores):
        print("ERROR: ya existe {}".format(carpeta_salida_descriptores))
        sys.exit(1)

    # Implementar la tarea con los siguientes pasos:
    #  1-leer los archivos con extension .m4a que están carpeta_entrada_audios
    #    puede servir la funcion util.listar_archivos_con_extension() que está definida en util.py
    input_audios = util.listar_archivos_con_extension(carpeta_entrada_audios, ".m4a")
    input_dir = [os.path.join(carpeta_entrada_audios, audio) for audio in input_audios]
    os.makedirs(carpeta_salida_descriptores, exist_ok=True)
    print(f"\n\nT2. Parte 1.1: {len(input_dir)} archivos de audio encontrados en {carpeta_entrada_audios}.\nGuardando descriptores en {carpeta_salida_descriptores}.")
    
    #  2-convertir cada archivo de audio a wav (guardar los wav temporales en carpeta_salida_descriptores)
    #    puede servir la funcion util.convertir_a_wav() que está definida en util.py
    sample_rate = 6000
    audios_wav = [util.convertir_a_wav(archivo_audio, sample_rate, carpeta_salida_descriptores) for archivo_audio in input_dir]

    #  3-calcular descriptores del archivo wav
    samples_por_ventana = 4096      # 512, 1024, 2048, 4096, 8192
    samples_salto = 4096            # puede ser igual a samples_por_ventana o samples_por_ventana/2
    dimension = 160               # por lo general entre 20 y 30

    for audio in audios_wav:
        name = os.path.basename(audio)
        descriptores = util.calcular_descriptores_mfcc(audio, sample_rate, samples_por_ventana, samples_salto, dimension)
        name_numpy = f"{name}-descriptor.npy"
        np.save(os.path.join(carpeta_salida_descriptores, name_numpy), descriptores)
        ventanas = util.lista_ventanas(name, descriptores.shape[0], sample_rate, samples_por_ventana)
        name_pickle = f"{name}-ventanas.pickle"

        #  4-escribir en carpeta_salida_descriptores los descriptores de cada archivo
        #    puede servir la funcion util.guardar_objeto() que está definida en util.py
        util.guardar_objeto(ventanas, carpeta_salida_descriptores, name_pickle)

    print(f"T2. Parte 1: Descriptores guardados en {carpeta_salida_descriptores}.")


# inicio de la tarea
if len(sys.argv) != 3:
    print("Uso: {} [carpeta_entrada_audios] [carpeta_salida_descriptores]".format(sys.argv[0]))
    sys.exit(1)

# lee los parametros de entrada
carpeta_entrada_audios = sys.argv[1]
carpeta_salida_descriptores = sys.argv[2]

# llamar a la tarea
tarea2_parte1(carpeta_entrada_audios, carpeta_salida_descriptores)
