"""Algoritmo Genético para PFSP."""
import random
import sys
import time

from operadores import (
    leer_parametros, validar_instancia, salir_con_error, leer_instancia,
    inicializar_poblacion, evaluar_secuencias, obtener_mejor, generar_nueva_poblacion,
    reportar_y_guardar,
)

USO = ("Uso: python ag.py instancia semilla poblacion iteraciones pc pm archivo_salida\n"
       "Ejemplo: python ag.py datos/ta001.txt 12345 50 200 0.8 0.1 resultados/res_ag.csv")


def ejecutar_ag(tiempos, semilla, tam_poblacion, iteraciones, prob_cruce, prob_mutacion):
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
        secuencia, cmax = obtener_mejor(poblacion, fitnesses)
        if cmax < mejor_cmax:
            mejor_secuencia, mejor_cmax = secuencia, cmax
        historial.append((iteracion, mejor_cmax, time.process_time() - inicio))

    return mejor_secuencia, mejor_cmax, historial


def main():
    (ruta, semilla, tam_poblacion, iteraciones, pc, pm, salida) = leer_parametros(
        sys.argv[1:], [str, int, int, int, float, float, str], USO)

    validar_instancia(ruta)
    if tam_poblacion < 2:
        salir_con_error("la población debe tener al menos 2 individuos")
    if iteraciones < 1:
        salir_con_error("las iteraciones deben ser al menos 1")
    if not (0 <= pc <= 1 and 0 <= pm <= 1):
        salir_con_error("pc y pm deben estar entre 0 y 1")

    try:
        n_trabajos, n_maquinas, tiempos = leer_instancia(ruta)
    except (OSError, ValueError, IndexError) as error:
        salir_con_error(f"no se pudo leer la instancia '{ruta}': {error}")

    print("Algoritmo Genético - PFSP")
    print(f"Instancia: {ruta} ({n_trabajos} trabajos, {n_maquinas} máquinas)")
    print(f"Semilla: {semilla} | población: {tam_poblacion} | iteraciones: {iteraciones} "
          f"| pc: {pc} | pm: {pm}")
    print()

    secuencia, cmax, historial = ejecutar_ag(tiempos, semilla, tam_poblacion, iteraciones, pc, pm)
    parametros = f"poblacion={tam_poblacion} iteraciones={iteraciones} pc={pc} pm={pm}"
    reportar_y_guardar("AG", ruta, semilla, parametros, secuencia, cmax, historial, salida)


if __name__ == "__main__":
    main()
