"""Genera la tabla resumen y los gráficos a partir del CSV de main.py."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

USO = "Uso: python graficar.py archivo_resultados.csv\nEjemplo: python graficar.py resultados/comparacion.csv"

ALGORITMOS = ["AG", "AM", "ACS"]
COLORES = {"AG": "#2a78d6", "AM": "#eb6834", "ACS": "#1baf7a"}
TEXTO = "#333333"
GRILLA = "#dddddd"
CARPETA_GRAFICOS = "graficos"
CARPETA_RESULTADOS = "resultados"


def estilo_ejes(ax):
    """Ejes simples, con grilla suave."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=TEXTO)


def crear_resumen(datos):
    """Resumen por instancia y algoritmo con el resultado final de cada corrida."""
    finales = datos.sort_values("iteracion").groupby(["algoritmo", "instancia", "semilla"]).last().reset_index()
    resumen = finales.groupby(["instancia", "algoritmo"]).agg(
        corridas=("semilla", "count"),
        cmax_promedio=("mejor_cmax", "mean"),
        cmax_desv=("mejor_cmax", "std"),
        cmax_mejor=("mejor_cmax", "min"),
        rpd_promedio=("rpd", "mean"),
        rpd_desv=("rpd", "std"),
        tiempo_promedio=("tiempo_cpu", "mean"),
    ).reset_index()
    resumen["algoritmo"] = pd.Categorical(resumen["algoritmo"], ALGORITMOS, ordered=True)
    resumen = resumen.sort_values(["instancia", "algoritmo"]).round(2)
    return resumen


def graficar_convergencia(datos, instancias):
    """RPD promedio por iteración, un gráfico por instancia."""
    fig, ejes = plt.subplots(1, len(instancias), figsize=(4.2 * len(instancias), 3.6), sharey=False)
    for ax, instancia in zip(ejes, instancias):
        sub = datos[datos["instancia"] == instancia]
        for algoritmo in ALGORITMOS:
            curva = sub[sub["algoritmo"] == algoritmo].groupby("iteracion")["rpd"].mean()
            ax.plot(curva.index, curva.values, color=COLORES[algoritmo], linewidth=2, label=algoritmo)
        ax.set_title(instancia, color=TEXTO)
        ax.set_xlabel("Iteración", color=TEXTO)
        estilo_ejes(ax)
    ejes[0].set_ylabel("RPD promedio (%)", color=TEXTO)
    ejes[-1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA_GRAFICOS, "convergencia.pdf"))
    plt.close(fig)


def graficar_barras(resumen, instancias, columna, etiqueta, archivo, escala_log=False):
    """Barras agrupadas por instancia con el valor sobre cada barra."""
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ancho = 0.26
    for k, algoritmo in enumerate(ALGORITMOS):
        valores = []
        for instancia in instancias:
            fila = resumen[(resumen["instancia"] == instancia) & (resumen["algoritmo"] == algoritmo)]
            valores.append(float(fila[columna].iloc[0]))
        posiciones = [i + (k - 1) * ancho for i in range(len(instancias))]
        barras = ax.bar(posiciones, valores, ancho * 0.9, color=COLORES[algoritmo], label=algoritmo)
        for barra, valor in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width() / 2, valor, f"{valor:.1f}", ha="center",
                    va="bottom", fontsize=8, color=TEXTO)
    ax.set_xticks(range(len(instancias)))
    ax.set_xticklabels(instancias, color=TEXTO)
    ax.set_ylabel(etiqueta, color=TEXTO)
    if escala_log:
        ax.set_yscale("log")
    estilo_ejes(ax)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA_GRAFICOS, archivo))
    plt.close(fig)


def main():
    if len(sys.argv) != 2:
        print("Error: falta el archivo de resultados")
        print(USO)
        sys.exit(1)
    ruta = sys.argv[1]
    if not os.path.isfile(ruta):
        print(f"Error: no se encontró el archivo '{ruta}'")
        sys.exit(1)

    datos = pd.read_csv(ruta)
    instancias = sorted(datos["instancia"].unique())
    os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

    resumen = crear_resumen(datos)
    resumen.to_csv(os.path.join(CARPETA_RESULTADOS, "resumen.csv"), index=False)
    print(resumen.to_string(index=False))

    graficar_convergencia(datos, instancias)
    graficar_barras(resumen, instancias, "rpd_promedio", "RPD promedio (%)", "comparacion_rpd.pdf")
    graficar_barras(resumen, instancias, "tiempo_promedio", "Tiempo de CPU promedio (s, escala log)",
                    "comparacion_tiempo.pdf", escala_log=True)
    print()
    print(f"Resumen guardado en {CARPETA_RESULTADOS}/resumen.csv y gráficos en {CARPETA_GRAFICOS}/")


if __name__ == "__main__":
    main()
