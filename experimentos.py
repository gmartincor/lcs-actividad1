"""experimentos.py - Mide tiempo de CPU y memoria maxima de las versiones A, B y C.

Cada medicion se ejecuta en un subproceso independiente:
  * Tiempo de CPU: time.process_time(), minimo de R repeticiones, sin tracemalloc.
  * Memoria maxima: pico de tracemalloc (memoria reservada por el algoritmo),
    en una ejecucion separada para no contaminar el tiempo. Ademas se anota
    la memoria residente maxima del proceso (ru_maxrss) en la ejecucion de
    tiempo, que incluye el propio interprete de Python.
Las cadenas se generan con semilla fija sobre el alfabeto {A, C, G, T}.
La serie 2 usa prefijos de una misma pareja y cuenta las llamadas de la version A.
Resultados: resultados/serie1.csv, resultados/serie2.csv y graficas PNG.
"""
import csv
import json
import os
import random
import subprocess
import sys

LIMITE_S = 60          # tiempo maximo por ejecucion (la version A es exponencial)
LIMITE_MEM_S = 900     # tracemalloc ralentiza la ejecucion: limite mayor para medir memoria
SERIE1 = [10, 100, 500, 1000, 2000, 4000]     # parejas P1..P6 (mayor >= 1000)
SERIE2 = [4, 6, 8, 10, 12, 14, 16, 18, 20]     # prefijos de una misma pareja (version A)
ALFABETO = "ACGT"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


def pareja(n, semilla):
    rnd = random.Random(semilla)
    X = "".join(rnd.choice(ALFABETO) for _ in range(n))
    Y = "".join(rnd.choice(ALFABETO) for _ in range(n))
    return X, Y


def llamadas_recursiva(X, Y):
    """Numero de llamadas que realiza la version A (misma recursion, sin cadenas)."""
    total = 0

    def rec(i, j):
        nonlocal total
        total += 1
        if i == 0 or j == 0:
            return
        if X[i - 1] == Y[j - 1]:
            rec(i - 1, j - 1)
        else:
            rec(i - 1, j)
            rec(i, j - 1)

    rec(len(X), len(Y))
    return total


HIJO = r"""
import sys, time, json, tracemalloc, resource
sys.path.insert(0, %r)
from lcs import VERSIONES
v, modo, X, Y, reps = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
f = VERSIONES[v][1]
if modo == "tiempo":
    mejor = None
    for _ in range(reps):
        t0 = time.process_time(); r = f(X, Y); t = time.process_time() - t0
        mejor = t if mejor is None else min(mejor, t)
        if t > 5: break
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin": rss //= 1024          # macOS informa en bytes
    print(json.dumps({"t": mejor, "rss": rss, "len": len(r)}))
else:
    tracemalloc.start(); r = f(X, Y); _, pico = tracemalloc.get_traced_memory()
    print(json.dumps({"mem": pico, "len": len(r)}))
""" % os.path.dirname(os.path.abspath(__file__))


def medir(v, X, Y, modo, reps=3):
    limite = LIMITE_S if modo == "tiempo" else LIMITE_MEM_S
    try:
        out = subprocess.run([sys.executable, "-c", HIJO, v, modo, X, Y, str(reps)],
                             capture_output=True, text=True, timeout=limite)
        return json.loads(out.stdout)
    except subprocess.TimeoutExpired:
        return None


def ejecutar_serie(tamanos, nombre, semilla_base, prefijos=False):
    filas = []
    agotada = set()
    if prefijos:   # todas las parejas son prefijos de una misma pareja base
        XB, YB = pareja(max(tamanos), semilla_base)
    for idx, n in enumerate(tamanos, 1):
        X, Y = (XB[:n], YB[:n]) if prefijos else pareja(n, semilla_base + n)
        for v in "ABC":
            if v in agotada:
                # ya supero el limite con una pareja menor: al ser el coste
                # creciente con n, no se vuelve a ejecutar
                t = m = None
            else:
                t = medir(v, X, Y, "tiempo")
                m = medir(v, X, Y, "memoria") if t else None
                if t is None:
                    agotada.add(v)
            fila = {"pareja": "P%d" % idx, "n": n, "version": v,
                    "tiempo_s": "%.6f" % t["t"] if t else "",
                    "memoria_kib": "%.1f" % (m["mem"] / 1024) if m else "",
                    "rss_max_kib": t["rss"] if t else "",
                    "long_lcs": t["len"] if t else "",
                    "estado": "ok" if t else "> %d s" % LIMITE_S}
            if prefijos:
                fila["llamadas_A"] = (llamadas_recursiva(X, Y)
                                      if v == "A" and t else "")
            filas.append(fila)
            print(nombre, fila, flush=True)
    with open(os.path.join(DIR, nombre + ".csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    return filas


def graficas(filas, nombre, xlog=True):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no disponible: se omiten las graficas")
        return
    estilos = {"A": ("o", "-"), "B": ("s", "--"), "C": ("^", ":")}
    etiquetas = {"A": "A - Recursiva", "B": "B - Hirschberg", "C": "C - PD tabular"}
    fig, ejes = plt.subplots(1, 2, figsize=(9, 3.4))
    for col, eje, tit in (("tiempo_s", ejes[0], "Tiempo de CPU (s)"),
                          ("memoria_kib", ejes[1], "Memoria maxima (KiB)")):
        for v in "ABC":
            pts = [(int(f["n"]), float(f[col])) for f in filas
                   if f["version"] == v and f[col] not in ("", None) and float(f[col]) > 0]
            if pts:
                xs, ys = zip(*pts)
                eje.plot(xs, ys, color="black", marker=estilos[v][0],
                         linestyle=estilos[v][1], markerfacecolor="white",
                         label=etiquetas[v])
        if xlog:
            eje.set_xscale("log")
        eje.set_yscale("log")
        eje.set_xlabel("n = |X| = |Y|"); eje.set_title(tit, fontsize=10)
        eje.grid(True, which="major", color="0.8", linewidth=0.5)
        eje.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(DIR, nombre + ".png"), dpi=200)


def main():
    os.makedirs(DIR, exist_ok=True)
    f1 = ejecutar_serie(SERIE1, "serie1", 1000)
    f2 = ejecutar_serie(SERIE2, "serie2", 2000, prefijos=True)
    # Las graficas se generan al final: importar matplotlib en el proceso padre
    # elevaria el ru_maxrss que heredan los subprocesos de medida.
    graficas(f1, "serie1")
    graficas(f2, "serie2", xlog=False)   # semilogaritmica: exponencial = recta


if __name__ == "__main__":
    main()
