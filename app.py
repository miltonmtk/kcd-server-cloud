from flask import Flask, jsonify, send_file
from kcd_orquestador import generar_reporte_pdf_real

app = Flask(__name__)

@app.route('/')
def home():
    return "Servidor KCD Activo"

@app.route('/ejecutar')
def ejecutar():
    generar_reporte_pdf_real()
    return send_file("reporte_continuity_digital.pdf", as_attachment=True)

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