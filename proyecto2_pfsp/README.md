# Proyecto 2: AG, AM y ACS para el PFSP

Este proyecto resuelve el Permutation Flow Shop Scheduling Problem con tres algoritmos: un Algoritmo Genético, un Algoritmo Memético y un Ant Colony System. Los tres usan las mismas instancias de Taillard y la misma función para calcular el makespan, así que se pueden comparar directamente con el RPD.

## Archivos

```
main.py           corre los tres algoritmos en las tres instancias con varias semillas
ag.py             Algoritmo Genético
am.py             Algoritmo Memético
acs.py            Ant Colony System
operadores.py     funciones que usan los tres algoritmos
graficar.py       tabla resumen y gráficos a partir del CSV
datos/            instancias de Taillard y best_known.csv
resultados/       CSV de salida
graficos/         gráficos de convergencia, RPD y tiempo
```

## Cómo usarlo

Se necesita Python 3. Solo `graficar.py` usa librerías externas, pandas y matplotlib.

Cada algoritmo se ejecuta con su propio script. Los parámetros van en un orden fijo.

```
python ag.py datos/ta001.txt 12345 50 200 0.8 0.1 resultados/res_ag.csv
python am.py datos/ta001.txt 12345 50 200 0.8 0.1 10 resultados/res_am.csv
python acs.py datos/ta001.txt 12345 50 200 0.1 2.0 0.9 resultados/res_acs.csv
```

Los parámetros son:

- `ag.py`: instancia, semilla, población, iteraciones, pc, pm, archivo de salida.
- `am.py`: lo mismo que el AG más la frecuencia de búsqueda local, antes del archivo de salida.
- `acs.py`: instancia, semilla, hormigas, iteraciones, evaporación, beta, q0, archivo de salida.

Para comparar los tres algoritmos con varias semillas:

```
python main.py 10 resultados/comparacion.csv
python graficar.py resultados/comparacion.csv
```

`main.py` usa semillas de 1 a la cantidad pedida y no sobrescribe archivos, si el archivo de salida ya existe avisa y termina. Con 10 semillas demora cerca de 50 minutos, casi todo en el memético sobre ta071. Para probar rápido sirve `python main.py 1 resultados/prueba.csv`, que demora unos 6 minutos.

Con la misma semilla y los mismos parámetros se obtiene siempre el mismo makespan y la misma secuencia.

## Instancias

Se usaron tres instancias de Taillard, una por cada tamaño pedido: ta001 de 20 trabajos y 5 máquinas, ta041 de 50 y 10, y ta071 de 100 y 10. El mejor valor conocido de cada una sale de `datos/best_known.csv` y se usa para calcular el RPD. Si una instancia no está en ese archivo, el programa avisa y no calcula el RPD.

## Algoritmos

**AG.** Cada individuo es una permutación de los trabajos. La selección es por torneo de tamaño 2, el cruce es Order Crossover y la mutación es por intercambio de dos posiciones. El reemplazo es generacional con elitismo, el mejor individuo anterior reemplaza al peor de la población nueva si lo supera.

**AM.** Es el mismo AG, pero cada cierto número de iteraciones se aplica una búsqueda local por inserción a los 3 mejores individuos distintos de la población. Se piden distintos porque por el elitismo el mejor suele estar repetido, y buscar dos veces sobre la misma secuencia no sirve. La cantidad es la constante `MEJORES` de `am.py`. La búsqueda local mueve un trabajo a otra posición y acepta la primera mejora, y sigue hasta que ningún movimiento mejora. El parámetro de frecuencia dice cada cuántas iteraciones se aplica.

**ACS.** La feromona tau[i][j] indica qué tan bueno es programar el trabajo j justo después del trabajo i. La visibilidad usa la regla SPT, eta es 1 sobre el tiempo total de procesamiento del trabajo. Cada hormiga parte de un trabajo al azar y elige el siguiente con la regla pseudo-aleatoria proporcional. Con probabilidad q0 elige el mejor candidato y si no sortea con probabilidad proporcional a tau por eta elevado a beta. La evaporación local se aplica en cada arista que la hormiga recorre y la global solo sobre la mejor secuencia encontrada. La feromona inicial es 1 sobre n por el makespan de una secuencia aleatoria.

Sobre el ACS. El enunciado llama alfa a la evaporación, así que en el programa es la evaporación y la feromona no lleva exponente. Pero alfa aparece con dos valores, 0.1 en la hoja de parámetros del curso y 1.0 en el ejemplo del enunciado, y nunca se aclaró con el profesor cuál era el correcto. Debido a esa notación confusa se decidió usar 0.1, porque es el valor estándar del ACS y porque mejora los resultados. Como elegir el valor mirando los resultados es ajustar sobre las mismas instancias, el ACS también se corrió con 1.0 y esos resultados están en `resultados/acs_evaporacion_1.0.csv`. Con 1.0 el RPD promedio del ACS fue 6.33, 18.08 y 11.53 en ta001, ta041 y ta071, y sigue siendo el último de los tres. El programa acepta cualquiera de los dos valores.

## Salida

Cada ejecución agrega al CSV una fila por iteración con estas columnas: algoritmo, instancia, semilla, parametros, iteracion, mejor_cmax, rpd, tiempo_cpu y secuencia_final. La secuencia final, con los trabajos numerados desde 1, solo aparece en la última fila de cada corrida. El tiempo es tiempo de CPU acumulado en segundos.

## Experimento

Se corrieron los tres algoritmos con 10 semillas en cada instancia, con estos parámetros: población de 50, 200 iteraciones, pc 0.8, pm 0.1 y búsqueda local cada 10 iteraciones para el AG y el AM, y 50 hormigas, evaporación 0.1, beta 2.0 y q0 0.9 para el ACS. Los parámetros no se ajustaron para cada algoritmo.

Promedio de 10 semillas, con el RPD en porcentaje y el tiempo de CPU en segundos. Los tiempos se midieron en un AMD Ryzen 5 5600X con Python 3.12 en Windows:

| Instancia | Algoritmo | Cmax promedio | Mejor Cmax | RPD promedio | Desv. RPD | Tiempo |
|---|---|---|---|---|---|---|
| ta001 | AG | 1306.0 | 1294 | 2.19 | 0.97 | 0.17 |
| ta001 | AM | 1287.9 | 1278 | 0.77 | 0.76 | 0.53 |
| ta001 | ACS | 1319.4 | 1302 | 3.24 | 1.15 | 0.33 |
| ta041 | AG | 3235.8 | 3169 | 8.18 | 1.25 | 0.67 |
| ta041 | AM | 3074.2 | 3049 | 2.78 | 0.94 | 36.27 |
| ta041 | ACS | 3456.3 | 3411 | 15.56 | 0.82 | 1.52 |
| ta071 | AG | 6167.9 | 6058 | 6.90 | 1.05 | 1.35 |
| ta071 | AM | 5801.6 | 5784 | 0.55 | 0.23 | 364.72 |
| ta071 | ACS | 6341.8 | 6254 | 9.91 | 0.82 | 4.40 |

La tabla completa está en `resultados/resumen.csv` y los gráficos en `graficos/`.

Lo que se ve:

- El AM obtiene el mejor RPD en las tres instancias, pero es lejos el más lento. Con la búsqueda local sobre 3 individuos, en ta041 tarda unas 50 veces más que el AG y en ta071 unas 270 veces, 365 s contra 1.4 s.
- En las curvas de convergencia el AM baja casi todo de golpe en la iteración 10, que es la primera búsqueda local, y después mejora muy poco. La explotación hace casi todo el trabajo y el cruce y la mutación aportan poco después de eso.
- El AG mejora más lento pero sigue bajando hasta el final, así que con más iteraciones probablemente seguiría mejorando.
- El ACS es el peor en las tres instancias. Su heurística SPT es débil y no tiene búsqueda local. En ta041 y ta071 casi no mejora después de las primeras 50 iteraciones, es decir que explora poco una vez que la feromona se concentra.
- Solo en ta001 hay corridas que llegan al mejor conocido, 4 de las 10 del AM y ninguna del AG ni del ACS. En ninguna corrida el RPD fue negativo.

Los archivos `acs_evaporacion_1.0.csv` y `acs_beta0.csv` se generan corriendo `acs.py` en las 3 instancias con las semillas de 1 a 10, cambiando solo la evaporación a 1.0 o beta a 0.0. El resto de los parámetros es el mismo del experimento. Si el archivo de salida ya existe, `acs.py` agrega filas al final, así que hay que borrarlo antes de repetir.

## Limitaciones

Los parámetros son los del enunciado y no se hizo una búsqueda de mejores valores, así que los resultados de cada algoritmo podrían mejorar. La comparación de tiempo depende del computador donde se corrió. También se corrió con beta 0, sin heurística, y esos resultados están en `resultados/acs_beta0.csv`. El RPD promedio fue 3.54, 13.59 y 10.19, contra 3.24, 15.56 y 9.91 con beta 2. La heurística SPT aporta poco o estorba, pero sin ella el ACS sigue siendo peor que el AG, así que el mal desempeño parece venir del diseño del ACS y no de ese parámetro. No se aplicó ningún test estadístico. Las diferencias entre algoritmos son grandes frente a la desviación, salvo en ta001, donde son más ajustadas.
