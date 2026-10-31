"""
Errores del analizador léxico.
"""


class ErrorAnalizador(Exception):
    """Clase base de todos los errores del proyecto."""


class ErrorDeSintaxis(ErrorAnalizador):

    def __init__(self, mensaje: str, expresion: str = "", posicion: int = -1):
        self.mensaje = mensaje
        self.expresion = expresion
        self.posicion = posicion
        super().__init__(mensaje)

    def __str__(self) -> str:
        if not self.expresion or self.posicion < 0:
            return self.mensaje

        # Señalador visual: la expresión y una flecha bajo el carácter culpable.
        return (
            f"{self.mensaje}\n"
            f"  {self.expresion}\n"
            f"  {' ' * self.posicion}^"
        )


class ErrorDeAutomata(ErrorAnalizador):
    """Se intentó una operación inválida sobre un AFN o un AFD."""