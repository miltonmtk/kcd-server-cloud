# ==============================================================================
# ESCUDO KCD - ORQUESTADOR DE PRODUCCIÓN PREMIUM
# ==============================================================================

import os
import sys
import warnings
import requests
import psutil
import tempfile
from fpdf import FPDF
import csv
from datetime import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def medir_velocidad_kcd():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disco = psutil.disk_usage('/').percent

    print("\n[KCD LAB-01] Medición real de velocidad")
    print(f"CPU: {cpu}%")
    print(f"RAM: {ram}%")
    print(f"DISCO: {disco}%")

    return {
        "cpu": cpu,
        "ram": ram,
        "disco": disco
    }


def calcular_indice_velocidad(cpu, ram, disco):
    penalizacion = 0

    if cpu > 60:
        penalizacion += 20

    if ram > 75:
        penalizacion += 30

    if disco > 80:
        penalizacion += 25

    indice = 100 - penalizacion
    return max(indice, 0)

def obtener_top_procesos_ram(limite=10):
    procesos = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            memoria_mb = proc.info['memory_info'].rss / 1024 / 1024

            procesos.append({
                "pid": proc.info['pid'],
                "nombre": proc.info['name'],
                "memoria_mb": round(memoria_mb, 2)
            })

        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            pass

    procesos.sort(
        key=lambda x: x['memoria_mb'],
        reverse=True
    )

    return procesos[:limite]


def diagnosticar_estado_ram(ram, procesos):
    diagnosticos = []

    if ram > 85:
        diagnosticos.append("RAM en estado crítico: posible lentitud durante trabajo en hora pico.")
    elif ram > 75:
        diagnosticos.append("RAM alta: el equipo puede presentar demoras al abrir programas o navegar.")
    else:
        diagnosticos.append("RAM en estado aceptable.")

    if procesos:
        proceso_mayor = procesos[0]
        diagnosticos.append(
            f"Proceso con mayor consumo de RAM: {proceso_mayor['nombre']} "
            f"({proceso_mayor['memoria_mb']} MB)."
        )

    return diagnosticos

def registrar_bitacora_kcd(datos, ivk, procesos_ram, diagnosticos_ram):
    nombre_archivo = "bitacora_kcd.csv"
    existe_archivo = os.path.exists(nombre_archivo)

    proceso_principal = procesos_ram[0] if procesos_ram else {
        "nombre": "N/A",
        "pid": "N/A",
        "memoria_mb": 0
    }

    with open(nombre_archivo, mode="a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)

        if not existe_archivo:
            escritor.writerow([
                "fecha_hora",
                "cpu",
                "ram",
                "disco",
                "ivk",
                "proceso_principal",
                "pid",
                "memoria_mb",
                "diagnostico"
            ])

        escritor.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datos["cpu"],
            datos["ram"],
            datos["disco"],
            ivk,
            proceso_principal["nombre"],
            proceso_principal["pid"],
            proceso_principal["memoria_mb"],
            " | ".join(diagnosticos_ram)
        ])

    print("\n[KCD BITÁCORA] Registro guardado en bitacora_kcd.csv")


def analizar_tendencias_kcd():
    nombre_archivo = "bitacora_kcd.csv"

    if not os.path.exists(nombre_archivo):
        print("\n[KCD TENDENCIAS] No existe bitácora.")
        return

    with open(nombre_archivo, mode="r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        registros = list(lector)

    if not registros:
        print("\n[KCD TENDENCIAS] No hay registros.")
        return

    ivks = [float(r["ivk"]) for r in registros]
    rams = [float(r["ram"]) for r in registros]

    print("\n[KCD TENDENCIAS]")
    print(f"Registros analizados: {len(registros)}")
    print(f"IVK promedio: {round(sum(ivks)/len(ivks), 2)}")
    print(f"Mejor IVK: {max(ivks)}")
    print(f"Peor IVK: {min(ivks)}")
    print(f"RAM promedio: {round(sum(rams)/len(rams), 2)}%")

def generar_recomendaciones_kcd(datos, ivk, procesos_ram):
    recomendaciones = []

    proceso_principal = procesos_ram[0] if procesos_ram else None

    if datos["ram"] > 85:
        recomendaciones.append("RAM crítica: cerrar programas o pestañas no esenciales.")

    if proceso_principal and "chrome" in proceso_principal["nombre"].lower():
        recomendaciones.append("Chrome consume más RAM: cerrar pestañas inactivas o reiniciar navegador.")

    if datos["disco"] > 80:
        recomendaciones.append("Disco alto: liberar espacio eliminando temporales y descargas innecesarias.")

    if ivk < 50:
        recomendaciones.append("IVK bajo: ejecutar optimización preventiva.")

    print("\n[KCD LAB-04] RECOMENDACIONES INTELIGENTES")
    for recomendacion in recomendaciones:
        print(f"- {recomendacion}")

    return recomendaciones

def evaluar_temporales_kcd():
    carpeta_temp = tempfile.gettempdir()

    total_archivos = 0
    total_bytes = 0

    for raiz, carpetas, archivos in os.walk(carpeta_temp):
        for archivo in archivos:
            try:
                ruta = os.path.join(raiz, archivo)

                total_archivos += 1
                total_bytes += os.path.getsize(ruta)

            except:
                pass

    total_mb = round(total_bytes / 1024 / 1024, 2)

    print("\n[KCD LAB-05A] EVALUACIÓN DE TEMPORALES")
    print(f"Archivos temporales detectados: {total_archivos}")
    print(f"Espacio recuperable estimado: {total_mb} MB")

    return {
        "archivos": total_archivos,
        "mb": total_mb
    }

def verificar_licencia_remota(clave_licencia, hardware_id):
    URL_API = "http://127.0.0.1:5000/api/validar-licencia"
    payload = {"licencia": clave_licencia, "hardware_id": hardware_id}

    try:
        respuesta = requests.post(URL_API, json=payload, timeout=5)

        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"\n[KCD SECURITY]: {datos.get('mensaje', 'Acceso Otorgado')}")
            return True

        print("\n[KCD ALERTA]: Acceso denegado por el servidor.")
        return False

    except Exception:
        print("\n[KCD ERROR CRÍTICO]: No se pudo conectar con la API de licencias.")
        return False


class PDF_KCD(FPDF):
    def header(self):
        self.set_fill_color(24, 43, 73)
        self.rect(0, 0, 210, 32, 'F')
        self.set_text_color(255, 255, 255)

        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 5, 'INFORME DE CONTINUIDAD DIGITAL Y AUDITORIA',
                  new_x="LMARGIN", new_y="NEXT", align='C')

        self.set_font('Helvetica', '', 9)
        self.cell(0, 6, 'Escudo KCD - Kit de Continuidad Digital Automatizado 24/7',
                  new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()} | Auditoria Interna Escudo KCD', align='C')

    def agregar_seccion_titulo(self, titulo):
        self.set_fill_color(230, 240, 250)
        self.set_text_color(24, 43, 73)
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, f" {titulo}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)


def generar_reporte_pdf_real():
    nombre_pdf = 'reporte_continuity_digital.pdf'

    print("[PROCESO]: Compilando informe KCD...")

    datos = medir_velocidad_kcd()
    ivk = calcular_indice_velocidad(datos["cpu"], datos["ram"], datos["disco"])

    pdf = PDF_KCD()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "ID Reporte: KCD-LAB-01", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Modulo: Laboratorio de Velocidad KCD", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.agregar_seccion_titulo("PARTE 1: MEDICION REAL DEL EQUIPO")

    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f"CPU detectado: {datos['cpu']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"RAM detectada: {datos['ram']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"DISCO detectado: {datos['disco']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Indice de Velocidad KCD: {ivk}%", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    pdf.agregar_seccion_titulo("PARTE 2: DIAGNOSTICO COMERCIAL")

    if ivk >= 80:
        diagnostico = "El equipo presenta buen nivel de respuesta."
    elif ivk >= 50:
        diagnostico = "El equipo presenta señales de ralentización que pueden afectar la productividad."
    else:
        diagnostico = "El equipo requiere intervención prioritaria para evitar pérdida de tiempo operativo."

    pdf.multi_cell(0, 6, diagnostico)

    pdf.output(nombre_pdf)

    print("\n========================================================")
    print(f"[OK KCD]: '{nombre_pdf}' generado correctamente.")
    print(f"[IVK]: Índice de Velocidad KCD: {ivk}%")
    print("========================================================")

    return True


if __name__ == '__main__':
    LICENCIA_ACTUAL = "KCD-COLOMBIA-2026"
    HARDWARE_ID_ACTUAL = "LAPTOP-MILTON-01"

    print("[PROCESO]: Solicitando verificacion de credenciales al servidor...")

    # Laboratorio: licencia desactivada temporalmente
    # if not verificar_licencia_remota(LICENCIA_ACTUAL, HARDWARE_ID_ACTUAL):
    #     sys.exit(1)

    datos = medir_velocidad_kcd()

    ivk = calcular_indice_velocidad(
        datos["cpu"],
        datos["ram"],
        datos["disco"]
    )

    print(f"\n[IVK] Índice de Velocidad KCD: {ivk}%")

    procesos_ram = obtener_top_procesos_ram()

    print("\n[KCD LAB-02] TOP PROCESOS POR RAM")
    for proceso in procesos_ram:
        print(
            f"{proceso['nombre']} | "
            f"PID {proceso['pid']} | "
            f"{proceso['memoria_mb']} MB"
        )

    diagnosticos_ram = diagnosticar_estado_ram(
        datos["ram"],
        procesos_ram
    )

    print("\n[KCD DIAGNÓSTICO RAM]")
    for diagnostico in diagnosticos_ram:
        print(f"- {diagnostico}")

    registrar_bitacora_kcd(
    datos,
    ivk,
    procesos_ram,
    diagnosticos_ram
)

analizar_tendencias_kcd()

generar_recomendaciones_kcd(
    datos,
    ivk,
    procesos_ram
)
evaluar_temporales_kcd()