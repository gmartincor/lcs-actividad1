"""
lcs.py - Tres algoritmos para la subsecuencia comun mas larga (LCS).

  Version A: recursiva directa (sin memorizacion).
  Version B: divide y conquista de Hirschberg (espacio lineal).
  Version C: programacion dinamica tabular.

Las tres funciones reciben dos cadenas X e Y y devuelven una LCS.
No se usa ninguna libreria externa especifica de LCS.
"""
import sys

sys.setrecursionlimit(100000)


# ----------------------------------------------------------------
# Version A - Recursiva directa
# ----------------------------------------------------------------
def lcs_recursiva(X, Y):
    """LCS por recursion directa sobre los prefijos X[0..i), Y[0..j).

    Peor caso (s = i + j): T(s) = 2 T(s-1) + c  ->  O(2^(m+n)).
    """
    def rec(i, j):
        if i == 0 or j == 0:              # caso base: prefijo vacio
            return ""
        if X[i - 1] == Y[j - 1]:          # ultimo simbolo comun
            return rec(i - 1, j - 1) + X[i - 1]
        a = rec(i - 1, j)                 # descartar ultimo de X
        b = rec(i, j - 1)                 # descartar ultimo de Y
        return a if len(a) >= len(b) else b

    return rec(len(X), len(Y))


# ----------------------------------------------------------------
# Version B - Divide y conquista de Hirschberg
# ----------------------------------------------------------------
def _ultima_fila(X, xi, xf, Y, yi, yf, inverso):
    """Ultima fila de la tabla de PD de X[xi:xf] frente a Y[yi:yf]
    guardando solo dos filas (espacio O(n)). Con inverso=True se
    recorren ambas subcadenas al reves (sufijos en vez de prefijos).
    """
    xs, ys = X[xi:xf], Y[yi:yf]
    if inverso:
        xs, ys = xs[::-1], ys[::-1]
    n = len(ys)
    previa = [0] * (n + 1)
    fila = [0] * (n + 1)
    for c in xs:
        for j in range(1, n + 1):
            if c == ys[j - 1]:
                fila[j] = previa[j - 1] + 1
            else:
                a, b = previa[j], fila[j - 1]
                fila[j] = a if a >= b else b
        previa, fila = fila, previa       # reutiliza las dos filas
    return previa


def lcs_hirschberg(X, Y):
    """DIVIDE X por la mitad y halla el corte k de Y con dos pasadas
    en espacio lineal; VENCE resolviendo (X1, Y[:k]) y (X2, Y[k:]);
    COMBINA concatenando ambas subsoluciones.

    Caso equilibrado: T(n) = 2 T(n/2) + c n^2  ->  O(n^2).
    Tiempo O(m*n); espacio O(m + n) (la recursion usa indices).
    """
    res = []

    def rec(xi, xf, yi, yf):
        m, n = xf - xi, yf - yi
        if m == 0 or n == 0:              # caso base trivial
            return
        if m == 1:                        # caso base: un simbolo
            if Y.find(X[xi], yi, yf) != -1:
                res.append(X[xi])
            return
        mid = xi + m // 2                 # DIVIDIR
        izq = _ultima_fila(X, xi, mid, Y, yi, yf, False)
        der = _ultima_fila(X, mid, xf, Y, yi, yf, True)
        mejor, k = -1, yi
        for j in range(n + 1):            # corte optimo de Y
            v = izq[j] + der[n - j]
            if v > mejor:
                mejor, k = v, yi + j
        rec(xi, mid, yi, k)               # VENCER (izquierda)
        rec(mid, xf, k, yf)               # VENCER (derecha)

    rec(0, len(X), 0, len(Y))
    return "".join(res)                   # COMBINAR


# ----------------------------------------------------------------
# Version C - Programacion dinamica tabular
# ----------------------------------------------------------------
def lcs_pd(X, Y):
    """Tabla L[m+1][n+1] rellenada de arriba abajo y de izquierda a
    derecha:
        L[i][j] = L[i-1][j-1] + 1              si X[i] = Y[j]
        L[i][j] = max(L[i-1][j], L[i][j-1])    en otro caso
    Tiempo O(m*n), espacio O(m*n). La LCS se reconstruye desde L[m][n].
    """
    m, n = len(X), len(Y)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        xi = X[i - 1]
        fila, previa = L[i], L[i - 1]
        for j in range(1, n + 1):
            if xi == Y[j - 1]:
                fila[j] = previa[j - 1] + 1
            else:
                a, b = previa[j], fila[j - 1]
                fila[j] = a if a >= b else b
    # Reconstruccion de la solucion recorriendo la tabla hacia atras
    res = []
    i, j = m, n
    while i > 0 and j > 0:
        if X[i - 1] == Y[j - 1]:
            res.append(X[i - 1])
            i -= 1
            j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(res))


VERSIONES = {
    "A": ("Recursiva directa", lcs_recursiva),
    "B": ("Divide y conquista (Hirschberg)", lcs_hirschberg),
    "C": ("Programacion dinamica tabular", lcs_pd),
}


def es_subsecuencia(s, T):
    """True si s es subsecuencia de T."""
    it = iter(T)
    return all(c in it for c in s)
