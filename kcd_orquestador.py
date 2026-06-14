# ==============================================================================
# ESCUDO KCD - ORQUESTADOR DE PRODUCCIÓN PREMIUM
# ==============================================================================
# ==============================================================================
# BLOQUE 0.0 - CONFIGURACIÓN GENERAL
# ==============================================================================
#
# 0.1 Imports
# 0.2 Configuración global
#
# ==============================================================================
import os
import sys
import warnings
import requests
import psutil
import tempfile
import platform
from fpdf import FPDF
import csv
from datetime import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ==============================================================================
# BLOQUE 1.0 - MOTOR IVK
# ==============================================================================
#
# 1.1 Medición de recursos
# 1.2 Cálculo del Índice de Velocidad KCD
#
# ==============================================================================
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

# ==============================================================================
# BLOQUE 2.0 - DIAGNÓSTICO DE MEMORIA
# ==============================================================================
#
# 2.1 Top procesos por RAM
# 2.2 Diagnóstico de memoria
#
# ==============================================================================

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

# ==============================================================================
# BLOQUE 3.0 - CHROME INTELIGENTE
# ==============================================================================
#
# 3.1 Análisis Chrome
# 3.2 Clasificación de subprocesos
# 3.3 Evidencia histórica Chrome
#
# ==============================================================================

def analizar_chrome_kcd():
    procesos_chrome = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            nombre = proc.info['name'] or ""

            if "chrome" in nombre.lower():
                memoria_mb = proc.info['memory_info'].rss / 1024 / 1024

                procesos_chrome.append({
                    "pid": proc.info['pid'],
                    "nombre": nombre,
                    "memoria_mb": round(memoria_mb, 2)
                })

        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            pass

    procesos_chrome.sort(
        key=lambda x: x["memoria_mb"],
        reverse=True
    )

    total_mb = round(
        sum(p["memoria_mb"] for p in procesos_chrome),
        2
    )

    proceso_principal = procesos_chrome[0] if procesos_chrome else None

    print("\n[KCD LAB-07A] ANÁLISIS DE CHROME")
    print(f"Procesos Chrome activos: {len(procesos_chrome)}")
    print(f"RAM total usada por Chrome: {total_mb} MB")

    if proceso_principal:
        print(
            f"Proceso Chrome principal: PID {proceso_principal['pid']} "
            f"| {proceso_principal['memoria_mb']} MB"
        )

        return {
        "procesos": procesos_chrome,
        "total_mb": total_mb,
        "principal": proceso_principal
    }

def clasificar_subprocesos_chrome_kcd():
    categorias = {
        "principal": 0,
        "gpu": 0,
        "red": 0,
        "almacenamiento": 0,
        "renderizadores": 0,
        "extensiones": 0,
        "fallos": 0,
        "otros": 0
    }

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            nombre = proc.info['name'] or ""

            if "chrome" not in nombre.lower():
                continue

            cmdline = " ".join(proc.info['cmdline'] or []).lower()

            if "--type=gpu-process" in cmdline:
                categorias["gpu"] += 1
            elif "networkservice" in cmdline or "network.mojom" in cmdline:
                categorias["red"] += 1
            elif "storageservice" in cmdline or "storage.mojom" in cmdline:
                categorias["almacenamiento"] += 1
            elif "--extension-process" in cmdline:
                categorias["extensiones"] += 1
            elif "crashpad-handler" in cmdline:
                categorias["fallos"] += 1
            elif "--type=renderer" in cmdline:
                categorias["renderizadores"] += 1
            elif "chrome.exe" in cmdline and "--type=" not in cmdline:
                categorias["principal"] += 1
            else:
                categorias["otros"] += 1

        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            pass

    print("\n[KCD LAB-07B] CLASIFICACIÓN CHROME")
    for categoria, cantidad in categorias.items():
        print(f"{categoria}: {cantidad}")

    return categorias

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

# ==============================================================================
# BLOQUE 4.0 - BITÁCORAS Y AUDITORÍA
# ==============================================================================
#
# 4.1 Bitácora general KCD
# 4.2 Registro de acciones
# 4.3 Evidencia histórica
#
# ==============================================================================

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


def registrar_accion_kcd(accion, resultado, detalle):
    nombre_archivo = "acciones_kcd.csv"

    existe_archivo = os.path.exists(nombre_archivo)

    with open(nombre_archivo, mode="a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)

        if not existe_archivo:
            escritor.writerow([
                "fecha_hora",
                "accion",
                "resultado",
                "detalle"
            ])

        escritor.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            accion,
            resultado,
            detalle
        ])

    print(f"\n[KCD ACCIÓN] {accion} registrada.")

def registrar_evidencia_chrome_kcd(
    total_mb,
    categorias
):
    nombre_archivo = "evidencia_chrome_kcd.csv"

    existe_archivo = os.path.exists(nombre_archivo)

    with open(nombre_archivo,
              mode="a",
              newline="",
              encoding="utf-8") as archivo:

        escritor = csv.writer(archivo)

        if not existe_archivo:
            escritor.writerow([
                "fecha_hora",
                "ram_total_chrome",
                "procesos_chrome",
                "renderizadores",
                "extensiones",
                "gpu",
                "red",
                "almacenamiento"
            ])

        escritor.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_mb,
            sum(categorias.values()),
            categorias["renderizadores"],
            categorias["extensiones"],
            categorias["gpu"],
            categorias["red"],
            categorias["almacenamiento"]
        ])

    print("\n[KCD EVIDENCIA] Evidencia Chrome registrada.")

# ==============================================================================
# BLOQUE 5.0 - ANALÍTICA KCD
# ==============================================================================
#
# 5.1 Tendencias
# 5.2 Recomendaciones inteligentes
# 5.3 Beneficios para el cliente
#
# ==============================================================================

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

def mostrar_beneficios_kcd(datos, ivk):
    beneficios = []

    if datos["ram"] > 80:
        beneficios.append(
            "Mayor velocidad en multitarea."
        )

        beneficios.append(
            "Menor espera al cambiar entre aplicaciones."
        )

    if ivk < 60:
        beneficios.append(
            "Mejor experiencia durante horas pico de trabajo."
        )

    if datos["disco"] > 80:
        beneficios.append(
            "Mayor disponibilidad de espacio para trabajo diario."
        )

    print("\n[KCD]")
    print("KCD detectó una oportunidad para mejorar la velocidad de trabajo.\n")

    print("BENEFICIOS\n")

    for beneficio in beneficios:
        print(f"✓ {beneficio}")

    return beneficios

# ==============================================================================
# BLOQUE 6.0 - OPTIMIZACIÓN DEL SISTEMA
# ==============================================================================
#
# 6.1 Evaluación de temporales
# 6.2 Limpieza de temporales
#
# ==============================================================================

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


def ejecutar_limpieza_temporales_kcd():
    carpeta_temp = tempfile.gettempdir()
    archivos_eliminados = 0
    bytes_liberados = 0

    for raiz, carpetas, archivos in os.walk(carpeta_temp):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)

            try:
                tamano = os.path.getsize(ruta)
                os.remove(ruta)

                archivos_eliminados += 1
                bytes_liberados += tamano

            except:
                pass

    mb_liberados = round(bytes_liberados / 1024 / 1024, 2)

    print("\n[KCD RESULTADOS]")
    print(f"✓ Archivos temporales procesados: {archivos_eliminados}")
    print(f"✓ Espacio recuperado: {mb_liberados} MB")

    

    return {
        "archivos": archivos_eliminados,
        "mb": mb_liberados
    }
# ------------------------------------------------------------------------------
# 6.3 Salud del disco
# ------------------------------------------------------------------------------

def analizar_salud_disco_kcd():

    uso = psutil.disk_usage('/')

    total_gb = round(uso.total / (1024 ** 3), 2)
    usado_gb = round(uso.used / (1024 ** 3), 2)
    libre_gb = round(uso.free / (1024 ** 3), 2)

    porcentaje_libre = round(
        (uso.free / uso.total) * 100,
        2
    )

    print("\n[KCD LAB-08A] SALUD DEL DISCO")
    print(f"Capacidad total: {total_gb} GB")
    print(f"Espacio usado: {usado_gb} GB")
    print(f"Espacio libre: {libre_gb} GB")
    print(f"Libre: {porcentaje_libre}%")

    if porcentaje_libre < 10:
        estado = "CRÍTICO"
    elif porcentaje_libre < 20:
        estado = "ALTO RIESGO"
    elif porcentaje_libre < 30:
        estado = "PREVENTIVO"
    else:
        estado = "SALUDABLE"

    print(f"Estado del disco: {estado}")

    return {
        "total_gb": total_gb,
        "usado_gb": usado_gb,
        "libre_gb": libre_gb,
        "porcentaje_libre": porcentaje_libre,
        "estado": estado
    }
# ==============================================================================
# BLOQUE 7.0 - SEGURIDAD Y LICENCIAMIENTO
# ==============================================================================
def crear_identidad_kcd():

    nombre_archivo = "identidad_kcd.csv"

    if os.path.exists(nombre_archivo):
        return

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    kcd_id = "KCD-2026-000001"

    with open(
        nombre_archivo,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow([
            "kcd_id",
            "fecha_activacion",
            "version_kcd",
	    "estado_kcd",
	    "administrador_id",
            "nombre_administrador",
            "equipo"
        ])

        escritor.writerow([
            kcd_id,
            fecha,
	    "LAB-09C",
            "ACTIVO",
            "ADM-000001",
            "MILTON MONTAÑO",
            platform.node()
        ])

    print("\n[KCD ID]")
    print(f"Identidad creada: {kcd_id}")

def crear_cliente_kcd():
    nombre_archivo = "clientes_kcd.csv"

    if os.path.exists(nombre_archivo):
        return

    cliente_id = "CLI-000001"
    nombre_cliente = "MILTON MONTAÑO"
    tipo_cliente = "INDEPENDIENTE"
    estado_cliente = "ACTIVO"
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(
        nombre_archivo,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow([
            "cliente_id",
            "nombre_cliente",
            "tipo_cliente",
            "estado_cliente",
            "fecha_registro"
        ])

        escritor.writerow([
            cliente_id,
            nombre_cliente,
            tipo_cliente,
            estado_cliente,
            fecha_registro
        ])

    print("\n[KCD CLIENTE]")
    print(f"Cliente creado: {cliente_id} | {nombre_cliente}")

def crear_organizacion_kcd():

    nombre_archivo = "organizaciones_kcd.csv"

    if os.path.exists(nombre_archivo):
        return

    with open(
        nombre_archivo,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow([
            "organizacion_id",
            "cliente_id",
            "nombre_organizacion",
            "estado_organizacion",
            "fecha_registro"
        ])

        escritor.writerow([
            "ORG-000001",
            "CLI-000001",
            "SALAMANDRA",
            "ACTIVO",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

    print("\n[KCD ORGANIZACIÓN]")
    print("Organización creada: ORG-000001 | SALAMANDRA")

# 7.1 Validación remota de licencia
#
# ==============================================================================

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

# ==============================================================================
# BLOQUE 8.0 - REPORTES PDF
# ==============================================================================
#
# 8.1 Clase PDF KCD
# 8.2 Generador de informes
#
# ==============================================================================

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

# ==============================================================================
# BLOQUE 9.0 - ORQUESTADOR PRINCIPAL
# ==============================================================================
#
# 9.1 Flujo principal de ejecución
#
# ==============================================================================

if __name__ == '__main__':
    LICENCIA_ACTUAL = "KCD-COLOMBIA-2026"
    HARDWARE_ID_ACTUAL = "LAPTOP-MILTON-01"

    crear_identidad_kcd()

    crear_cliente_kcd()

    crear_organizacion_kcd()

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

    mostrar_beneficios_kcd(
        datos,
        ivk
    )

    temporales = evaluar_temporales_kcd()

    ejecutar_limpieza_temporales_kcd()

    analizar_salud_disco_kcd()

    datos_chrome = analizar_chrome_kcd()

    categorias_chrome = clasificar_subprocesos_chrome_kcd()

    registrar_evidencia_chrome_kcd(
        datos_chrome["total_mb"],
        categorias_chrome
    )
