import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OPTIMO = 7544.37  #optimo conocido de berlin52
PARAMETROS = ["num_hormigas", "num_iteraciones", "alpha", "beta", "q0"]

if len(sys.argv) != 2:
    print("Uso: python graficar.py resultados.csv")
    sys.exit()
if not os.path.exists(sys.argv[1]):
    print(f"Error: no existe el archivo {sys.argv[1]}")
    sys.exit()

df = pd.read_csv(sys.argv[1])
os.makedirs("graficos", exist_ok=True)

#una fila por corrida: la ultima iteracion de cada (configuracion, semilla)
finales = df[df["iteracion"] == df["num_iteraciones"]]

#configuracion base: la que tiene mas corridas
base = pd.Series(finales.groupby(PARAMETROS).size().idxmax(), index=PARAMETROS)
filas_base = (df[PARAMETROS] == base).all(axis=1)
finales_base = finales[(finales[PARAMETROS] == base).all(axis=1)]
print("Configuracion base:", base.to_dict())

#para comparar configuraciones se usan solo las semillas que todas tienen (1..k)
semilla_comun = finales.groupby(PARAMETROS)["semilla"].max().min()
comparables = finales[finales["semilla"] <= semilla_comun]

#resumen por configuracion
resumen = comparables.groupby(PARAMETROS).agg(
    corridas=("semilla", "count"),
    costo_promedio=("mejor_costo", "mean"),
    costo_desv=("mejor_costo", "std"),
    costo_mejor=("mejor_costo", "min"),
    tiempo_promedio=("tiempo", "mean"),
)
print(f"Resumen por configuración (semillas 1 a {semilla_comun}):")
print(resumen.round(2).to_string())

#1. convergencia de la configuracion base (promedio y desviacion entre semillas)
por_iteracion = df[filas_base].groupby("iteracion")["mejor_costo"]
promedio = por_iteracion.mean()
desviacion = por_iteracion.std().fillna(0)
plt.figure(figsize=(7, 4))
plt.plot(promedio.index, promedio, label="promedio de las semillas")
plt.fill_between(promedio.index, promedio - desviacion, promedio + desviacion, alpha=0.25, label="± desviación")
plt.axhline(OPTIMO, color="gray", linestyle="--", label="óptimo conocido")
plt.xlabel("iteración")
plt.ylabel("mejor costo")
plt.title("Convergencia (configuración base)")
plt.legend()
plt.tight_layout()
plt.savefig("graficos/convergencia.pdf")
plt.close()

#2. resultado final de cada semilla (configuracion base)
plt.figure(figsize=(7, 4))
plt.bar(finales_base["semilla"], finales_base["mejor_costo"])
plt.axhline(OPTIMO, color="gray", linestyle="--", label="óptimo conocido")
plt.axhline(finales_base["mejor_costo"].mean(), color="tab:red", label="promedio")
plt.ylim(OPTIMO * 0.95, finales_base["mejor_costo"].max() * 1.01)
plt.xlabel("semilla")
plt.ylabel("mejor costo final")
plt.title("Resultado por semilla (configuración base)")
plt.legend()
plt.tight_layout()
plt.savefig("graficos/semillas.pdf")
plt.close()

#3. efecto de cada parametro (los demas quedan en el valor base)
paneles = []
for parametro in PARAMETROS:
    otros = [p for p in PARAMETROS if p != parametro]
    filas = comparables[(comparables[otros] == base[otros]).all(axis=1)]
    if filas[parametro].nunique() > 1:
        paneles.append((parametro, filas))

if paneles:
    fig, ejes = plt.subplots(1, len(paneles), figsize=(3.2 * len(paneles), 4), sharey=True)
    if len(paneles) == 1:
        ejes = [ejes]
    for eje, (parametro, filas) in zip(ejes, paneles):
        valores = sorted(filas[parametro].unique())
        eje.boxplot([filas[filas[parametro] == v]["mejor_costo"] for v in valores])
        eje.set_xticklabels(valores)
        eje.axhline(OPTIMO, color="gray", linestyle="--")
        eje.set_xlabel(parametro)
    ejes[0].set_ylabel("mejor costo final")
    fig.suptitle("Efecto de cada parámetro")
    plt.tight_layout()
    plt.savefig("graficos/parametros.pdf")
    plt.close()

#4. calidad de la solucion contra tiempo de ejecucion (una marca por configuracion)
plt.figure(figsize=(7, 4))
plt.scatter(resumen["tiempo_promedio"], resumen["costo_promedio"])
for (hormigas, iteraciones, alpha, beta, q0), fila in resumen.iterrows():
    plt.annotate(f"{hormigas}h {iteraciones}i a{alpha} b{beta} q{q0}", (fila["tiempo_promedio"], fila["costo_promedio"]), fontsize=6)
plt.axhline(OPTIMO, color="gray", linestyle="--", label="óptimo conocido")
plt.xlabel("tiempo promedio (s)")
plt.ylabel("costo promedio")
plt.title("Calidad contra tiempo")
plt.legend()
plt.tight_layout()
plt.savefig("graficos/tiempo_vs_costo.pdf")
plt.close()

print("Gráficos guardados en graficos/")
