import random 
import time
from operadores import(
    leer_instancia,
    calcular_matriz_distancias,
    calcular_heurtistica,
    evaluar_ruta
    inicializar_feromona,
    actualizar_feromona_local,
    actualizar_feromona_global
)

def_construir_solucion(tau, eta, n, alpha, beta, q0):
    #Implementación de la construcción de solución
    #Partida desde ciudad random
    actual = random.randit(0, n-1)
    ruta = [actual]
    no_visitadas = set(range(n)) - {actual}

    #Construcción de la ruta
    while no_visitadas:
        rand = random.random()

        if rand < q0:
            #Aquí hacemos explotacion
            mejor_siguiente = None
            mejor_valor = -1

            for siguiente in no_visitadas:
                #Calculamos la atraccion
                valor = (tau[actual][siguiente]**alpha)*(eta[actual][siguiente]**beta)
                mejor_valor = valor
                mejor_siguiente = siguiente
            siguiente = mejor_siguiente
        else:
            #Aquí hacemos exploracion
            suma = 0
            for j in no_visitadas:
                suma += (tau[actual][j]**alpha)*(eta[actual][j]**beta)

            if suma > 0:
                #Ruleta 
                probs = []
                for j in no_visitadas:
                    prob = (tau[actual][j]**alpha)*(eta[actual][j]**beta)/suma
                    probs.append((prob, j)) 

                #ordenamos
                probs.sort()
                #giramos
                rand_selec = random.random()
                acum = 0
                siguiente = None
                for prob, j in probs:
                    acum += prob
                    if rand_selec <= acum:
                        siguiente = j
                        break
                if siguiente is None:
                    siguiente = probs[-1][1]
            else:
                siguiente = random.choice(list(no_visitadas))


        #aAgregamos la cidudad a la ruta y la marcamos como visitada
        ruta.append(siguiente)
        no_visitadas.remove(siguiente)
        actual = siguiente
    
    return ruta
