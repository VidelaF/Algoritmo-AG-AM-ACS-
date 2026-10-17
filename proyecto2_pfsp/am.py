"""Algoritmo Memético para PFSP. Es el AG con búsqueda local sobre el mejor individuo."""
import random
import sys
import time

from operadores import (
    leer_parametros, validar_instancia, salir_con_error, leer_instancia,
    inicializar_poblacion, evaluar_secuencias, obtener_mejor, generar_nueva_poblacion,
    busqueda_local_insercion, calcular_makespan, reportar_y_guardar,
)

USO = ("Uso: python am.py instancia semilla poblacion iteraciones pc pm frecuencia_bl archivo_salida\n"
       "Ejemplo: python am.py datos/ta001.txt 12345 50 200 0.8 0.1 10 resultados/res_am.csv")


def ejecutar_am(tiempos, semilla, tam_poblacion, iteraciones, prob_cruce, prob_mutacion,
                frecuencia_bl):
    """Devuelve la mejor secuencia, su cmax y el historial."""
    random.seed(semilla)
    inicio = time.process_time()

    poblacion = inicializar_poblacion(tam_poblacion, len(tiempos[0]))
    fitnesses = evaluar_secuencias(poblacion, tiempos)
    mejor_secuencia, mejor_cmax = obtener_mejor(poblacion, fitnesses)

    historial = []
    for iteracion in range(1, iteraciones + 1):
        poblacion, fitnesses = generar_nueva_poblacion(poblacion, fitnesses, tiempos,
                                                       prob_cruce, prob_mutacion)

        # búsqueda local cada frecuencia_bl iteraciones
        if iteracion % frecuencia_bl == 0:
            indice = fitnesses.index(min(fitnesses))
            poblacion[indice] = busqueda_local_insercion(poblacion[indice], tiempos)
            fitnesses[indice] = calcular_makespan(poblacion[indice], tiempos)

        secuencia, cmax = obtener_mejor(poblacion, fitnesses)
        if cmax < mejor_cmax:
            mejor_secuencia, mejor_cmax = secuencia, cmax
        historial.append((iteracion, mejor_cmax, time.process_time() - inicio))

    return mejor_secuencia, mejor_cmax, historial


def main():
    (ruta, semilla, tam_poblacion, iteraciones, pc, pm, frecuencia_bl, salida) = leer_parametros(
        sys.argv[1:], [str, int, int, int, float, float, int, str], USO)

    validar_instancia(ruta)
    if tam_poblacion < 2:
        salir_con_error("la población debe tener al menos 2 individuos")
    if iteraciones < 1:
        salir_con_error("las iteraciones deben ser al menos 1")
    if not (0 <= pc <= 1 and 0 <= pm <= 1):
        salir_con_error("pc y pm deben estar entre 0 y 1")
    if frecuencia_bl < 1:
        salir_con_error("la frecuencia de búsqueda local debe ser al menos 1")

    try:
        n_trabajos, n_maquinas, tiempos = leer_instancia(ruta)
    except (OSError, ValueError, IndexError) as error:
        salir_con_error(f"no se pudo leer la instancia '{ruta}': {error}")

    print("Algoritmo Memético - PFSP")
    print(f"Instancia: {ruta} ({n_trabajos} trabajos, {n_maquinas} máquinas)")
    print(f"Semilla: {semilla} | población: {tam_poblacion} | iteraciones: {iteraciones} "
          f"| pc: {pc} | pm: {pm} | búsqueda local cada {frecuencia_bl} iteraciones")
    print()

    secuencia, cmax, historial = ejecutar_am(tiempos, semilla, tam_poblacion, iteraciones,
                                             pc, pm, frecuencia_bl)
    parametros = (f"poblacion={tam_poblacion} iteraciones={iteraciones} pc={pc} pm={pm} "
                  f"frecuencia_bl={frecuencia_bl}")
    reportar_y_guardar("AM", ruta, semilla, parametros, secuencia, cmax, historial, salida)


if __name__ == "__main__":
    main()
