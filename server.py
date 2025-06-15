from flask import Flask, jsonify, request, make_response, send_file, render_template, flash, session, Response
import os
import pg_database


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Esto genera una clave secreta aleatoria

@app.after_request
def add_header(response):
    """Evitar cache en respuestas"""
    response.headers["Cache-Control"] = "no-store"
    return response

# Instancias de módulos
pgdb = pg_database

# ============ RUTAS DE LA APLICACIÓN ============

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/test-connection")
def test_connection():
    try:
        result = pgdb.test_connection_only()
        if result["success"]:
            return f"<h1>✅ {result['message']}</h1>"
        else:
            return f"<h1>❌ Error: {result['error']}</h1>"
    except Exception as e:
        return f"<h1>❌ Error: {e}</h1>"

def test_db():
    try:
        print("=== PROBANDO CONEXIÓN DB ===")
        conn = pgdb.get_db_connection()
        if conn:
            print("✅ Conexión exitosa")
            conn.close()
            return "<h1>✅ Conexión a DB exitosa</h1>"
        else:
            return "<h1>❌ No se pudo conectar</h1>"
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return f"<h1>❌ Error: {e}</h1>"

@app.route("/n8nreservations")
def n8nreservations():
    try:
        print("=== INICIO SIMPLE TEST ===")
        return "<h1>Test básico funcionando</h1>"
    except Exception as e:
        print(f"Error en test simple: {e}")
        return f"Error: {e}", 500
        
@app.route("/n8nmessages")
def n8nmessages():
    try:
        print("=== TEST MENSAJES ===")
        return "<h1>Test mensajes funcionando</h1>"
    except Exception as e:
        print(f"Error en test mensajes: {e}")
        return f"Error: {e}", 500

# ============ CONFIGURACIÓN PARA RAILWAY ============

# Para Railway/Gunicorn
application = app

# Para desarrollo local
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
    
