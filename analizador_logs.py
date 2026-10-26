

import re
from datetime import datetime
from collections import Counter
from tkinter import Tk, filedialog


# Niveles permitidos
NIVELES = ("INFO", "WARNING", "ERROR")

# Formatos de fecha y hora
FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M:%S"


def seleccionar_archivo():
    # Permite al usuario seleccionar un archivo de texto
    ventana = Tk()
    ventana.withdraw()

    try:
        ruta = filedialog.askopenfilename(
            title="Selecciona el archivo de logs",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )
    finally:
        ventana.destroy()

    return ruta


def analizar_linea(linea):
    
    # Analiza la severidad, la fecha, la hora y el mensaje.
    # La hora es opcional, pero debe ser válida si esta presente en la linea de texto.
    
    resultado = {
        "severidad": None,
        "fecha_valida": False,
        "hora_valida": None,
        "mensaje": "",
        "errores": [],
        "advertencias": []
    }

    # Identificar la severidad
    patron = r"^\s*\[(INFO|WARNING|ERROR)\]\s*(.*)$"
    coincidencia = re.match(patron, linea, re.IGNORECASE)

    if not coincidencia:
        resultado["errores"].append(
            "Severidad ausente o inválida"
        )
        return resultado

    resultado["severidad"] = coincidencia.group(1).upper()
    contenido = coincidencia.group(2).strip()

    if not contenido:
        resultado["errores"].append("Fecha ausente")
        return resultado

    # Separar fecha y contenido restante
    partes = contenido.split(maxsplit=1)
    texto_fecha = partes[0]

    # Validar fecha y comprobar que exista en el calendario
    try:
        datetime.strptime(texto_fecha, FORMATO_FECHA)
        resultado["fecha_valida"] = True

    except ValueError:
        resultado["errores"].append(
            "Fecha invalida o mal formateada (formato esperado: AAAA-MM-DD)"
        )
        return resultado

    restante = partes[1].strip() if len(partes) > 1 else ""

    if not restante:
        resultado["errores"].append("Mensaje ausente")
        return resultado

    # Comprobar si el contenido comienza con una hora hh:mm:ss
    partes_restantes = restante.split(maxsplit=1)
    posible_hora = partes_restantes[0]

    if re.fullmatch(r"\d{2}:\d{2}:\d{2}", posible_hora):
        try:
            datetime.strptime(posible_hora, FORMATO_HORA)
            resultado["hora_valida"] = True

            # El texto despues de la hora es el mensaje
            resultado["mensaje"] = (
                partes_restantes[1].strip()
                if len(partes_restantes) > 1
                else ""
            )

        except ValueError:
            resultado["hora_valida"] = False
            resultado["errores"].append(
                "Hora inválida (formato esperado: HH:MM:SS)"
            )
            resultado["mensaje"] = (
                partes_restantes[1].strip()
                if len(partes_restantes) > 1
                else ""
            )

    else:
        # Si parece una hora pero tiene un formato incorrecto
        # se informa como error en lugar de mensaje.
        if re.match(r"^\d{1,2}:\d{1,2}", posible_hora):
            resultado["hora_valida"] = False
            resultado["errores"].append(
                "Hora mal formateada (formato esperado: HH:MM:SS)"
            )
            resultado["mensaje"] = (
                partes_restantes[1].strip()
                if len(partes_restantes) > 1
                else ""
            )
        else:
            # No hay hora: el contenido restante es el mensaje
            resultado["hora_valida"] = None
            resultado["mensaje"] = restante

    # Verificar que exista un mensaje
    if not resultado["mensaje"]:
        resultado["errores"].append("Mensaje ausente")

    return resultado


def analizar_archivo(ruta):
    # Lee el archivo y genera las estadisticas
    conteo = Counter()
    total_eventos = 0
    lineas_incorrectas = 0
    total_advertencias = 0

    try:
        with open(ruta, "r", encoding="utf-8-sig") as archivo:
            for numero, linea in enumerate(archivo, start=1):

                # Ignorar líneas vacias
                if not linea.strip():
                    continue

                total_eventos += 1
                resultado = analizar_linea(linea.strip())

                # Contabilizar la severidad original
                if resultado["severidad"]:
                    conteo[resultado["severidad"]] += 1
                else:
                    conteo["DESCONOCIDO"] += 1

                # Informar errores
                if resultado["errores"]:
                    lineas_incorrectas += 1

                    for error in resultado["errores"]:
                        print(
                            f"Línea {numero}: ERROR - {error}"
                        )

                # Informar advertencias, si se agregan reglas futuras
                for advertencia in resultado["advertencias"]:
                    total_advertencias += 1
                    print(
                        f"Línea {numero}: ADVERTENCIA - {advertencia}"
                    )

        mostrar_resumen(
            total_eventos,
            conteo,
            lineas_incorrectas,
            total_advertencias
        )

    except (OSError, UnicodeError) as error:
        print(f"\nNo se pudo leer el archivo: {error}")


def mostrar_resumen(total, conteo, incorrectas, advertencias):
    """Muestra las estadísticas finales en consola."""
    print("\n" + "=" * 45)
    print("          RESUMEN DEL ANÁLISIS")
    print("=" * 45)

    print(f"Total de eventos: {total}")

    for nivel in (*NIVELES, "DESCONOCIDO"):
        print(f"Eventos {nivel}: {conteo[nivel]}")

    print(f"Líneas mal formateadas o incompletas: {incorrectas}")
    print(f"Total de advertencias: {advertencias}")

    print("=" * 45)


def main():
    """Punto de entrada del programa."""
    print("ANALIZADOR DE LOGS")
    print("-" * 45)

    ruta = seleccionar_archivo()

    if not ruta:
        print("No seleccionaste ningún archivo.")
        return

    print(f"\nArchivo seleccionado: {ruta}\n")
    analizar_archivo(ruta)


if __name__ == "__main__":
    main()
