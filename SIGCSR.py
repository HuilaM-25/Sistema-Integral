# SIGCSR - Sistema Integral de Gestion de Clientes, Servicios y Reservas.
# Empresa: Software FJ

# Autores:
# Robinson Meneses CC 1007201017
# Julian Coronado CC 1117486332
# Santiago Murcia CC 1084897608

# Descripción general del aplicativo:
#   Aplicación de escritorio (Tkinter) que gestiona clientes, servicios y reservas
#   completamente en memoria (objetos y listas). No usa motores de bases de datos;
#   el único archivo que se escribe es el registro de eventos "sistema_logs.txt".

import os                                   # Para ubicar el archivo de logs junto al script
import math                                 # Para detectar valores no finitos (nan / inf)
import tkinter as tk                        # Biblioteca gráfica estándar de Python
from tkinter import messagebox              # Cuadros de diálogo (info / error)
from datetime import datetime               # Fecha y hora para los logs
from abc import ABC, abstractmethod         # Soporte para clases abstractas


# SISTEMA DE LOGS (archivo plano sistema_logs.txt)


class GestorLogs:
    """Escribe eventos en un archivo de texto plano con fecha, hora, nivel y descripción.

    Nunca lanza excepciones hacia el resto del sistema: si no puede escribir en el
    archivo, lo informa por consola y continúa (el programa no debe detenerse).
    """

    def __init__(self, nombre_archivo="sistema_logs.txt"):
        # Ruta absoluta: el archivo se crea en la misma carpeta que este script.
        carpeta = os.path.dirname(os.path.abspath(__file__))
        self.__ruta = os.path.join(carpeta, nombre_archivo)

    def registrar(self, nivel, descripcion):
        """Agrega una línea al log con el formato: FECHA HORA | NIVEL | DESCRIPCIÓN."""
        # Marca de tiempo legible con fecha y hora.
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Se reemplazan saltos de línea para que cada evento ocupe una sola línea.
        texto = str(descripcion).replace("\n", " | ")
        linea = f"{marca} | {nivel:<5} | {texto}\n"
        try:
            # Modo "a" (append): conserva lo escrito anteriormente.
            archivo = open(self.__ruta, "a", encoding="utf-8")
        except OSError as error:
            # Si el archivo no se puede abrir, solo se avisa por consola.
            print(f"[LOG NO DISPONIBLE] {error}")
        else:
            # try / except / else / finally: se escribe y SIEMPRE se cierra el archivo.
            try:
                archivo.write(linea)
            except OSError as error:
                print(f"[LOG NO ESCRITO] {error}")
            finally:
                archivo.close()

    def info(self, descripcion):
        """Registra un evento informativo (operación exitosa o evento relevante)."""
        self.registrar("INFO", descripcion)

    def error(self, descripcion):
        """Registra un error o excepción capturada."""
        self.registrar("ERROR", descripcion)


# Instancia única de logs, compartida por todo el sistema.
logger = GestorLogs("sistema_logs.txt")

# EXCEPCIONES PERSONALIZADAS


class SIGCSRError(Exception):
    """Excepción base del sistema: todas las excepciones propias heredan de ella."""


class ParametroFaltanteError(SIGCSRError):
    """Se lanza cuando falta un dato obligatorio (vacío o None)."""


class ParametroInvalidoError(SIGCSRError):
    """Se lanza cuando un dato existe pero su valor/formato no es válido."""


class ServicioNoDisponibleError(SIGCSRError):
    """Se lanza cuando el servicio no existe o está marcado como no disponible."""


class ReservaInvalidaError(SIGCSRError):
    """Se lanza cuando una reserva tiene datos inconsistentes (duración, cliente...)."""


class OperacionNoPermitidaError(SIGCSRError):
    """Se lanza cuando una operación no es válida para el estado actual del objeto."""


class CalculoInconsistenteError(SIGCSRError):
    """Se lanza cuando el cálculo de un costo produce un resultado no coherente."""


def convertir_numero(valor, nombre_campo, entero=False):
    """Convierte 'valor' a número validando que exista y que sea numérico.

    - Lanza ParametroFaltanteError si el valor es None o texto vacío.
    - Lanza ParametroInvalidoError (encadenada con 'from') si no es convertible.
    """
    # Un valor None o una cadena en blanco equivale a "dato faltante".
    if valor is None or not str(valor).strip():
        raise ParametroFaltanteError(f"Falta el parámetro obligatorio: {nombre_campo}.")
    try:
        # Se convierte a entero o decimal según lo solicitado.
        return int(str(valor).strip()) if entero else float(str(valor).strip())
    except (TypeError, ValueError) as error_original:
        # ENCADENAMIENTO DE EXCEPCIONES: la nueva excepción conserva la causa original.
        tipo = "un número entero" if entero else "un número"
        raise ParametroInvalidoError(
            f"El campo '{nombre_campo}' debe ser {tipo}."
        ) from error_original

# USUARIO Y ARQUITECTURA BASE


class Usuario:
    """Representa al usuario autorizado para ingresar al sistema."""

    def __init__(self):
        # Credenciales por defecto (encapsuladas como atributos "protegidos").
        self._usuario = "Grupo"
        self._password = "1234"

    def validar(self, usuario_ingresado, password_ingresada):
        """Retorna True solo si usuario y contraseña coinciden."""
        return usuario_ingresado == self._usuario and password_ingresada == self._password


# Robin:________________________Clase abstracta sistema
class Entidad(ABC):
    """Clase abstracta base de todas las entidades del sistema (clientes, servicios, reservas)."""

    def __init__(self, identificador):
        # Atributo privado: solo se accede mediante el getter.
        self.__identificador = identificador

    def obtener_identificador(self):
        """Devuelve el identificador único de la entidad."""
        return self.__identificador

    @abstractmethod
    def mostrar_informacion(self):
        """Cada entidad concreta debe devolver su información como texto."""
        pass


# MÓDULO DE CLIENTES + LOGS


class Cliente(Entidad):
    """Cliente de Software FJ con datos encapsulados y validados."""

    def __init__(self, identificador, nombre, cedula, correo):
        super().__init__(identificador)

        # Robin:______________Validacion de datos del cliente
        if not str(identificador).strip():
            raise ValueError("Insertar datos para validar.")

        if not nombre.strip():
            raise ValueError("Insertar nombre.")

        if not str(cedula).strip().isdigit():
            raise ValueError("La cedula debe contener solo números.")

        if not correo.strip() or "@" not in correo or "." not in correo:
            raise ValueError("El correo electronico no es valido.")

        # Atributos privados (encapsulamiento).
        self.__nombre = nombre
        self.__cc = cedula
        self.__correo = correo

    def obtener_nombre(self):
        """Getter del nombre (necesario para mostrar datos en las reservas)."""
        return self.__nombre

    def mostrar_informacion(self):
        """Devuelve los datos del cliente en varias líneas."""
        return (
            f"Cliente ID: {self.obtener_identificador()}\n"
            f"Nombre: {self.__nombre}\n"
            f"Cedula: {self.__cc}\n"
            f"Correo: {self.__correo}"
        )


# Robin:_________Gestion de clientes.
class GestorClientes:
    """Almacena y administra los clientes en una lista privada (memoria)."""

    def __init__(self):
        self.__clientes = []

    def registrar_cliente(self, identificador, nombre, cedula, correo):
        """Registra un cliente nuevo. Lanza ValueError si hay duplicado o datos inválidos."""
        try:
            # Se evita el duplicado por identificador.
            for cliente in self.__clientes:
                if str(cliente.obtener_identificador()) == str(identificador):
                    raise ValueError("El cliente ya existe.")
            # La construcción valida todos los datos (puede lanzar ValueError).
            nuevo_cliente = Cliente(identificador, nombre, cedula, correo)
        except ValueError as error:
            # Se deja constancia en el log y se relanza para que la interfaz lo muestre.
            logger.error(f"Registro de cliente fallido (ID '{identificador}'): {error}")
            raise
        else:
            # Solo si no hubo errores se agrega a la lista y se registra el evento.
            self.__clientes.append(nuevo_cliente)
            logger.info(f"Cliente registrado correctamente: ID {identificador} - {nombre}")
            return "Cliente registrado correctamente."

    def listar_clientes(self):
        """Devuelve una copia de la lista (protege la lista interna)."""
        return self.__clientes.copy()

    def buscar_cliente(self, identificador):
        """Busca un cliente por ID; lanza ReservaInvalidaError si no existe."""
        for cliente in self.__clientes:
            if str(cliente.obtener_identificador()) == str(identificador).strip():
                return cliente
        raise ReservaInvalidaError(f"No existe un cliente con ID '{identificador}'.")





