#Corre AG, AM y ACS sobre las instancias de prueba con varias semillas y guarda todo en un CSV
import os
import sys

from operadores import (
    leer_parametros, salir_con_error, validar_instancia, leer_instancia, nombre_instancia,
    obtener_mejor_conocido, calcular_rpd, guardar_resultados,
)
from ag import ejecutar_ag
from am import ejecutar_am
from acs import ejecutar_acs

USO = ("Uso: python main.py num_semillas archivo_salida\n"
       "Ejemplo: python main.py 10 resultados/comparacion.csv")

INSTANCIAS = ["datos/ta001.txt", "datos/ta041.txt", "datos/ta071.txt"]

#parámetros iguales para todas las instancias
POBLACION = 50
ITERACIONES = 200
PC = 0.8
PM = 0.1
FRECUENCIA_BL = 10
HORMIGAS = 50
EVAPORACION = 0.1
BETA = 2.0
Q0 = 0.9


def main():
    num_semillas, salida = leer_parametros(sys.argv[1:], [int, str], USO)

    if num_semillas < 1:
        salir_con_error("num_semillas debe ser al menos 1")
    if os.path.exists(salida):
        salir_con_error(f"el archivo '{salida}' ya existe, bórralo o usa otro nombre")
    for ruta in INSTANCIAS:
        validar_instancia(ruta)

    print("Comparación AG, AM y ACS en PFSP")
    print(f"Instancias: {', '.join(nombre_instancia(r) for r in INSTANCIAS)} | semillas: 1 a {num_semillas}")
    print()

    parametros_ag = f"poblacion={POBLACION} iteraciones={ITERACIONES} pc={PC} pm={PM}"
    parametros_am = parametros_ag + f" frecuencia_bl={FRECUENCIA_BL}"
    parametros_acs = (f"hormigas={HORMIGAS} iteraciones={ITERACIONES} evaporacion={EVAPORACION} "
                      f"beta={BETA} q0={Q0}")

    total = len(INSTANCIAS) * 3 * num_semillas
    corrida = 0
    for ruta in INSTANCIAS:
        nombre = nombre_instancia(ruta)
        _, _, tiempos = leer_instancia(ruta)
        mejor_conocido = obtener_mejor_conocido(nombre, os.path.join("datos", "best_known.csv"))

        for semilla in range(1, num_semillas + 1):
            for algoritmo in ["AG", "AM", "ACS"]:
                if algoritmo == "AG":
                    parametros = parametros_ag
                    resultado = ejecutar_ag(tiempos, semilla, POBLACION, ITERACIONES, PC, PM)
                elif algoritmo == "AM":
                    parametros = parametros_am
                    resultado = ejecutar_am(tiempos, semilla, POBLACION, ITERACIONES, PC, PM,
                                            FRECUENCIA_BL)
                else:
                    parametros = parametros_acs
                    resultado = ejecutar_acs(tiempos, semilla, HORMIGAS, ITERACIONES, EVAPORACION,
                                             BETA, Q0)

                secuencia, cmax, historial = resultado
                guardar_resultados(salida, algoritmo, nombre, semilla, parametros, historial,
                                   secuencia, mejor_conocido)
                corrida += 1
                rpd = calcular_rpd(cmax, mejor_conocido)
                print(f"[{corrida}/{total}] {nombre} {algoritmo:<3} semilla {semilla:>2}: "
                      f"Cmax = {cmax}, RPD = {rpd:.2f} %, CPU = {historial[-1][2]:.1f} s")

    print()
    print(f"Resultados guardados en {salida}")


if __name__ == "__main__":
    main()
