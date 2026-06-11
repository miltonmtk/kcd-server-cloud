# ==============================================================================
# BACKEND KCD - SERVIDOR DE LICENCIAS LOCAL (SaaS EXPERIMENTAL)
# ==============================================================================
# Versión: 1.0 (Entorno Local Controlado - Localhost)
# ==============================================================================

from flask import Flask, request, jsonify

app = Flask(__name__)

# Base de datos simulada en memoria
BASE_DATOS_LICENCIAS = {
    "KCD-COLOMBIA-2026": None,  # Licencia disponible
    "KCD-PRUEBA-TEST": "0x9999"  # Licencia bloqueada a otra máquina
}

@app.route('/api/validar-licencia', methods=['POST'])
def validar_licencia():
    datos = request.get_json()
    licencia_cliente = datos.get("licencia")
    hardware_id_cliente = datos.get("hardware_id")

    if licencia_cliente not in BASE_DATOS_LICENCIAS:
        return jsonify({"status": "RECHAZADO", "mensaje": "La clave ingresada no existe."}), 403

    hardware_id_guardado = BASE_DATOS_LICENCIAS[licencia_cliente]

    if hardware_id_guardado is None:
        BASE_DATOS_LICENCIAS[licencia_cliente] = hardware_id_cliente
        print(f"[REGISTRO]: Licencia {licencia_cliente} vinculada al hardware {hardware_id_cliente}")
        return jsonify({"status": "AUTORIZADO", "mensaje": "Equipo registrado con exito por primera vez."}), 200

    if hardware_id_guardado == hardware_id_cliente:
        return jsonify({"status": "AUTORIZADO", "mensaje": "Validacion correcta de licencia activa."}), 200
    else:
        print(f"[ALERTA DE PIRATERÍA]: Uso ilegal de clave {licencia_cliente} desde hardware {hardware_id_cliente}")
        return jsonify({"status": "RECHAZADO", "mensaje": "Esta licencia pertenece a otro equipo."}), 403

if __name__ == '__main__':
    print("========================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)