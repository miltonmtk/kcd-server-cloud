from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Servidor KCD Activo"

@app.route('/ejecutar')
def ejecutar():
    return "Orquestador ejecutado correctamente"

# RUTA NUEVA: Fase P (Planear) del PHVA
@app.route('/check-maintenance', methods=['GET'])
def check_maintenance():
    # Aquí el servidor define la política de mantenimiento
    return jsonify({
        "ejecutar_mantenimiento": True, 
        "tipo": "limpieza_temporales"
    })

if __name__ == '__main__':
    app.run()