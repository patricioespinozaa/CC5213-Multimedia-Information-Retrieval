# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
## Fecha: 08 de mayo de 2025
## Profesor: Juan Manuel Barrios

# Tarea 2

Para la tarea 2 debe crear tres programas:

  * `tarea2-parte1.py`
     Recibe dos parámetros por la línea de comandos:
	   1. Una carpeta con audios. Procesar todos los archivos .m4a en esa carpeta.
       2. Una carpeta donde guardar descriptores calculados.

  * `tarea2-parte2.py`
     Recibe tres parámetros por la línea de comandos:
	   1. La carpeta con descriptores de Q (radio).
	   2. La carpeta con descriptores de R (canciones).
	   3. Una carpeta donde guardar el resultado de la comparación de los descriptores de Q y R.

  * `tarea2-parte3.py`
     Recibe tres parámetros por la línea de comandos:
	   1. La carpeta con el resultado de la comparación de Q y R.
	   2. El archivo a crear con el resultado de la detección de canciones.

El archivo de salida debe tener un formato de 4 columnas separadas por tabulador. En cada
fila debe tener un archivo de Q (radio), un tiempo de inicio en segundos de Q, un archivo
de R (canción) y el valor de confianza de que detección sea correcta.

Por ejemplo, un posible archivo de resultados sería este:

```
radio-disney-ar-1.m4a	105.63	Bee Gees - Stayin' alive (10).m4a	21.0
radio-disney-ar-1.m4a	352.48	Polima Westcoast - Ultra Solo (7).m4a	32.0
radio-disney-ar-1.m4a	1159.72	Mago de Oz - La posada de los muertos (17).m4a	167.0
[......]
radio-disney-mx-1.m4a	817.37	Pink Floyd - Money (15).m4a	56.0
radio-disney-mx-1.m4a	3563.16	31 Minutos - Lala (30).m4a	37.0
```

Para probar su tarea debe usar el programa de evaluación:

  `python evaluarTarea2.py`

Este programa llamará su tarea con todos los datasets y mostrará el resultado obtenido y la nota.

Si quiere probar la tarea con un solo dataset, puede ejecutar:

  `python evaluarTarea2.py dataset_a`

Su tarea no puede demorar más de 15 minutos en evaluar cada dataset.
