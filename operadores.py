import math
import random

#Lectura de datos

def leer_instancia(archivo):
#ciudad_id x y

    ciudades = []
    with open(archivo, 'r') as f:
        for linea in f:
            linea = linea.strip()
            
            #Tenemos que ignorar lineas vacias
            if not linea or linea.startswith('NAME') or linea.startswith('TYPE') or linea.startswith('COMMENT') or linea.startswith('DIMENSION') or linea.startswith('EDGE_WRIGHT') or linea.startswith('NODE_COORD') or linea == 'EOF':
                continue
            
            #Parseamos a coordenadas
            try:
                partes = linea.split()
                if len(partes) >= 3:
                    x = float(partes[1])
                    y = float(partes[2])
                    ciudades.append((x,y))
            except(ValueError, IndexError):
                continue
    return cidudades


#Calculo de distancias, dos ciudades 

def calcular_distancia(c1,c2):
    return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)

def calcular_matriz_distancias(ciudades):
    n = len(ciudades)
    dist = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i +1, n):
            d = calcular_distancia(ciudades[i], ciudades[j])
            dist[i][j] = d
            dist[j][i] = d
    return dist

def calcular_heurtistica(dist)

n = len(dist)
eta = [[0.0]*n for _ in range(n)]

for i in range(n):
    for j in range(n):
        if i != j and dist[i][j] > 0:
            eta[i][j] = 1.0 / dist[i][j]
return eta


#Costo todal de una ruta, ida y vuelta, incluyendo el regreso a la ciudad
evaluar_ruta(ruta, dist):
costo = 0 
for i in range(len(ruta)):
    siguiente = (i + 1) % len(ruta)
    costo += dist[ruta[i]][ruta[siguiente]]
return costo

#Matriz de feromona
def inicializar_feromona(n, tau0):
    tau = [[tau0]*n for _ in range(n)]
for i in range(n):
    tau[i][i] = 0
return tau

#Actualización de las feromonas
def actualizar_feromona_local(tau, ruta, rho):
for i in range(len(ruta)):
    siguiente = (i+1) % len(ruta)
    ij = ruta[i]
    jj = ruta[siguiente]
    tau[ij][jj] = (1-alpha)* tau[ij][jj] + alpha * tau0
    tau[jj][ij] = (1-alpha)* tau[jj][ij] + alpha * tau0

def actualizar_feromona_global(tau, mejor_ruta, delta, alpha)
for i in range(len(mejor_ruta)):
    siguiente = (i+1) % len(mejor_ruta)
    ij = mejor_ruta[i]
    jj = mejor_ruta[siguiente]
    tau[ij][jj] = (1-alpha)* tau[ij][jj] + alpha * delta
    tau[jj][ij] = (1-alpha)* tau[jj][ij] + alpha * delta
    
    

                

