# Pre Proyecto 2: Ant Colony System para TSP (Berlin52)

Este trabajo implementa el algoritmo Ant Colony System (ACS) para resolver el problema del vendedor viajero (TSP). La instancia que se usó es Berlin52, cuyo óptimo conocido es 7542 con distancias redondeadas y 7544.37 con distancias reales. Como el programa calcula distancias reales, el valor que hay que comparar es 7544.37.

La idea del trabajo era separar bien el algoritmo (`acs.py`) de las operaciones del problema (`operadores.py`), para poder reutilizar la estructura más adelante en el PFSP.

## Qué hay en la carpeta

```
acs.py            algoritmo principal y lectura de parámetros por consola
operadores.py     funciones que usa el algoritmo (leer datos, distancias, feromonas, etc.)
tests.py          pruebas de los operadores
experimento.py    corre los experimentos y guarda los resultados
graficar.py       hace los gráficos a partir del CSV de experimentos
datos/            berlin52.txt
resultados/       CSV con los resultados
graficos/         gráficos generados
```

## Cómo usarlo

Se necesita Python 3. Para `graficar.py` además hay que instalar pandas y matplotlib (`pip install pandas matplotlib`). Lo demás usa solo la biblioteca estándar.

Ejecutar el algoritmo:

```
python acs.py datos/berlin52.txt 50 200 1.0 2.0 0.9 12345 resultados/resultados.csv
```

Los argumentos van en este orden: archivo de la instancia, número de hormigas, iteraciones, alfa, beta, q0, semilla y archivo de salida. Con la misma semilla y los mismos parámetros siempre da el mismo resultado.

Correr las pruebas:

```
python tests.py
```

Correr los experimentos y hacer los gráficos (los experimentos demoran varios minutos):

```
python experimento.py
python graficar.py resultados/experimentos.csv
```

## Parámetros

- **alfa**: exponente de la feromona en la regla de selección de ciudad (se usó 1.0).
- **beta**: exponente de la heurística, que es 1/distancia (se usó 2.0).
- **q0**: probabilidad de elegir directamente la mejor ciudad en vez de sortear (se usó 0.9).
- **rho**: evaporación de la feromona, tanto en la actualización local como en la global. Está fija en 0.1 dentro del código y no se pasa por consola.

Una duda que quedó: la hoja de parámetros dice "alfa = 0.1" como factor de evaporación, pero el ejemplo del enunciado usa `1.0 2.0 0.9` para alfa, beta y q0. Para que ambas cosas coincidan, interpretamos alfa como el exponente de la feromona

Otros detalles de la implementación:

- La feromona inicial es tau0 = 1 / (n * costo de una ruta aleatoria), con n la cantidad de ciudades.
- La actualización local se aplica a las rutas de todas las hormigas: tau = (1 - rho) * tau + rho * tau0.
- La actualización global se aplica solo a la mejor ruta encontrada: tau = (1 - rho) * tau + rho * (1 / mejor costo).

## Archivo de salida

Por cada iteración se guarda una fila con: instancia, semilla, número de hormigas, iteraciones, alfa, beta, q0, rho, iteración, costo de esa iteración, mejor costo hasta el momento, tiempo transcurrido y la mejor ruta (ciudades numeradas desde 1). Si el archivo ya existe, se agregan filas al final sin repetir el encabezado.

## Pruebas

`tests.py` revisa cinco cosas: que la instancia se lea bien (52 ciudades), que las rutas generadas sean permutaciones válidas, que el costo de una ruta se calcule bien, que las feromonas se inicialicen y actualicen correctamente, y que la mejor solución nunca empeore

## Experimentos

Se partió de una configuración base (30 hormigas, 200 iteraciones, alfa 1.0, beta 2.0, q0 0.9) y se cambió un parámetro a la vez. Para comparar de forma justa, todas las configuraciones se corrieron con las mismas semillas (1 a 10). Los resultados completos están en `resultados/experimentos.csv` y los gráficos en `graficos/`.

Promedio del mejor costo con 10 semillas (el mejor valor posible es 7544.37):

| Configuración | Promedio | Tiempo promedio (s) |
|---|---|---|
| Base (30 hormigas, 200 iteraciones) | 7703 | 1.69 |
| 10 hormigas | 7826 | 0.47 |
| 50 hormigas | 7703 | 2.37 |
| 100 hormigas | 7678 | 4.71 |
| 100 iteraciones | 7730 | 0.71 |
| 500 iteraciones | 7694 | 3.54 |
| alfa 0.5 | 7669 | 1.52 |
| alfa 2.0 | 7926 | 1.50 |
| beta 3.5 | 7609 | 1.41 |
| beta 5.0 | 7624 | 1.43 |
| q0 0.5 | 7937 | 2.23 |
| q0 0.8 | 7694 | 1.63 |
| q0 0.95 | 7715 | 1.31 |


## Conclusiones

- Hormigas: con muy pocas (10) los resultados son peores. Desde 30 en adelante casi no mejora, pero el tiempo sube casi en proporción. Más hormigas no se justifican.
- Iteraciones: pasar de 200 a 500 mejora muy poco y el tiempo se duplica.
- Parámetros de ACS: lo que claramente empeora es un alfa alto (2.0) y un q0 bajo (0.5), que explora demasiado y además es más lento. Entre q0 0.8 y 0.95 no hay diferencia clara. Beta más alto (3.5 y 5.0) dio mejores promedios y menos dispersión, pero la diferencia no es tan grande frente al ruido, así que es una pista y no una conclusión tan sólida.
- Semillas: el resultado cambia bastante de una semilla a otra (desviación entre 90 y 260 según la configuración). Varias semillas llegan al óptimo 7544.37, pero el promedio queda unos 150 puntos más arriba. Por eso no basta con correrla una sola vez.
- Calidad y tiempo: hay una relación clara y es que gastar el doble de tiempo no mejora el doble.

Limitaciones: se usaron solo 10 semillas por configuración, así que las diferencias pequeñas (menos de unos 100 puntos) no se pueden distinguir del azar. Además solo se probó Berlin52 y se cambió un parámetro a la vez, sin probar combinaciones.

## Transferencia al PFSP

**1. ¿Qué partes de acs.py se podrían mantener?**
Casi todo. El ciclo (inicializar, construir soluciones, evaluar, actualizar feromonas, actualizar la mejor, repetir), la lectura de parámetros, la semilla, el historial con el tiempo y la escritura del CSV. Lo único que cambia es la lectura de la instancia y el cálculo de tau0.

**2. ¿Qué operaciones de operadores.py habría que cambiar?**
- Hay que reemplazar `leer_instancia` (ahora tendría que leer la matriz de tiempos de proceso), `calcular_matriz_distancias` (ya no existe), `calcular_heuristica` (habría que inventar una heurística para el PFSP) y `evaluar_ruta` (pasaría a calcular el makespan).
- Hay que modificar `seleccionar_ciudad` y `construir_solucion`, que ahora elegirían el siguiente trabajo y no tienen regreso al origen, y las actualizaciones de feromona, porque la permutación ya no es un ciclo y no existe el tramo del último al primero. También `calcular_tau0`, que usaría el makespan de una secuencia aleatoria.
- Se mantienen casi igual `inicializar_feromona`, `construir_soluciones`, `evaluar_soluciones`, `actualizar_mejor_solucion` y `guardar_resultados`.

**3. ¿Qué información nueva hay que representar?**
La solución sigue siendo una permutación, pero de trabajos, y el mismo orden vale para todas las máquinas. Lo nuevo está en la instancia: la matriz de tiempos de proceso de cada trabajo en cada máquina y el número de máquinas. La feromona se podría asociar a pares de trabajos consecutivos o a la posición de cada trabajo.

**4. ¿Qué cambiaría en la evaluación?**
Dejaría de sumar distancias entre ciudades consecutivas y pasaría a calcular el makespan, que es el momento en que el último trabajo termina en la última máquina. Se calcula trabajo por trabajo y máquina por máquina con C[i][j] = max(C[i-1][j], C[i][j-1]) + p[i][j], y no se cierra el ciclo.
