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


#MÓDULO DE SERVICIOS


# Constantes del negocio usadas en las variantes de cálculo.
TASA_IVA = 0.19                 # IVA del 19 %
DESCUENTO_FRECUENTE = 0.10      # 10 % de descuento a clientes frecuentes


class Servicio(Entidad):
    """Clase abstracta de un servicio ofrecido por Software FJ.

    El código del servicio se guarda como identificador de la entidad padre.
    """

    def __init__(self, codigo, nombre, tarifa_base, disponible=True):
        # Validación del código (dato obligatorio).
        if codigo is None or not str(codigo).strip():
            raise ParametroFaltanteError("El código del servicio es obligatorio.")
        super().__init__(str(codigo).strip())

        # Validación del nombre (dato obligatorio).
        if nombre is None or not str(nombre).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")

        # La tarifa debe ser numérica y positiva.
        tarifa = convertir_numero(tarifa_base, "tarifa base")
        if tarifa <= 0:
            raise ParametroInvalidoError("La tarifa base debe ser mayor que cero.")

        # Atributos encapsulados (privados).
        self.__nombre = str(nombre).strip()
        self.__tarifa_base = tarifa
        self.__disponible = bool(disponible)

    # ---- Propiedades (acceso controlado a los atributos privados) ----
    @property
    def codigo(self):
        """Código único del servicio."""
        return self.obtener_identificador()

    @property
    def nombre(self):
        """Nombre del servicio."""
        return self.__nombre

    @property
    def tarifa_base(self):
        """Tarifa base (por hora o por unidad/día según el servicio)."""
        return self.__tarifa_base

    @property
    def disponible(self):
        """Indica si el servicio puede reservarse."""
        return self.__disponible

    @disponible.setter
    def disponible(self, valor):
        """Permite activar o desactivar el servicio."""
        self.__disponible = bool(valor)

    # ---- Métodos abstractos (cada hijo los sobrescribe: POLIMORFISMO) ----
    @abstractmethod
    def calcular_costo(self, duracion, *args, **kwargs):
        """Calcula el costo total. Sobrecargado con *args/**kwargs (iva, cliente_frecuente, recargo)."""

    @abstractmethod
    def describir_servicio(self):
        """Devuelve una descripción de una línea del servicio."""

    @abstractmethod
    def validar_parametros(self):
        """Valida los parámetros propios del servicio; lanza excepciones propias si falla."""

    # ---- Utilidades comunes para la SOBRECARGA de cálculo ----
    @staticmethod
    def _extraer_variantes(args, kwargs):
        """Interpreta las variantes de cálculo recibidas por posición (*args) o nombre (**kwargs).

        Orden posicional admitido: (iva, cliente_frecuente, recargo).
        Ejemplos válidos:
            calcular_costo(3)                          -> sin variantes
            calcular_costo(3, True)                    -> con IVA
            calcular_costo(3, True, True, 15000)       -> IVA + descuento + recargo
            calcular_costo(3, cliente_frecuente=True)  -> solo descuento
        """
        nombres = ("iva", "cliente_frecuente", "recargo")
        if len(args) > len(nombres):
            raise ParametroInvalidoError("Demasiados parámetros opcionales en el cálculo.")
        # Valores por defecto de cada variante.
        opciones = {"iva": False, "cliente_frecuente": False, "recargo": 0.0}
        # Se asignan los argumentos posicionales en orden.
        opciones.update(zip(nombres, args))
        # Se asignan los argumentos con nombre, rechazando los desconocidos.
        for clave, valor in kwargs.items():
            if clave not in opciones:
                raise ParametroInvalidoError(f"Opción de cálculo desconocida: '{clave}'.")
            opciones[clave] = valor
        return opciones

    @staticmethod
    def _aplicar_variantes(subtotal, opciones):
        """Aplica descuento, recargo adicional e IVA sobre el subtotal calculado."""
        recargo = convertir_numero(opciones["recargo"], "recargo")
        if recargo < 0:
            raise ParametroInvalidoError("El recargo adicional no puede ser negativo.")
        total = subtotal
        if opciones["cliente_frecuente"]:
            total -= subtotal * DESCUENTO_FRECUENTE    # Descuento por cliente frecuente
        total += recargo                               # Recargo adicional
        if opciones["iva"]:
            total *= (1 + TASA_IVA)                    # Impuesto (IVA)
        return round(total, 2)

    def mostrar_informacion(self):
        """Implementa el método abstracto de Entidad usando la descripción del servicio."""
        return self.describir_servicio()


class ReservaSala(Servicio):
    """Reserva de salas: tarifa por hora, con capacidad y recargo por equipo audiovisual."""

    MAX_HORAS = 12                  # Máximo de horas por reserva
    MAX_CAPACIDAD = 200             # Capacidad máxima admitida
    RECARGO_AUDIOVISUAL = 0.15      # 15 % del subtotal si incluye audiovisuales

    def __init__(self, codigo, nombre, tarifa_base, capacidad, audiovisual=False, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.__capacidad = convertir_numero(capacidad, "capacidad", entero=True)
        self.__audiovisual = bool(audiovisual)
        # Se validan los parámetros propios apenas se crea el objeto.
        self.validar_parametros()

    def validar_parametros(self):
        """La capacidad debe estar entre 1 y MAX_CAPACIDAD personas."""
        if not 1 <= self.__capacidad <= self.MAX_CAPACIDAD:
            raise ParametroInvalidoError(
                f"La capacidad debe estar entre 1 y {self.MAX_CAPACIDAD} personas."
            )

    def calcular_costo(self, duracion, *args, **kwargs):
        """Costo = tarifa x horas (+15 % si hay audiovisual), más variantes opcionales."""
        horas = convertir_numero(duracion, "horas")
        if not 0 < horas <= self.MAX_HORAS:
            raise ReservaInvalidaError(f"Las horas deben estar entre 1 y {self.MAX_HORAS}.")
        subtotal = self.tarifa_base * horas
        if self.__audiovisual:
            subtotal += subtotal * self.RECARGO_AUDIOVISUAL
        return self._aplicar_variantes(subtotal, self._extraer_variantes(args, kwargs))

    def describir_servicio(self):
        """Descripción en una línea."""
        av = "con audiovisual" if self.__audiovisual else "sin audiovisual"
        estado = "Disponible" if self.disponible else "NO disponible"
        return (f"[Sala] {self.codigo} - {self.nombre} | Cap: {self.__capacidad} | "
                f"{av} | ${self.tarifa_base:,.0f}/hora | {estado}")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos: tarifa por unidad y por día, con seguro opcional."""

    MAX_CANTIDAD = 100              # Máximo de unidades por alquiler
    MAX_DIAS = 30                   # Máximo de días por alquiler
    TASA_SEGURO = 0.08              # 8 % del subtotal si se contrata seguro

    def __init__(self, codigo, nombre, tarifa_base, cantidad, seguro=False, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.__cantidad = convertir_numero(cantidad, "cantidad", entero=True)
        self.__seguro = bool(seguro)
        self.validar_parametros()

    def validar_parametros(self):
        """La cantidad de unidades debe estar entre 1 y MAX_CANTIDAD."""
        if not 1 <= self.__cantidad <= self.MAX_CANTIDAD:
            raise ParametroInvalidoError(
                f"La cantidad debe estar entre 1 y {self.MAX_CANTIDAD} unidades."
            )

    def calcular_costo(self, duracion, *args, **kwargs):
        """Costo = tarifa x unidades x días (+8 % si hay seguro), más variantes opcionales."""
        dias = convertir_numero(duracion, "días")
        if not 0 < dias <= self.MAX_DIAS:
            raise ReservaInvalidaError(f"Los días deben estar entre 1 y {self.MAX_DIAS}.")
        subtotal = self.tarifa_base * self.__cantidad * dias
        if self.__seguro:
            subtotal += subtotal * self.TASA_SEGURO
        return self._aplicar_variantes(subtotal, self._extraer_variantes(args, kwargs))

    def describir_servicio(self):
        """Descripción en una línea."""
        seg = "con seguro" if self.__seguro else "sin seguro"
        estado = "Disponible" if self.disponible else "NO disponible"
        return (f"[Equipo] {self.codigo} - {self.nombre} | Unid: {self.__cantidad} | "
                f"{seg} | ${self.tarifa_base:,.0f}/unidad-día | {estado}")


class AsesoriaEspecializada(Servicio):
    """Asesoría profesional: tarifa por hora multiplicada según el nivel del asesor."""

    MAX_HORAS = 8                   # Máximo de horas por sesión
    # Multiplicador de la tarifa profesional según el nivel.
    NIVELES = {"JUNIOR": 1.0, "SENIOR": 1.3, "EXPERTO": 1.6}

    def __init__(self, codigo, nombre, tarifa_base, especialidad, nivel="Junior", disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        # La especialidad es obligatoria.
        if especialidad is None or not str(especialidad).strip():
            raise ParametroFaltanteError("La especialidad de la asesoría es obligatoria.")
        self.__especialidad = str(especialidad).strip()
        self.__nivel = str(nivel).strip().upper() if nivel else "JUNIOR"
        self.validar_parametros()

    def validar_parametros(self):
        """El nivel debe ser Junior, Senior o Experto."""
        if self.__nivel not in self.NIVELES:
            raise ParametroInvalidoError("El nivel debe ser Junior, Senior o Experto.")

    def calcular_costo(self, duracion, *args, **kwargs):
        """Costo = tarifa x multiplicador de nivel x horas, más variantes opcionales."""
        horas = convertir_numero(duracion, "horas")
        if not 0 < horas <= self.MAX_HORAS:
            raise ReservaInvalidaError(f"Las horas deben estar entre 1 y {self.MAX_HORAS}.")
        subtotal = self.tarifa_base * self.NIVELES[self.__nivel] * horas
        return self._aplicar_variantes(subtotal, self._extraer_variantes(args, kwargs))

    def describir_servicio(self):
        """Descripción en una línea."""
        estado = "Disponible" if self.disponible else "NO disponible"
        return (f"[Asesoría] {self.codigo} - {self.nombre} | {self.__especialidad} | "
                f"Nivel: {self.__nivel.title()} | ${self.tarifa_base:,.0f}/hora | {estado}")


class GestorServicios:
    """Administra los servicios registrados (lista privada en memoria)."""

    def __init__(self):
        self.__servicios = []

    def registrar_servicio(self, servicio):
        """Agrega un servicio ya construido; evita códigos duplicados."""
        if any(s.codigo == servicio.codigo for s in self.__servicios):
            raise OperacionNoPermitidaError(f"Ya existe un servicio con código '{servicio.codigo}'.")
        self.__servicios.append(servicio)
        logger.info(f"Servicio registrado: {servicio.describir_servicio()}")
        return "Servicio registrado correctamente."

    def crear_servicio(self, tipo, codigo, nombre, tarifa_base, extra1="", extra2="", opcion=False):
        """Fábrica de servicios a partir de datos de texto (los que llegan de la interfaz).

        tipo: 'sala' | 'equipo' | 'asesoria'
          sala     -> extra1 = capacidad,  opcion = audiovisual
          equipo   -> extra1 = cantidad,   opcion = seguro
          asesoria -> extra1 = especialidad, extra2 = nivel
        """
        try:
            if tipo == "sala":
                servicio = ReservaSala(codigo, nombre, tarifa_base, extra1, opcion)
            elif tipo == "equipo":
                servicio = AlquilerEquipo(codigo, nombre, tarifa_base, extra1, opcion)
            elif tipo == "asesoria":
                servicio = AsesoriaEspecializada(codigo, nombre, tarifa_base, extra1, extra2)
            else:
                raise ParametroInvalidoError(f"Tipo de servicio desconocido: '{tipo}'.")
            mensaje = self.registrar_servicio(servicio)
        except SIGCSRError as error:
            # Se registra el fallo y se relanza para que lo gestione quien llamó.
            logger.error(f"Creación de servicio fallida (tipo '{tipo}', código '{codigo}'): "
                         f"{type(error).__name__}: {error}")
            raise
        else:
            return mensaje

    def buscar_servicio(self, codigo):
        """Devuelve el servicio con ese código o lanza ServicioNoDisponibleError."""
        for servicio in self.__servicios:
            if servicio.codigo == str(codigo).strip():
                return servicio
        raise ServicioNoDisponibleError(f"El servicio '{codigo}' no existe.")

    def listar_servicios(self):
        """Devuelve una copia de la lista de servicios."""
        return self.__servicios.copy()

# MÓDULO DE RESERVAS


class Reserva(Entidad):
    """Reserva que une un Cliente, un Servicio, una duración y un estado."""

    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"

    def __init__(self, identificador, cliente, servicio, duracion, **opciones):
        super().__init__(identificador)
        # Se valida que los objetos recibidos sean del tipo correcto.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")
        # La duración debe ser un número positivo.
        duracion_num = convertir_numero(duracion, "duración")
        if duracion_num <= 0:
            raise ReservaInvalidaError("La duración debe ser mayor que cero.")

        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion_num
        self.__opciones = opciones          # iva / cliente_frecuente / recargo
        self.__estado = self.PENDIENTE      # Toda reserva nace Pendiente
        self.__total = 0.0

    @property
    def estado(self):
        """Estado actual de la reserva."""
        return self.__estado

    @property
    def total(self):
        """Total calculado (0 hasta que se procese)."""
        return self.__total

    @property
    def servicio(self):
        """Servicio reservado."""
        return self.__servicio

    def procesar_reserva(self):
        """Valida disponibilidad, duración y consistencia del cálculo; guarda el total.

        Usa try / except / else / finally y encadenamiento de excepciones.
        """
        logger.info(f"Procesando reserva {self.obtener_identificador()}...")
        try:
            # 1) El servicio debe estar disponible.
            if not self.__servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.__servicio.codigo}' no está disponible."
                )
            # 2) La duración debe ser válida.
            if self.__duracion <= 0:
                raise ReservaInvalidaError("La duración de la reserva no es válida.")
            # 3) Cálculo del costo; los errores aritméticos/de tipo se encadenan.
            try:
                total = self.__servicio.calcular_costo(self.__duracion, **self.__opciones)
            except (TypeError, ArithmeticError) as error_original:
                raise CalculoInconsistenteError(
                    "No fue posible calcular el costo de la reserva."
                ) from error_original
            # 4) El total debe ser un número finito y positivo.
            if (not isinstance(total, (int, float)) or math.isnan(total)
                    or math.isinf(total) or total <= 0):
                raise CalculoInconsistenteError(f"Total inconsistente: {total}.")
        except SIGCSRError as error:
            # Se deja constancia del fallo y se relanza.
            logger.error(f"Reserva {self.obtener_identificador()} no procesada: "
                         f"{type(error).__name__}: {error}")
            raise
        else:
            # Solo si todo salió bien se guarda el total.
            self.__total = total
            logger.info(f"Reserva {self.obtener_identificador()} procesada. Total: ${total:,.2f}")
            return total
        finally:
            # Se ejecuta SIEMPRE, haya o no error.
            logger.info(f"Fin del procesamiento de la reserva {self.obtener_identificador()}.")

    def confirmar(self):
        """Confirma la reserva (solo si está Pendiente y se procesa correctamente)."""
        try:
            if self.__estado == self.CANCELADA:
                raise OperacionNoPermitidaError("No se puede confirmar una reserva cancelada.")
            if self.__estado == self.CONFIRMADA:
                raise OperacionNoPermitidaError("La reserva ya está confirmada.")
            self.procesar_reserva()
        except SIGCSRError as error:
            logger.error(f"Confirmación fallida de {self.obtener_identificador()}: "
                         f"{type(error).__name__}: {error}")
            raise
        else:
            self.__estado = self.CONFIRMADA
            logger.info(f"Reserva {self.obtener_identificador()} CONFIRMADA.")
            return "Reserva confirmada correctamente."

    def cancelar(self):
        """Cancela la reserva (no se puede cancelar dos veces)."""
        try:
            if self.__estado == self.CANCELADA:
                raise OperacionNoPermitidaError("La reserva ya estaba cancelada.")
        except OperacionNoPermitidaError as error:
            logger.error(f"Cancelación fallida de {self.obtener_identificador()}: {error}")
            raise
        else:
            self.__estado = self.CANCELADA
            logger.info(f"Reserva {self.obtener_identificador()} CANCELADA.")
            return "Reserva cancelada correctamente."

    def mostrar_informacion(self):
        """Resumen de una línea de la reserva."""
        return (f"{self.obtener_identificador()} | Cliente: {self.__cliente.obtener_nombre()} | "
                f"Servicio: {self.__servicio.nombre} | Duración: {self.__duracion:g} | "
                f"Estado: {self.__estado} | Total: ${self.__total:,.2f}")


class GestorReservas:
    """Crea y administra reservas usando los gestores de clientes y servicios."""

    def __init__(self, gestor_clientes, gestor_servicios):
        self.__reservas = []
        self.__gc = gestor_clientes
        self.__gs = gestor_servicios
        self.__contador = 0                 # Para generar IDs R001, R002...

    def crear_reserva(self, id_cliente, codigo_servicio, duracion, **opciones):
        """Crea una reserva Pendiente validando cliente, servicio y duración."""
        try:
            cliente = self.__gc.buscar_cliente(id_cliente)           # Puede lanzar ReservaInvalidaError
            servicio = self.__gs.buscar_servicio(codigo_servicio)    # Puede lanzar ServicioNoDisponibleError
            if not servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{codigo_servicio}' no está disponible.")
            identificador = f"R{self.__contador + 1:03d}"
            reserva = Reserva(identificador, cliente, servicio, duracion, **opciones)
        except SIGCSRError as error:
            logger.error(f"Creación de reserva fallida: {type(error).__name__}: {error}")
            raise
        else:
            self.__contador += 1
            self.__reservas.append(reserva)
            logger.info(f"Reserva {identificador} creada (Pendiente) para cliente {id_cliente}.")
            return reserva

    def buscar_reserva(self, identificador):
        """Devuelve la reserva con ese ID o lanza ReservaInvalidaError."""
        for reserva in self.__reservas:
            if reserva.obtener_identificador() == str(identificador).strip():
                return reserva
        raise ReservaInvalidaError(f"No existe la reserva '{identificador}'.")

    def confirmar_reserva(self, identificador):
        """Confirma una reserva existente."""
        return self.buscar_reserva(identificador).confirmar()

    def cancelar_reserva(self, identificador):
        """Cancela una reserva existente."""
        return self.buscar_reserva(identificador).cancelar()

    def listar_reservas(self):
        """Devuelve una copia de la lista de reservas."""
        return self.__reservas.copy()


# Gestores globales usados por la interfaz gráfica.
# Robin:__________________Ventana Abministrar clientes.
gestor_clientes = GestorClientes()
gestor_servicios = GestorServicios()
gestor_reservas = GestorReservas(gestor_clientes, gestor_servicios)

# Ventanas de Tkinter (se crean en main()).
ventana = None
entrada_usuario = None
entrada_password = None

#SIMULACIÓN DE OPERACIONES


def ejecutar_simulacion():
    """Ejecuta 20 operaciones variadas y controladas; devuelve las líneas de resultado.

    Usa gestores NUEVOS y aislados para que la simulación sea repetible y no
    mezcle datos de prueba con los del usuario. Todo error se captura, se muestra
    y se escribe en sistema_logs.txt sin interrumpir el programa.
    """
    logger.info("===== INICIO DE LA SIMULACIÓN DE PRUEBAS =====")
    gc = GestorClientes()
    gs = GestorServicios()
    gr = GestorReservas(gc, gs)
    resultados = []         # Líneas que se mostrarán en pantalla
    contador = [0]          # Lista para poder modificarlo dentro de la función interna

    def paso(descripcion, accion):
        """Ejecuta una operación, captura cualquier error y anota el resultado."""
        contador[0] += 1
        etiqueta = f"{contador[0]:02d}. {descripcion}"
        try:
            salida = accion()
        except (SIGCSRError, ValueError) as error:
            # Errores esperados (propios del sistema o de validación de clientes).
            logger.error(f"[Simulación] {descripcion}: {type(error).__name__}: {error}")
            resultados.append(f"✘ {etiqueta}\n      Error controlado -> {type(error).__name__}: {error}")
        except Exception as error:      # Red de seguridad: nada detiene la simulación
            logger.error(f"[Simulación] Error inesperado en '{descripcion}': {error}")
            resultados.append(f"✘ {etiqueta}\n      Error inesperado -> {error}")
        else:
            logger.info(f"[Simulación] {descripcion}: OK")
            resultados.append(f"✔ {etiqueta}\n      Resultado -> {salida}")

    def no_disponible_y_reservar():
        """Marca el equipo como no disponible y luego intenta reservarlo."""
        gs.buscar_servicio("E001").disponible = False
        return gr.crear_reserva("C002", "E001", "2")

    def variantes_costo():
        """Muestra la sobrecarga del cálculo: mismo servicio, distintas variantes."""
        sala = gs.buscar_servicio("S001")
        base = sala.calcular_costo(2)
        con_iva = sala.calcular_costo(2, True)
        completo = sala.calcular_costo(2, iva=True, cliente_frecuente=True, recargo=20000)
        return f"Base ${base:,.0f} | Con IVA ${con_iva:,.0f} | IVA+descuento+recargo ${completo:,.0f}"

    # --- Clientes ---
    paso("Cliente válido (Ana)", lambda: gc.registrar_cliente("C001", "Ana Pérez", "1001234567", "ana@correo.com"))
    paso("Cliente inválido (cédula con letras)", lambda: gc.registrar_cliente("C002", "Luis Gómez", "12ab", "luis@correo.com"))
    paso("Cliente duplicado (ID repetido)", lambda: gc.registrar_cliente("C001", "Otra Ana", "1000000000", "otra@correo.com"))
    paso("Cliente válido (Luis)", lambda: gc.registrar_cliente("C002", "Luis Gómez", "1098765432", "luis@correo.com"))
    # --- Servicios ---
    paso("ReservaSala válida", lambda: gs.crear_servicio("sala", "S001", "Sala Ejecutiva", "80000", "20", opcion=True))
    paso("ReservaSala con capacidad inválida (0)", lambda: gs.crear_servicio("sala", "S002", "Sala Mini", "50000", "0"))
    paso("AlquilerEquipo válido", lambda: gs.crear_servicio("equipo", "E001", "Videobeam", "30000", "3", opcion=True))
    paso("AlquilerEquipo con cantidad faltante", lambda: gs.crear_servicio("equipo", "E002", "Portátil", "40000", ""))
    paso("AsesoriaEspecializada válida", lambda: gs.crear_servicio("asesoria", "A001", "Asesoría Cloud", "120000", "Computación en la nube", "Senior"))
    paso("AsesoriaEspecializada sin especialidad", lambda: gs.crear_servicio("asesoria", "A002", "Asesoría Datos", "100000", "", "Junior"))
    # --- Reservas ---
    paso("Reserva exitosa (Ana, sala, 3 h, con IVA)", lambda: gr.crear_reserva("C001", "S001", "3", iva=True).mostrar_informacion())
    paso("Confirmar reserva R001", lambda: gr.confirmar_reserva("R001"))
    paso("Reserva con servicio no disponible", no_disponible_y_reservar)
    paso("Reserva con duración faltante", lambda: gr.crear_reserva("C001", "A001", ""))
    paso("Reserva con duración fuera de rango (50 h)", lambda: gr.crear_reserva("C002", "S001", "50").mostrar_informacion())
    paso("Confirmar R002 (debe fallar por duración)", lambda: gr.confirmar_reserva("R002"))
    paso("Cancelar reserva R002", lambda: gr.cancelar_reserva("R002"))
    paso("Cancelar R002 por segunda vez", lambda: gr.cancelar_reserva("R002"))
    paso("Reserva con cliente inexistente", lambda: gr.crear_reserva("C999", "S001", "2"))
    paso("Cálculo con variantes (sobrecarga IVA/descuento/recargo)", variantes_costo)

    exitosas = sum(1 for linea in resultados if linea.startswith("✔"))
    fallidas = len(resultados) - exitosas
    resumen = (f"\nResumen: {len(resultados)} operaciones | {exitosas} exitosas | "
               f"{fallidas} errores controlados | El programa NO se interrumpió.")
    resultados.append(resumen)
    logger.info(f"===== FIN DE LA SIMULACIÓN: {exitosas} exitosas, {fallidas} errores controlados =====")
    return resultados
