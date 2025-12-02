#!/usr/bin/env python3
"""
Programa de Pruebas de Comunicación - Arduino Mega
Prueba la comunicación serie entre Raspberry Pi y Arduino Mega
para el control del brazo robot de 6DOF.
"""

import serial
import serial.tools.list_ports
import time
import logging
from datetime import datetime
import sys
import os

class ArduinoTester:
    """Clase para manejar pruebas de comunicación con Arduino Mega"""
    
    def __init__(self, baudrate=115200, timeout=5):
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port = None
        self.is_connected = False
        self.log_file = f"pruebas_comunicacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configurar logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # También mostrar en consola
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        
        logging.info("Sistema de pruebas de comunicación iniciado")
    
    def detectar_puerto_arduino(self):
        """Detecta automáticamente el puerto del Arduino Mega"""
        logging.info("Buscando dispositivo Arduino...")
        
        puertos = list(serial.tools.list_ports.comports())
        
        for puerto in puertos:
            # Buscar por descripción común de Arduino
            if any(keyword in puerto.description.lower() for keyword in 
                  ['arduino', 'mega', 'usb serial', 'ttyacm', 'ttyusb']):
                logging.info(f"Puerto candidato encontrado: {puerto.device} - {puerto.description}")
                return puerto.device
        
        # Si no encuentra por descripción, mostrar todos los puertos disponibles
        if puertos:
            logging.warning("No se detectó Arduino automáticamente. Puertos disponibles:")
            for puerto in puertos:
                logging.warning(f"  {puerto.device}: {puerto.description}")
            
            # Pedir al usuario que seleccione
            while True:
                try:
                    seleccion = input("Ingrese el número del puerto a usar (1-{}): ".format(len(puertos)))
                    indice = int(seleccion) - 1
                    if 0 <= indice < len(puertos):
                        return puertos[indice].device
                except ValueError:
                    pass
                logging.error("Selección inválida. Intente nuevamente.")
        else:
            logging.error("No se encontraron puertos serie disponibles")
            return None
    
    def conectar(self, puerto=None):
        """Establece conexión con el Arduino Mega"""
        try:
            if puerto is None:
                puerto = self.detectar_puerto_arduino()
                if puerto is None:
                    return False
            
            logging.info(f"Conectando a {puerto} a {self.baudrate} baudios...")
            
            self.serial_port = serial.Serial(
                port=puerto,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=2
            )
            
            time.sleep(2)  # Esperar a que se estabilice la conexión
            
            # --- VERIFICACIÓN DE HANDSHAKE ---
            logging.info("Verificando dispositivo (Handshake)...")
            self.is_connected = True # Temporalmente True para permitir enviar_comando
            
            # Intentar obtener respuesta válida
            respuesta = self.enviar_comando("S", esperar_respuesta=True)
            
            if not respuesta:
                logging.error("❌ Handshake fallido: El dispositivo no respondió")
                self.desconectar()
                return False
                
            if not respuesta.startswith("S:"):
                logging.warning(f"⚠️ Respuesta inesperada durante handshake: {respuesta}")
            
            logging.info("✅ Conexión exitosa con Arduino Mega")
            return True
            
        except serial.SerialException as e:
            logging.error(f"❌ Error de conexión: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logging.error(f"❌ Error inesperado: {e}")
            self.is_connected = False
            return False
    
    def desconectar(self):
        """Cierra la conexión serie"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.is_connected = False
            logging.info("Conexión cerrada")
    
    def enviar_comando(self, comando, esperar_respuesta=True):
        """Envía un comando al Arduino y opcionalmente espera respuesta"""
        if not self.is_connected:
            logging.error("No hay conexión con Arduino")
            return None
        
        try:
            # Limpiar buffer de entrada
            self.serial_port.reset_input_buffer()
            
            # Enviar comando con nueva línea
            comando_completo = comando + "\n"
            self.serial_port.write(comando_completo.encode('utf-8'))
            
            logging.info(f"📤 Enviado: {comando}")
            
            if esperar_respuesta:
                return self.esperar_respuesta()
            return None
            
        except serial.SerialTimeoutException:
            logging.error("Timeout al enviar comando")
            return None
        except Exception as e:
            logging.error(f"Error al enviar comando: {e}")
            return None
    
    def esperar_respuesta(self, timeout=None):
        """Espera respuesta del Arduino"""
        if timeout is None:
            timeout = self.timeout
        
        try:
            inicio = time.time()
            respuesta = ""
            
            while time.time() - inicio < timeout:
                if self.serial_port.in_waiting > 0:
                    linea = self.serial_port.readline().decode('utf-8').strip()
                    if linea:
                        respuesta = linea
                        logging.info(f"📥 Recibido: {respuesta}")
                        return respuesta
                
                time.sleep(0.01)  # Pequeña pausa para no saturar CPU
            
            logging.warning(f"⏰ Timeout esperando respuesta ({timeout}s)")
            return None
            
        except Exception as e:
            logging.error(f"Error esperando respuesta: {e}")
            return None
    
    def probar_conexion(self):
        """Prueba básica de conexión enviando comando de status"""
        logging.info("\n=== PRUEBA DE CONEXIÓN ===")
        
        inicio = time.time()
        respuesta = self.enviar_comando("S")  # Status request
        tiempo_respuesta = time.time() - inicio
        
        if respuesta and respuesta.startswith("S:"):
            logging.info(f"✅ Conexión exitosa (tiempo: {tiempo_respuesta:.3f}s)")
            # Parsear la respuesta para mostrar información útil
            try:
                partes = respuesta.split(":")[1].split(",")
                posiciones = partes[:6]  # Primeras 6 son posiciones
                logging.info(f"📊 Posiciones actuales: {posiciones}")
            except:
                logging.info("📊 Respuesta de telemetría recibida")
            return True
        else:
            logging.error(f"❌ Falló prueba de conexión. Respuesta: {respuesta}")
            return False
    
    def probar_eje(self, eje, pasos=100):
        """Prueba movimientos básicos de un eje"""
        logging.info(f"\n=== PRUEBA DE EJE {eje} ===")
        
        exito = True
        
        # Movimiento positivo
        logging.info(f"Moviendo eje {eje} +{pasos} pasos...")
        respuesta_ok = self.enviar_comando(f"M{eje}{pasos}")
        
        if respuesta_ok != "OK":
            logging.error(f"❌ Error de confirmación. Esperado: OK, Recibido: {respuesta_ok}")
            exito = False
        else:
            respuesta_done = self.esperar_respuesta(timeout=10)
            if respuesta_done != f"D{eje}":
                logging.error(f"❌ Error en movimiento positivo. Esperado: D{eje}, Recibido: {respuesta_done}")
                exito = False
        
        time.sleep(0.5)  # Pausa
        
        # Movimiento negativo (volver)
        logging.info(f"Moviendo eje {eje} -{pasos} pasos...")
        respuesta_ok = self.enviar_comando(f"M{eje}-{pasos}")
        
        if respuesta_ok != "OK":
            logging.error(f"❌ Error de confirmación. Esperado: OK, Recibido: {respuesta_ok}")
            exito = False
        else:
            respuesta_done = self.esperar_respuesta(timeout=10)
            if respuesta_done != f"D{eje}":
                logging.error(f"❌ Error en movimiento negativo. Esperado: D{eje}, Recibido: {respuesta_done}")
                exito = False
        
        if exito:
            logging.info(f"✅ Eje {eje}: OK")
        else:
            logging.error(f"❌ Eje {eje}: FALLÓ")
        
        return exito
    
    def probar_homing(self, eje):
        """Prueba el homing de un eje"""
        logging.info(f"\n=== PRUEBA DE HOMING - EJE {eje} ===")
        
        logging.info(f"Ejecutando homing en eje {eje}...")
        respuesta_ok = self.enviar_comando(f"H{eje}")
        
        if respuesta_ok != "OK":
            logging.error(f"❌ Error de confirmación homing. Esperado: OK, Recibido: {respuesta_ok}")
            return False
        else:
            # Esperar confirmación de finalización
            respuesta_done = self.esperar_respuesta(timeout=30)  # Timeout más largo para homing
            if respuesta_done != f"D{eje}":
                logging.error(f"❌ Error en homing. Esperado: D{eje}, Recibido: {respuesta_done}")
                return False
        
        logging.info(f"✅ Homing eje {eje}: OK")
        return True
    
    def probar_emergency_stop(self):
        """Prueba el emergency stop"""
        logging.info("\n=== PRUEBA DE EMERGENCY STOP ===")
        
        respuesta = self.enviar_comando("E")
        
        if respuesta == "OK":
            logging.info("✅ Emergency stop: OK")
            return True
        else:
            logging.error(f"❌ Emergency stop falló. Respuesta: {respuesta}")
            return False
    
    def ejecutar_pruebas_completas(self):
        """Ejecuta toda la batería de pruebas"""
        logging.info("\n" + "="*50)
        logging.info("INICIANDO BATERÍA COMPLETA DE PRUEBAS")
        logging.info("="*50)
        
        resultados = {}
        
        # Prueba de conexión
        resultados['conexion'] = self.probar_conexion()
        
        if not resultados['conexion']:
            logging.error("❌ No se puede continuar sin conexión básica")
            return resultados
        
        time.sleep(1)
        
        # Prueba de ejes
        resultados['ejes'] = {}
        for eje in range(1, 7):  # Ejes 1-6
            resultados['ejes'][eje] = self.probar_eje(eje)
            time.sleep(0.5)
        
        # Prueba de homing
        resultados['homing'] = {}
        for eje in range(1, 7):
            resultados['homing'][eje] = self.probar_homing(eje)
            time.sleep(1)
        
        # Prueba de emergency stop
        resultados['emergency'] = self.probar_emergency_stop()
        
        # Resumen final
        self.mostrar_resumen(resultados)
        
        return resultados
    
    def mostrar_resumen(self, resultados):
        """Muestra resumen de todas las pruebas"""
        logging.info("\n" + "="*50)
        logging.info("RESUMEN DE PRUEBAS")
        logging.info("="*50)
        
        if resultados.get('conexion'):
            logging.info("✅ Conexión básica: OK")
        else:
            logging.info("❌ Conexión básica: FALLÓ")
        
        if 'ejes' in resultados:
            logging.info("Motores:")
            for eje, exito in resultados['ejes'].items():
                status = "✅ OK" if exito else "❌ FALLÓ"
                logging.info(f"  Eje {eje}: {status}")
        
        if 'homing' in resultados:
            logging.info("Homing:")
            for eje, exito in resultados['homing'].items():
                status = "✅ OK" if exito else "❌ FALLÓ"
                logging.info(f"  Eje {eje}: {status}")
        
        if resultados.get('emergency'):
            logging.info("✅ Emergency Stop: OK")
        else:
            logging.info("❌ Emergency Stop: FALLÓ")
        
        logging.info(f"\n📄 Log completo guardado en: {self.log_file}")
    
    def modo_manual(self):
        """Modo interactivo para enviar comandos manualmente"""
        logging.info("\n=== MODO MANUAL ===")
        logging.info("Comandos disponibles:")
        logging.info("  S - Status")
        logging.info("  M<eje><pasos> - Movimiento relativo (ej: M1100)")
        logging.info("  A<eje><pos> - Movimiento absoluto (ej: A1500)")
        logging.info("  H<eje> - Homing (ej: H1)")
        logging.info("  E - Emergency stop")
        logging.info("  K<eje> - Kill axis (ej: K1)")
        logging.info("  Q - Salir del modo manual")
        logging.info("")
        
        while True:
            try:
                comando = input("Comando a enviar (Q para salir): ").strip().upper()
                
                if comando == 'Q':
                    break
                
                if comando:
                    respuesta = self.enviar_comando(comando)
                    if respuesta:
                        logging.info(f"Respuesta: {respuesta}")
                    else:
                        logging.warning("No se recibió respuesta")
                
            except KeyboardInterrupt:
                logging.info("Modo manual interrumpido")
                break
            except Exception as e:
                logging.error(f"Error en modo manual: {e}")

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*50)
    print("PROGRAMA DE PRUEBAS DE COMUNICACIÓN")
    print("ARDUINO MEGA - BRAZO ROBOT 6DOF")
    print("="*50)
    print("1. Probar conexión básica")
    print("2. Probar movimientos básicos (todos los ejes)")
    print("3. Probar homing (todos los ejes)")
    print("4. Probar emergency stop")
    print("5. Ejecutar batería completa de pruebas")
    print("6. Modo manual (comandos personalizados)")
    print("7. Salir")
    print("="*50)

def main():
    """Función principal del programa"""
    print("Iniciando programa de pruebas de comunicación...")
    
    tester = ArduinoTester()
    
    try:
        while True:
            mostrar_menu()
            
            try:
                opcion = input("Seleccione opción (1-7): ").strip()
                
                if opcion == "1":
                    if not tester.is_connected:
                        if not tester.conectar():
                            continue
                    
                    tester.probar_conexion()
                
                elif opcion == "2":
                    if not tester.is_connected:
                        if not tester.conectar():
                            continue
                    
                    for eje in range(1, 7):
                        tester.probar_eje(eje)
                        time.sleep(0.5)
                
                elif opcion == "3":
                    if not tester.is_connected:
                        if not tester.conectar():
                            continue
                    
                    for eje in range(1, 7):
                        tester.probar_homing(eje)
                        time.sleep(1)
                
                elif opcion == "4":
                    if not tester.is_connected:
                        if not tester.conectar():
                            continue
                    
                    tester.probar_emergency_stop()
                
                elif opcion == "5":
                    if not tester.is_connected:
                        if not tester.conectar():
                            continue
                    
                    tester.ejecutar_pruebas_completas()
                
                elif opcion == "6":
                    if not tester.is_connected:
                        if not tester.conectar():
                            continue
                    
                    tester.modo_manual()
                
                elif opcion == "7":
                    print("Saliendo del programa...")
                    break
                
                else:
                    print("Opción inválida. Intente nuevamente.")
                
                input("\nPresione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\nPrograma interrumpido por el usuario")
                break
            except Exception as e:
                logging.error(f"Error en la opción seleccionada: {e}")
                input("Presione Enter para continuar...")
    
    finally:
        tester.desconectar()
        print(f"\nSesión terminada. Log guardado en: {tester.log_file}")

if __name__ == "__main__":
    main()