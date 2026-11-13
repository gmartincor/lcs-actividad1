# Actividad 1 - Subsecuencia común más larga (LCS)

Tres versiones del cálculo de la LCS de dos cadenas:

| Versión | Técnica | Fichero / función |
|---|---|---|
| A | Recursiva directa (sin memorización) | `lcs.py` / `lcs_recursiva` |
| B | Divide y conquista de Hirschberg | `lcs.py` / `lcs_hirschberg` |
| C | Programación dinámica tabular | `lcs.py` / `lcs_pd` |

## Requisitos

- Python 3.8 o superior (probado con Python 3.13).
- `make` (incluido en macOS con las Command Line Tools y en Linux).
- Opcional: `matplotlib` para generar las gráficas (`pip install matplotlib`).
  Sin matplotlib se generan igualmente las tablas CSV.

No se usa ninguna librería externa específica de LCS.

## Ejecución (un único comando)

```
make
```

Ejecuta primero el juego de pruebas (`tests.py`) y después los experimentos
(`experimentos.py`). Los resultados se escriben en la carpeta `resultados/`:

- `serie1.csv`, `serie1.png`: parejas P1-P6 con n = 10, 100, 500, 1000, 2000, 4000.
- `serie2.csv`, `serie2.png`: prefijos n = 4 ... 20 de una misma pareja, con el número
  de llamadas recursivas de la versión A.

Otros objetivos: `make test`, `make experimentos`, `make limpiar`.

## Metodología de medida

- Cadenas aleatorias sobre {A, C, G, T} con semilla fija (reproducibles).
- Cada medición se lanza en un subproceso independiente con un límite de 60 s.
- Tiempo de CPU: `time.process_time()`, mínimo de 3 repeticiones.
- Memoria máxima: pico de `tracemalloc` (memoria reservada por el algoritmo) en
  una ejecución separada, y `ru_maxrss` (memoria residente máxima del proceso,
  incluido el intérprete) en la ejecución de tiempo.

El repositorio incluye en `resultados/` los CSV obtenidos para la memoria de la
actividad (Linux, Intel Xeon 2,10 GHz, Python 3.13). Al ejecutar `make` se
regeneran, junto con las gráficas, en la máquina local.
