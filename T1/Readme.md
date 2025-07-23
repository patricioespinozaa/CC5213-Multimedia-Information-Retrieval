# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
## Fecha: 27 de marzo de 2025
## Profesor: Juan Manuel Barrios

# Tarea 1

Para la tarea 1 debe crear dos programas:

* `tarea1-parte1.py`
  Fase offline de la tarea. Recibe dos parámetros por la línea de comandos:
    1. La carpeta de entrada con imágenes originales R.
    2. Una carpeta de salida donde guardar los descriptores de R.

* `tarea1-parte2.py`
  Fase online de la tarea. Recibe tres parámetros por la línea de comandos:
    1. La carpeta de entrada con imágenes de consulta Q.
    2. La carpeta donde están guardados los descriptores de R (creado por tarea1-parte1.py).
    3. Un nombre de archivo de salida para guardar el resultado de buscar Q en R.

El archivo de salida debe tener un formato de 3 columnas separadas por un tabulador. En cada
fila debe tener el nombre de una imagen de Q, el nombre de la imagen de R más cercana y la
distancia entre ambas imágenes.

Por ejemplo, un posible archivo de resultados sería este:

```
q0001.jpg r0432.jpg 610.2
q0002.jpg 0231.jpg  126.1
[......]
q4346.jpg r0156.jpg 11.5
q4347.jpg r1849.jpg 119.5
```

Para probar su tarea debe usar el programa de evaluación:

`python evaluarTarea1.py`

Este programa llamará su tarea con todos los datasets y mostrará el resultado obtenido y la nota.

Si quiere probar la tarea con un solo dataset, puede ejecutar:

`python evaluarTarea1.py dataset_a`

Su tarea no puede demorar más de 15 minutos en cada dataset.
