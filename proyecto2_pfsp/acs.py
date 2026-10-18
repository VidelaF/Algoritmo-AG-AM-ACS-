#Ant Colony System para PFSP. La visibilidad usa la regla SPT.
import random
import sys
import time

from operadores import (
    leer_parametros, validar_instancia, salir_con_error, leer_instancia,
    calcular_heuristica, calcular_tau0, inicializar_feromona, construir_secuencia,
    evaluar_secuencias, actualizar_feromona_global, reportar_y_guardar,
)

USO = ("Uso: python acs.py instancia semilla hormigas iteraciones evaporacion beta q0 archivo_salida\n"
       "Ejemplo: python acs.py datos/ta001.txt 12345 50 200 0.1 2.0 0.9 resultados/res_acs.csv")


def ejecutar_acs(tiempos, semilla, num_hormigas, iteraciones, evaporacion, beta, q0):
    #Devuelve la mejor secuencia, su cmax y el historial
    random.seed(semilla)
    inicio = time.process_time()

    #inicializar
    n_trabajos = len(tiempos[0])
    eta_beta = calcular_heuristica(tiempos, beta)
    tau0 = calcular_tau0(tiempos)
    tau = inicializar_feromona(n_trabajos, tau0)
    mejor_secuencia = None
    mejor_cmax = float("inf")
    historial = []

    for iteracion in range(1, iteraciones + 1):
        #construir soluciones, la evaporación local ocurre mientras avanzan
        secuencias = [construir_secuencia(tau, eta_beta, tau0, q0, evaporacion)
                      for _ in range(num_hormigas)]

        #evaluar soluciones
        costos = evaluar_secuencias(secuencias, tiempos)

        #actualizar mejor solución
        indice = costos.index(min(costos))
        if costos[indice] < mejor_cmax:
            mejor_secuencia = secuencias[indice]
            mejor_cmax = costos[indice]

        #actualizar feromonas con la mejor solución
        actualizar_feromona_global(tau, mejor_secuencia, mejor_cmax, evaporacion)

        historial.append((iteracion, mejor_cmax, time.process_time() - inicio))

    return mejor_secuencia, mejor_cmax, historial


def main():
    (ruta, semilla, num_hormigas, iteraciones, evaporacion, beta, q0, salida) = leer_parametros(
        sys.argv[1:], [str, int, int, int, float, float, float, str], USO)

    validar_instancia(ruta)
    if num_hormigas < 1:
        salir_con_error("debe haber al menos 1 hormiga")
    if iteraciones < 1:
        salir_con_error("las iteraciones deben ser al menos 1")
    if not (0 < evaporacion <= 1):
        salir_con_error("la evaporación debe estar en el rango (0, 1]")
    if beta < 0:
        salir_con_error("beta no puede ser negativo")
    if not (0 <= q0 <= 1):
        salir_con_error("q0 debe estar entre 0 y 1")

    try:
        n_trabajos, n_maquinas, tiempos = leer_instancia(ruta)
    except (OSError, ValueError, IndexError) as error:
        salir_con_error(f"no se pudo leer la instancia '{ruta}': {error}")

    print("Ant Colony System - PFSP")
    print(f"Instancia: {ruta} ({n_trabajos} trabajos, {n_maquinas} máquinas)")
    print(f"Semilla: {semilla} | hormigas: {num_hormigas} | iteraciones: {iteraciones} "
          f"| evaporación: {evaporacion} | beta: {beta} | q0: {q0}")
    print()

    secuencia, cmax, historial = ejecutar_acs(tiempos, semilla, num_hormigas, iteraciones,
                                              evaporacion, beta, q0)
    parametros = (f"hormigas={num_hormigas} iteraciones={iteraciones} evaporacion={evaporacion} "
                  f"beta={beta} q0={q0}")
    reportar_y_guardar("ACS", ruta, semilla, parametros, secuencia, cmax, historial, salida)


if __name__ == "__main__":
    main()
