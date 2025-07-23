# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# Fecha: 08 de mayo de 2025
# Programa de evaluación de la Tarea 2
# Autor: Juan Manuel Barrios

import sys
import subprocess
import os
import numpy
import shutil
import time


class Deteccion:
    def __init__(self, id_deteccion, tipo, radio, desde, largo, cancion, confianza):
        self.id_deteccion = id_deteccion
        self.tipo = tipo
        self.radio = radio
        self.desde = desde
        self.largo = largo
        self.cancion = cancion
        self.confianza = confianza

    def interseccion(self, det_gt):
        # deben coincidir nombres de radio y cancion
        if self.radio != det_gt.radio or self.cancion != det_gt.cancion:
            return 0
        # el largo se obtiene desde gt
        ini1 = self.desde
        end1 = self.desde + det_gt.largo
        ini2 = det_gt.desde
        end2 = det_gt.desde + det_gt.largo
        inter = min(end1, end2) - max(ini1, ini2)
        union = max(end1, end2) - min(ini1, ini2)
        if inter <= 0 or union <= 0:
            return 0
        return inter / union


def get_filename(filepath):
    name = filepath.lower().strip()
    if name.rfind('/') >= 0:
        name = name[name.rfind('/') + 1:]
    if name.rfind('\\') >= 0:
        name = name[name.rfind('\\') + 1:]
    return name


def parsear_deteccion(id_deteccion, archivo_fuente, linea, es_gt):
    linea = linea.rstrip("\r\n")
    # se ignoran lineas vacias o comentarios
    if linea == "" or linea.startswith("#"):
        return None
    partes = linea.split("\t")
    tipo = radio = cancion = ""
    desde = largo = confianza = 0
    if es_gt:
        if len(partes) != 5:
            raise Exception(archivo_fuente + " tiene formato invalido (es correcto el dataset?)")
        tipo = partes[0]
        radio = get_filename(partes[1])
        desde = round(float(partes[2]), 3)
        largo = round(float(partes[3]), 3)
        cancion = get_filename(partes[4])
    else:
        if len(partes) != 4:
            raise Exception(archivo_fuente + " tiene formato incorrecto (se esperan 4 columnas separadas por un tabulador)")
        radio = get_filename(partes[0])
        desde = round(float(partes[1]), 3)
        cancion = get_filename(partes[2])
        confianza = float(partes[3])
        if desde < 0:
            raise Exception("valor incorrecto desde={} en {}".format(desde, archivo_fuente))
        if confianza <= 0:
            raise Exception("valor incorrecto confianza={} en {}".format(confianza, archivo_fuente))
    if radio == "":
        raise Exception("nombre radio invalido en " + archivo_fuente)
    if cancion == "":
        raise Exception("nombre cancion invalido en " + archivo_fuente)
    det = Deteccion(id_deteccion, tipo, radio, desde, largo, cancion, confianza)
    return det


def leer_detecciones(filename, es_gt):
    if not os.path.isfile(filename):
        raise Exception("no existe el archivo {}".format(filename))
    cont_lineas = 0
    lista = list()
    with open(filename) as f:
        for linea in f:
            cont_lineas += 1
            try:
                # el id es su posición en la lista
                det = parsear_deteccion(len(lista), filename, linea, es_gt)
                if det is not None:
                    lista.append(det)
            except Exception as ex:
                print("Error {} (linea {}): {}".format(filename, cont_lineas, ex))
    print("{} detecciones en archivo {}".format(len(lista), filename))
    return lista


class ResultadoDeteccion:
    def __init__(self, deteccion):
        self.deteccion = deteccion
        self.es_incorrecta = False
        self.es_duplicada = False
        self.es_correcta = False
        self.gt = None
        self.iou = 0

    def to_string(self):
        s1 = ""
        s2 = ""
        if self.es_correcta:
            s1 = " OK)"
            s2 = "   //IoU={:.1%}".format(self.iou)
        elif self.es_duplicada:
            s1 = "dup)"
        elif self.es_incorrecta:
            s1 = " --)"
        d = self.deteccion
        return "{} {} {} {} {}{}".format(s1, d.radio, d.desde, d.cancion, d.confianza, s2)


class Metricas:
    def __init__(self, threshold):
        self.threshold = threshold
        self.total_gt = 0
        self.total_detecciones = 0
        self.correctas = 0
        self.incorrectas = 0
        self.recall = 0
        self.precision = 0
        self.f1 = 0
        self.iou = 0
        self.f1_iou = 0
        self.correctas_por_tipo = dict()
        self.recall_por_tipo = dict()


class EvaluadorT2:
    def __init__(self):
        self.detecciones_gt = None
        self.total_gt_por_tipo = None
        self.detecciones = None
        self.resultado_por_deteccion = list()
        self.resultado_global = None

    def leer_archivo_gt(self, file_gt):
        # cargar el ground-truth
        self.detecciones_gt = leer_detecciones(file_gt, True)
        self.total_gt_por_tipo = dict()
        for gt in self.detecciones_gt:
            self.total_gt_por_tipo[gt.tipo] = self.total_gt_por_tipo.get(gt.tipo, 0) + 1

    def leer_archivo_detecciones(self, file_detecciones):
        # cargar las detecciones
        self.detecciones = leer_detecciones(file_detecciones, False)

    def evaluar_cada_deteccion(self):
        # se evaluan las detecciones por confianza de mayor a menor
        self.detecciones.sort(key=lambda x: x.confianza, reverse=True)
        # para descartar las detecciones duplicadas
        ids_encontradas = set()
        # revisar cada deteccion
        for det in self.detecciones:
            # evaluar cada deteccion si es correcta a no
            gt_encontrada, iou = self.buscar_deteccion_en_gt(det)
            # retorna resultado
            res = ResultadoDeteccion(det)
            if gt_encontrada is None:
                res.es_incorrecta = True
            elif gt_encontrada.id_deteccion in ids_encontradas:
                res.es_duplicada = True
            else:
                res.es_correcta = True
                res.gt = gt_encontrada
                res.iou = iou
                # marcar que fue encontrada (para no encontrarla dos veces)
                ids_encontradas.add(gt_encontrada.id_deteccion)
            self.resultado_por_deteccion.append(res)

    def buscar_deteccion_en_gt(self, deteccion):
        gt_encontrada = None
        max_iou = 0
        # busca en gt la deteccion que tiene mayor iou
        for det_gt in self.detecciones_gt:
            iou = deteccion.interseccion(det_gt)
            if iou > max_iou:
                gt_encontrada = det_gt
                max_iou = iou
        return gt_encontrada, max_iou

    def calcular_metricas(self):
        # todos los umbrales posibles
        set_confianzas = set()
        for res in self.resultado_por_deteccion:
            if res.es_correcta:
                set_confianzas.add(res.deteccion.confianza)
        set_confianzas.add(0)
        # calcular las metricas para cada confianza y seleccionar el mejor
        for confianza in sorted(list(set_confianzas), reverse=True):
            met = self.evaluar_con_threshold(confianza)
            if self.resultado_global is None or met.f1_iou > self.resultado_global.f1_iou:
                self.resultado_global = met

    def evaluar_con_threshold(self, threshold):
        met = Metricas(threshold)
        met.total_gt = len(self.detecciones_gt)
        suma_iou = 0
        correctas_por_tipo = dict()
        for res in self.resultado_por_deteccion:
            # ignorar detecciones con confianza bajo el umbral
            if res.deteccion.confianza < threshold:
                continue
            met.total_detecciones += 1
            if res.es_correcta:
                met.correctas += 1
                suma_iou += res.iou
                correctas_por_tipo[res.gt.tipo] = correctas_por_tipo.get(res.gt.tipo, 0) + 1
            if res.es_incorrecta or res.es_duplicada:
                met.incorrectas += 1
        if met.correctas > 0:
            # recall mide lo detectado con respecto al total de detecciones
            met.recall = met.correctas / met.total_gt
            # precision mide la relacion entre detecciones correctas e incorrectas
            met.precision = met.correctas / met.total_detecciones
            # F1 combina precision con recall usando la media armónica
            met.f1 = (2 * met.precision * met.recall) / (met.precision + met.recall)
            # IoU (intersection over union) mide que tan exacto es el intervalo detectado
            met.iou = suma_iou / met.correctas
            # para evaluar se usa una combinacion 80% de F1 con 20% de IoU
            met.f1_iou = met.f1 * 0.8 + met.iou * 0.2
        for tipo in self.total_gt_por_tipo:
            total = self.total_gt_por_tipo[tipo]
            correctas = correctas_por_tipo.get(tipo, 0)
            met.correctas_por_tipo[tipo] = correctas
            met.recall_por_tipo[tipo] = correctas / total
        return met

    def imprimir_resultado_por_deteccion(self):
        if len(self.resultado_por_deteccion) == 0:
            return
        # ordenar los resultados como estan en el archivo de entrada
        self.resultado_por_deteccion.sort(key=lambda x: x.deteccion.id_deteccion)
        print()
        print("Resultado de cada una de las {} detecciones:".format(len(self.resultado_por_deteccion)))
        for res in self.resultado_por_deteccion:
            print("  {}".format(res.to_string()))

    def imprimir_resultado_global(self):
        if self.resultado_global is None:
            return
        m = self.resultado_global
        print()
        print("Resultado global:")
        print(" {} detecciones a evaluar, {} detecciones en GT".format(len(self.resultado_por_deteccion), m.total_gt))
        print(" Al usar umbral={} se seleccionan {} detecciones:".format(m.threshold, m.total_detecciones))
        print("    {} detecciones correctas, {} detecciones incorrectas".format(m.correctas, m.incorrectas))
        print("    Precision={:.3f} ({}/{})  Recall={:.3f} ({}/{})".format(m.precision, m.correctas,
                                                                           m.total_detecciones, m.recall, m.correctas,
                                                                           m.total_gt))
        print("    F1={:.3f}  IoU={:.1%}  ->  F1-IOU={:.3f}".format(m.f1, m.iou, m.f1_iou))

    def imprimir_resultado_por_transformacion(self):
        if self.resultado_global is None:
            return
        m = self.resultado_global
        print()
        print("Resultado por transformacion:")
        for tipo in m.recall_por_tipo:
            print("    {:15s}={:3} correctas ({:.0f}%)".format(tipo, m.correctas_por_tipo[tipo],
                                                               100 * m.recall_por_tipo[tipo]))

    def imprimir_incorrectas(self, incorrectas_a_mostrar):
        # ordenar los resultados por confianza
        self.resultado_por_deteccion.sort(key=lambda x: x.deteccion.confianza, reverse=True)
        print()
        print("Las {} detecciones incorrectas de mayor confianza:".format(incorrectas_a_mostrar))
        cont = 0
        for res in self.resultado_por_deteccion:
            if res.es_incorrecta or res.es_duplicada:
                print("  {}".format(res.to_string()))
                cont += 1
                if cont == incorrectas_a_mostrar:
                    break


def evaluar_resultado_en_dataset(nombre_dataset, filename_gt, filename_resultados):
    print()
    print("---------")
    print("Comparando \"{}\" con respuestas correctas en \"{}\"".format(filename_resultados, filename_gt))
    ev = EvaluadorT2()
    ev.leer_archivo_gt(filename_gt)
    ev.leer_archivo_detecciones(filename_resultados)
    ev.evaluar_cada_deteccion()
    ev.calcular_metricas()
    ev.imprimir_resultado_por_deteccion()
    ev.imprimir_resultado_global()
    ev.imprimir_resultado_por_transformacion()
    ev.imprimir_incorrectas(3)
    return ev.resultado_global.f1_iou


def validar_tiempo_maximo(t0):
    segundos = time.time() - t0
    # el enunciado dice que no puede demorar mas de 15 minutos
    if segundos > 15 * 60:
        print("La tarea no puede demorar más de 15 minutos!!")
        sys.exit(1)


def ejecutar_comando(comando):
    print()
    print("Ejecutando:")
    print("[{}] ".format(time.strftime("%d-%m-%Y %H:%M:%S")) + " ".join(comando))
    t0 = time.time()
    code = subprocess.call(comando)
    print()
    if code != 0:
        print("EL PROGRAMA {} RETORNA ERROR!".format(comando[1]))
        sys.exit(1)
    validar_tiempo_maximo(t0)


def ejecutar_tarea(nombre_dataset, carpeta_radio, carpeta_canciones, dir_evaluacion, esCppWindows=False, esCppLinux=False):
    datos_temporales = os.path.join(dir_evaluacion, nombre_dataset)
    dir_descriptores_canciones = os.path.join(datos_temporales, "descriptores_canciones")
    dir_descriptores_radio = os.path.join(datos_temporales, "descriptores_radio")
    dir_ventanas_similares = os.path.join(datos_temporales, "ventanas_similares")
    file_detecciones = os.path.join(datos_temporales, "detecciones.{}.txt".format(nombre_dataset))
    # comando para calcular descriptores R
    comando1 = [sys.executable, "tarea2-parte1.py", carpeta_canciones, dir_descriptores_canciones]
    # comando para calcular descriptores Q
    comando2 = [sys.executable, "tarea2-parte1.py", carpeta_radio, dir_descriptores_radio]
    # comando para buscar
    comando3 = [sys.executable, "tarea2-parte2.py", dir_descriptores_radio, dir_descriptores_canciones, dir_ventanas_similares]
    # comando para detectar
    comando4 = [sys.executable, "tarea2-parte3.py", dir_ventanas_similares, file_detecciones]
    # para C++
    if esCppWindows:
        ## comandos para binarios (C++) en Windows
        comando1 = ["tarea2-parte1.exe", carpeta_canciones, dir_descriptores_canciones]
        comando2 = ["tarea2-parte1.exe", carpeta_radio, dir_descriptores_radio]
        comando3 = ["tarea2-parte2.exe", dir_descriptores_radio, dir_descriptores_canciones, dir_ventanas_similares]
        comando4 = ["tarea2-parte3.exe", dir_ventanas_similares, file_detecciones]
    elif esCppLinux:
        ## comandos para binarios (C++) en Linux
        comando1 = ["./tarea2-parte1", carpeta_canciones, dir_descriptores_canciones]
        comando2 = ["./tarea2-parte1", carpeta_radio, dir_descriptores_radio]
        comando3 = ["./tarea2-parte2", dir_descriptores_radio, dir_descriptores_canciones, dir_ventanas_similares]
        comando4 = ["./tarea2-parte3", dir_ventanas_similares, file_detecciones]
    ejecutar_comando(comando1)
    ejecutar_comando(comando2)
    ejecutar_comando(comando3)
    ejecutar_comando(comando4)
    return file_detecciones


def evaluar_en_dataset(nombre_dataset, dir_evaluacion):
    dataset_basedir = os.path.join("datasets", nombre_dataset)
    if not os.path.isdir(dataset_basedir):
        print("no existe {}".format(dataset_basedir))
        sys.exit(1)
    carpeta_radio = os.path.join(dataset_basedir, "radio")
    carpeta_canciones = os.path.join(dataset_basedir, "canciones")
    filename_gt = os.path.join(dataset_basedir, "gt.txt")
    if not os.path.isdir(carpeta_radio):
        print("error leyendo {}. No existe {}".format(nombre_dataset, carpeta_radio))
        sys.exit(1)
    if not os.path.isdir(carpeta_canciones):
        print("error leyendo {}. No existe {}".format(nombre_dataset, carpeta_canciones))
        sys.exit(1)
    if not os.path.isfile(filename_gt):
        print("error leyendo {}. No existe {}".format(nombre_dataset, filename_gt))
        sys.exit(1)
    t0 = time.time()
    filename_detecciones = ejecutar_tarea(nombre_dataset, carpeta_radio, carpeta_canciones, dir_evaluacion)
    validar_tiempo_maximo(t0)
    segundos = time.time() - t0
    print("  tiempo {}: {:.1f} segundos".format(nombre_dataset, segundos))
    f1 = evaluar_resultado_en_dataset(nombre_dataset, filename_gt, filename_detecciones)
    return f1, segundos


def calcular_nota(f1_promedio):
    f1_para_4 = 0.30
    f1_para_7 = 0.80
    f1_max_bonus = 0.98
    if f1_promedio <= f1_para_4:
        nota = 1 + round(3 * f1_promedio / f1_para_4, 1)
        bonus = 0
    elif f1_promedio <= f1_para_7:
        nota = 4 + round(3 * (f1_promedio - f1_para_4) / (f1_para_7 - f1_para_4), 1)
        bonus = 0
    elif f1_promedio <= f1_max_bonus:
        nota = 7
        bonus = round((f1_promedio - f1_para_7) / (f1_max_bonus - f1_para_7), 1)
    else:
        nota = 7
        bonus = 1
    return nota, bonus


def evaluar_tarea2(datasets):
    print("CC5213 - Recuperación de Información Multimedia")
    print("Evaluación Tarea 2 - 2025a")
    # datos para la evaluacion
    dir_evaluacion = "evaluacion_tarea2"
    if os.path.exists(dir_evaluacion):
        print("borrando datos previos en {}...".format(dir_evaluacion))
        shutil.rmtree(dir_evaluacion)
    # evaluar sobre los datasets
    resultados = {}
    for nombre_dataset in datasets:
        print()
        print("------- EVALUACION EN {} -------".format(nombre_dataset))
        f1, segundos = evaluar_en_dataset(nombre_dataset, dir_evaluacion)
        resultados[nombre_dataset] = (f1, segundos)
    print()
    print("--------------------------------------------")
    print("Resultado evaluación:")
    f1s = []
    for nombre_dataset in resultados:
        (f1, segundos) = resultados[nombre_dataset]
        f1s.append(f1)
        print("    F1-IOU en {}: {:.3f}   (tiempo={:.1f} segundos)".format(nombre_dataset, f1, segundos))
    f1_promedio = numpy.average(f1s)
    print("    ==> Promedio F1-IOU: {:.3f}".format(f1_promedio))
    nota, bonus = calcular_nota(f1_promedio)
    print()
    print("    ==> Nota tarea 2 = {:.1f}".format(nota))
    if bonus > 0:
        print("    ==> Bonus = {:.1f}".format(bonus))


# parametros de entrada
datasets = ["dataset_a", "dataset_b", "dataset_c"]
if len(sys.argv) > 1:
    datasets = sys.argv[1:]

evaluar_tarea2(datasets)
