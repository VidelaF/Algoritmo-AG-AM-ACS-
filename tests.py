import os
import random
import tempfile
from operadores import (
    leer_instancia,
    calcular_matriz_distancias,
    calcular_heuristica,
    evaluar_ruta,
    calcular_tau0,
    inicializar_feromona,
    actualizar_feromona_local,
    actualizar_feromona_global,
    construir_solucion,
    seleccionar_ciudad,
    actualizar_mejor_solucion
)
from acs import acs

INSTANCIA = "datos/berlin52.txt"

#ruta optima conocida de berlin52 (ciudades numeradas desde 1)
RUTA_OPTIMA = [1, 49, 32, 45, 19, 41, 8, 9, 10, 43, 33, 51, 11, 52, 14, 13, 47, 26, 27, 28, 12, 25, 4, 6, 15, 5,
               24, 48, 38, 37, 40, 39, 36, 35, 34, 44, 46, 16, 29, 50, 20, 23, 30, 2, 7, 42, 21, 17, 3, 18, 31, 22]


def es_permutacion(ruta, n):
    return sorted(ruta) == list(range(n))


#1. los datos se leen correctamente

def test_leer_instancia():
    ciudades = leer_instancia(INSTANCIA)
    assert len(ciudades) == 52
    assert ciudades[0] == (565.0, 575.0)
    assert ciudades[-1] == (1740.0, 245.0)

    #un archivo con encabezado TSPLIB tambien se lee bien
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("NAME: prueba\nTYPE: TSP\nDIMENSION: 2\nNODE_COORD_SECTION\n1 0.0 0.0\n2 3.0 4.0\nEOF\n")
    assert leer_instancia(f.name) == [(0.0, 0.0), (3.0, 4.0)]
    os.remove(f.name)


#2. las soluciones generadas son validas

def test_soluciones_validas():
    ciudades = leer_instancia(INSTANCIA)
    n = len(ciudades)
    dist = calcular_matriz_distancias(ciudades)
    eta = calcular_heuristica(dist)
    tau = inicializar_feromona(n, calcular_tau0(dist))

    #q0 = 0 usa solo la ruleta, q0 = 1 solo la explotacion
    for q0 in (0.0, 0.9, 1.0):
        for semilla in range(5):
            random.seed(semilla)
            ruta = construir_solucion(tau, eta, n, 1.0, 2.0, q0)
            assert es_permutacion(ruta, n)

    no_visitadas = {3, 7, 11}
    assert seleccionar_ciudad(tau, eta, 0, no_visitadas, 1.0, 2.0, 0.9) in no_visitadas


#3. el costo de una ruta se calcula correctamente

def test_costo_ruta():
    #rectangulo de 3 x 4: la ruta por el borde mide 14 y la que se cruza mide 18
    dist = calcular_matriz_distancias([(0, 0), (0, 3), (4, 3), (4, 0)])
    assert abs(evaluar_ruta([0, 1, 2, 3], dist) - 14.0) < 1e-9
    assert abs(evaluar_ruta([0, 2, 1, 3], dist) - 18.0) < 1e-9

    #la ruta optima de berlin52 mide 7544.37
    dist = calcular_matriz_distancias(leer_instancia(INSTANCIA))
    costo = evaluar_ruta([c - 1 for c in RUTA_OPTIMA], dist)
    assert abs(costo - 7544.37) < 0.01


#4. las feromonas se inicializan y actualizan correctamente

def test_feromonas():
    tau = inicializar_feromona(4, 0.5)
    for i in range(4):
        for j in range(4):
            assert tau[i][j] == (0 if i == j else 0.5)

    #local: el tramo recorrido se acerca a tau0, los demas no cambian
    tau[0][1] = tau[1][0] = 1.0
    actualizar_feromona_local(tau, [0, 1, 2], 0.5, 0.1)
    assert abs(tau[0][1] - 0.95) < 1e-12 and abs(tau[1][0] - 0.95) < 1e-12
    assert tau[0][3] == 0.5 and tau[3][0] == 0.5

    #global: el tramo de la mejor ruta se acerca a delta
    tau[0][1] = tau[1][0] = 1.0
    actualizar_feromona_global(tau, [0, 1, 2], 0.2, 0.1)
    assert abs(tau[0][1] - 0.92) < 1e-12 and abs(tau[1][0] - 0.92) < 1e-12
    assert tau[0][3] == 0.5


#5. el algoritmo mejora o mantiene la mejor solucion

def test_mejor_solucion():
    #una solucion peor no reemplaza a la mejor global
    ruta, costo = actualizar_mejor_solucion([[0, 1], [1, 0]], [9.0, 8.0], [0, 1], 7.0)
    assert ruta == [0, 1] and costo == 7.0

    random.seed(1)
    mejor_ruta, mejor_costo, historial = acs(INSTANCIA, 10, 30, 1.0, 2.0, 0.9, 0.1)
    costos = [h["mejor_costo"] for h in historial]
    for anterior, actual in zip(costos, costos[1:]):
        assert actual <= anterior
    assert mejor_costo == min(h["costo_iteracion"] for h in historial)

    dist = calcular_matriz_distancias(leer_instancia(INSTANCIA))
    assert es_permutacion(mejor_ruta, 52)
    assert abs(evaluar_ruta(mejor_ruta, dist) - mejor_costo) < 1e-9


if __name__ == "__main__":
    pruebas = [test_leer_instancia, test_soluciones_validas, test_costo_ruta, test_feromonas, test_mejor_solucion]
    for prueba in pruebas:
        prueba()
        print("OK", prueba.__name__)
    print("Todas las pruebas pasaron")
