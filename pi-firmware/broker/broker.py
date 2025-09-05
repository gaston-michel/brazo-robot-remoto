# broker.py
"""
Serial Broker entre PC (servidor) y Arduino Mega.
Recibe comandos ASCII del PC por puerto USB virtual (ej. /dev/ttyUSB0), los procesa y reenvía al Mega por otro puerto (ej. /dev/ttyACM0).
También recoge respuestas del Mega y las envía de vuelta al PC.
Implementa:
 - Creación del directorio de logs
 - Heartbeat (`C\n` → `c\n`)
 - Conversión de unidades (grados `G` o pasos `S`) a pasos
 - ACK inmediato (`OK\n`) para comandos válidos
 - Envío de errores de protocolo
 - Manejo de reconexión automática
 - Logging robusto y validación de configuración
"""
import os
import serial
import threading
import yaml
import re
import time
import logging

# Asegurar existencia del directorio de logs
os.makedirs('logs', exist_ok=True)

# Configurar logging
glogging = logging.getLogger()
logging.basicConfig(
    filename='logs/broker.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class SerialBroker:
    def __init__(self, config_path='config.yaml'):
        # Validar archivo de configuración
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"No se encontró {config_path}")
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        # Validar secciones necesarias
        if 'ports' not in cfg or 'axes' not in cfg:
            raise KeyError("Faltan claves 'ports' o 'axes' en config.yaml")
        self.pc_port = cfg['ports'].get('pc')
        self.mega_port = cfg['ports'].get('mega')
        if not self.pc_port or not self.mega_port:
            raise KeyError("Define 'pc' y 'mega' en la sección 'ports' de config.yaml")
        self.baudrate = cfg.get('baudrate', 115200)
        self.timeout = cfg.get('timeout', 1.0)
        self.axes = cfg['axes']

        # Regex para comandos
        self.cmd_regex = re.compile(r'^([MA])([1-6])([+-]?\d+)([GS])?\n$')
        self.homing_regex = re.compile(r'^(H[1-6])\n$')
        self.status_regex = re.compile(r'^(S)\n$')
        self.estop_regex = re.compile(r'^(E)\n$')
        self.kill_regex = re.compile(r'^(K[1-6])\n$')
        self.profile_regex = re.compile(r'^(P[VA]\d+)\n$')
        self.timeout_regex = re.compile(r'^(T\d+)\n$')

        self.running = True
        self.thread_pc = threading.Thread(target=self._read_pc_loop, daemon=True)
        self.thread_mega = threading.Thread(target=self._read_mega_loop, daemon=True)

        self._open_serials()

    def _open_serials(self):
        # Intentar abrir puertos con reconexión cada 2s
        while True:
            try:
                self.ser_pc = serial.Serial(self.pc_port, self.baudrate, timeout=self.timeout)
                self.ser_mega = serial.Serial(self.mega_port, self.baudrate, timeout=self.timeout)
                logging.info(f"Puertos abiertos: PC={self.pc_port}, Mega={self.mega_port}")
                break
            except serial.SerialException as e:
                logging.error(f"Error abrir puertos: {e}. Reintentando en 2s...")
                time.sleep(2)

    def start(self):
        self.thread_pc.start()
        self.thread_mega.start()
        logging.info("SerialBroker iniciado.")
        print("SerialBroker iniciado.")

    def stop(self):
        self.running = False
        self.thread_pc.join()
        self.thread_mega.join()
        try:
            self.ser_pc.close()
            self.ser_mega.close()
        except Exception:
            pass
        logging.info("SerialBroker detenido.")

    def _convert_to_steps(self, axis, value, unit):
        cfg = self.axes.get(str(axis))
        if not cfg or 'steps_per_rev' not in cfg:
            raise KeyError(f"Configuración del eje {axis} faltante en axes")
        steps_per_rev = cfg['steps_per_rev']
        gear = cfg.get('gear_ratio', 1)
        if unit == 'G':
            return int(round(value * steps_per_rev * gear / 360.0))
        return value

    def _read_pc_loop(self):
        """Lee comandos del PC, procesa y reenvía o responde"""
        while self.running:
            try:
                line = self.ser_pc.readline().decode('utf-8', errors='ignore')
                if not line:
                    continue
                logging.info(f"PC → {line.strip()}")

                # Heartbeat
                if line == 'C\n':
                    self.ser_pc.write(b'c\n')
                    continue

                # M/A con unidades
                m = self.cmd_regex.match(line)
                if m:
                    cmd, axis_str, val_str, unit = m.groups()
                    axis, val = int(axis_str), int(val_str)
                    unit = unit or 'S'
                    steps = self._convert_to_steps(axis, val, unit)
                    mega_cmd = f"{cmd}{axis}{steps}\n"
                    self.ser_pc.write(b'OK\n')
                    self.ser_mega.write(mega_cmd.encode())
                    continue

                # Otros comandos: H, S, E, K, P, T
                if (self.homing_regex.match(line)
                        or self.status_regex.match(line)
                        or self.estop_regex.match(line)
                        or self.kill_regex.match(line)
                        or self.profile_regex.match(line)
                        or self.timeout_regex.match(line)):
                    self.ser_pc.write(b'OK\n')
                    self.ser_mega.write(line.encode())
                    continue

                # Comando inválido
                self.ser_pc.write(b'ERR1:BadCmd\n')
            except serial.SerialException as e:
                logging.error(f"SerialException en PC: {e}. Reabriendo puertos...")
                self._open_serials()
            except Exception as e:
                logging.error(f"Error en lectura PC: {e}")
                time.sleep(0.1)

    def _read_mega_loop(self):
        """Lee respuestas del Mega y las reenvía al PC"""
        while self.running:
            try:
                line = self.ser_mega.readline().decode('utf-8', errors='ignore')
                if line:
                    logging.info(f"Mega → {line.strip()}")
                    self.ser_pc.write(line.encode())
            except serial.SerialException as e:
                logging.error(f"SerialException en Mega: {e}. Reabriendo puertos...")
                self._open_serials()
            except Exception as e:
                logging.error(f"Error en lectura Mega: {e}")
                time.sleep(0.1)

if __name__ == '__main__':
    broker = SerialBroker('config.yaml')
    try:
        broker.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        broker.stop()
        print("SerialBroker detenido.")
