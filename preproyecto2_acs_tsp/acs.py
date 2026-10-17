import os
import random
import sys
import time
from operadores import (
    leer_instancia,
    calcular_matriz_distancias,
    calcular_heuristica,
    calcular_tau0,
    inicializar_feromona,
    construir_soluciones,
    evaluar_soluciones,
    actualizar_feromona_local,
    actualizar_mejor_solucion,
    actualizar_feromona_global,
    guardar_resultados
)


def acs(instancia, num_hormigas, num_iteraciones, alpha, beta, q0, rho):
    #alpha y beta: exponentes de la feromona y de la heuristica
    #q0: probabilidad de explotacion, rho: factor de evaporacion
    inicio = time.time()

    #leemos la instancia y precalculamos las matrices
    ciudades = leer_instancia(instancia)
    n = len(ciudades)
    dist = calcular_matriz_distancias(ciudades)
    eta = calcular_heuristica(dist)

    #inicializamos la feromona
    tau0 = calcular_tau0(dist)
    tau = inicializar_feromona(n, tau0)

    #mejor solucion global
    mejor_ruta = None
    mejor_costo = float('inf')
    historial = []

    for iteracion in range(1, num_iteraciones + 1):
        soluciones = construir_soluciones(tau, eta, n, num_hormigas, alpha, beta, q0)
        costos = evaluar_soluciones(soluciones, dist)

        for ruta in soluciones:
            actualizar_feromona_local(tau, ruta, tau0, rho)

        mejor_ruta, mejor_costo = actualizar_mejor_solucion(soluciones, costos, mejor_ruta, mejor_costo)
        actualizar_feromona_global(tau, mejor_ruta, 1.0 / mejor_costo, rho)

        historial.append({
            'iteracion': iteracion,
            'costo_iteracion': min(costos),
            'mejor_costo': mejor_costo,
            'mejor_ruta': mejor_ruta,
            'tiempo': time.time() - inicio
        })

    return mejor_ruta, mejor_costo, historial


if __name__ == "__main__":
    if len(sys.argv) != 9:
        print("Uso: python acs.py instancia num_hormigas num_iteraciones alpha beta q0 semilla archivo_salida")
        print("Ejemplo: python acs.py datos/berlin52.txt 50 200 1.0 2.0 0.9 12345 resultados/resultados.csv")
        sys.exit()

    instancia = sys.argv[1]
    archivo_salida = sys.argv[8]
    try:
        num_hormigas = int(sys.argv[2])
        num_iteraciones = int(sys.argv[3])
        alpha = float(sys.argv[4])
        beta = float(sys.argv[5])
        q0 = float(sys.argv[6])
        semilla = int(sys.argv[7])
    except ValueError:
        print("Error: hormigas, iteraciones y semilla deben ser enteros; alpha, beta y q0 deben ser numeros")
        sys.exit()

    if not os.path.exists(instancia):
        print(f"Error: no existe el archivo {instancia}")
        sys.exit()
    if num_hormigas < 1 or num_iteraciones < 1 or not 0 <= q0 <= 1:
        print("Error: hormigas e iteraciones deben ser al menos 1 y q0 debe estar entre 0 y 1")
        sys.exit()

    rho = 0.1  #factor de evaporacion (fijo)

    random.seed(semilla)
    mejor_ruta, mejor_costo, historial = acs(instancia, num_hormigas, num_iteraciones, alpha, beta, q0, rho)

    for h in historial:
        if h['iteracion'] % 10 == 0:
            print(f"Iteración {h['iteracion']}: mejor costo = {h['mejor_costo']:.2f}")
    print(f"Mejor costo encontrado: {mejor_costo:.2f}")
    print("Mejor ruta:", [ciudad + 1 for ciudad in mejor_ruta])
    print(f"Tiempo de ejecución: {historial[-1]['tiempo']:.2f} segundos")

    guardar_resultados(archivo_salida, instancia, semilla, num_hormigas, num_iteraciones, alpha, beta, q0, rho, historial)
