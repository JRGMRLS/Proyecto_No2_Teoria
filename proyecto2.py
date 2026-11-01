"""Entrada por consola para el proyecto 2."""

import argparse
import json
from pathlib import Path

from analizador.automatas.pda import PDA
from analizador.cyk import reconocer as reconocer_cyk
from analizador.gramatica import PRODUCCIONES


def main():
    parser = argparse.ArgumentParser(
        description="Reconocimiento de frases con PDA y CYK."
    )

    parser.add_argument(
        "frase",
        nargs="?",
        help="Frase entre comillas.",
    )

    parser.add_argument(
        "--metodo",
        choices=["pda", "cyk", "ambos"],
        default="ambos",
    )

    parser.add_argument(
        "--pasos",
        action="store_true",
        help="Mostrar el registro completo.",
    )

    parser.add_argument(
        "--json",
        type=Path,
        help="Archivo donde guardar resultados y pasos.",
    )

    args = parser.parse_args()

    frase = args.frase

    if frase is None:
        frase = input("Ingrese una frase: ")

    palabras = frase.split()
    resultados = {}

    if args.metodo in ("pda", "ambos"):
        pda = PDA(PRODUCCIONES)
        resultados["PDA"] = pda.reconocer(palabras)

    if args.metodo in ("cyk", "ambos"):
        resultados["CYK"] = reconocer_cyk(
            palabras,
            PRODUCCIONES,
        )

    for metodo, resultado in resultados.items():
        estado = (
            "ACEPTADA"
            if resultado["aceptada"]
            else "RECHAZADA"
        )

        print(f"\n{metodo}: {estado}")
        print("Operaciones:", resultado["operaciones"])

        if metodo == "PDA" and resultado["aceptada"]:
            print("\nCamino aceptante:")

            for paso in resultado["camino"]:
                print(" ", paso)

        if metodo == "CYK" and resultado["aceptada"]:
            print("\nDerivación:")

            for paso in resultado["derivacion"]:
                print(" ", paso)

        if args.pasos:
            print("\nRegistro completo:")

            if metodo == "PDA":
                for paso in resultado["registro"]:
                    print(paso)
            else:
                for celda in resultado["registro"]:
                    variables = (
                        ", ".join(celda["variables"]) or "vacío"
                    )

                    print(
                        f"T[{celda['inicio']},{celda['fin']}) "
                        f"'{celda['frase']}' = {{{variables}}}"
                    )

                    for combinacion in celda["combinaciones"]:
                        print(
                            f"  corte={combinacion['corte']}: "
                            f"{combinacion['regla']}"
                        )

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)

        contenido = {
            "palabras": palabras,
            "resultados": resultados,
        }

        args.json.write_text(
            json.dumps(
                contenido,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        print(f"\nRegistro guardado en: {args.json}")


if __name__ == "__main__":
    main()