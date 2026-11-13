PYTHON ?= python3

# Unico comando: make  (ejecuta las pruebas y despues los experimentos)
all: test experimentos

test:
	$(PYTHON) tests.py

experimentos:
	$(PYTHON) experimentos.py

limpiar:
	rm -rf resultados __pycache__

.PHONY: all test experimentos limpiar
