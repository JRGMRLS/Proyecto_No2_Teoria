"""Algoritmo CYK para la gramática del proyecto."""


def reconocer(palabras, producciones, inicial="S"):
    palabras = tuple(palabras)
    n = len(palabras)

    lexicas = [
        (variable, rhs[0])
        for variable, reglas in producciones.items()
        for rhs in reglas
        if len(rhs) == 1
    ]

    binarias = [
        (variable, rhs[0], rhs[1])
        for variable, reglas in producciones.items()
        for rhs in reglas
        if len(rhs) == 2
    ]

    # tabla[i][j]: variables que generan palabras[i:j].
    tabla = [
        [set() for _ in range(n + 1)]
        for _ in range(n)
    ]

    testigos = {}
    registro = []

    pruebas_lexicas = 0
    pruebas_binarias = 0

    # Inicializar intervalos de una palabra.
    for i, palabra in enumerate(palabras):
        for variable, terminal in lexicas:
            pruebas_lexicas += 1

            if palabra == terminal:
                tabla[i][i + 1].add(variable)
                testigos[i, i + 1, variable] = (palabra,)

        registro.append({
            "inicio": i,
            "fin": i + 1,
            "frase": palabra,
            "variables": sorted(tabla[i][i + 1]),
            "combinaciones": [],
        })

    # Completar intervalos de dos o más palabras.
    for longitud in range(2, n + 1):
        for i in range(n - longitud + 1):
            j = i + longitud
            combinaciones = []

            for k in range(i + 1, j):
                for variable, izquierda, derecha in binarias:
                    pruebas_binarias += 1

                    if (
                        izquierda in tabla[i][k]
                        and derecha in tabla[k][j]
                    ):
                        tabla[i][j].add(variable)

                        testigos.setdefault(
                            (i, j, variable),
                            (k, izquierda, derecha),
                        )

                        combinaciones.append({
                            "corte": k,
                            "regla": (
                                f"{variable} -> "
                                f"{izquierda} {derecha}"
                            ),
                        })

            registro.append({
                "inicio": i,
                "fin": j,
                "frase": " ".join(palabras[i:j]),
                "variables": sorted(tabla[i][j]),
                "combinaciones": combinaciones,
            })

    aceptada = n > 0 and inicial in tabla[0][n]

    # Reconstruir una derivación izquierda.
    derivacion = []

    if aceptada:
        forma = [(0, n, inicial)]
        derivacion.append(inicial)

        while any(isinstance(elemento, tuple) for elemento in forma):
            indice = next(
                i
                for i, elemento in enumerate(forma)
                if isinstance(elemento, tuple)
            )

            i, j, variable = forma[indice]
            testigo = testigos[i, j, variable]

            if len(testigo) == 1:
                reemplazo = [testigo[0]]
            else:
                k, izquierda, derecha = testigo

                reemplazo = [
                    (i, k, izquierda),
                    (k, j, derecha),
                ]

            forma[indice:indice + 1] = reemplazo

            derivacion.append(
                " ".join(
                    elemento[2]
                    if isinstance(elemento, tuple)
                    else elemento
                    for elemento in forma
                )
            )

    return {
        "aceptada": aceptada,
        "derivacion": derivacion,
        "registro": registro,
        "operaciones": {
            "pruebas_lexicas": pruebas_lexicas,
            "pruebas_binarias": pruebas_binarias,
        },
    }