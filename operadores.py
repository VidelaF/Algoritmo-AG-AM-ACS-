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


#Calculo de distancias

def calcular_distancia(c1,c2):