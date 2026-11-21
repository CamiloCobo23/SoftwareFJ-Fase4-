"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programación 213023 - Fase 4
Estudiante: Camilo Andrés Cobo Fonseca
Grupo: 494
Tutora: Martha Liliana Quevedo

Implementación de:
- Abstracción, herencia, polimorfismo y encapsulación
- Manejo avanzado de excepciones (personalizadas, try/except/else/finally y chaining)
- Gestión sin bases de datos (listas + archivo de logs)
- Simulación de más de 10 operaciones válidas e inválidas
"""

from abc import ABC, abstractmethod
from datetime import datetime
import os

# ==================== EXCEPCIONES PERSONALIZADAS ====================
class ErrorAplicacion(Exception):
    """Excepción base de la aplicación."""
    pass

class ErrorValidacion(ErrorAplicacion):
    pass

class ErrorCliente(ErrorValidacion):
    pass

class ErrorServicio(ErrorValidacion):
    pass

class ErrorReserva(ErrorValidacion):
    pass


# ==================== CLASE ABSTRACTA ====================
class Entidad(ABC):
    """Clase abstracta para entidades del sistema."""

    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ==================== CLASE CLIENTE ====================
class Cliente(Entidad):
    def __init__(self, nombre_completo, documento, telefono="", email=""):
        self._nombre_completo = ""
        self._documento = ""
        self._telefono = ""
        self._email = ""
        self.nombre_completo = nombre_completo
        self.documento = documento
        self.telefono = telefono
        self.email = email
        self.validar()

    @property
    def nombre_completo(self):
        return self._nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, valor):
        if not valor or len(str(valor).strip()) < 4:
            raise ErrorCliente("El nombre completo debe tener al menos 4 caracteres.")
        self._nombre_completo = str(valor).strip().title()

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, valor):
        valor = str(valor).strip()
        if not valor.isdigit() or len(valor) < 6:
            raise ErrorCliente("El documento debe ser numérico y contener mínimo 6 dígitos.")
        self._documento = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if valor and (not str(valor).isdigit() or len(str(valor)) < 7):
            raise ErrorCliente("El teléfono debe ser numérico y tener al menos 7 dígitos.")
        self._telefono = str(valor).strip() if valor else ""

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if valor and ("@" not in valor or "." not in valor):
            raise ErrorCliente("El correo electrónico no tiene un formato válido.")
        self._email = str(valor).strip().lower() if valor else ""

    def validar(self):
        if not self.nombre_completo or not self.documento:
            raise ErrorCliente("Nombre y documento son obligatorios.")

    def mostrar_informacion(self):
        return f"{self.nombre_completo} (Doc: {self.documento})"


# ==================== CLASE ABSTRACTA SERVICIO ====================
class Servicio(Entidad, ABC):
    def __init__(self, nombre, precio_base, disponible=True):
        self.nombre = nombre
        self.precio_base = float(precio_base)
        self.disponible = disponible

    @abstractmethod
    def calcular_precio(self, unidades=1, impuesto=0.19, descuento=0.0):
        """Cálculo de precio con parámetros opcionales."""
        pass

    @abstractmethod
    def descripcion(self):
        pass

    def validar(self):
        if self.precio_base <= 0:
            raise ErrorServicio(f"El precio base de '{self.nombre}' debe ser mayor a cero.")
        if not self.disponible:
            raise ErrorServicio(f"El servicio '{self.nombre}' no está disponible.")

    def mostrar_informacion(self):
        return self.descripcion()


# ==================== SERVICIOS ESPECIALIZADOS ====================
class ReservaSala(Servicio):
    def calcular_precio(self, unidades=1, impuesto=0.19, descuento=0.0):
        self.validar()
        if unidades <= 0:
            raise ErrorReserva("La cantidad de unidades debe ser mayor a cero.")
        subtotal = self.precio_base * unidades
        con_descuento = subtotal * (1 - descuento / 100)
        return round(con_descuento * (1 + impuesto), 2)

    def descripcion(self):
        return f"Reserva de Sala | ${self.precio_base:.2f}/hora | Disponible: {self.disponible}"


class AlquilerEquipo(Servicio):
    def calcular_precio(self, unidades=1, impuesto=0.19, descuento=0.0):
        self.validar()
        if unidades <= 0:
            raise ErrorReserva("La cantidad de unidades debe ser mayor a cero.")
        subtotal = self.precio_base * unidades
        con_descuento = subtotal * (1 - descuento / 100)
        return round(con_descuento * (1 + impuesto), 2)

    def descripcion(self):
        return f"Alquiler de Equipo | ${self.precio_base:.2f}/día | Disponible: {self.disponible}"


class AsesoriaEspecializada(Servicio):
    def calcular_precio(self, unidades=1, impuesto=0.19, descuento=0.0):
        self.validar()
        if unidades <= 0:
            raise ErrorReserva("La cantidad de unidades debe ser mayor a cero.")
        subtotal = self.precio_base * unidades
        con_descuento = subtotal * (1 - descuento / 100)
        return round(con_descuento * (1 + impuesto), 2)

    def descripcion(self):
        return f"Asesoría Especializada | ${self.precio_base:.2f}/hora | Disponible: {self.disponible}"


# ==================== CLASE RESERVA ====================
class Reserva:
    def __init__(self, cliente, servicio, unidades, estado="Pendiente"):
        self.cliente = cliente
        self.servicio = servicio
        self.unidades = unidades
        self.estado = estado
        self.precio_total = 0.0
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    def confirmar(self, impuesto=0.19, descuento=0.0):
        try:
            self.precio_total = self.servicio.calcular_precio(self.unidades, impuesto, descuento)
            self.estado = "Confirmada"
            return True
        except Exception as e:
            raise ErrorReserva(f"No fue posible confirmar la reserva: {e}") from e

    def cancelar(self):
        if self.estado in ("Cancelada", "Procesada"):
            raise ErrorReserva("La reserva no puede ser cancelada en su estado actual.")
        self.estado = "Cancelada"
        return True

    def procesar(self):
        if self.estado != "Confirmada":
            raise ErrorReserva("Solo se pueden procesar reservas confirmadas.")
        self.estado = "Procesada"
        return True


# ==================== GESTOR DEL SISTEMA ====================
class SistemaFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
        self.archivo_log = "eventos_sistema.log"
        self._preparar_log()

    def _preparar_log(self):
        with open(self.archivo_log, "a", encoding="utf-8") as f:
            f.write(f"\n===== SESIÓN INICIADA: {datetime.now()} =====\n")

    def registrar(self, mensaje, es_error=False):
        tipo = "ERROR" if es_error else "INFO"
        linea = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{tipo}] {mensaje}"
        with open(self.archivo_log, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        print(linea)

    def registrar_cliente(self, nombre, documento, telefono="", email=""):
        try:
            cliente = Cliente(nombre, documento, telefono, email)
            self.clientes.append(cliente)
            self.registrar(f"Cliente registrado: {cliente.mostrar_informacion()}")
            return cliente
        except Exception as e:
            self.registrar(f"Fallo en registro de cliente: {e}", es_error=True)
            raise

    def crear_servicio(self, tipo, nombre, precio, disponible=True):
        try:
            tipo = tipo.lower().strip()
            if tipo == "sala":
                servicio = ReservaSala(nombre, precio, disponible)
            elif tipo == "equipo":
                servicio = AlquilerEquipo(nombre, precio, disponible)
            elif tipo == "asesoria":
                servicio = AsesoriaEspecializada(nombre, precio, disponible)
            else:
                raise ErrorServicio("Tipo de servicio no reconocido.")
            servicio.validar()
            self.servicios.append(servicio)
            self.registrar(f"Servicio creado: {servicio.descripcion()}")
            return servicio
        except Exception as e:
            self.registrar(f"Fallo al crear servicio: {e}", es_error=True)
            raise

    def generar_reserva(self, documento_cliente, nombre_servicio, unidades, descuento=0.0):
        try:
            cliente = next((c for c in self.clientes if c.documento == str(documento_cliente)), None)
            if not cliente:
                raise ErrorReserva("No se encontró el cliente indicado.")

            servicio = next((s for s in self.servicios if s.nombre.lower() == nombre_servicio.lower()), None)
            if not servicio:
                raise ErrorServicio("No se encontró el servicio indicado.")

            reserva = Reserva(cliente, servicio, unidades)
            reserva.confirmar(descuento=descuento)
            self.reservas.append(reserva)
            self.registrar(f"Reserva confirmada: {cliente.nombre_completo} → {servicio.nombre} | Total: ${reserva.precio_total}")
            return reserva
        except Exception as e:
            self.registrar(f"Fallo al generar reserva: {e}", es_error=True)
            raise

    def listar_informacion(self):
        print("\n========== RESUMEN ==========")
        print("CLIENTES:")
        for c in self.clientes:
            print(f"  • {c.mostrar_informacion()}")
        print("\nSERVICIOS:")
        for s in self.servicios:
            print(f"  • {s.descripcion()}")
        print("\nRESERVAS:")
        for r in self.reservas:
            print(f"  • {r.cliente.nombre_completo} | {r.servicio.nombre} | {r.unidades} | ${r.precio_total} | {r.estado}")


# ==================== SIMULACIÓN ====================
def ejecutar_simulacion():
    sistema = SistemaFJ()
    print("=== SIMULACIÓN DE OPERACIONES ===\n")

    casos = [
        ("Cliente válido", lambda: sistema.registrar_cliente("Andrés Ramírez", "1029384756", "3209876543", "andres@correo.com")),
        ("Nombre demasiado corto", lambda: sistema.registrar_cliente("Ana", "123456")),
        ("Documento no numérico", lambda: sistema.registrar_cliente("Sofía López", "DOC123")),
        ("Servicio sala válido", lambda: sistema.crear_servicio("sala", "Sala Premium", 90.0)),
        ("Servicio equipo válido", lambda: sistema.crear_servicio("equipo", "Cámara 4K", 55.0)),
        ("Servicio asesoría válida", lambda: sistema.crear_servicio("asesoria", "Consultoría DevOps", 180.0)),
        ("Precio inválido", lambda: sistema.crear_servicio("sala", "Sala Básica", 0)),
        ("Reserva exitosa", lambda: sistema.generar_reserva("1029384756", "Sala Premium", 3, descuento=10)),
        ("Cliente inexistente", lambda: sistema.generar_reserva("999999", "Cámara 4K", 2)),
        ("Servicio inexistente", lambda: sistema.generar_reserva("1029384756", "Servicio Fantasma", 1)),
        ("Unidades inválidas", lambda: sistema.generar_reserva("1029384756", "Consultoría DevOps", 0)),
    ]

    for i, (desc, accion) in enumerate(casos, 1):
        print(f"\n--- Caso {i}: {desc} ---")
        try:
            accion()
            print("→ Operación exitosa")
        except Exception as e:
            print(f"→ Error controlado: {e}")
        else:
            print("→ (else) Sin excepciones")
        finally:
            print("→ (finally) Operación finalizada")

    print("\n" + "="*60)
    sistema.listar_informacion()
    print(f"\nLogs guardados en: {os.path.abspath(sistema.archivo_log)}")


# ==================== MENÚ ====================
def menu_principal():
    sistema = SistemaFJ()
    while True:
        print("\n" + "="*55)
        print("   SISTEMA SOFTWARE FJ - Gestión Integral")
        print("="*55)
        print("1. Registrar cliente")
        print("2. Crear servicio")
        print("3. Generar reserva")
        print("4. Ver resumen")
        print("5. Ejecutar simulación completa")
        print("0. Salir")
        opcion = input("\nSeleccione una opción: ").strip()

        try:
            if opcion == "1":
                nom = input("Nombre completo: ")
                doc = input("Documento: ")
                tel = input("Teléfono (opcional): ")
                mail = input("Email (opcional): ")
                sistema.registrar_cliente(nom, doc, tel, mail)
            elif opcion == "2":
                tip = input("Tipo (sala/equipo/asesoria): ")
                nom = input("Nombre del servicio: ")
                pre = float(input("Precio base: "))
                sistema.crear_servicio(tip, nom, pre)
            elif opcion == "3":
                doc = input("Documento del cliente: ")
                nom = input("Nombre del servicio: ")
                uni = int(input("Unidades/Duración: "))
                sistema.generar_reserva(doc, nom, uni)
            elif opcion == "4":
                sistema.listar_informacion()
            elif opcion == "5":
                ejecutar_simulacion()
            elif opcion == "0":
                print("Saliendo...")
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print(f"Error controlado: {e}")


if __name__ == "__main__":
    menu_principal()
