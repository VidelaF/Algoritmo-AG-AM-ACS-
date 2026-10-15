import csv
import math
import os
import random

#leemos datos
def leer_instancia(archivo):
    """Lee archivo TSP formato: ciudad_id x y"""
    ciudades = []
    with open(archivo, 'r') as f:
        for linea in f:
            linea = linea.strip()
            
            #para ignorar encabezados y líneas vacías
            if not linea or linea.startswith('NAME') or linea.startswith('TYPE') or \
               linea.startswith('COMMENT') or linea.startswith('DIMENSION') or \
               linea.startswith('EDGE_WEIGHT') or linea.startswith('NODE_COORD') or \
               linea == 'EOF':
                continue
            
            #parseamos a coordenadas
            try:
                partes = linea.split()
                if len(partes) >= 3:
                    x = float(partes[1])
                    y = float(partes[2])
                    ciudades.append((x, y))
            except (ValueError, IndexError):
                continue
    
    return ciudades



#calculo de distancias


def calcular_distancia(c1, c2):
    #distancia entre dos ciudades c1 y c2 (x,y)
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)


def calcular_matriz_distancias(ciudades):
    #matriz de distancias entre todas las ciudades
    n = len(ciudades)
    dist = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            d = calcular_distancia(ciudades[i], ciudades[j])
            dist[i][j] = d
            dist[j][i] = d
    
    return dist


def calcular_heuristica(dist):
    #heurística: inverso de distancia 
    n = len(dist)
    eta = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] > 0:
                eta[i][j] = 1.0 / dist[i][j]
    
    return eta


#evaluación de rutas

def evaluar_ruta(ruta, dist):
    #costo total de la ruta (distancia recorrida)
    costo = 0
    for i in range(len(ruta)):
        siguiente = (i + 1) % len(ruta)
        costo += dist[ruta[i]][ruta[siguiente]]
    
    return costo


#iniciamos feromona

def inicializar_feromona(n, tau0):
    #matriz de feromona inicializada con tau0
    tau = [[tau0] * n for _ in range(n)]
    
    for i in range(n):
        tau[i][i] = 0
    
    return tau



#actualizamos feromona  

def actualizar_feromona_local(tau, ruta, tau0, rho):
    #actualizacion local
    for i in range(len(ruta)):
        siguiente = (i + 1) % len(ruta)
        ij = ruta[i]
        jj = ruta[siguiente]
        tau[ij][jj] = (1 - rho) * tau[ij][jj] + rho * tau0
        tau[jj][ij] = (1 - rho) * tau[jj][ij] + rho * tau0


def actualizar_feromona_global(tau, mejor_ruta, delta, rho):
    #actualizacion global
    for i in range(len(mejor_ruta)):
        siguiente = (i + 1) % len(mejor_ruta)
        ij = mejor_ruta[i]
        jj = mejor_ruta[siguiente]
        tau[ij][jj] = (1 - rho) * tau[ij][jj] + rho * delta
        tau[jj][ij] = (1 - rho) * tau[jj][ij] + rho * delta


#calculamos tau0

def calcular_tau0(dist):
    #tau0 = 1 / (n * costo de una solucion inicial aleatoria)
    n = len(dist)
    ruta_inicial = list(range(n))
    random.shuffle(ruta_inicial)
    return 1.0 / (n * evaluar_ruta(ruta_inicial, dist))


#construccion de soluciones

def seleccionar_ciudad(tau, eta, actual, no_visitadas, alpha, beta, q0):
    #elige la siguiente ciudad con la regla pseudoaleatoria proporcional del ACS
    rand = random.random()

    if rand < q0:
        #explotacion: la ciudad con mayor atraccion
        mejor_siguiente = None
        mejor_valor = -1

        for siguiente in no_visitadas:
            #calcula atraccion
            valor = (tau[actual][siguiente] ** alpha) * (eta[actual][siguiente] ** beta)
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_siguiente = siguiente

        siguiente = mejor_siguiente

    else:
        #exploracion
        suma = 0
        for j in no_visitadas:
            suma += (tau[actual][j] ** alpha) * (eta[actual][j] ** beta)

        if suma > 0:
            #crea ruleta
            probs = []
            for j in no_visitadas:
                prob = ((tau[actual][j] ** alpha) * (eta[actual][j] ** beta)) / suma
                probs.append((prob, j))

            #ordena para iterar
            probs.sort()

            #gira la ruleta
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
            #si no hay atraccion elegimos aleatoriamente
            siguiente = random.choice(list(no_visitadas))

    return siguiente


def construir_solucion(tau, eta, n, alpha, beta, q0):
    #una hormiga construye una ruta que visita todas las ciudades
    actual = random.randint(0, n - 1)
    ruta = [actual]
    no_visitadas = set(range(n)) - {actual}

    while no_visitadas:
        siguiente = seleccionar_ciudad(tau, eta, actual, no_visitadas, alpha, beta, q0)
        ruta.append(siguiente)
        no_visitadas.remove(siguiente)
        actual = siguiente

    return ruta


def construir_soluciones(tau, eta, n, num_hormigas, alpha, beta, q0):
    #cada hormiga construye una solucion
    soluciones = []
    for _ in range(num_hormigas):
        soluciones.append(construir_solucion(tau, eta, n, alpha, beta, q0))

    return soluciones


#evaluacion de soluciones y mejor solucion

def evaluar_soluciones(soluciones, dist):
    #costo de cada ruta, en el mismo orden que las soluciones
    costos = []
    for ruta in soluciones:
        costos.append(evaluar_ruta(ruta, dist))

    return costos


def actualizar_mejor_solucion(soluciones, costos, mejor_ruta, mejor_costo):
    #si la mejor de esta iteracion supera a la mejor global, la reemplaza
    index_mejor = costos.index(min(costos))
    if costos[index_mejor] < mejor_costo:
        return soluciones[index_mejor], costos[index_mejor]

    return mejor_ruta, mejor_costo


#salida de resultados

def guardar_resultados(archivo_csv, instancia, semilla, num_hormigas, num_iteraciones, alpha, beta, q0, rho, historial):
    #agrega al csv una fila por iteracion (el encabezado solo si el archivo es nuevo)
    carpeta = os.path.dirname(archivo_csv)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    archivo_nuevo = not os.path.exists(archivo_csv)
    with open(archivo_csv, "a", newline="") as archivo:
        escritor = csv.writer(archivo)
        if archivo_nuevo:
            escritor.writerow(["instancia", "semilla", "num_hormigas", "num_iteraciones", "alpha", "beta", "q0", "rho",
                               "iteracion", "costo_iteracion", "mejor_costo", "tiempo", "mejor_ruta"])
        for h in historial:
            escritor.writerow([os.path.basename(instancia), semilla, num_hormigas, num_iteraciones, alpha, beta, q0, rho,
                               h["iteracion"], round(h["costo_iteracion"], 2), round(h["mejor_costo"], 2),
                               round(h["tiempo"], 3), [ciudad + 1 for ciudad in h["mejor_ruta"]]])
