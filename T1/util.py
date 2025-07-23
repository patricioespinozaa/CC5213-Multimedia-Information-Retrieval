# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# Fecha: 27 de marzo de 2025
# Alumno: Patricio Espinoza A.

# Este archivo es usado por tarea1-parte1.py y tarea1-parte2.py
# Permite tener funciones compartidas entre ambos programas

# Se puede modificar este archivo para agregar más funciones (si es necesario)
# Incluir este archivo en la entrega de la tarea si fue modificado.

import os
import pickle

# Parte 1
import numpy
import cv2
import time
import pandas

# Retorna todos los archivos que terminan con el parametro extension
# ejemplo: listar_archivos_con_extension(dir, ".jpg") retorna los archivos en dir cuyo nombre termina con .jpg
def listar_archivos_con_extension(carpeta, extension):
    lista = []
    for archivo in os.listdir(carpeta):
        # los que terminan con la extension se agregan a la lista de nombres
        if archivo.endswith(extension):
            lista.append(archivo)
    lista.sort()
    return lista


# escribe el objeto de python en un archivo binario
def guardar_objeto(objeto, carpeta, nombre_archivo):
    if carpeta == "" or carpeta == "." or carpeta is None:
        archivo = nombre_archivo
    else:
        archivo = os.path.join(carpeta, nombre_archivo)
        # asegura que la carpeta exista
        os.makedirs(carpeta, exist_ok=True)
    # usa la librería pickle para escribir el objeto en un archivo binario
    # ver https://docs.python.org/3/library/pickle.html
    with open(archivo, 'wb') as handle:
        pickle.dump(objeto, handle, protocol=pickle.HIGHEST_PROTOCOL)


# reconstruye el objeto de python que está guardado en un archivo
def leer_objeto(carpeta, nombre_archivo):
    if carpeta == "" or carpeta == "." or carpeta is None:
        archivo = nombre_archivo
    else:
        archivo = os.path.join(carpeta, nombre_archivo)
    with open(archivo, 'rb') as handle:
        objeto = pickle.load(handle)
    return objeto


# Recibe una lista de listas y lo escribe en un archivo separado por \t
# Por ejemplo:
# listas = [
#           ["dato1a", "dato1b", "dato1c"],
#           ["dato2a", "dato2b", "dato2c"],
#           ["dato3a", "dato3b", "dato3c"] ]
# al llamar:
#   escribir_lista_de_columnas_en_archivo(listas, "archivo.txt")
# escribe un archivo de texto con:
# dato1a  dato1b   dato1c
# dato2a  dato2b   dato3c
# dato2a  dato2b   dato3c
def escribir_lista_de_columnas_en_archivo(lista_con_columnas, archivo_texto_salida):
    with open(archivo_texto_salida, 'w') as handle:
        for columnas in lista_con_columnas:
            textos = []
            for col in columnas:
                textos.append(str(col))
            texto = "\t".join(textos)
            print(texto, file=handle)


# Parte 1
# (0) Vector de intensidades
def vector_de_intensidades(nombre_imagen, imagenes_dir):
    archivo_imagen = imagenes_dir + "/" + nombre_imagen
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise Exception("no puedo abrir: " + archivo_imagen)
    # se puede cambiar a otra interpolacion, como cv2.INTER_CUBIC
    imagen_reducida = cv2.resize(imagen, (5, 5), interpolation=cv2.INTER_AREA)
    # flatten convierte una matriz de nxm en un array de largo nxm
    descriptor_imagen = imagen_reducida.flatten()
    return descriptor_imagen

# (1) vector de colores
def vector_de_colores(imagen, imagen_mostrar):
    size_x = 3
    size_y = 3
    imagen_reducida = cv2.resize(imagen, (size_x, size_y), interpolation=cv2.INTER_AREA)
    # flatten convierte la matriz de w x h x 3 en un array de largo w x h x 3
    descriptor_imagen = imagen_reducida.flatten()
    # mostrar el descriptor
    if imagen_mostrar is not None:
        cv2.resize(imagen_reducida, (imagen.shape[1],imagen.shape[0]), dst=imagen_mostrar, interpolation=cv2.INTER_NEAREST)
    return descriptor_imagen

# (2) Histograma por zona y por canales
def calcular_limites(maximo_no_incluido, cantidad):
    list = [round(maximo_no_incluido * i / cantidad) for i in range(cantidad)]
    list.append(maximo_no_incluido)
    return list

def descriptor_por_zona_generico(imagen, num_zonas_x, num_zonas_y, funcion_descriptor_zona, imagen_mostrar):
    descriptor = []
    limites_y = calcular_limites(imagen.shape[0], num_zonas_y)
    limites_x = calcular_limites(imagen.shape[1], num_zonas_x)
    for j in range(num_zonas_y):
        desde_y = limites_y[j]
        hasta_y = limites_y[j + 1]
        for i in range(num_zonas_x):
            desde_x = limites_x[i]
            hasta_x = limites_x[i + 1]
            # recortar la zona de la imagen a la que se calcula el descriptor
            zona = imagen[desde_y:hasta_y, desde_x:hasta_x]
            # recortar la zona imagen de visualizacion para mostrar el resultado del descriptor
            zona_mostrar = None
            if imagen_mostrar is not None:
                cv2.rectangle(imagen_mostrar, (desde_x,desde_y), (hasta_x-1,hasta_y-1), (0,0,0), 3)
                zona_mostrar = imagen_mostrar[desde_y:hasta_y, desde_x:hasta_x]
            # descriptor de la zona
            descriptor_zona = funcion_descriptor_zona(zona, zona_mostrar)
            # agregar descriptor de la zona al descriptor global
            descriptor.extend(descriptor_zona)
    # como visualizacion marco las zonas en la imagen original para entender qué zona representa cada descriptor
    return descriptor

def color_de_cada_bin_3x1d(cantidad_bins):
    limites_gris = calcular_limites(256, cantidad_bins)
    grises = [round((limites_gris[i] + limites_gris[i + 1] - 1) / 2) for i in range(cantidad_bins)]
    colores_r = [(0, 0, gris) for gris in grises]
    colores_g = [(0, gris, 0) for gris in grises]
    colores_b = [(gris, 0, 0) for gris in grises]
    return (colores_r, colores_g, colores_b)
   
def calcular_histograma_1d(imagen_gris, cantidad_bins):
    hist = cv2.calcHist(images=[imagen_gris], channels=[0], mask=None, histSize=[cantidad_bins], ranges=(0, 256))
    array = hist.flatten()
    return array / numpy.sum(array)

def histograma_por_canal_3x1d(imagen_zona, imagen_zona_mostrar):
    cantidad_bins_3x1d = 64

    # separa la imagen en imagenes independiente por canal
    canales_bgr = cv2.split(imagen_zona)
    # un histograma (array de numeros) para cada canal
    histograma_b = calcular_histograma_1d(canales_bgr[0], cantidad_bins_3x1d)
    histograma_g = calcular_histograma_1d(canales_bgr[1], cantidad_bins_3x1d)
    histograma_r = calcular_histograma_1d(canales_bgr[2], cantidad_bins_3x1d)
    # el descriptor es unir los tres arrays
    descriptor_zona = []
    descriptor_zona.extend(histograma_r)
    descriptor_zona.extend(histograma_g)
    descriptor_zona.extend(histograma_b)
    return descriptor_zona

def histograma_por_canal_por_zonas(imagen, imagen_mostrar):
    zonas_x_3x1d = 3
    zonas_y_3x1d = 3
    descriptor_imagen = descriptor_por_zona_generico(imagen, zonas_x_3x1d, zonas_y_3x1d, histograma_por_canal_3x1d, imagen_mostrar)
    return descriptor_imagen

# (3) Histograma 3D por zonas
def color_de_cada_bin_3d(cantidad_bins):
    limites_dim = calcular_limites(256, cantidad_bins)
    colores_bins = []
    for i in range(cantidad_bins):
        val1 = round((limites_dim[i] + limites_dim[i + 1] - 1) / 2)
        for j in range(cantidad_bins):
            val2 = round((limites_dim[j] + limites_dim[j + 1] - 1) / 2)
            for k in range(cantidad_bins):
                val3 = round((limites_dim[k] + limites_dim[k + 1] - 1) / 2)
                colores_bins.append((val1, val2, val3))
    return colores_bins
                    
def histograma_3d(imagen_zona, imagen_zona_mostrar):
    cantidad_bins_3d = 3
    hist = cv2.calcHist(images=[imagen_zona], channels=[0, 1, 2], mask=None, histSize=[cantidad_bins_3d,cantidad_bins_3d,cantidad_bins_3d], ranges=[0, 256, 0, 256, 0, 256])
    descriptor_zona = hist.flatten()
    descriptor_zona = descriptor_zona / numpy.sum(descriptor_zona)
    return descriptor_zona


def histograma_3d_por_zonas(imagen, imagen_mostrar):
    zonas_x_3d = 3
    zonas_y_3d = 3
    descriptor_imagen = descriptor_por_zona_generico(imagen, zonas_x_3d, zonas_y_3d, histograma_3d, imagen_mostrar)
    return descriptor_imagen

# (4) vector de intensidades con ecualizacion de histograma
def vector_de_intensidades_equalizeHist(nombre_imagen, imagenes_dir):
    archivo_imagen = imagenes_dir + "/" + nombre_imagen
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise Exception("no puedo abrir: " + archivo_imagen)
    # ecualizacion
    imagen = cv2.equalizeHist(imagen)
    # se puede cambiar a otra interpolacion, como cv2.INTER_CUBIC
    imagen_reducida = cv2.resize(imagen, (5, 5), interpolation=cv2.INTER_AREA)
    # flatten convierte una matriz de nxm en un array de largo nxm
    descriptor_imagen = imagen_reducida.flatten()
    return descriptor_imagen

# (5) Descriptor OMD
def vector_de_intensidades_omd(nombre_imagen, imagenes_dir):
    archivo_imagen = imagenes_dir + "/" + nombre_imagen
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise Exception("no puedo abrir: " + archivo_imagen)
    # se puede cambiar a otra interpolacion, como cv2.INTER_CUBIC
    imagen_reducida = cv2.resize(imagen, (5, 5), interpolation=cv2.INTER_AREA)
    # flatten convierte una matriz de nxm en un array de largo nxm
    descriptor_imagen = imagen_reducida.flatten()
    # la posicion si se ordenan
    posiciones = numpy.argsort(descriptor_imagen)
    # reemplazar el valor gris por su  posicion
    for i in range(len(posiciones)):
        descriptor_imagen[posiciones[i]] = i
    return descriptor_imagen

# (6) Histogramas por zona
def histograma_por_zona(imagen, imagen_hists):
    # divisiones
    num_zonas_x = 4
    num_zonas_y = 4
    num_bins_por_zona = 16
    # procesar cada zona
    descriptor = []
    for j in range(num_zonas_y):
        desde_y = int(imagen.shape[0] / num_zonas_y * j)
        hasta_y = int(imagen.shape[0] / num_zonas_y * (j + 1))
        for i in range(num_zonas_x):
            desde_x = int(imagen.shape[1] / num_zonas_x * i)
            hasta_x = int(imagen.shape[1] / num_zonas_x * (i + 1))
            # recortar zona de la imagen
            zona = imagen[desde_y: hasta_y, desde_x: hasta_x]
            # histograma de los pixeles de la zona
            histograma, limites = numpy.histogram(zona, bins=num_bins_por_zona, range=(0, 255))
            # normalizar histograma (bins suman 1)
            histograma = histograma / numpy.sum(histograma)
            # agregar descriptor de la zona al descriptor global
            descriptor.extend(histograma)
    return descriptor


def histogramas_por_zonas(nombre_imagen, imagenes_dir):
    archivo_imagen = imagenes_dir + "/" + nombre_imagen
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise Exception("no puedo abrir: " + archivo_imagen)
    # ecualizacion
    imagen = cv2.equalizeHist(imagen)
    # imagen donde se dibujan los histogramas
    mostrar_imagenes = False
    imagen_hists = None
    if mostrar_imagenes:
        imagen_hists = numpy.full((imagen.shape[0], imagen.shape[1], 3), (200, 255, 200), dtype=numpy.uint8)
    descriptor = histograma_por_zona(imagen, imagen_hists)
    return descriptor

# (7) Descriptor de bordes por zona (HOG)
import math

def angulos_en_zona(angulos, mascara):
    # calcular angulos de la zona
    angulos_zona = []
    for row in range(mascara.shape[0]):
        for col in range(mascara.shape[1]):
            if not mascara[row][col]:
                continue
            angulo = round(math.degrees(angulos[row][col]))
            # dejar angulos en el rango -90 a 90
            if angulo < -180 or angulo > 180:
                raise Exception("angulo invalido {}, verificar si funciona la mascara".format(angulo))
            elif angulo <= -90:
                angulo += 180
            elif angulo > 90:
                angulo -= 180
            angulos_zona.append(angulo)
    return angulos_zona


def bordes_por_zona(angulos, mascara, imagen_hists):
    # divisiones
    num_zonas_x = 4
    num_zonas_y = 4
    num_bins_por_zona = 10
    # procesar cada zona
    descriptor = []
    for j in range(num_zonas_y):
        desde_y = int(mascara.shape[0] / num_zonas_y * j)
        hasta_y = int(mascara.shape[0] / num_zonas_y * (j + 1))
        for i in range(num_zonas_x):
            desde_x = int(mascara.shape[1] / num_zonas_x * i)
            hasta_x = int(mascara.shape[1] / num_zonas_x * (i + 1))
            # calcular angulos de la zona
            angulos_zona = angulos_en_zona(angulos[desde_y: hasta_y, desde_x: hasta_x],
                                      mascara[desde_y: hasta_y, desde_x: hasta_x])
            # histograma de los angulos de la zona
            histograma, limites = numpy.histogram(angulos_zona, bins=num_bins_por_zona, range=(-90, 90))
            # normalizar histograma (bins suman 1)
            if numpy.sum(histograma) != 0:
                histograma = histograma / numpy.sum(histograma)
            # agregar descriptor de la zona al descriptor global
            descriptor.extend(histograma)
    return descriptor


def histograma_bordes_por_zona(nombre_imagen, imagenes_dir):
    archivo_imagen = imagenes_dir + "/" + nombre_imagen
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise Exception("no puedo abrir: " + archivo_imagen)
    # calcular filtro de sobel (usa cv2.GaussianBlur para borrar ruido)
    imagen2 = cv2.GaussianBlur(imagen, (5, 5), 0, 0)
    sobelX = cv2.Sobel(imagen2, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
    sobelY = cv2.Sobel(imagen2, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=3)
    # calcula la magnitud del gradiente en cada pixel de la imagen
    magnitud = numpy.sqrt(numpy.square(sobelX) + numpy.square(sobelY))
    # selecciona los pixeles donde la magnitud del gradiente supera un valor umbral
    threshold_magnitud_gradiente = 100
    th, imagen_bordes = cv2.threshold(magnitud, threshold_magnitud_gradiente, 255, cv2.THRESH_BINARY)
    # definir una mascara donde estan los pixeles de borde
    mascara = imagen_bordes == 255
    # para los pixeles de la mascara calcular el angulo del gradiente
    angulos = numpy.arctan2(sobelY, sobelX, where=mascara)
    # imagen donde se dibujan los histogramas
    mostrar_imagenes = False
    imagen_hists = None
    if mostrar_imagenes:
        imagen_hists = numpy.full((imagen.shape[0], imagen.shape[1], 3), (200, 255, 200), dtype=numpy.uint8)
    # calcular descriptor (histograms de angulos por zonas)
    descriptor = bordes_por_zona(angulos, mascara, imagen_hists)
    return descriptor

# Calculadora de varios descriptores de una imagen
def concat_features(nombre_imagen, imagenes_dir):
    imagen_mostrar = None
    imagen_path = os.path.join(imagenes_dir, nombre_imagen)
    imagen = cv2.imread(imagen_path, cv2.IMREAD_COLOR)
    # (0) vector de intensidades
    #descriptor0 = vector_de_intensidades(nombre_imagen, imagenes_dir)
    # (1) vector de colores
    #descriptor1 = vector_de_colores(imagen, imagen_mostrar)
    # (2) Histograma por zona y por canales
    descriptor2 = histograma_por_canal_por_zonas(imagen, imagen_mostrar)
    # (3) Histograma 3D por zonas
    #descriptor3 = histograma_3d_por_zonas(imagen, imagen_mostrar)
    # (4) vector de intensidades con ecualizacion de histograma
    #descriptor4 = vector_de_intensidades_equalizeHist(nombre_imagen, imagenes_dir)
    # (5) descriptor OMD
    #descriptor5 = vector_de_intensidades_omd(nombre_imagen, imagenes_dir)
    # (6) Histogramas por zona
    #descriptor6 = histogramas_por_zonas(nombre_imagen, imagenes_dir)
    # (7) Histogramas de bordes por zona
    #descriptor7 = histograma_bordes_por_zona(nombre_imagen, imagenes_dir)

    return descriptor2