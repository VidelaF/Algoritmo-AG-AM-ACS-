"""Funciones que usan el AG, el AM y el ACS para resolver el PFSP."""
import csv
import os
import random
import sys


# Parámetros y errores

def salir_con_error(mensaje):
    """Muestra el error y termina el programa."""
    print(f"Error: {mensaje}")
    sys.exit(1)


def leer_parametros(argumentos, tipos, uso):
    """Convierte los argumentos al tipo pedido. Si algo no calza muestra el uso y termina."""
    if len(argumentos) != len(tipos):
        print(f"Error: se esperaban {len(tipos)} parámetros y llegaron {len(argumentos)}")
        print(uso)
        sys.exit(1)
    valores = []
    for texto, tipo in zip(argumentos, tipos):
        try:
            if tipo is float:
                texto = texto.replace(",", ".")
            valores.append(tipo(texto))
        except ValueError:
            print(f"Error: '{texto}' no es un valor válido, se esperaba {tipo.__name__}")
            print(uso)
            sys.exit(1)
    return valores


def validar_instancia(ruta):
    """Termina si el archivo de la instancia no existe."""
    if not os.path.isfile(ruta):
        salir_con_error(f"no se encontró el archivo de instancia '{ruta}'")


# Datos, makespan y RPD

def leer_instancia(ruta):
    """Lee una instancia de Taillard. tiempos[j][i] es el tiempo del trabajo i en la máquina j."""
    with open(ruta, "r") as archivo:
        lineas = [linea.strip() for linea in archivo]
    lineas = [linea for linea in lineas if linea != "" and not linea.startswith("#")]

    n_trabajos, n_maquinas = [int(x) for x in lineas[0].split()[:2]]
    tiempos = []
    for j in range(n_maquinas):
        fila = [int(x) for x in lineas[1 + j].split()]
        if len(fila) != n_trabajos:
            raise ValueError(f"la máquina {j + 1} no tiene {n_trabajos} tiempos")
        tiempos.append(fila)
    return n_trabajos, n_maquinas, tiempos


def calcular_makespan(secuencia, tiempos):
    """Cmax con C(i,j) = max(C(i-1,j), C(i,j-1)) + p. c[j] es el último fin en la máquina j."""
    n_maquinas = len(tiempos)
    c = [0] * n_maquinas
    for trabajo in secuencia:
        c[0] += tiempos[0][trabajo]
        for j in range(1, n_maquinas):
            c[j] = max(c[j], c[j - 1]) + tiempos[j][trabajo]
    return c[-1]


def nombre_instancia(ruta):
    """Nombre del archivo sin extensión, por ejemplo ta001."""
    return os.path.splitext(os.path.basename(ruta))[0]


def obtener_mejor_conocido(nombre, ruta_csv):
    """Busca el mejor valor conocido en best_known.csv. Devuelve None si no está."""
    if not os.path.isfile(ruta_csv):
        return None
    with open(ruta_csv, "r") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["Name"] == nombre:
                return int(fila["UB"])
    return None


def calcular_rpd(cmax, mejor_conocido):
    """RPD en porcentaje respecto al mejor conocido."""
    return (cmax - mejor_conocido) / mejor_conocido * 100


# AG y AM

def inicializar_poblacion(tam_poblacion, n_trabajos):
    """Permutaciones aleatorias de los trabajos."""
    poblacion = []
    for _ in range(tam_poblacion):
        individuo = list(range(n_trabajos))
        random.shuffle(individuo)
        poblacion.append(individuo)
    return poblacion


def evaluar_secuencias(secuencias, tiempos):
    """Makespan de cada secuencia de la lista."""
    return [calcular_makespan(secuencia, tiempos) for secuencia in secuencias]


def obtener_mejor(secuencias, costos):
    """Devuelve una copia de la mejor secuencia y su costo."""
    indice = costos.index(min(costos))
    return list(secuencias[indice]), costos[indice]


def seleccionar_por_torneo(poblacion, fitnesses, tam_torneo=2):
    """Gana el individuo con menor makespan entre los sorteados."""
    mejor = random.randint(0, len(poblacion) - 1)
    for _ in range(tam_torneo - 1):
        candidato = random.randint(0, len(poblacion) - 1)
        if fitnesses[candidato] < fitnesses[mejor]:
            mejor = candidato
    return poblacion[mejor]


def cruzar_ox(padre1, padre2):
    """Order Crossover. Copia un tramo del padre 1 y completa con el orden del padre 2."""
    n = len(padre1)
    punto1 = random.randint(0, n - 1)
    punto2 = random.randint(0, n - 1)
    if punto1 > punto2:
        punto1, punto2 = punto2, punto1

    hijo = [None] * n
    hijo[punto1:punto2 + 1] = padre1[punto1:punto2 + 1]
    copiados = set(padre1[punto1:punto2 + 1])

    posicion_hijo = (punto2 + 1) % n
    posicion_padre = (punto2 + 1) % n
    while None in hijo:
        trabajo = padre2[posicion_padre]
        if trabajo not in copiados:
            hijo[posicion_hijo] = trabajo
            posicion_hijo = (posicion_hijo + 1) % n
        posicion_padre = (posicion_padre + 1) % n
    return hijo


def mutar_intercambio(individuo):
    """Intercambia dos posiciones al azar."""
    mutado = list(individuo)
    pos1 = random.randint(0, len(mutado) - 1)
    pos2 = random.randint(0, len(mutado) - 1)
    mutado[pos1], mutado[pos2] = mutado[pos2], mutado[pos1]
    return mutado


def generar_nueva_poblacion(poblacion, fitnesses, tiempos, prob_cruce, prob_mutacion):
    """Reemplazo generacional con elitismo. Devuelve la nueva población y sus costos."""
    mejor_anterior, cmax_anterior = obtener_mejor(poblacion, fitnesses)

    nueva = []
    while len(nueva) < len(poblacion):
        padre1 = seleccionar_por_torneo(poblacion, fitnesses)
        padre2 = seleccionar_por_torneo(poblacion, fitnesses)
        if random.random() < prob_cruce:
            hijo = cruzar_ox(padre1, padre2)
        else:
            hijo = list(padre1)
        if random.random() < prob_mutacion:
            hijo = mutar_intercambio(hijo)
        nueva.append(hijo)

    fitnesses_nueva = evaluar_secuencias(nueva, tiempos)

    # elitismo: el mejor anterior reemplaza al peor si lo supera
    indice_peor = fitnesses_nueva.index(max(fitnesses_nueva))
    if cmax_anterior < fitnesses_nueva[indice_peor]:
        nueva[indice_peor] = mejor_anterior
        fitnesses_nueva[indice_peor] = cmax_anterior
    return nueva, fitnesses_nueva


def seleccionar_mejores_distintos(poblacion, fitnesses, cantidad):
    """Índices de los mejores individuos, sin repetir secuencias iguales."""
    orden = sorted(range(len(poblacion)), key=lambda i: fitnesses[i])
    elegidos = []
    for indice in orden:
        if all(poblacion[indice] != poblacion[otro] for otro in elegidos):
            elegidos.append(indice)
        if len(elegidos) == cantidad:
            break
    return elegidos


def busqueda_local_insercion(individuo, tiempos):
    """Mueve trabajos a otra posición y acepta la primera mejora. Termina sin mejoras."""
    mejor = list(individuo)
    cmax_mejor = calcular_makespan(mejor, tiempos)
    n = len(mejor)

    hay_mejora = True
    while hay_mejora:
        hay_mejora = False
        for origen in range(n):
            for destino in range(n):
                if destino == origen:
                    continue
                candidato = list(mejor)
                trabajo = candidato.pop(origen)
                candidato.insert(destino, trabajo)
                cmax_candidato = calcular_makespan(candidato, tiempos)
                if cmax_candidato < cmax_mejor:
                    mejor = candidato
                    cmax_mejor = cmax_candidato
                    hay_mejora = True
                    break
            if hay_mejora:
                break
    return mejor


# ACS

def calcular_heuristica(tiempos, beta):
    """Regla SPT: eta del trabajo j es 1 sobre su tiempo total, elevado a beta."""
    n_trabajos = len(tiempos[0])
    eta_beta = []
    for trabajo in range(n_trabajos):
        total = sum(fila[trabajo] for fila in tiempos)
        eta_beta.append((1.0 / total) ** beta)
    return eta_beta


def calcular_tau0(tiempos):
    """Feromona inicial: 1 sobre n por el makespan de una secuencia aleatoria."""
    n_trabajos = len(tiempos[0])
    secuencia = list(range(n_trabajos))
    random.shuffle(secuencia)
    return 1.0 / (n_trabajos * calcular_makespan(secuencia, tiempos))


def inicializar_feromona(n_trabajos, tau0):
    """tau[i][j] es qué tan bueno es programar j justo después de i."""
    return [[tau0] * n_trabajos for _ in range(n_trabajos)]


def seleccionar_trabajo(tau, eta_beta, actual, pendientes, q0):
    """Con probabilidad q0 elige el mejor, si no sortea con probabilidad proporcional."""
    valores = [tau[actual][j] * eta_beta[j] for j in pendientes]

    if random.random() < q0:
        return pendientes[valores.index(max(valores))]

    punto = random.random() * sum(valores)
    acumulado = 0.0
    for trabajo, valor in zip(pendientes, valores):
        acumulado += valor
        if punto <= acumulado:
            return trabajo
    return pendientes[-1]


def actualizar_feromona_local(tau, i, j, tau0, evaporacion):
    """Evaporación local en la arista recorrida."""
    tau[i][j] = (1 - evaporacion) * tau[i][j] + evaporacion * tau0


def actualizar_feromona_global(tau, secuencia, cmax, evaporacion):
    """Deposita feromona solo en las aristas de la mejor secuencia."""
    for i, j in zip(secuencia, secuencia[1:]):
        tau[i][j] = (1 - evaporacion) * tau[i][j] + evaporacion / cmax


def construir_secuencia(tau, eta_beta, tau0, q0, evaporacion):
    """Una hormiga arma una secuencia completa, partiendo de un trabajo al azar."""
    n_trabajos = len(eta_beta)
    actual = random.randint(0, n_trabajos - 1)
    secuencia = [actual]
    pendientes = [j for j in range(n_trabajos) if j != actual]

    while pendientes:
        siguiente = seleccionar_trabajo(tau, eta_beta, actual, pendientes, q0)
        actualizar_feromona_local(tau, actual, siguiente, tau0, evaporacion)
        secuencia.append(siguiente)
        pendientes.remove(siguiente)
        actual = siguiente
    return secuencia


# Salida

def guardar_resultados(archivo_csv, algoritmo, instancia, semilla, parametros, historial,
                       secuencia_final, mejor_conocido):
    """Agrega una fila por iteración. La secuencia final va solo en la última fila."""
    carpeta = os.path.dirname(archivo_csv)
    if carpeta != "":
        os.makedirs(carpeta, exist_ok=True)
    es_nuevo = not os.path.exists(archivo_csv)

    with open(archivo_csv, "a", newline="") as archivo:
        escritor = csv.writer(archivo)
        if es_nuevo:
            escritor.writerow(["algoritmo", "instancia", "semilla", "parametros", "iteracion",
                               "mejor_cmax", "rpd", "tiempo_cpu", "secuencia_final"])
        for posicion, (iteracion, cmax, tiempo) in enumerate(historial):
            rpd = ""
            if mejor_conocido is not None:
                rpd = round(calcular_rpd(cmax, mejor_conocido), 4)
            secuencia = ""
            if posicion == len(historial) - 1:
                secuencia = " ".join(str(trabajo + 1) for trabajo in secuencia_final)
            escritor.writerow([algoritmo, instancia, semilla, parametros, iteracion, cmax, rpd,
                               round(tiempo, 4), secuencia])


def reportar_y_guardar(algoritmo, ruta_instancia, semilla, parametros, secuencia, cmax, historial,
                       archivo_salida):
    """Muestra el progreso y el resultado por pantalla y guarda el CSV."""
    nombre = nombre_instancia(ruta_instancia)
    ruta_best = os.path.join(os.path.dirname(ruta_instancia), "best_known.csv")
    mejor_conocido = obtener_mejor_conocido(nombre, ruta_best)

    paso = max(1, len(historial) // 10)
    for iteracion, mejor_cmax, _ in historial[paso - 1::paso]:
        print(f"  iteración {iteracion:>5}: mejor Cmax = {mejor_cmax}")

    print()
    print(f"Mejor secuencia: {' '.join(str(trabajo + 1) for trabajo in secuencia)}")
    print(f"Makespan (Cmax): {cmax}")
    if mejor_conocido is not None:
        print(f"Mejor conocido:  {mejor_conocido}")
        print(f"RPD:             {calcular_rpd(cmax, mejor_conocido):.2f} %")
    else:
        print(f"No hay mejor conocido para '{nombre}' en {ruta_best}, no se calcula el RPD")
    print(f"Tiempo de CPU:   {historial[-1][2]:.2f} s")

    guardar_resultados(archivo_salida, algoritmo, nombre, semilla, parametros, historial,
                       secuencia, mejor_conocido)
    print(f"Resultados guardados en {archivo_salida}")
