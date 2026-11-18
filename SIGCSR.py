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

class Usuario:
    def __init__(self):
        self._usuario = "Grupo"
        self._password = "1234"

    def validar(self, usuario_ingresado, password_ingresada):
            return usuario_ingresado == self._usuario and password_ingresada == self._password
        
#Robin:________________________Clase abstracta sistema        
class Entidad(ABC):
    
    def __init__(self, identificador):
        self.__identificador = identificador
        
    def obtener_identificador(self):
        return self.__identificador
    
    @abstractmethod
    def mostrar_informacion(self):
        pass    
        
class Cliente(Entidad):
    def __init__(self, identificador, nombre, cedula, correo):
        super().__init__(identificador)
        
#Robin:______________Validacion de datos del cliente 
        if not str(identificador).strip():
            raise ValueError("Insertar datos para validar.")
        
        if not nombre.strip():
            raise ValueError("Insertar nombre.")
        
        if not str(cedula).strip().isdigit():
            raise ValueError("La cedula debe contener solo números.")
        
        if not correo.strip() or "@" not in correo or "." not in correo:
            raise ValueError("El correo electronico no es valido.")

        self.__nombre = nombre
        self.__cc = cedula
        self.__correo = correo
        
    def mostrar_informacion(self):
        return (
                f"Cliente ID: {self.obtener_identificador()}\n"
                f"Nombre: {self.__nombre}\n"
                f"Cedula: {self.__cc}\n"
                f"Correo: {self.__correo}"
        )
#Robin:_________Gestion de clientes.        
class GestorClientes:
    def __init__(self):
        self.__clientes = []
        
    def registrar_cliente(self, identificador, nombre, cedula, correo):
        for cliente in self.__clientes:
            if  str(cliente.obtener_identificador()) == str(identificador):
                raise ValueError("El cliente ya existe.")
        nuevo_cliente = Cliente(identificador, nombre, cedula, correo)
        self.__clientes.append(nuevo_cliente)
        return "Cliente registrado correctamente."
    
    def listar_clientes(self):
        return self.__clientes.copy()
    
#Robin:__________________Ventana Abministrar clientes.
gestor_clientes = GestorClientes()
    
def abrir_ventana_clientes():
    
    ventana_clientes = tk.Toplevel(ventana)
    ventana_clientes.title("Gestión de Clientes")
    ventana_clientes.geometry("600x550")
    
    tk.Label(ventana_clientes,text="GESTIÓN DE CLIENTES",font=("Arial", 16, "bold")).pack(pady=15)
    
    tk.Label(ventana_clientes, text="Identificador").pack()
    entrada_id = tk.Entry(ventana_clientes)
    entrada_id.pack(pady=5)
    
    tk.Label(ventana_clientes, text="Nombre").pack()
    entrada_nombre = tk.Entry(ventana_clientes)
    entrada_nombre.pack(pady=5)
    
    tk.Label(ventana_clientes, text="Cédula").pack()
    entrada_cedula = tk.Entry(ventana_clientes)
    entrada_cedula.pack(pady=5)
    
    tk.Label(ventana_clientes, text="Correo electrónico").pack()
    entrada_correo = tk.Entry(ventana_clientes)
    entrada_correo.pack(pady=5)
    
#Robin:________________________Funcion para registrar clientes   
    def registrar():
        try:
            resultado = gestor_clientes.registrar_cliente(
            entrada_id.get(),
            entrada_nombre.get(),
            entrada_cedula.get(),
            entrada_correo.get()
            )
        
            messagebox.showinfo("Registro", resultado)
            
            entrada_id.delete(0, tk.END)
            entrada_nombre.delete(0, tk.END)
            entrada_cedula.delete(0, tk.END)
            entrada_correo.delete(0, tk.END)
            
        except ValueError as error:
            messagebox.showerror("Error de registro", str(error))
            
            
#Robin:_______________Funcion de lista de clientes
    def consultar():
        lista_clientes.delete(0, tk.END)
        clientes = gestor_clientes.listar_clientes()
        
        if not clientes:
                messagebox.showinfo("Clientes", "Aún no hay clientes registrados.")
                return
        for cliente in clientes:
            lista_clientes.insert(
                tk.END,
                cliente.mostrar_informacion()
                )             
    tk.Button(ventana_clientes,text="Registrar Cliente",width=25,command=registrar).pack(pady=10)
    
    tk.Button(ventana_clientes,text="Consultar Clientes",width=25,command=consultar).pack(pady=5)
    
#Robin:_______________Mostrar clientes.
    lista_clientes = tk.Listbox(ventana_clientes,width=65,height=8)
    lista_clientes.pack(pady=15)    
            
    
    
    
    
    
#Robin:________________________Funcion para abrir el sistema
def abrir_sistema():
    ventana_principal = tk.Toplevel(ventana)
    ventana_principal.title("Software SIGCSR - Main Menu")
    ventana_principal.geometry("600x450")

    tk.Label(ventana_principal, text="SISTEMA INTEGRAL", font=("Arial", 16, "bold")).pack(pady=12)
    
    tk.Label(ventana_principal, text="S.I.G.C.S.R", font=("Arial", 16, "bold")).pack(pady=12)
    
    tk.Button(ventana_principal,text="Clientes",width=25,command=abrir_ventana_clientes).pack(pady=10)

    tk.Button(ventana_principal,text="Servicios",width=25).pack(pady=10)

    tk.Button(ventana_principal,text="Reservas",width=25).pack(pady=10)

#Robin:________________________Funcion para iniciar sesion
def iniciar_sesion():
    usuario = entrada_usuario.get()
    password = entrada_password.get()

    usuario1 = Usuario()

    if usuario1.validar(usuario, password):
        abrir_sistema()
        ventana.withdraw()
    else:
        messagebox.showerror(
            "Login",
            "Usuario o contraseña incorrectos"
        )

#Robin:_____________________Ventana de inicio de sesion o login.
ventana = tk.Tk()
ventana.title("Software SIGCSR - Login")
ventana.geometry("600x450")

tk.Label(ventana, text="INICIAR SESION", font=("Arial", 16, "bold")).pack(pady=12)

tk.Label(ventana, text="Usuario").pack(pady=10)

entrada_usuario = tk.Entry(ventana)
entrada_usuario.pack()

tk.Label(ventana, text="Contraseña").pack(pady=10)

entrada_password = tk.Entry(ventana, show="*")
entrada_password.pack()

boton_login = tk.Button(
    ventana,
    text="Login",
    command=iniciar_sesion
)
boton_login.pack(pady=20)
ventana.mainloop()

# Hola soy julian prueba 1
