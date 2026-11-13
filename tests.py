"""tests.py - Juego de pruebas de correccion de las tres versiones."""
import random
from lcs import lcs_recursiva, lcs_hirschberg, lcs_pd, es_subsecuencia


def cadena(rnd, a, b):
    """Cadena aleatoria sobre {A,C,G,T} de longitud entre a y b."""
    return "".join(rnd.choice("ACGT") for _ in range(rnd.randint(a, b)))


def comprobar(X, Y, esperado=None, con_recursiva=True):
    fs = [lcs_hirschberg, lcs_pd]
    if con_recursiva:
        fs.append(lcs_recursiva)
    res = [f(X, Y) for f in fs]
    longitudes = {len(r) for r in res}
    assert len(longitudes) == 1, (X, Y, res)       # misma longitud
    for r in res:                                  # subsecuencia comun
        assert es_subsecuencia(r, X), (X, Y, r)
        assert es_subsecuencia(r, Y), (X, Y, r)
    if esperado is not None:
        assert longitudes == {esperado}, (X, Y, res)


def main():
    # Casos limite
    comprobar("", "", 0)
    comprobar("A", "", 0)
    comprobar("ABC", "DEF", 0)
    comprobar("ABC", "ABC", 3)
    comprobar("ABCBDAB", "BDCABA", 4)
    # Ejemplo del Tema 3 (Entrenamiento 3): longitud 20
    comprobar("ACCGGTCGAGTGCGCGGAAGCCGGCCGAA",
              "GTCGTTCGGAATGCCGTTGCTCTGTAAA", 20,
              con_recursiva=False)
    # Pruebas aleatorias: las versiones deben coincidir en longitud
    rnd = random.Random(7)
    for _ in range(300):
        comprobar(cadena(rnd, 0, 9), cadena(rnd, 0, 9))
    for _ in range(30):
        comprobar(cadena(rnd, 50, 300), cadena(rnd, 50, 300),
                  con_recursiva=False)
    print("OK - todas las pruebas superadas")


if __name__ == "__main__":
    main()
