import os
import random
from acs import acs
from operadores import guardar_resultados

INSTANCIA = "datos/berlin52.txt"
ARCHIVO_SALIDA = "resultados/experimentos.csv"
RHO = 0.1

#configuraciones: (hormigas, iteraciones, alpha, beta, q0)
#la primera es la base; cada una de las otras cambia un solo parametro
BASE = (30, 200, 1.0, 2.0, 0.9)
CONFIGURACIONES = [
    BASE,
    (10, 200, 1.0, 2.0, 0.9),
    (50, 200, 1.0, 2.0, 0.9),
    (100, 200, 1.0, 2.0, 0.9),
    (30, 100, 1.0, 2.0, 0.9),
    (30, 500, 1.0, 2.0, 0.9),
    (30, 200, 0.5, 2.0, 0.9),
    (30, 200, 2.0, 2.0, 0.9),
    (30, 200, 1.0, 3.5, 0.9),
    (30, 200, 1.0, 5.0, 0.9),
    (30, 200, 1.0, 2.0, 0.5),
    (30, 200, 1.0, 2.0, 0.8),
    (30, 200, 1.0, 2.0, 0.95),
]

#la base se repite con 30 semillas, las demas con 10 (las mismas semillas para todas)
if os.path.exists(ARCHIVO_SALIDA):
    os.remove(ARCHIVO_SALIDA)

for config in CONFIGURACIONES:
    num_hormigas, num_iteraciones, alpha, beta, q0 = config
    if config == BASE:
        semillas = range(1, 31)
    else:
        semillas = range(1, 11)

    costos = []
    for semilla in semillas:
        random.seed(semilla)
        mejor_ruta, mejor_costo, historial = acs(INSTANCIA, num_hormigas, num_iteraciones, alpha, beta, q0, RHO)
        guardar_resultados(ARCHIVO_SALIDA, INSTANCIA, semilla, num_hormigas, num_iteraciones, alpha, beta, q0, RHO, historial)
        costos.append(mejor_costo)

    print(f"{config}: promedio {sum(costos) / len(costos):.2f}, mejor {min(costos):.2f}")
