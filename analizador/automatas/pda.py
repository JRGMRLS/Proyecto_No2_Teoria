"""PDA construido desde una gramática en CNF sin epsilon."""

from collections import deque

from .afn import AFN
from ..tokens import EPSILON


class PDA(AFN):
    def __init__(self, producciones, inicial="S"):
        super().__init__(inicial=0, aceptacion=())

        if inicial not in producciones:
            raise ValueError("El símbolo inicial no tiene producciones.")

        variables = set(producciones)

        # La poda del simulador requiere CNF sin epsilon.
        for reglas in producciones.values():
            for rhs in reglas:
                es_terminal = (
                    len(rhs) == 1
                    and rhs[0] not in variables
                    and rhs[0] != EPSILON
                )

                es_binaria = (
                    len(rhs) == 2
                    and all(simbolo in variables for simbolo in rhs)
                )

                if not (es_terminal or es_binaria):
                    raise ValueError("Se requiere CNF sin epsilon.")

        self.simbolo_inicial = inicial
        self.alfabeto_pila = set(variables)
        self.transiciones_pila = {}

        terminales = {
            simbolo
            for reglas in producciones.values()
            for rhs in reglas
            for simbolo in rhs
            if simbolo not in variables
        }

        self.alfabeto.update(terminales)
        self.alfabeto_pila.update(terminales)

        # Expandir variables sin consumir entrada.
        for variable, reglas in producciones.items():
            self.transiciones_pila[0, EPSILON, variable] = [
                (0, tuple(rhs)) for rhs in reglas
            ]

        # Consumir una palabra cuando coincide con la cima.
        for terminal in sorted(terminales):
            self.transiciones_pila[0, terminal, terminal] = [
                (0, ())
            ]

    def reconocer(self, palabras):
        palabras = tuple(palabras)
        n = len(palabras)

        # Configuración: (estado, posición de entrada, pila).
        # La cima de la pila está a la izquierda.
        inicio = (self.inicial, 0, (self.simbolo_inicial,))

        pendientes = deque([inicio])
        padres = {inicio: None}
        registro = []

        final = None
        configuraciones = 0
        transiciones = 0

        def describir(configuracion):
            estado, posicion, pila = configuracion
            restante = " ".join(palabras[posicion:]) or EPSILON
            contenido = " ".join(pila) or EPSILON

            return f"(q{estado}, {restante}, {contenido})"

        while pendientes:
            actual = pendientes.popleft()
            estado, posicion, pila = actual

            configuraciones += 1
            registro.append(f"Examinar {describir(actual)}")

            if not pila:
                if posicion == n:
                    final = actual
                    registro.append(
                        "Entrada agotada y pila vacía: aceptar."
                    )
                    break

                registro.append(
                    "Bloqueada: queda entrada y la pila está vacía."
                )
                continue

            # Cada símbolo de pila necesita al menos una palabra.
            if len(pila) > n - posicion:
                registro.append(
                    "Podada: pila mayor que entrada restante."
                )
                continue

            entradas = [EPSILON]

            if posicion < n and palabras[posicion] != EPSILON:
                entradas.append(palabras[posicion])

            hubo_transicion = False

            for entrada in entradas:
                clave = (estado, entrada, pila[0])

                for destino, reemplazo in self.transiciones_pila.get(
                    clave, []
                ):
                    hubo_transicion = True
                    transiciones += 1

                    nueva_posicion = posicion + int(entrada != EPSILON)
                    nueva_pila = reemplazo + pila[1:]

                    descripcion = (
                        f"  entrada={entrada}, cima={pila[0]}, "
                        f"reemplazo={' '.join(reemplazo) or EPSILON}"
                    )

                    if len(nueva_pila) > n - nueva_posicion:
                        registro.append(descripcion + " -> podada")
                        continue

                    siguiente = (
                        destino,
                        nueva_posicion,
                        nueva_pila,
                    )

                    if siguiente in padres:
                        registro.append(
                            descripcion + " -> ya visitada"
                        )
                        continue

                    padres[siguiente] = actual
                    pendientes.append(siguiente)
                    registro.append(descripcion + " -> encolada")

            if not hubo_transicion:
                registro.append(
                    "Bloqueada: no hay transición aplicable."
                )

        aceptada = final is not None
        camino = []

        if aceptada:
            while final is not None:
                camino.append(describir(final))
                final = padres[final]

            camino.reverse()
        else:
            registro.append(
                "No quedan configuraciones viables: rechazar."
            )

        return {
            "aceptada": aceptada,
            "camino": camino,
            "registro": registro,
            "operaciones": {
                "configuraciones": configuraciones,
                "transiciones_intentadas": transiciones,
            },
        }