import os
import sys
import json
import base64
import threading
from datetime import datetime

# Manejo mejorado de imports para PyInstaller
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError as e:
    print(f"Error importando tkinter: {e}")
    sys.exit(1)

class RansomwareRecoveryTool:
    def __init__(self):
        try:
            self.setup_gui()
        except Exception as e:
            self.show_error(f"Error inicializando la aplicación: {e}")
    
    def setup_gui(self):
        """Configurar interfaz con manejo de errores"""
        try:
            self.root = tk.Tk()
            self.root.title("🔓 System Recovery Tool - Laboratorio")
            self.root.geometry("700x600")
            self.root.minsize(600, 500)
            
            # Centrar ventana
            self.center_window()
            
            # Variables
            self.recovery_key = tk.StringVar()
            self.selected_folder = tk.StringVar(value=os.path.expanduser("~"))
            self.progress = tk.DoubleVar()
            self.status_text = tk.StringVar(value="Listo para recuperar archivos")
            
            # Contadores
            self.files_found = 0
            self.files_recovered = 0
            self.files_failed = 0
            self.encrypted_files = []
            
            self.create_widgets()
            self.setup_bindings()
            
        except Exception as e:
            self.show_error(f"Error configurando interfaz: {e}")
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="🔓 HERRAMIENTA DE RECUPERACIÓN DE ARCHIVOS", 
                               font=("Arial", 14, "bold"),
                               foreground="#2E7D32",
                               justify="center")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Frame de clave
        key_frame = ttk.LabelFrame(main_frame, text="🔑 Clave de Recuperación", padding="10")
        key_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(key_frame, text="Clave proporcionada por el soporte técnico:").grid(row=0, column=0, sticky=tk.W)
        
        self.key_entry = ttk.Entry(key_frame, textvariable=self.recovery_key, 
                                  width=40, font=("Arial", 10))
        self.key_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.key_entry.focus()
        
        # Frame de carpeta
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Ubicación de Archivos", padding="10")
        folder_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(folder_frame, text="Carpeta donde buscar archivos afectados:").grid(row=0, column=0, sticky=tk.W)
        
        folder_grid = ttk.Frame(folder_frame)
        folder_grid.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.folder_entry = ttk.Entry(folder_grid, textvariable=self.selected_folder, width=50)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(folder_grid, text="📂 Examinar", 
                  command=self.browse_folder).grid(row=0, column=1, padx=(5, 0))
        
        # Botón de DEBUG
        debug_frame = ttk.Frame(main_frame)
        debug_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Button(debug_frame, text="🐛 Debug - Ver Clave en Archivos", 
                  command=self.debug_files, width=25).grid(row=0, column=0, padx=5)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        self.scan_btn = ttk.Button(button_frame, text="🔍 Buscar Archivos Afectados", 
                                  command=self.start_scan, width=20)
        self.scan_btn.grid(row=0, column=0, padx=5)
        
        self.recover_btn = ttk.Button(button_frame, text="🔓 Recuperar Archivos", 
                                     command=self.start_recovery, width=20,
                                     state="disabled")
        self.recover_btn.grid(row=0, column=1, padx=5)
        
        # Progreso
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progreso", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress, length=500)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_text)
        self.status_label.grid(row=1, column=0, pady=5)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="📋 Resultados y Logs", padding="10")
        results_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        # Área de texto con scroll
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.results_text = tk.Text(text_frame, height=12, width=80, wrap=tk.WORD,
                                   font=("Consolas", 9), bg="#F5F5F5")
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configurar pesos de grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        folder_grid.columnconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_bindings(self):
        """Configurar eventos del teclado"""
        self.root.bind('<Return>', lambda e: self.start_recovery())
        self.root.bind('<F5>', lambda e: self.start_scan())
        self.key_entry.bind('<KeyRelease>', self.on_key_change)
    
    def on_key_change(self, event):
        """Habilitar botones cuando haya clave"""
        if self.recovery_key.get().strip():
            self.recover_btn.config(state="normal")
        else:
            self.recover_btn.config(state="disabled")
    
    def browse_folder(self):
        """Seleccionar carpeta"""
        folder = filedialog.askdirectory(initialdir=self.selected_folder.get())
        if folder:
            self.selected_folder.set(folder)
            self.log_message(f"📍 Carpeta seleccionada: {folder}")
    
    def debug_files(self):
        """Función de debugging - muestra las claves reales en los archivos"""
        folder = self.selected_folder.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Selecciona una carpeta válida")
            return
        
        self.log_message("\n🔍 INICIANDO DEBUGGING...")
        self.log_message("Buscando archivos .encrypted y mostrando sus claves:")
        
        encrypted_files = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.encrypted'):
                    encrypted_files.append(os.path.join(root, file))
        
        if not encrypted_files:
            self.log_message("❌ No se encontraron archivos .encrypted")
            return
        
        self.log_message(f"📁 Encontrados {len(encrypted_files)} archivos:")
        
        # Revisar los primeros 3 archivos
        for i, file_path in enumerate(encrypted_files[:3]):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                file_key = data.get('recovery_key', 'NO_HAY_CLAVE')
                self.log_message(f"   {i+1}. {os.path.basename(file_path)}")
                self.log_message(f"      🔑 Clave en archivo: '{file_key}'")
                
            except Exception as e:
                self.log_message(f"   {i+1}. {os.path.basename(file_path)} - ERROR: {e}")
        
        if len(encrypted_files) > 3:
            self.log_message(f"   ... y {len(encrypted_files) - 3} archivos más")
        
        self.log_message("🐛 DEBUGGING COMPLETADO")
    
    def log_message(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.results_text.insert(tk.END, formatted_message)
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Limpiar área de logs"""
        self.results_text.delete(1.0, tk.END)
    
    def start_scan(self):
        """Iniciar escaneo"""
        folder = self.selected_folder.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Selecciona una carpeta válida")
            return
        
        self.clear_log()
        self.scan_btn.config(state="disabled")
        self.recover_btn.config(state="disabled")
        
        thread = threading.Thread(target=self.scan_thread)
        thread.daemon = True
        thread.start()
    
    def scan_thread(self):
        """Hilo de escaneo"""
        try:
            folder = self.selected_folder.get()
            self.log_message(f"🔍 Iniciando escaneo en: {folder}")
            
            encrypted_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.encrypted'):
                        encrypted_files.append(os.path.join(root, file))
            
            self.encrypted_files = encrypted_files
            self.root.after(0, self.scan_completed, encrypted_files)
            
        except Exception as e:
            self.root.after(0, lambda: self.scan_error(f"Error en escaneo: {e}"))
    
    def scan_completed(self, files):
        """Escaneo completado"""
        self.scan_btn.config(state="normal")
        self.files_found = len(files)
        
        if files:
            self.status_text.set(f"✅ Encontrados {len(files)} archivos para recuperar")
            self.log_message(f"📊 Escaneo completado: {len(files)} archivos encontrados")
            self.recover_btn.config(state="normal")
        else:
            self.status_text.set("❌ No se encontraron archivos .encrypted")
            self.log_message("ℹ️  No se encontraron archivos cifrados")
    
    def scan_error(self, error):
        """Error en escaneo"""
        self.scan_btn.config(state="normal")
        messagebox.showerror("Error", error)
        self.log_message(f"❌ {error}")
    
    def start_recovery(self):
        """Iniciar recuperación"""
        key = self.recovery_key.get().strip()
        if not key:
            messagebox.showerror("Error", "Ingresa la clave de recuperación")
            return
        
        if not self.encrypted_files:
            messagebox.showwarning("Advertencia", "Primero busca los archivos afectados")
            return
        
        confirm = messagebox.askyesno(
            "Confirmar", 
            f"¿Recuperar {len(self.encrypted_files)} archivos?\n\n"
            f"Clave: {key}\n"
            f"Ubicación: {self.selected_folder.get()}"
        )
        
        if confirm:
            self.recover_btn.config(state="disabled")
            self.scan_btn.config(state="disabled")
            thread = threading.Thread(target=self.recovery_thread, args=(key,))
            thread.daemon = True
            thread.start()
    
    def recovery_thread(self, key):
        """Hilo de recuperación"""
        try:
            total = len(self.encrypted_files)
            recovered = 0
            
            self.log_message(f"🔓 Iniciando recuperación de {total} archivos...")
            self.log_message(f"🔑 Clave usada: '{key}'")
            
            for i, file_path in enumerate(self.encrypted_files):
                progress = (i / total) * 100
                self.progress.set(progress)
                self.status_text.set(f"Procesando {i+1}/{total}")
                
                success, result = self.recover_file(file_path, key)
                if success:
                    recovered += 1
                    self.log_message(f"✅ {os.path.basename(result)}")
                else:
                    self.log_message(f"❌ {os.path.basename(file_path)}: {result}")
            
            self.progress.set(100)
            self.root.after(0, self.recovery_completed, recovered, total - recovered)
            
        except Exception as e:
            self.root.after(0, lambda: self.recovery_error(f"Error: {e}"))
    
    def recover_file(self, encrypted_path, key):
        """Recuperar archivo individual - CON DEBUGGING DETALLADO"""
        try:
            self.log_message(f"🔍 Procesando: {os.path.basename(encrypted_path)}")
            
            with open(encrypted_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # DEBUG DETALLADO
            file_key = data.get('recovery_key', 'NO_HAY_CLAVE')
            self.log_message(f"   🔑 Clave en archivo: '{file_key}'")
            self.log_message(f"   🔑 Clave ingresada: '{key}'")
            self.log_message(f"   ✅ ¿Coinciden? {file_key == key}")
            
            if data.get('recovery_key') != key:
                self.log_message(f"   ❌ FALLO - Claves no coinciden")
                return False, "Clave incorrecta"
            
            original_data = base64.b64decode(data['original_data'])
            original_path = data['original_path']
            
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            with open(original_path, 'wb') as f:
                f.write(original_data)
            
            os.remove(encrypted_path)
            backup = original_path + ".backup"
            if os.path.exists(backup):
                os.remove(backup)
            
            self.log_message(f"   ✅ ÉXITO - Archivo recuperado")
            return True, original_path
            
        except Exception as e:
            self.log_message(f"   ❌ ERROR: {str(e)}")
            return False, str(e)
    
    def recovery_completed(self, success, failed):
        """Recuperación completada"""
        self.scan_btn.config(state="normal")
        self.recover_btn.config(state="normal")
        
        self.log_message("\n🎉 PROCESO COMPLETADO")
        self.log_message("=" * 40)
        self.log_message(f"✅ Recuperados: {success}")
        self.log_message(f"❌ Fallidos: {failed}")
        
        if success > 0:
            self.status_text.set(f"✅ Recuperación exitosa - {success} archivos")
            messagebox.showinfo("Éxito", f"Recuperados {success} archivos correctamente")
        else:
            self.status_text.set("❌ No se recuperaron archivos")
            messagebox.showerror("Error", "No se pudo recuperar ningún archivo")
    
    def recovery_error(self, error):
        """Error en recuperación"""
        self.scan_btn.config(state="normal")
        self.recover_btn.config(state="normal")
        messagebox.showerror("Error", error)
    
    def show_error(self, message):
        """Mostrar error crítico"""
        if hasattr(self, 'root') and self.root:
            messagebox.showerror("Error Crítico", message)
        else:
            print(f"Error: {message}")
        sys.exit(1)
    
    def run(self):
        """Ejecutar aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.show_error(f"Error ejecutando aplicación: {e}")

def main():
    """Función principal con manejo de errores"""
    try:
        app = RansomwareRecoveryTool()
        app.run()
    except Exception as e:
        messagebox.showerror("Error Inicial", f"No se pudo iniciar la aplicación:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()