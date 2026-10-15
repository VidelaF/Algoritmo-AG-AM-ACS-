# Pre Proyecto 2: Ant Colony System (ACS) para TSP

Implementación de Ant Colony System para el Problema del Vendedor Viajero (TSP), probada sobre la instancia **Berlin52** (óptimo conocido: 7542 con distancias enteras, 7544.37 con distancias reales). Es el paso previo al Proyecto 2 (AG, AM y ACS sobre PFSP).

## Estructura

```
acs.py           Algoritmo principal y línea de comandos (el ciclo se lee por etapas)
operadores.py    Biblioteca de operadores: lectura, distancias, heurística, feromona,
                 construcción de soluciones, selección de ciudad, evaluación, CSV
tests.py         Pruebas básicas de corrección
experimento.py   Corre la batería de experimentos y guarda resultados/experimentos.csv
graficar.py      Genera los gráficos a partir de un CSV de resultados
datos/           Instancias (berlin52.txt)
resultados/      CSV de salida
graficos/        Gráficos generados
```

## Requisitos

- Python 3.
- `acs.py`, `operadores.py`, `tests.py` y `experimento.py` usan solo la biblioteca estándar.
- `graficar.py` necesita `pandas` y `matplotlib` (`pip install pandas matplotlib`).

## Ejecución

```
python acs.py datos/berlin52.txt 50 200 1.0 2.0 0.9 12345 resultados/resultados.csv
```

Argumentos, en orden: archivo de instancia, número de hormigas, iteraciones, α, β, q0, semilla, archivo CSV de salida.

La misma semilla con los mismos parámetros entrega siempre el mismo resultado.

## Parámetros

| Parámetro | Significado | Valor del ejemplo |
|-----------|-------------|-------------------|
| α | exponente de la feromona en la regla de transición | 1.0 |
| β | exponente de la heurística (η = 1/d) | 2.0 |
| q0 | probabilidad de explotación (elegir el mejor candidato) | 0.9 |
| ρ | tasa de evaporación, local y global | 0.1 (fija en el código) |

Nota de interpretación: la hoja de parámetros del profesor indica "α = 0.1" como factor de evaporación, mientras que el ejemplo del enunciado usa `1.0 2.0 0.9` para α, β y q0. Para que ambos sean coherentes, aquí α es el exponente de la feromona (1.0 como en el ejemplo) y la evaporación se llama ρ y vale 0.1 fijo. Conviene confirmarlo con el profesor.

Otros valores del algoritmo:

- τ0 = 1 / (n · costo de una ruta aleatoria inicial).
- Actualización local sobre las rutas de todas las hormigas: τ = (1 − ρ)·τ + ρ·τ0.
- Actualización global sobre la mejor ruta encontrada: τ = (1 − ρ)·τ + ρ·(1 / mejor_costo).

## Salida (CSV)

Se agrega una fila por iteración (el encabezado se escribe solo si el archivo es nuevo):

`instancia, semilla, num_hormigas, num_iteraciones, alpha, beta, q0, rho, iteracion, costo_iteracion, mejor_costo, tiempo, mejor_ruta`

`mejor_ruta` usa ciudades numeradas desde 1. Si abres el CSV en Excel con configuración regional chilena, los decimales con punto se pueden leer mal; el archivo está bien, conviene leerlo con pandas.

## Pruebas

```
python tests.py
```

Verifica: lectura de la instancia, que las soluciones sean permutaciones válidas, el cálculo del costo (rectángulo de costo conocido y tour óptimo de Berlin52 ≈ 7544.37), las matrices de feromona y la actualización de la mejor solución.

## Experimentos y gráficos

```
python experimento.py
python graficar.py resultados/experimentos.csv
```

`experimento.py` parte de una configuración base (30 hormigas, 200 iteraciones, α=1.0, β=2.0, q0=0.9; 30 semillas) y cambia un parámetro a la vez (hormigas, iteraciones, α, β, q0; 10 semillas cada una). Toma varios minutos. `graficar.py` imprime una tabla resumen y guarda en `graficos/`: `convergencia.pdf`, `semillas.pdf`, `parametros.pdf` y `tiempo_vs_costo.pdf`.

## Transferencia a PFSP

1. **¿Qué partes de acs.py podrían mantenerse?** Casi todo. El ciclo por etapas (inicializar, construir soluciones, evaluar, actualizar feromonas, actualizar mejor solución, repetir), la lectura de parámetros por línea de comandos, la semilla, el registro del historial y del tiempo, y la escritura del CSV. Solo cambia la llamada que lee la instancia y calcula τ0.
2. **¿Qué operaciones de operadores.py deberían modificarse o reemplazarse?**
   - Reemplazar: `leer_instancia` (ahora lee la matriz de tiempos de proceso, trabajos por máquinas), `calcular_matriz_distancias` (ya no existe), `calcular_heuristica` (hay que definir una η propia del PFSP) y `evaluar_ruta` (pasa a calcular el makespan).
   - Modificar: `seleccionar_ciudad` y `construir_solucion` (eligen el siguiente trabajo no programado; no hay regreso al origen), las actualizaciones de feromona (la permutación ya no es un ciclo, así que no existe el tramo último → primero) y `calcular_tau0` (usa el makespan de una secuencia aleatoria).
   - Se mantienen: `inicializar_feromona`, `construir_soluciones`, `evaluar_soluciones`, `actualizar_mejor_solucion` y `guardar_resultados`.
3. **¿Qué nueva información necesitaría representar una solución?** La solución sigue siendo una permutación, ahora de trabajos, y el mismo orden vale para todas las máquinas. Lo nuevo está en la instancia: la matriz de tiempos de proceso p[trabajo][máquina] y el número de máquinas. La feromona puede indexarse por pares de trabajos consecutivos o por (trabajo, posición).
4. **¿Qué cambiaría en la función que evalúa una solución?** Se deja de sumar distancias entre ciudades consecutivas. Se calcula el makespan: el instante en que el último trabajo termina en la última máquina, con C[i][j] = max(C[i-1][j], C[i][j-1]) + p[i][j]. Es un cálculo por trabajo y por máquina, no por pares de elementos, y no se cierra el ciclo.
