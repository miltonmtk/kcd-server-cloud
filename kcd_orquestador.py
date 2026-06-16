# ==============================================================================
# ESCUDO KCD - ORQUESTADOR DE PRODUCCIÓN PREMIUM
# ==============================================================================
# # ==============================================================================
# BLOQUE 0.0 - CONFIGURACIÓN GENERAL
# ==============================================================================
#
# 0.1 Imports
# 0.2 Configuración global
#
# ==============================================================================

import os
import sys
import csv
import time
import tempfile
import platform
import warnings
from datetime import datetime

import psutil
import requests

from fpdf import FPDF

warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning
)

warnings.filterwarnings(
    "ignore",
    category=UserWarning
)
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
# # ==============================================================================
# BLOQUE 2.0 - DIAGNÓSTICO DE MEMORIA
# ==============================================================================
#
# 2.1 Top procesos por RAM
# 2.2 Diagnóstico de memoria
#
# ==============================================================================

def obtener_top_procesos_ram(
    limite=10
):

    procesos = []

    for proc in psutil.process_iter(
        ['pid', 'name', 'memory_info']
    ):

        try:

            memoria_mb = (
                proc.info['memory_info'].rss
                / 1024
                / 1024
            )

            procesos.append({
                "pid": proc.info['pid'],
                "nombre": proc.info['name'],
                "memoria_mb": round(
                    memoria_mb,
                    2
                )
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            pass

    procesos.sort(
        key=lambda x: x["memoria_mb"],
        reverse=True
    )

    return procesos[:limite]


def diagnosticar_estado_ram(
    uso_ram,
    procesos_ram
):

    diagnosticos = []

    if uso_ram >= 90:

        diagnosticos.append(
            "RAM en estado crítico: posible lentitud durante trabajo en hora pico."
        )

    elif uso_ram >= 75:

        diagnosticos.append(
            "RAM con alta ocupación: se recomienda monitoreo."
        )

    else:

        diagnosticos.append(
            "RAM en estado saludable."
        )

    if procesos_ram:

        principal = procesos_ram[0]

        diagnosticos.append(
            f"Proceso con mayor consumo de RAM: "
            f"{principal['nombre']} "
            f"({principal['memoria_mb']} MB)."
        )

    return diagnosticos

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

    for proc in psutil.process_iter(
        ['pid', 'name', 'memory_info']
    ):

        try:

            nombre = (
                proc.info['name']
                or ""
            )

            if "chrome" in nombre.lower():

                memoria_mb = (
                    proc.info['memory_info'].rss
                    / 1024
                    / 1024
                )

                procesos_chrome.append({
                    "pid": proc.info['pid'],
                    "nombre": nombre,
                    "memoria_mb": round(
                        memoria_mb,
                        2
                    )
                })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            pass

    procesos_chrome.sort(
        key=lambda x: x["memoria_mb"],
        reverse=True
    )

    total_mb = round(
        sum(
            p["memoria_mb"]
            for p in procesos_chrome
        ),
        2
    )

    proceso_principal = (
        procesos_chrome[0]
        if procesos_chrome
        else None
    )

    print(
        "\n[KCD LAB-07A] ANÁLISIS DE CHROME"
    )

    print(
        f"Procesos Chrome activos: {len(procesos_chrome)}"
    )

    print(
        f"RAM total usada por Chrome: {total_mb} MB"
    )

    if proceso_principal:

        print(
            f"Proceso Chrome principal: "
            f"PID {proceso_principal['pid']} "
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

    for proc in psutil.process_iter(
        ['pid', 'name', 'cmdline']
    ):

        try:

            nombre = (
                proc.info['name']
                or ""
            )

            if "chrome" not in nombre.lower():
                continue

            cmdline = " ".join(
                proc.info['cmdline']
                or []
            ).lower()

            if "--type=gpu-process" in cmdline:

                categorias["gpu"] += 1

            elif (
                "networkservice" in cmdline
                or
                "network.mojom" in cmdline
            ):

                categorias["red"] += 1

            elif (
                "storageservice" in cmdline
                or
                "storage.mojom" in cmdline
            ):

                categorias["almacenamiento"] += 1

            elif "--extension-process" in cmdline:

                categorias["extensiones"] += 1

            elif "crashpad-handler" in cmdline:

                categorias["fallos"] += 1

            elif "--type=renderer" in cmdline:

                categorias["renderizadores"] += 1

            elif (
                "chrome.exe" in cmdline
                and
                "--type=" not in cmdline
            ):

                categorias["principal"] += 1

            else:

                categorias["otros"] += 1

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            pass

    print(
        "\n[KCD LAB-07B] CLASIFICACIÓN CHROME"
    )

    for categoria, cantidad in categorias.items():

        print(
            f"{categoria}: {cantidad}"
        )

    return categorias


# ==============================================================================
# BLOQUE 4.0 - BITÁCORA Y EVIDENCIAS
# ==============================================================================
# 4. BITÁCORA, ACCIONES Y EVIDENCIA KCD
# ==============================================================================
# 4.1 Bitácora general KCD
# 4.2 Registro de acciones
# 4.3 Evidencia histórica
# ==============================================================================

def escribir_csv_kcd(
    nombre_archivo,
    encabezados,
    fila
):
    existe_archivo = os.path.exists(
        nombre_archivo
    )

    with open(
        nombre_archivo,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        if not existe_archivo:
            escritor.writerow(
                encabezados
            )

        escritor.writerow(
            fila
        )


def obtener_fecha_hora_kcd():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def registrar_bitacora_kcd(
    datos,
    ivk,
    procesos_ram,
    diagnosticos_ram
):

    nombre_archivo = "bitacora_kcd.csv"

    proceso_principal = (
        procesos_ram[0]
        if procesos_ram
        else {
            "nombre": "N/A",
            "pid": "N/A",
            "memoria_mb": 0
        }
    )

    encabezados = [
        "fecha_hora",
        "cpu",
        "ram",
        "disco",
        "ivk",
        "proceso_principal",
        "pid",
        "memoria_mb",
        "diagnostico"
    ]

    fila = [
        obtener_fecha_hora_kcd(),
        datos.get("cpu", 0),
        datos.get("ram", 0),
        datos.get("disco", 0),
        ivk,
        proceso_principal.get("nombre", "N/A"),
        proceso_principal.get("pid", "N/A"),
        proceso_principal.get("memoria_mb", 0),
        " | ".join(
            diagnosticos_ram
            if diagnosticos_ram
            else ["Sin diagnóstico registrado"]
        )
    ]

    escribir_csv_kcd(
        nombre_archivo,
        encabezados,
        fila
    )

    print(
        "\n[KCD BITÁCORA] Registro guardado en bitacora_kcd.csv"
    )


def registrar_accion_kcd(
    accion,
    resultado,
    detalle
):

    nombre_archivo = "acciones_kcd.csv"

    encabezados = [
        "fecha_hora",
        "accion",
        "resultado",
        "detalle"
    ]

    fila = [
        obtener_fecha_hora_kcd(),
        accion,
        resultado,
        detalle
    ]

    escribir_csv_kcd(
        nombre_archivo,
        encabezados,
        fila
    )

    print(
        f"\n[KCD ACCIÓN] {accion} registrada."
    )


def registrar_evidencia_chrome_kcd(
    total_mb,
    categorias
):

    nombre_archivo = "evidencia_chrome_kcd.csv"

    renderizadores = categorias.get(
        "renderizadores",
        0
    )

    extensiones = categorias.get(
        "extensiones",
        0
    )

    gpu = categorias.get(
        "gpu",
        0
    )

    red = categorias.get(
        "red",
        0
    )

    almacenamiento = categorias.get(
        "almacenamiento",
        0
    )

    procesos_chrome = (
        renderizadores
        + extensiones
        + gpu
        + red
        + almacenamiento
    )

    encabezados = [
        "fecha_hora",
        "ram_total_chrome",
        "procesos_chrome",
        "renderizadores",
        "extensiones",
        "gpu",
        "red",
        "almacenamiento"
    ]

    fila = [
        obtener_fecha_hora_kcd(),
        total_mb,
        procesos_chrome,
        renderizadores,
        extensiones,
        gpu,
        red,
        almacenamiento
    ]

    escribir_csv_kcd(
        nombre_archivo,
        encabezados,
        fila
    )

    print(
        "\n[KCD EVIDENCIA] Evidencia Chrome registrada."
    )


def registrar_evidencia_correccion_kcd(
    accion,
    antes,
    despues,
    resultado
):

    nombre_archivo = "evidencia_correccion_kcd.csv"

    encabezados = [
        "fecha_hora",
        "accion",
        "antes",
        "despues",
        "resultado"
    ]

    fila = [
        obtener_fecha_hora_kcd(),
        accion,
        antes,
        despues,
        resultado
    ]

    escribir_csv_kcd(
        nombre_archivo,
        encabezados,
        fila
    )

    print(
        f"\n[KCD CORRECCIÓN] Evidencia registrada: {accion}"
    )

# # ==============================================================================
# ==============================================================================
# BLOQUE 5.0 - ANÁLISIS, TENDENCIAS Y RECOMENDACIONES KCD
# ==============================================================================
# 5.1 Análisis de tendencias
# 5.2 Recomendaciones automáticas
# 5.3 Beneficios técnicos
# 5.4 Clasificación de acciones recomendadas
# ==============================================================================

def analizar_tendencias_kcd():

    nombre_archivo = "bitacora_kcd.csv"

    tendencias = {
        "registros": 0,
        "cpu_promedio": 0,
        "ram_promedio": 0,
        "disco_promedio": 0,
        "ivk_promedio": 0,
        "estado": "Sin datos suficientes"
    }

    if not os.path.exists(
        nombre_archivo
    ):
        print(
            "\n[KCD TENDENCIAS] No existe bitacora_kcd.csv para analizar."
        )
        return tendencias

    registros = []

    try:
        with open(
            nombre_archivo,
            mode="r",
            encoding="utf-8"
        ) as archivo:

            lector = csv.DictReader(
                archivo
            )

            for fila in lector:
                try:
                    registros.append({
                        "cpu": float(
                            fila.get("cpu", 0)
                        ),
                        "ram": float(
                            fila.get("ram", 0)
                        ),
                        "disco": float(
                            fila.get("disco", 0)
                        ),
                        "ivk": float(
                            fila.get("ivk", 0)
                        )
                    })
                except Exception:
                    continue

    except Exception as error:
        print(
            f"\n[KCD ERROR] No se pudo analizar la bitácora: {error}"
        )
        return tendencias

    total_registros = len(
        registros
    )

    if total_registros == 0:
        print(
            "\n[KCD TENDENCIAS] No hay registros válidos para analizar."
        )
        return tendencias

    cpu_promedio = sum(
        item["cpu"] for item in registros
    ) / total_registros

    ram_promedio = sum(
        item["ram"] for item in registros
    ) / total_registros

    disco_promedio = sum(
        item["disco"] for item in registros
    ) / total_registros

    ivk_promedio = sum(
        item["ivk"] for item in registros
    ) / total_registros

    if ivk_promedio <= 45:
        estado = "Crítico"
    elif (
        ram_promedio >= 85
        or cpu_promedio >= 85
        or disco_promedio >= 90
    ):
        estado = "Crítico"
    elif ivk_promedio <= 65:
        estado = "Preventivo"
    elif (
        ram_promedio >= 70
        or cpu_promedio >= 70
        or disco_promedio >= 80
    ):
        estado = "Preventivo"
    else:
        estado = "Estable"

    tendencias = {
        "registros": total_registros,
        "cpu_promedio": round(
            cpu_promedio,
            2
        ),
        "ram_promedio": round(
            ram_promedio,
            2
        ),
        "disco_promedio": round(
            disco_promedio,
            2
        ),
        "ivk_promedio": round(
            ivk_promedio,
            2
        ),
        "estado": estado
    }

    print(
        "\n[KCD TENDENCIAS] Análisis completado."
    )
    print(
        f"Registros analizados: {tendencias['registros']}"
    )
    print(
        f"CPU promedio: {tendencias['cpu_promedio']}%"
    )
    print(
        f"RAM promedio: {tendencias['ram_promedio']}%"
    )
    print(
        f"Disco promedio: {tendencias['disco_promedio']}%"
    )
    print(
        f"IVK promedio: {tendencias['ivk_promedio']}"
    )
    print(
        f"Estado general: {tendencias['estado']}"
    )

    return tendencias


def generar_recomendaciones_kcd(
    datos=None,
    ivk=None,
    procesos_ram=None,
    diagnosticos_ram=None
):

    recomendaciones = []

    if datos is None:
        datos = {}

    if procesos_ram is None:
        procesos_ram = []

    if diagnosticos_ram is None:
        diagnosticos_ram = []

    cpu = float(
        datos.get("cpu", 0)
    )

    ram = float(
        datos.get("ram", 0)
    )

    disco = float(
        datos.get("disco", 0)
    )

    if ivk is None:
        ivk = 100

    try:
        ivk = float(
            ivk
        )
    except Exception:
        ivk = 100

    if cpu >= 85:
        recomendaciones.append(
            "Revisar procesos con alto consumo de CPU y cerrar tareas no críticas."
        )
    elif cpu >= 70:
        recomendaciones.append(
            "Monitorear CPU y validar aplicaciones en segundo plano."
        )

    if ram >= 85:
        recomendaciones.append(
            "Liberar memoria RAM cerrando procesos pesados o reiniciando aplicaciones críticas."
        )
    elif ram >= 70:
        recomendaciones.append(
            "Aplicar mantenimiento preventivo sobre consumo de memoria RAM."
        )

    if disco >= 90:
        recomendaciones.append(
            "Liberar espacio en disco eliminando temporales, cachés y archivos innecesarios."
        )
    elif disco >= 80:
        recomendaciones.append(
            "Programar limpieza preventiva de disco."
        )

    if ivk <= 45:
        recomendaciones.append(
            "Priorizar corrección inmediata por IVK bajo."
        )
    elif ivk <= 65:
        recomendaciones.append(
            "Mantener vigilancia preventiva por IVK medio."
        )

    if procesos_ram:
        proceso_principal = procesos_ram[0]
        nombre = proceso_principal.get(
            "nombre",
            "N/A"
        )
        memoria = proceso_principal.get(
            "memoria_mb",
            0
        )

        recomendaciones.append(
            f"Auditar el proceso con mayor consumo de RAM: {nombre} ({memoria} MB)."
        )

    for diagnostico in diagnosticos_ram:
        if diagnostico not in recomendaciones:
            recomendaciones.append(
                diagnostico
            )

    if not recomendaciones:
        recomendaciones.append(
            "El sistema se encuentra estable. Continuar monitoreo preventivo periódico."
        )

    print(
        "\n[KCD RECOMENDACIONES] Recomendaciones generadas."
    )

    for recomendacion in recomendaciones:
        print(
            f"- {recomendacion}"
        )

    return recomendaciones


def mostrar_beneficios_kcd(
    datos=None,
    ivk=None
):

    beneficios = [
        "Reducción de fallas por mantenimiento preventivo.",
        "Identificación temprana de consumo elevado de CPU, RAM y disco.",
        "Registro histórico de evidencias técnicas.",
        "Soporte para auditoría de acciones correctivas.",
        "Mejora de continuidad digital del equipo.",
        "Mayor control operativo sobre procesos críticos.",
        "Base técnica para informes PDF y trazabilidad KCD."
    ]

    if datos is None:
        datos = {}

    try:
        ivk_valor = float(
            ivk
        )
    except Exception:
        ivk_valor = None

    cpu = datos.get(
        "cpu",
        None
    )

    ram = datos.get(
        "ram",
        None
    )

    disco = datos.get(
        "disco",
        None
    )

    print(
        "\n[KCD BENEFICIOS] Beneficios del sistema ESCUDO KCD:"
    )

    for beneficio in beneficios:
        print(
            f"- {beneficio}"
        )

    if cpu is not None:
        print(
            f"- CPU monitoreada: {cpu}%"
        )

    if ram is not None:
        print(
            f"- RAM monitoreada: {ram}%"
        )

    if disco is not None:
        print(
            f"- Disco monitoreado: {disco}%"
        )

    if ivk_valor is not None:
        print(
            f"- IVK evaluado: {ivk_valor}"
        )

    return beneficios


def clasificar_acciones_recomendadas_kcd(
    recomendaciones=None
):

    if recomendaciones is None:
        recomendaciones = []

    clasificacion = {
        "correctivas": [],
        "preventivas": [],
        "auditoria": [],
        "monitoreo": []
    }

    for recomendacion in recomendaciones:

        texto = recomendacion.lower()

        if (
            "cerrar" in texto
            or "liberar" in texto
            or "corrección" in texto
            or "corregir" in texto
            or "reiniciando" in texto
            or "eliminando" in texto
            or "inmediata" in texto
            or "ivk bajo" in texto
        ):
            clasificacion["correctivas"].append(
                recomendacion
            )

        elif (
            "preventivo" in texto
            or "preventiva" in texto
            or "programar" in texto
            or "mantenimiento" in texto
            or "vigilancia" in texto
            or "ivk medio" in texto
        ):
            clasificacion["preventivas"].append(
                recomendacion
            )

        elif (
            "auditar" in texto
            or "auditoría" in texto
            or "evidencia" in texto
            or "registro" in texto
        ):
            clasificacion["auditoria"].append(
                recomendacion
            )

        else:
            clasificacion["monitoreo"].append(
                recomendacion
            )

    print(
        "\n[KCD CLASIFICACIÓN] Acciones recomendadas clasificadas."
    )

    print(
        f"Correctivas: {len(clasificacion['correctivas'])}"
    )
    print(
        f"Preventivas: {len(clasificacion['preventivas'])}"
    )
    print(
        f"Auditoría: {len(clasificacion['auditoria'])}"
    )
    print(
        f"Monitoreo: {len(clasificacion['monitoreo'])}"
    )

    return clasificacion
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

# ------------------------------------------------------------------------------
# 6.4 Programas de inicio automático
# ------------------------------------------------------------------------------
def analizar_inicio_windows_kcd():

    print("\n[KCD LAB-08B] PROGRAMAS DE INICIO")

    programas_detectados = []

    try:
        import winreg

        rutas = [
            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            ),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
        ]

        total = 0

        for raiz, ruta in rutas:

            try:
                clave = winreg.OpenKey(raiz, ruta)
                cantidad = winreg.QueryInfoKey(clave)[1]

                for i in range(cantidad):
                    nombre, valor, _ = winreg.EnumValue(clave, i)
                    total += 1
                    programas_detectados.append(nombre)
                    print(f"{total}. {nombre}")

            except Exception:
                pass

        print(f"\nProgramas detectados: {total}")

        if total >= 20:
            print("Estado: ALTO IMPACTO EN ARRANQUE")
        elif total >= 10:
            print("Estado: IMPACTO MODERADO")
        else:
            print("Estado: ARRANQUE SALUDABLE")

    except Exception as error:
        print(f"Error: {error}")

    return programas_detectados


# ------------------------------------------------------------------------------
# 6.5 Inventario técnico del equipo
# ------------------------------------------------------------------------------

def inventario_tecnico_kcd():

    print("\n[KCD LAB-08C] INVENTARIO TÉCNICO")

    equipo = platform.node()

    sistema = platform.system()

    version = platform.release()

    procesador = platform.processor()

    nucleos_fisicos = psutil.cpu_count(logical=False)

    nucleos_logicos = psutil.cpu_count(logical=True)

    ram_total = round(
        psutil.virtual_memory().total / (1024 ** 3),
        2
    )

    print(f"Equipo: {equipo}")
    print(f"Sistema operativo: {sistema}")
    print(f"Versión: {version}")
    print(f"Procesador: {procesador}")
    print(f"Núcleos físicos: {nucleos_fisicos}")
    print(f"Núcleos lógicos: {nucleos_logicos}")
    print(f"RAM instalada: {ram_total} GB")

    return {
        "equipo": equipo,
        "sistema": sistema,
        "version": version,
        "procesador": procesador,
        "nucleos_fisicos": nucleos_fisicos,
        "nucleos_logicos": nucleos_logicos,
        "ram_total": ram_total
    }

# ------------------------------------------------------------------------------
# 6.6 Tiempo de actividad del sistema
# ------------------------------------------------------------------------------

def analizar_uptime_kcd():

    print("\n[KCD LAB-08D] TIEMPO DE ACTIVIDAD")

    tiempo_arranque = datetime.fromtimestamp(
        psutil.boot_time()
    )

    ahora = datetime.now()

    tiempo_activo = ahora - tiempo_arranque

    dias = tiempo_activo.days

    horas = tiempo_activo.seconds // 3600

    print(
        f"Último arranque: "
        f"{tiempo_arranque.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(
        f"Tiempo activo: "
        f"{dias} días y {horas} horas"
    )

    if dias >= 30:
        estado = "REINICIO RECOMENDADO"

    elif dias >= 15:
        estado = "PREVENTIVO"

    else:
        estado = "SALUDABLE"

    print(f"Estado: {estado}")

    return {
        "dias": dias,
        "horas": horas,
        "estado": estado
    }


# ------------------------------------------------------------------------------
# 6.7 Ocupación del espacio del usuario
# ------------------------------------------------------------------------------

def analizar_espacio_usuario_kcd():

    print("\n[KCD LAB-08E] OCUPACIÓN DEL ESPACIO DEL USUARIO")

    carpetas = {
        "Escritorio": os.path.join(os.path.expanduser("~"), "Desktop"),
        "Documentos": os.path.join(os.path.expanduser("~"), "Documents"),
        "Descargas": os.path.join(os.path.expanduser("~"), "Downloads"),
        "Imágenes": os.path.join(os.path.expanduser("~"), "Pictures"),
        "Videos": os.path.join(os.path.expanduser("~"), "Videos")
    }

    resultados = {}

    for nombre, ruta in carpetas.items():

        total_bytes = 0

        if os.path.exists(ruta):

            for raiz, directorios, archivos in os.walk(ruta):

                for archivo in archivos:

                    try:
                        archivo_completo = os.path.join(
                            raiz,
                            archivo
                        )

                        total_bytes += os.path.getsize(
                            archivo_completo
                        )

                    except Exception:
                        pass

        total_gb = round(
            total_bytes / (1024 ** 3),
            2
        )

        resultados[nombre] = total_gb

        print(f"{nombre}: {total_gb} GB")

    return resultados

# ------------------------------------------------------------------------------
# 6.8 Servicios activos del sistema
# ------------------------------------------------------------------------------

def analizar_servicios_kcd():

    print("\n[KCD LAB-08F] SERVICIOS ACTIVOS")

    servicios_activos = []

    try:

        for servicio in psutil.win_service_iter():

            try:

                info = servicio.as_dict()

                if info["status"] == "running":

                    servicios_activos.append(
                        info["name"]
                    )

            except Exception:
                pass

        total = len(servicios_activos)

        print(f"Servicios activos detectados: {total}")

        print("\nPrimeros 10 servicios:")

        for servicio in servicios_activos[:10]:

            print(f"- {servicio}")

        if total >= 200:
            estado = "ALTO CONSUMO"

        elif total >= 120:
            estado = "MODERADO"

        else:
            estado = "SALUDABLE"

        print(f"\nEstado: {estado}")

        return {
            "total": total,
            "estado": estado
        }

    except Exception as error:

        print(f"Error: {error}")

        return None

# ------------------------------------------------------------------------------
# 6.9 Rendimiento básico del disco
# ------------------------------------------------------------------------------

def analizar_rendimiento_disco_kcd():

    print("\n[KCD LAB-08G] RENDIMIENTO DEL DISCO")

    archivo_prueba = "kcd_test.tmp"
    tamaño_mb = 10

    datos = os.urandom(
        tamaño_mb * 1024 * 1024
    )

    inicio = time.time()

    with open(archivo_prueba, "wb") as archivo:
        archivo.write(datos)

    tiempo_escritura = time.time() - inicio

    inicio = time.time()

    with open(archivo_prueba, "rb") as archivo:
        archivo.read()

    tiempo_lectura = time.time() - inicio

    if tiempo_lectura == 0:
        tiempo_lectura = 0.001

    if tiempo_escritura == 0:
        tiempo_escritura = 0.001

    os.remove(archivo_prueba)

    velocidad_escritura = round(
        tamaño_mb / tiempo_escritura,
        2
    )

    velocidad_lectura = round(
        tamaño_mb / tiempo_lectura,
        2
    )

    print(f"Escritura: {velocidad_escritura} MB/s")
    print(f"Lectura: {velocidad_lectura} MB/s")

    if velocidad_lectura < 50:
        estado = "RENDIMIENTO BAJO"

    elif velocidad_lectura < 150:
        estado = "RENDIMIENTO MODERADO"

    else:
        estado = "RENDIMIENTO ÓPTIMO"

    print(f"Estado: {estado}")

    return {
        "lectura": velocidad_lectura,
        "escritura": velocidad_escritura,
        "estado": estado
    }


# ------------------------------------------------------------------------------
# 6.10 Red y conectividad
# ------------------------------------------------------------------------------

def analizar_red_kcd():

    print("\n[KCD LAB-08H] RED Y CONECTIVIDAD")

    import socket

    nombre_host = socket.gethostname()

    try:
        ip_local = socket.gethostbyname(nombre_host)
    except Exception:
        ip_local = "No detectada"

    print(f"Nombre del equipo en red: {nombre_host}")
    print(f"IP local: {ip_local}")

    try:
        socket.create_connection(
            ("8.8.8.8", 53),
            timeout=3
        )

        estado = "CONECTADO"

    except Exception:
        estado = "SIN CONEXIÓN"

    print(f"Estado de conectividad: {estado}")

    return {
        "host": nombre_host,
        "ip_local": ip_local,
        "estado": estado
    }

# ------------------------------------------------------------------------------
# 6.11 Capacidad de memoria instalada
# ------------------------------------------------------------------------------

def analizar_memoria_instalada_kcd():

    print("\n[KCD LAB-08I] CAPACIDAD DE MEMORIA")

    ram_total = round(
        psutil.virtual_memory().total / (1024 ** 3),
        2
    )

    print(f"RAM instalada: {ram_total} GB")

    if ram_total < 4:

        estado = "INSUFICIENTE"

        recomendacion = (
            "Se recomienda ampliar memoria RAM."
        )

    elif ram_total < 8:

        estado = "LIMITADA"

        recomendacion = (
            "Adecuada para tareas básicas."
        )

    else:

        estado = "ADECUADA"

        recomendacion = (
            "Capacidad apropiada para multitarea."
        )

    print(f"Estado: {estado}")
    print(f"Recomendación: {recomendacion}")

    return {
        "ram_total": ram_total,
        "estado": estado,
        "recomendacion": recomendacion
    }


# ------------------------------------------------------------------------------
# 6.12 Información y estado del procesador
# ------------------------------------------------------------------------------

def analizar_procesador_kcd():

    print("\n[KCD LAB-08J] ANÁLISIS DEL PROCESADOR")

    frecuencia = psutil.cpu_freq()

    frecuencia_actual = round(
        frecuencia.current,
        2
    )

    frecuencia_maxima = round(
        frecuencia.max,
        2
    )

    uso_cpu = psutil.cpu_percent(interval=1)

    print(f"Frecuencia actual: {frecuencia_actual} MHz")
    print(f"Frecuencia máxima: {frecuencia_maxima} MHz")
    print(f"Uso actual CPU: {uso_cpu}%")

    if uso_cpu >= 80:

        estado = "ALTA CARGA"

    elif uso_cpu >= 50:

        estado = "CARGA MODERADA"

    else:

        estado = "SALUDABLE"

    print(f"Estado: {estado}")

    return {
        "frecuencia_actual": frecuencia_actual,
        "frecuencia_maxima": frecuencia_maxima,
        "uso_cpu": uso_cpu,
        "estado": estado
    }


# ==============================================================================
# BLOQUE 7.0 - SEGURIDAD Y LICENCIAMIENTO
# ==============================================================================
#
# 7.1 Identidad KCD
# 7.2 Cliente
# 7.3 Organización
# 7.4 Validación remota de licencia
#
# ==============================================================================

def crear_identidad_kcd():

    nombre_archivo = "identidad_kcd.csv"

    if os.path.exists(nombre_archivo):
        return

    fecha = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    kcd_id = "KCD-2026-000001"

    with open(
        nombre_archivo,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

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
    print(
        f"Identidad creada: {kcd_id}"
    )


def crear_cliente_kcd():

    nombre_archivo = "clientes_kcd.csv"

    if os.path.exists(nombre_archivo):
        return

    cliente_id = "CLI-000001"

    fecha_registro = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        nombre_archivo,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        escritor.writerow([
            "cliente_id",
            "nombre_cliente",
            "tipo_cliente",
            "estado_cliente",
            "fecha_registro"
        ])

        escritor.writerow([
            cliente_id,
            "MILTON MONTAÑO",
            "INDEPENDIENTE",
            "ACTIVO",
            fecha_registro
        ])

    print("\n[KCD CLIENTE]")
    print(
        f"Cliente creado: {cliente_id} | MILTON MONTAÑO"
    )


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

        escritor = csv.writer(
            archivo
        )

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
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ])

    print("\n[KCD ORGANIZACIÓN]")
    print(
        "Organización creada: ORG-000001 | SALAMANDRA"
    )


def verificar_licencia_remota(
    clave_licencia,
    hardware_id
):

    url_api = (
        "http://127.0.0.1:5000/api/validar-licencia"
    )

    payload = {
        "licencia": clave_licencia,
        "hardware_id": hardware_id
    }

    try:

        respuesta = requests.post(
            url_api,
            json=payload,
            timeout=5
        )

        if respuesta.status_code == 200:

            datos = respuesta.json()

            print(
                f"\n[KCD SECURITY]: "
                f"{datos.get('mensaje', 'Acceso Otorgado')}"
            )

            return True

        print(
            "\n[KCD ALERTA]: "
            "Acceso denegado por el servidor."
        )

        return False

    except Exception:

        print(
            "\n[KCD ERROR CRÍTICO]: "
            "No se pudo conectar con la API de licencias."
        )

        return False


# ==============================================================================
# BLOQUE 8.0 - REPORTES PDF EJECUTIVOS KCD
# ==============================================================================
#
# 8.1 Clase PDF KCD
# 8.2 Generador de informes ejecutivos
# 8.3 Diagnostico ejecutivo unificado
# 8.4 Plan de accion ejecutivo
#
# ==============================================================================

class PDF_KCD(FPDF):

    def header(self):

        self.set_fill_color(
            24,
            43,
            73
        )

        self.rect(
            0,
            0,
            210,
            28,
            "F"
        )

        self.set_text_color(
            255,
            255,
            255
        )

        self.set_font(
            "Helvetica",
            "B",
            14
        )

        self.cell(
            0,
            8,
            "INFORME EJECUTIVO DE CONTINUIDAD DIGITAL",
            ln=1,
            align="C"
        )

        self.set_font(
            "Helvetica",
            "",
            9
        )

        self.cell(
            0,
            6,
            "Escudo KCD - Auditoria preventiva y correctiva del equipo",
            ln=1,
            align="C"
        )

        self.ln(
            14
        )

    def footer(self):

        self.set_y(
            -15
        )

        self.set_font(
            "Helvetica",
            "I",
            8
        )

        self.set_text_color(
            120,
            120,
            120
        )

        self.cell(
            0,
            10,
            f"Pagina {self.page_no()}",
            align="C"
        )

    def agregar_seccion_titulo(
        self,
        titulo
    ):

        self.set_font(
            "Helvetica",
            "B",
            11
        )

        self.set_text_color(
            24,
            43,
            73
        )

        self.set_fill_color(
            230,
            240,
            250
        )

        self.cell(
            0,
            8,
            titulo,
            border=0,
            ln=1,
            fill=True
        )

        self.ln(
            2
        )

    def agregar_texto(
        self,
        texto
    ):

        self.set_font(
            "Helvetica",
            "",
            10
        )

        self.set_text_color(
            40,
            40,
            40
        )

        texto_limpio = str(
            texto
        ).replace(
            "\n",
            " "
        )

        self.multi_cell(
            0,
            6,
            texto_limpio
        )

        self.ln(
            2
        )

    def agregar_item(
        self,
        texto
    ):

        self.set_font(
            "Helvetica",
            "",
            10
        )

        self.set_text_color(
            40,
            40,
            40
        )

        texto_limpio = str(
            texto
        ).replace(
            "\n",
            " "
        )

        self.cell(
            0,
            6,
            f"- {texto_limpio[:110]}",
            ln=1
        )

    def agregar_metrica(
        self,
        etiqueta,
        valor
    ):

        self.set_font(
            "Helvetica",
            "B",
            10
        )

        self.set_text_color(
            24,
            43,
            73
        )

        self.cell(
            45,
            6,
            f"{etiqueta}:",
            ln=0
        )

        self.set_font(
            "Helvetica",
            "",
            10
        )

        self.set_text_color(
            40,
            40,
            40
        )

        self.cell(
            0,
            6,
            str(
                valor
            ),
            ln=1
        )


def generar_reporte_pdf_real():

    print(
        "[PROCESO]: Compilando informe ejecutivo KCD..."
    )

    nombre_pdf = "reporte_ejecutivo_kcd.pdf"

    datos = medir_velocidad_kcd()

    ivk = calcular_indice_velocidad(
        datos["cpu"],
        datos["ram"],
        datos["disco"]
    )

    ram_total = round(
        psutil.virtual_memory().total / (1024 ** 3),
        2
    )

    disco = psutil.disk_usage(
        "/"
    )

    espacio_libre_pct = round(
        (disco.free / disco.total) * 100,
        2
    )

    diagnostico = diagnostico_ejecutivo_kcd(
        datos,
        ivk,
        ram_total,
        espacio_libre_pct
    )

    pdf = PDF_KCD()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.set_margins(
        12,
        12,
        12
    )

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.set_text_color(
        40,
        40,
        40
    )

    pdf.cell(
        0,
        6,
        "ID Reporte: KCD-EJECUTIVO-01",
        ln=1
    )

    pdf.cell(
        0,
        6,
        "Modulo: Continuidad Digital y Mantenimiento Preventivo",
        ln=1
    )

    pdf.cell(
        0,
        6,
        f"Fecha de generacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ln=1
    )

    pdf.ln(
        4
    )

    pdf.agregar_seccion_titulo(
        "1. RESUMEN EJECUTIVO"
    )

    pdf.agregar_texto(
        diagnostico["resumen"]
    )

    pdf.agregar_seccion_titulo(
        "2. NIVEL DE RIESGO"
    )

    pdf.agregar_metrica(
        "Riesgo general",
        diagnostico["riesgo"]
    )

    pdf.agregar_metrica(
        "IVK",
        f"{ivk}%"
    )

    pdf.agregar_metrica(
        "CPU",
        f"{datos['cpu']}%"
    )

    pdf.agregar_metrica(
        "RAM",
        f"{datos['ram']}%"
    )

    pdf.agregar_metrica(
        "Disco usado",
        f"{datos['disco']}%"
    )

    pdf.agregar_metrica(
        "RAM instalada",
        f"{ram_total} GB"
    )

    pdf.agregar_metrica(
        "Espacio libre",
        f"{espacio_libre_pct}%"
    )

    pdf.ln(
        2
    )

    pdf.agregar_seccion_titulo(
        "3. HALLAZGO PRINCIPAL"
    )

    pdf.agregar_texto(
        diagnostico["hallazgo"]
    )

    pdf.agregar_seccion_titulo(
        "4. PROBLEMAS DETECTADOS"
    )

    for problema in diagnostico["problemas"]:

        pdf.agregar_item(
            problema
        )

    pdf.ln(
        2
    )

    pdf.agregar_seccion_titulo(
        "5. ACCIONES RECOMENDADAS"
    )

    for accion in diagnostico["acciones"]:

        pdf.agregar_item(
            accion
        )

    pdf.ln(
        2
    )

    pdf.agregar_seccion_titulo(
        "6. BENEFICIOS ESPERADOS"
    )

    for beneficio in diagnostico["beneficios"]:

        pdf.agregar_item(
            beneficio
        )

    pdf.ln(
        2
    )

    pdf.agregar_seccion_titulo(
        "7. CONCLUSION EJECUTIVA"
    )

    pdf.agregar_texto(
        diagnostico["conclusion"]
    )

    pdf.output(
        nombre_pdf
    )

    print(
        "\n========================================================"
    )

    print(
        f"[OK KCD]: '{nombre_pdf}' generado correctamente."
    )

    print(
        f"[RIESGO]: {diagnostico['riesgo']}"
    )

    print(
        f"[IVK]: Indice de Velocidad KCD: {ivk}%"
    )

    print(
        "========================================================"
    )

    return True


def diagnostico_ejecutivo_kcd(
    datos,
    ivk,
    ram_total,
    espacio_libre_pct
):

    print(
        "\n[KCD LAB-09A] DIAGNOSTICO EJECUTIVO"
    )

    cpu = float(
        datos.get(
            "cpu",
            0
        )
    )

    ram = float(
        datos.get(
            "ram",
            0
        )
    )

    disco = float(
        datos.get(
            "disco",
            0
        )
    )

    try:

        ivk = float(
            ivk
        )

    except Exception:

        ivk = 100

    problemas = []
    acciones = []

    if ivk <= 45:

        problemas.append(
            f"Indice IVK bajo ({ivk}%). El equipo requiere intervencion prioritaria."
        )

        acciones.append(
            "Ejecutar optimizacion preventiva y correctiva del sistema."
        )

    elif ivk <= 65:

        problemas.append(
            f"Indice IVK medio ({ivk}%). Se recomienda seguimiento preventivo."
        )

        acciones.append(
            "Programar mantenimiento preventivo y revisar consumo de recursos."
        )

    if cpu >= 85:

        problemas.append(
            f"Consumo alto de CPU ({cpu}%)."
        )

        acciones.append(
            "Revisar procesos activos y cerrar tareas no esenciales."
        )

    elif cpu >= 70:

        problemas.append(
            f"Consumo moderado de CPU ({cpu}%)."
        )

        acciones.append(
            "Monitorear aplicaciones en segundo plano."
        )

    if ram >= 85:

        problemas.append(
            f"Consumo alto de RAM ({ram}%)."
        )

        acciones.append(
            "Liberar memoria RAM y revisar programas de alto consumo."
        )

    elif ram >= 70:

        problemas.append(
            f"Consumo moderado de RAM ({ram}%)."
        )

        acciones.append(
            "Aplicar mantenimiento preventivo sobre memoria RAM."
        )

    if disco >= 90:

        problemas.append(
            f"Uso critico de disco ({disco}%)."
        )

        acciones.append(
            "Liberar espacio en disco y eliminar archivos temporales."
        )

    elif disco >= 80:

        problemas.append(
            f"Uso elevado de disco ({disco}%)."
        )

        acciones.append(
            "Programar limpieza preventiva de disco."
        )

    if ram_total < 4:

        problemas.append(
            f"Memoria RAM instalada insuficiente ({ram_total} GB)."
        )

        acciones.append(
            "Evaluar ampliacion de memoria RAM."
        )

    elif ram_total < 8:

        problemas.append(
            f"Memoria RAM instalada limitada ({ram_total} GB)."
        )

        acciones.append(
            "Considerar ampliacion de RAM para mejorar continuidad operativa."
        )

    if espacio_libre_pct < 15:

        problemas.append(
            f"Espacio libre critico ({espacio_libre_pct}%)."
        )

        acciones.append(
            "Liberar espacio de almacenamiento de forma prioritaria."
        )

    elif espacio_libre_pct < 25:

        problemas.append(
            f"Espacio libre reducido ({espacio_libre_pct}%)."
        )

        acciones.append(
            "Realizar limpieza preventiva de almacenamiento."
        )

    if not problemas:

        problemas.append(
            "No se detectan problemas criticos en la medicion actual."
        )

    if not acciones:

        acciones.append(
            "Continuar monitoreo preventivo periodico con ESCUDO KCD."
        )

    if (
        ivk <= 45
        or cpu >= 85
        or ram >= 85
        or disco >= 90
        or ram_total < 4
        or espacio_libre_pct < 15
    ):

        riesgo = "ALTO"

    elif (
        ivk <= 65
        or cpu >= 70
        or ram >= 70
        or disco >= 80
        or ram_total < 8
        or espacio_libre_pct < 25
    ):

        riesgo = "MODERADO"

    else:

        riesgo = "BAJO"

    if ivk <= 45:

        hallazgo = (
            f"El equipo presenta un IVK bajo ({ivk}%), lo que indica perdida de rendimiento y necesidad de correccion."
        )

    elif ram_total < 4:

        hallazgo = (
            f"La memoria RAM instalada es insuficiente ({ram_total} GB), limitando la estabilidad operativa."
        )

    elif espacio_libre_pct < 15:

        hallazgo = (
            f"El almacenamiento disponible es critico ({espacio_libre_pct}%), afectando la continuidad digital."
        )

    elif ram >= 85:

        hallazgo = (
            f"El consumo de RAM es alto ({ram}%), lo que puede causar lentitud o bloqueos."
        )

    elif cpu >= 85:

        hallazgo = (
            f"El consumo de CPU es alto ({cpu}%), afectando la respuesta del sistema."
        )

    else:

        hallazgo = (
            "El equipo se encuentra operativo y no presenta limitaciones criticas en la medicion actual."
        )

    beneficios = [
        "Mejorar la estabilidad general del equipo.",
        "Reducir riesgos de lentitud, bloqueo o perdida de continuidad.",
        "Prevenir fallas por saturacion de CPU, RAM o disco.",
        "Contar con evidencia tecnica para decisiones de mantenimiento.",
        "Fortalecer la continuidad digital del usuario o negocio."
    ]

    resumen = (
        f"ESCUDO KCD realizo una evaluacion del estado actual del equipo. "
        f"El nivel de riesgo identificado es {riesgo}. "
        f"El IVK registrado fue de {ivk}%, con CPU en {cpu}%, RAM en {ram}% "
        f"y disco usado en {disco}%. "
        f"El objetivo del informe es convertir la medicion tecnica en una lectura ejecutiva "
        f"para tomar decisiones de mantenimiento preventivo o correctivo."
    )

    conclusion = (
        f"Con base en la evaluacion realizada, el equipo presenta un nivel de riesgo {riesgo}. "
        f"La accion recomendada es atender el hallazgo principal y ejecutar el plan de accion sugerido. "
        f"Este reporte permite priorizar decisiones tecnicas, mejorar el rendimiento y sostener la continuidad digital."
    )

    print(
        f"Riesgo general: {riesgo}"
    )

    print(
        f"Hallazgo principal: {hallazgo}"
    )

    return {
        "riesgo": riesgo,
        "hallazgo": hallazgo,
        "problemas": problemas,
        "acciones": acciones,
        "beneficios": beneficios,
        "resumen": resumen,
        "conclusion": conclusion
    }
# ==============================================================================
# BLOQUE 9.0 - ORQUESTADOR PRINCIPAL
# ==============================================================================
#
# 9.1 Flujo principal de ejecución
#
# ==============================================================================

if __name__ == "__main__":

    LICENCIA_ACTUAL = "KCD-COLOMBIA-2026"
    HARDWARE_ID_ACTUAL = "LAPTOP-MILTON-01"

    crear_identidad_kcd()

    crear_cliente_kcd()

    crear_organizacion_kcd()

    print(
        "[PROCESO]: Solicitando verificacion de credenciales al servidor..."
    )

    # Laboratorio: licencia desactivada temporalmente
    # if not verificar_licencia_remota(
    #     LICENCIA_ACTUAL,
    #     HARDWARE_ID_ACTUAL
    # ):
    #     sys.exit(1)

    datos = medir_velocidad_kcd()

    ivk = calcular_indice_velocidad(
        datos["cpu"],
        datos["ram"],
        datos["disco"]
    )

    print(
        f"\n[IVK] Índice de Velocidad KCD: {ivk}%"
    )

    procesos_ram = obtener_top_procesos_ram()

    print(
        "\n[KCD LAB-02] TOP PROCESOS POR RAM"
    )

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

    print(
        "\n[KCD DIAGNÓSTICO RAM]"
    )

    for diagnostico in diagnosticos_ram:

        print(
            f"- {diagnostico}"
        )

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

    evaluar_temporales_kcd()

    ejecutar_limpieza_temporales_kcd()

    salud_disco = analizar_salud_disco_kcd()

    programas_inicio = analizar_inicio_windows_kcd()

    inventario = inventario_tecnico_kcd()

    analizar_uptime_kcd()

    analizar_espacio_usuario_kcd()

    analizar_servicios_kcd()

    analizar_rendimiento_disco_kcd()

    analizar_red_kcd()

    memoria_info = analizar_memoria_instalada_kcd()

    analizar_procesador_kcd()

    diagnostico = diagnostico_ejecutivo_kcd(
        datos,
        ivk,
        memoria_info["ram_total"],
        salud_disco["porcentaje_libre"]
    )

    datos_chrome = analizar_chrome_kcd()

    categorias_chrome = clasificar_subprocesos_chrome_kcd()

    registrar_evidencia_chrome_kcd(
        datos_chrome["total_mb"],
        categorias_chrome
    )

    registrar_evidencia_correccion_kcd(
        "DIAGNOSTICO_EJECUTIVO",
        "ANALISIS_INICIAL",
        diagnostico["riesgo"],
        "COMPLETADO"
    )

    generar_reporte_pdf_real()


# ==============================================================================
# ==============================================================================
# BLOQUE 10.0 - MOTOR DE REMEDIACION KCD
# ==============================================================================
#
# 10.1 Clasificacion avanzada de problemas detectados
# 10.2 Priorizacion de remediacion
# 10.3 Planes de accion automaticos
# 10.4 Registro de evidencia
# 10.5 Impacto esperado
# 10.6 Control de acciones duplicadas
# 10.7 Preparacion para validacion posterior
#
# ==============================================================================

def obtener_prioridad_kcd(
    problema,
    ivk,
    ram_total,
    espacio_libre_pct
):

    if (
        ivk <= 30
        or espacio_libre_pct < 10
        or ram_total < 4
    ):
        return "CRITICA"

    if (
        ivk <= 45
        or espacio_libre_pct < 15
    ):
        return "ALTA"

    if (
        ivk <= 65
        or espacio_libre_pct < 25
        or ram_total < 8
    ):
        return "MEDIA"

    return "BAJA"


def accion_ya_registrada_kcd(
    problema,
    accion
):

    nombre_archivo = "evidencia_remediacion_kcd.csv"

    if not os.path.exists(
        nombre_archivo
    ):
        return False

    try:

        with open(
            nombre_archivo,
            mode="r",
            encoding="utf-8"
        ) as archivo:

            lector = csv.DictReader(
                archivo
            )

            for fila in lector:

                problema_registrado = fila.get(
                    "problema",
                    ""
                )

                accion_registrada = fila.get(
                    "accion_aplicada",
                    ""
                )

                estado_registrado = fila.get(
                    "estado",
                    ""
                )

                if (
                    problema_registrado == problema
                    and accion_registrada == accion
                    and estado_registrado in [
                        "PENDIENTE",
                        "REGISTRADA",
                        "EN_SEGUIMIENTO"
                    ]
                ):
                    return True

    except Exception:
        return False

    return False


def registrar_evidencia_remediacion_kcd(
    problema,
    accion_aplicada,
    resultado,
    estado,
    categoria,
    prioridad,
    impacto,
    antes
):

    nombre_archivo = "evidencia_remediacion_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha_hora",
        "problema",
        "accion_aplicada",
        "resultado",
        "estado",
        "categoria",
        "prioridad",
        "ram_liberada_estimada_mb",
        "espacio_recuperable_estimado_mb",
        "mejora_ivk_esperada",
        "antes_ivk",
        "antes_ram_total_gb",
        "antes_espacio_libre_pct"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        problema,
        accion_aplicada,
        resultado,
        estado,
        categoria,
        prioridad,
        impacto.get(
            "ram_liberada_estimada_mb",
            0
        ),
        impacto.get(
            "espacio_recuperable_estimado_mb",
            0
        ),
        impacto.get(
            "mejora_ivk_esperada",
            0
        ),
        antes.get(
            "ivk",
            0
        ),
        antes.get(
            "ram_total",
            0
        ),
        antes.get(
            "espacio_libre_pct",
            0
        )
    ]

    with open(
        nombre_archivo,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        if not existe_archivo:

            escritor.writerow(
                encabezados
            )

        escritor.writerow(
            fila
        )


def calcular_impacto_esperado_kcd(
    categoria,
    problema,
    ivk,
    ram_total,
    espacio_libre_pct
):

    impacto = {
        "ram_liberada_estimada_mb": 0,
        "espacio_recuperable_estimado_mb": 0,
        "mejora_ivk_esperada": 0
    }

    texto = problema.lower()

    if (
        "disco" in texto
        or "espacio" in texto
        or categoria == "SOFTWARE"
    ):

        if espacio_libre_pct < 10:
            impacto["espacio_recuperable_estimado_mb"] = 3000
            impacto["mejora_ivk_esperada"] = 15

        elif espacio_libre_pct < 15:
            impacto["espacio_recuperable_estimado_mb"] = 2000
            impacto["mejora_ivk_esperada"] = 10

        elif espacio_libre_pct < 25:
            impacto["espacio_recuperable_estimado_mb"] = 1000
            impacto["mejora_ivk_esperada"] = 5

    if (
        "ram" in texto
        or "memoria" in texto
    ):

        if ram_total < 4:
            impacto["ram_liberada_estimada_mb"] = 300
            impacto["mejora_ivk_esperada"] = max(
                impacto["mejora_ivk_esperada"],
                8
            )

        elif ram_total < 8:
            impacto["ram_liberada_estimada_mb"] = 200
            impacto["mejora_ivk_esperada"] = max(
                impacto["mejora_ivk_esperada"],
                5
            )

    if ivk <= 45:

        impacto["ram_liberada_estimada_mb"] = max(
            impacto["ram_liberada_estimada_mb"],
            250
        )

        impacto["mejora_ivk_esperada"] = max(
            impacto["mejora_ivk_esperada"],
            12
        )

    elif ivk <= 65:

        impacto["mejora_ivk_esperada"] = max(
            impacto["mejora_ivk_esperada"],
            6
        )

    return impacto


def crear_problema_kcd(
    categoria,
    problema,
    ivk,
    ram_total,
    espacio_libre_pct,
    acciones
):

    prioridad = obtener_prioridad_kcd(
        problema,
        ivk,
        ram_total,
        espacio_libre_pct
    )

    impacto = calcular_impacto_esperado_kcd(
        categoria,
        problema,
        ivk,
        ram_total,
        espacio_libre_pct
    )

    return {
        "categoria": categoria,
        "problema": problema,
        "prioridad": prioridad,
        "acciones": acciones,
        "impacto": impacto,
        "antes": {
            "ivk": ivk,
            "ram_total": ram_total,
            "espacio_libre_pct": espacio_libre_pct
        },
        "estado": "PENDIENTE"
    }


def clasificar_problemas_kcd(
    ivk,
    ram_total,
    espacio_libre_pct
):

    print(
        "\n[KCD LAB-10A] CLASIFICACION AVANZADA DE PROBLEMAS"
    )

    try:

        ivk = float(
            ivk
        )

    except Exception:

        ivk = 100

    try:

        ram_total = float(
            ram_total
        )

    except Exception:

        ram_total = 0

    try:

        espacio_libre_pct = float(
            espacio_libre_pct
        )

    except Exception:

        espacio_libre_pct = 100

    software = []
    configuracion = []
    usuario = []
    hardware = []

    if espacio_libre_pct < 25:

        software.append(
            crear_problema_kcd(
                "SOFTWARE",
                f"Espacio libre reducido en disco ({espacio_libre_pct}%).",
                ivk,
                ram_total,
                espacio_libre_pct,
                [
                    "Ejecutar limpieza de archivos temporales.",
                    "Eliminar caches innecesarias.",
                    "Vaciar papelera de reciclaje."
                ]
            )
        )

        configuracion.append(
            crear_problema_kcd(
                "CONFIGURACION",
                "Sistema sin optimizacion automatica de almacenamiento.",
                ivk,
                ram_total,
                espacio_libre_pct,
                [
                    "Activar sensor de almacenamiento si esta disponible.",
                    "Configurar limpieza periodica de temporales.",
                    "Revisar aplicaciones de inicio que generan cache excesiva."
                ]
            )
        )

        usuario.append(
            crear_problema_kcd(
                "USUARIO",
                "Archivos personales o descargas pueden estar ocupando espacio significativo.",
                ivk,
                ram_total,
                espacio_libre_pct,
                [
                    "Revisar carpeta Descargas.",
                    "Mover archivos grandes a respaldo externo.",
                    "Eliminar duplicados y archivos no necesarios."
                ]
            )
        )

    if ivk <= 65:

        software.append(
            crear_problema_kcd(
                "SOFTWARE",
                f"IVK por debajo del nivel optimo ({ivk}%).",
                ivk,
                ram_total,
                espacio_libre_pct,
                [
                    "Ejecutar optimizacion preventiva del sistema.",
                    "Revisar procesos con consumo elevado.",
                    "Registrar evidencia antes de aplicar correcciones."
                ]
            )
        )

        configuracion.append(
            crear_problema_kcd(
                "CONFIGURACION",
                "Configuracion del sistema puede estar afectando el rendimiento.",
                ivk,
                ram_total,
                espacio_libre_pct,
                [
                    "Revisar programas de inicio.",
                    "Validar servicios no esenciales.",
                    "Ajustar configuraciones de rendimiento de Windows."
                ]
            )
        )

    if ram_total < 8:

        hardware.append(
            crear_problema_kcd(
                "HARDWARE",
                f"Memoria RAM fisica limitada ({ram_total} GB).",
                ivk,
                ram_total,
                espacio_libre_pct,
                [
                    "Evaluar ampliacion fisica de memoria RAM.",
                    "Verificar compatibilidad del equipo.",
                    "Programar intervencion tecnica si aplica."
                ]
            )
        )

        usuario.append(
            crear_problema_kcd(
                "USUARIO",
                "Uso simultaneo de aplicaciones puede saturar la memoria disponible.",
                ivk,
                ram_total,
                espacio_libre_pct,
                [
                    "Cerrar aplicaciones no utilizadas.",
                    "Evitar abrir muchas pestanas del navegador.",
                    "Reiniciar aplicaciones pesadas cuando sea necesario."
                ]
            )
        )

    corregibles = []

    for item in software:
        corregibles.append(
            item["problema"]
        )

    for item in configuracion:
        corregibles.append(
            item["problema"]
        )

    for item in usuario:
        corregibles.append(
            item["problema"]
        )

    no_corregibles = []

    for item in hardware:
        no_corregibles.append(
            item["problema"]
        )

    clasificacion = {
        "software": software,
        "configuracion": configuracion,
        "usuario": usuario,
        "hardware": hardware,
        "corregibles": corregibles,
        "no_corregibles": no_corregibles
    }

    categorias = [
        ("SOFTWARE", software),
        ("CONFIGURACION", configuracion),
        ("USUARIO", usuario),
        ("HARDWARE", hardware)
    ]

    for nombre_categoria, elementos in categorias:

        print(
            f"\nPROBLEMAS CORREGIBLES POR {nombre_categoria}:"
        )

        if elementos:

            for item in elementos:

                print(
                    f"- [{item['prioridad']}] {item['problema']}"
                )

        else:

            print(
                "- Ninguno"
            )

    return clasificacion


def generar_plan_accion_kcd(
    clasificacion
):

    print(
        "\n[KCD LAB-10B] PLAN DE ACCION AUTOMATICO"
    )

    acciones_generadas = []

    categorias = [
        "software",
        "configuracion",
        "usuario",
        "hardware"
    ]

    for categoria in categorias:

        problemas = clasificacion.get(
            categoria,
            []
        )

        for problema in problemas:

            for accion in problema.get(
                "acciones",
                []
            ):

                accion_detalle = {
                    "categoria": problema.get(
                        "categoria",
                        categoria.upper()
                    ),
                    "problema": problema.get(
                        "problema",
                        "Problema no especificado"
                    ),
                    "prioridad": problema.get(
                        "prioridad",
                        "BAJA"
                    ),
                    "accion": accion,
                    "resultado": "PENDIENTE",
                    "estado": "PENDIENTE",
                    "impacto": problema.get(
                        "impacto",
                        {}
                    ),
                    "antes": problema.get(
                        "antes",
                        {}
                    )
                }

                if accion_ya_registrada_kcd(
                    accion_detalle["problema"],
                    accion_detalle["accion"]
                ):

                    print(
                        f"[KCD DUPLICADO] Accion omitida: {accion_detalle['accion']}"
                    )

                    continue

                acciones_generadas.append(
                    accion_detalle
                )

    if acciones_generadas:

        for numero, item in enumerate(
            acciones_generadas,
            start=1
        ):

            print(
                f"{numero}. [{item['prioridad']}] {item['accion']}"
            )

    else:

        print(
            "No se requieren acciones nuevas o ya fueron registradas."
        )

    return acciones_generadas


def registrar_plan_accion_kcd(
    acciones
):

    if not acciones:

        print(
            "\n[KCD LAB-10C] No hay acciones nuevas para registrar."
        )

        return False

    for item in acciones:

        if isinstance(
            item,
            dict
        ):

            problema = item.get(
                "problema",
                "Problema no especificado"
            )

            accion = item.get(
                "accion",
                "Accion no especificada"
            )

            resultado = item.get(
                "resultado",
                "PENDIENTE"
            )

            estado = item.get(
                "estado",
                "PENDIENTE"
            )

            categoria = item.get(
                "categoria",
                "SIN_CATEGORIA"
            )

            prioridad = item.get(
                "prioridad",
                "BAJA"
            )

            impacto = item.get(
                "impacto",
                {}
            )

            antes = item.get(
                "antes",
                {}
            )

        else:

            problema = "Plan de accion KCD"
            accion = str(
                item
            )
            resultado = "PENDIENTE"
            estado = "PENDIENTE"
            categoria = "GENERAL"
            prioridad = "MEDIA"
            impacto = {}
            antes = {}

        registrar_evidencia_remediacion_kcd(
            problema,
            accion,
            resultado,
            estado,
            categoria,
            prioridad,
            impacto,
            antes
        )

        registrar_accion_kcd(
            "PLAN_ACCION",
            estado,
            f"[{prioridad}] {categoria} | {problema} | {accion}"
        )

    print(
        "\n[KCD LAB-10C] PLAN DE REMEDIACION REGISTRADO EN EVIDENCIA"
    )

    return True
# ==============================================================================
# BLOQUE 11.0 - VALIDACION Y CERTIFICACION DE RESULTADOS KCD
# ==============================================================================
#
# 11.1 Medicion ANTES con promedio
# 11.2 Medicion DESPUES con promedio
# 11.3 Comparacion de resultados
# 11.4 Evaluacion de efectividad
# 11.5 Evidencia CSV
# 11.6 Mensaje claro para cliente
# 11.7 Certificacion de efectividad KCD
#
# ==============================================================================

def promedio_kcd(
    valores
):

    if not valores:
        return 0

    return round(
        sum(
            valores
        ) / len(
            valores
        ),
        2
    )


def medir_estado_validacion_kcd(
    etapa,
    muestras=3,
    intervalo_segundos=1
):

    print(
        f"\n[KCD VALIDACION] Medicion {etapa} con promedio de {muestras} muestras."
    )

    mediciones_cpu = []
    mediciones_ram = []
    mediciones_disco = []
    mediciones_espacio_libre = []
    mediciones_ivk = []

    ram_total_gb = round(
        psutil.virtual_memory().total / (1024 ** 3),
        2
    )

    for numero in range(
        muestras
    ):

        datos = medir_velocidad_kcd()

        ivk = calcular_indice_velocidad(
            datos["cpu"],
            datos["ram"],
            datos["disco"]
        )

        disco = psutil.disk_usage(
            "/"
        )

        espacio_libre_pct = round(
            (disco.free / disco.total) * 100,
            2
        )

        mediciones_cpu.append(
            float(
                datos.get(
                    "cpu",
                    0
                )
            )
        )

        mediciones_ram.append(
            float(
                datos.get(
                    "ram",
                    0
                )
            )
        )

        mediciones_disco.append(
            float(
                datos.get(
                    "disco",
                    0
                )
            )
        )

        mediciones_espacio_libre.append(
            float(
                espacio_libre_pct
            )
        )

        mediciones_ivk.append(
            float(
                ivk
            )
        )

        if numero < muestras - 1:

            time.sleep(
                intervalo_segundos
            )

    medicion = {
        "etapa": etapa,
        "fecha_hora": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "muestras": muestras,
        "cpu": promedio_kcd(
            mediciones_cpu
        ),
        "ram": promedio_kcd(
            mediciones_ram
        ),
        "disco": promedio_kcd(
            mediciones_disco
        ),
        "espacio_libre_pct": promedio_kcd(
            mediciones_espacio_libre
        ),
        "ivk": promedio_kcd(
            mediciones_ivk
        ),
        "ram_total_gb": ram_total_gb
    }

    print(
        f"CPU promedio: {medicion['cpu']}%"
    )

    print(
        f"RAM promedio: {medicion['ram']}%"
    )

    print(
        f"Disco usado promedio: {medicion['disco']}%"
    )

    print(
        f"Espacio libre promedio: {medicion['espacio_libre_pct']}%"
    )

    print(
        f"IVK promedio: {medicion['ivk']}%"
    )

    print(
        f"RAM instalada: {medicion['ram_total_gb']} GB"
    )

    return medicion


def medir_antes_kcd(
    accion_evaluada="PLAN_ACCION_KCD",
    muestras=3
):

    print(
        "\n[KCD LAB-11A] MEDICION ANTES"
    )

    medicion = medir_estado_validacion_kcd(
        "ANTES",
        muestras
    )

    medicion["accion_evaluada"] = accion_evaluada

    return medicion


def medir_despues_kcd(
    accion_evaluada="PLAN_ACCION_KCD",
    muestras=3
):

    print(
        "\n[KCD LAB-11B] MEDICION DESPUES"
    )

    medicion = medir_estado_validacion_kcd(
        "DESPUES",
        muestras
    )

    medicion["accion_evaluada"] = accion_evaluada

    return medicion


def comparar_mediciones_kcd(
    antes,
    despues
):

    print(
        "\n[KCD LAB-11C] COMPARACION DE RESULTADOS"
    )

    diferencia = {
        "cambio_ivk": round(
            despues["ivk"] - antes["ivk"],
            2
        ),
        "cambio_cpu": round(
            antes["cpu"] - despues["cpu"],
            2
        ),
        "cambio_ram": round(
            antes["ram"] - despues["ram"],
            2
        ),
        "cambio_disco": round(
            antes["disco"] - despues["disco"],
            2
        ),
        "cambio_espacio_libre": round(
            despues["espacio_libre_pct"] - antes["espacio_libre_pct"],
            2
        ),
        "cambio_ram_total_gb": round(
            despues["ram_total_gb"] - antes["ram_total_gb"],
            2
        )
    }

    print(
        f"Cambio IVK: {diferencia['cambio_ivk']}"
    )

    print(
        f"Cambio CPU: {diferencia['cambio_cpu']}"
    )

    print(
        f"Cambio RAM: {diferencia['cambio_ram']}"
    )

    print(
        f"Cambio disco usado: {diferencia['cambio_disco']}"
    )

    print(
        f"Cambio espacio libre: {diferencia['cambio_espacio_libre']}"
    )

    print(
        f"Cambio RAM instalada: {diferencia['cambio_ram_total_gb']} GB"
    )

    return diferencia


def evaluar_efectividad_kcd(
    diferencia
):

    print(
        "\n[KCD LAB-11D] EVALUACION DE EFECTIVIDAD"
    )

    cambio_ivk = diferencia.get(
        "cambio_ivk",
        0
    )

    cambio_ram = diferencia.get(
        "cambio_ram",
        0
    )

    cambio_disco = diferencia.get(
        "cambio_disco",
        0
    )

    cambio_espacio_libre = diferencia.get(
        "cambio_espacio_libre",
        0
    )

    puntaje = 0

    if cambio_ivk >= 8:
        puntaje += 2

    elif cambio_ivk >= 3:
        puntaje += 1

    if cambio_ram >= 8:
        puntaje += 2

    elif cambio_ram >= 3:
        puntaje += 1

    if cambio_disco >= 5:
        puntaje += 2

    elif cambio_disco >= 2:
        puntaje += 1

    if cambio_espacio_libre >= 5:
        puntaje += 2

    elif cambio_espacio_libre >= 2:
        puntaje += 1

    if (
        cambio_ivk <= -5
        or cambio_ram <= -8
        or cambio_disco <= -5
        or cambio_espacio_libre <= -5
    ):

        resultado = "EMPEORO"

    elif puntaje >= 5:

        resultado = "MEJORA ALTA"

    elif puntaje >= 2:

        resultado = "MEJORA MODERADA"

    else:

        resultado = "SIN CAMBIO"

    print(
        f"Resultado de efectividad: {resultado}"
    )

    return resultado


def detectar_problema_estructural_kcd(
    antes,
    despues,
    diferencia,
    resultado
):

    ram_total = despues.get(
        "ram_total_gb",
        0
    )

    espacio_libre = despues.get(
        "espacio_libre_pct",
        100
    )

    cambio_ram_total = diferencia.get(
        "cambio_ram_total_gb",
        0
    )

    if (
        ram_total < 4
        and cambio_ram_total == 0
        and resultado in [
            "SIN CAMBIO",
            "EMPEORO"
        ]
    ):

        return {
            "requiere_hardware": True,
            "motivo": "La memoria RAM instalada es insuficiente y no puede corregirse por software."
        }

    if (
        espacio_libre < 10
        and resultado in [
            "SIN CAMBIO",
            "EMPEORO"
        ]
    ):

        return {
            "requiere_hardware": True,
            "motivo": "El almacenamiento disponible sigue en nivel critico; puede requerir ampliacion o respaldo externo."
        }

    return {
        "requiere_hardware": False,
        "motivo": "No se detecta limitacion estructural obligatoria."
    }


def certificar_efectividad_kcd(
    resultado,
    antes,
    despues,
    diferencia
):

    print(
        "\n[KCD LAB-11F] CERTIFICACION DE EFECTIVIDAD KCD"
    )

    diagnostico_estructural = detectar_problema_estructural_kcd(
        antes,
        despues,
        diferencia,
        resultado
    )

    if diagnostico_estructural["requiere_hardware"]:

        certificacion = "REQUIERE HARDWARE"

    elif resultado == "MEJORA ALTA":

        certificacion = "EFECTIVO"

    elif resultado == "MEJORA MODERADA":

        certificacion = "PARCIALMENTE EFECTIVO"

    elif resultado == "SIN CAMBIO":

        certificacion = "NO EFECTIVO"

    else:

        certificacion = "NO EFECTIVO"

    print(
        f"Certificacion KCD: {certificacion}"
    )

    print(
        f"Motivo: {diagnostico_estructural['motivo']}"
    )

    return {
        "certificacion": certificacion,
        "requiere_hardware": diagnostico_estructural["requiere_hardware"],
        "motivo": diagnostico_estructural["motivo"]
    }


def generar_mensaje_cliente_kcd(
    resultado,
    diferencia,
    certificacion
):

    cambio_ivk = diferencia.get(
        "cambio_ivk",
        0
    )

    cambio_ram = diferencia.get(
        "cambio_ram",
        0
    )

    cambio_disco = diferencia.get(
        "cambio_disco",
        0
    )

    cambio_espacio = diferencia.get(
        "cambio_espacio_libre",
        0
    )

    detalle = (
        f"IVK cambio {cambio_ivk} puntos. "
        f"RAM cambio {cambio_ram}%. "
        f"Disco usado cambio {cambio_disco}%. "
        f"Espacio libre cambio {cambio_espacio}%."
    )

    if certificacion["certificacion"] == "EFECTIVO":

        mensaje = (
            "KCD certifica que la intervencion fue efectiva. "
            + detalle
        )

    elif certificacion["certificacion"] == "PARCIALMENTE EFECTIVO":

        mensaje = (
            "KCD certifica una mejora parcial. "
            "Se recomienda continuar con mantenimiento preventivo. "
            + detalle
        )

    elif certificacion["certificacion"] == "REQUIERE HARDWARE":

        mensaje = (
            "KCD detecta que la mejora por software es limitada. "
            f"{certificacion['motivo']} "
            + detalle
        )

    elif resultado == "EMPEORO":

        mensaje = (
            "KCD detecto empeoramiento posterior a la medicion. "
            "Se recomienda revision tecnica antes de aplicar nuevas correcciones. "
            + detalle
        )

    else:

        mensaje = (
            "KCD no detecto una mejora significativa. "
            "Puede requerirse una accion adicional, revision tecnica o ajuste de hardware. "
            + detalle
        )

    print(
        "\n[KCD MENSAJE CLIENTE]"
    )

    print(
        mensaje
    )

    return mensaje


def registrar_validacion_resultados_kcd(
    accion_evaluada,
    antes,
    despues,
    diferencia,
    resultado,
    certificacion,
    mensaje
):

    nombre_archivo = "validacion_resultados_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha_hora",
        "accion_evaluada",
        "resultado",
        "certificacion",
        "requiere_hardware",
        "motivo_certificacion",
        "mensaje_cliente",
        "antes_fecha_hora",
        "antes_muestras",
        "antes_ivk",
        "antes_cpu",
        "antes_ram",
        "antes_disco",
        "antes_espacio_libre",
        "antes_ram_total_gb",
        "despues_fecha_hora",
        "despues_muestras",
        "despues_ivk",
        "despues_cpu",
        "despues_ram",
        "despues_disco",
        "despues_espacio_libre",
        "despues_ram_total_gb",
        "cambio_ivk",
        "cambio_cpu",
        "cambio_ram",
        "cambio_disco",
        "cambio_espacio_libre",
        "cambio_ram_total_gb"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        accion_evaluada,
        resultado,
        certificacion.get(
            "certificacion",
            ""
        ),
        certificacion.get(
            "requiere_hardware",
            False
        ),
        certificacion.get(
            "motivo",
            ""
        ),
        mensaje,
        antes.get(
            "fecha_hora",
            ""
        ),
        antes.get(
            "muestras",
            0
        ),
        antes.get(
            "ivk",
            0
        ),
        antes.get(
            "cpu",
            0
        ),
        antes.get(
            "ram",
            0
        ),
        antes.get(
            "disco",
            0
        ),
        antes.get(
            "espacio_libre_pct",
            0
        ),
        antes.get(
            "ram_total_gb",
            0
        ),
        despues.get(
            "fecha_hora",
            ""
        ),
        despues.get(
            "muestras",
            0
        ),
        despues.get(
            "ivk",
            0
        ),
        despues.get(
            "cpu",
            0
        ),
        despues.get(
            "ram",
            0
        ),
        despues.get(
            "disco",
            0
        ),
        despues.get(
            "espacio_libre_pct",
            0
        ),
        despues.get(
            "ram_total_gb",
            0
        ),
        diferencia.get(
            "cambio_ivk",
            0
        ),
        diferencia.get(
            "cambio_cpu",
            0
        ),
        diferencia.get(
            "cambio_ram",
            0
        ),
        diferencia.get(
            "cambio_disco",
            0
        ),
        diferencia.get(
            "cambio_espacio_libre",
            0
        ),
        diferencia.get(
            "cambio_ram_total_gb",
            0
        )
    ]

    with open(
        nombre_archivo,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        if not existe_archivo:

            escritor.writerow(
                encabezados
            )

        escritor.writerow(
            fila
        )

    registrar_accion_kcd(
        "VALIDACION_RESULTADOS",
        certificacion.get(
            "certificacion",
            resultado
        ),
        accion_evaluada
    )

    print(
        "\n[KCD LAB-11E] Evidencia de validacion registrada."
    )

    print(
        f"Archivo: {nombre_archivo}"
    )


def validar_resultados_kcd(
    antes,
    accion_evaluada="PLAN_ACCION_KCD",
    muestras=3
):

    print(
        "\n[KCD LAB-11] VALIDACION DE RESULTADOS KCD"
    )

    if not antes:

        print(
            "\n[KCD VALIDACION] No existe medicion ANTES para comparar."
        )

        print(
            "Ejecute primero medir_antes_kcd() antes de aplicar acciones."
        )

        return None

    despues = medir_despues_kcd(
        accion_evaluada,
        muestras
    )

    diferencia = comparar_mediciones_kcd(
        antes,
        despues
    )

    resultado = evaluar_efectividad_kcd(
        diferencia
    )

    certificacion = certificar_efectividad_kcd(
        resultado,
        antes,
        despues,
        diferencia
    )

    mensaje = generar_mensaje_cliente_kcd(
        resultado,
        diferencia,
        certificacion
    )

    registrar_validacion_resultados_kcd(
        accion_evaluada,
        antes,
        despues,
        diferencia,
        resultado,
        certificacion,
        mensaje
    )

    return {
        "accion_evaluada": accion_evaluada,
        "antes": antes,
        "despues": despues,
        "diferencia": diferencia,
        "resultado": resultado,
        "certificacion": certificacion,
        "mensaje": mensaje
    }


def ejecutar_validacion_manual_kcd(
    accion_evaluada="PLAN_ACCION_KCD",
    muestras=3
):

    print(
        "\n[KCD LAB-11 MANUAL] INICIO DE VALIDACION"
    )

    print(
        "Paso 1: Se tomara medicion ANTES con promedio."
    )

    antes = medir_antes_kcd(
        accion_evaluada,
        muestras
    )

    print(
        "\nPaso 2: Ejecute ahora las acciones del Bloque 10."
    )

    print(
        "Paso 3: Luego llame validar_resultados_kcd(antes, accion_evaluada)."
    )

    return antes

# ==============================================================================
# BLOQUE 12.0 - MONITOREO CONTINUO Y ALERTAS KCD
# ==============================================================================
#
# 12.1 Monitoreo continuo CPU
# 12.2 Monitoreo continuo RAM
# 12.3 Monitoreo continuo Disco
# 12.4 Monitoreo continuo Chrome
# 12.5 Alertas automaticas
# 12.6 Registro historico de alertas
# 12.7 Escalamiento de riesgo
# 12.8 Resumen automatico diario
#
# ==============================================================================

def obtener_config_monitoreo_kcd():

    return {
        "cpu_alerta": 75,
        "cpu_critico": 90,
        "ram_alerta": 75,
        "ram_critico": 90,
        "disco_alerta": 80,
        "disco_critico": 90,
        "espacio_libre_alerta": 25,
        "espacio_libre_critico": 15,
        "chrome_ram_alerta_mb": 800,
        "chrome_ram_critico_mb": 1500,
        "chrome_procesos_alerta": 20,
        "chrome_procesos_critico": 40,
        "cooldown_alertas_minutos": 30
    }


def medir_recursos_monitoreo_kcd():

    datos = medir_velocidad_kcd()

    ivk = calcular_indice_velocidad(
        datos["cpu"],
        datos["ram"],
        datos["disco"]
    )

    disco = psutil.disk_usage(
        "/"
    )

    espacio_libre_pct = round(
        (disco.free / disco.total) * 100,
        2
    )

    metricas = {
        "fecha_hora": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "cpu": float(
            datos.get(
                "cpu",
                0
            )
        ),
        "ram": float(
            datos.get(
                "ram",
                0
            )
        ),
        "disco": float(
            datos.get(
                "disco",
                0
            )
        ),
        "espacio_libre_pct": espacio_libre_pct,
        "ivk": float(
            ivk
        )
    }

    return metricas


def monitorear_chrome_kcd():

    total_mb = 0
    procesos = 0

    categorias = {
        "renderizadores": 0,
        "extensiones": 0,
        "gpu": 0,
        "red": 0,
        "almacenamiento": 0,
        "otros": 0
    }

    for proceso in psutil.process_iter(
        [
            "pid",
            "name",
            "cmdline",
            "memory_info"
        ]
    ):

        try:

            nombre = (
                proceso.info.get(
                    "name",
                    ""
                )
                or ""
            ).lower()

            if "chrome" not in nombre:
                continue

            procesos += 1

            memoria = proceso.info.get(
                "memory_info",
                None
            )

            if memoria:

                total_mb += round(
                    memoria.rss / (1024 ** 2),
                    2
                )

            cmdline = proceso.info.get(
                "cmdline",
                []
            )

            texto_cmd = " ".join(
                cmdline
            ).lower()

            if "renderer" in texto_cmd:
                categorias["renderizadores"] += 1

            elif "extension" in texto_cmd:
                categorias["extensiones"] += 1

            elif "gpu" in texto_cmd:
                categorias["gpu"] += 1

            elif "network" in texto_cmd:
                categorias["red"] += 1

            elif "storage" in texto_cmd:
                categorias["almacenamiento"] += 1

            else:
                categorias["otros"] += 1

        except Exception:
            continue

    chrome = {
        "chrome_procesos": procesos,
        "chrome_ram_mb": round(
            total_mb,
            2
        ),
        "chrome_renderizadores": categorias["renderizadores"],
        "chrome_extensiones": categorias["extensiones"],
        "chrome_gpu": categorias["gpu"],
        "chrome_red": categorias["red"],
        "chrome_almacenamiento": categorias["almacenamiento"],
        "chrome_otros": categorias["otros"]
    }

    return chrome


def crear_alerta_kcd(
    tipo,
    nivel,
    mensaje,
    valor,
    umbral,
    sugerencia
):

    return {
        "fecha_hora": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "tipo": tipo,
        "nivel": nivel,
        "mensaje": mensaje,
        "valor": valor,
        "umbral": umbral,
        "sugerencia": sugerencia,
        "estado": "REGISTRADA"
    }


def alerta_reciente_kcd(
    tipo,
    mensaje,
    cooldown_minutos
):

    nombre_archivo = "alertas_kcd.csv"

    if not os.path.exists(
        nombre_archivo
    ):
        return False

    try:

        with open(
            nombre_archivo,
            mode="r",
            encoding="utf-8"
        ) as archivo:

            lector = csv.DictReader(
                archivo
            )

            ahora = datetime.now()

            for fila in lector:

                if (
                    fila.get(
                        "tipo",
                        ""
                    ) != tipo
                ):
                    continue

                if (
                    fila.get(
                        "mensaje",
                        ""
                    ) != mensaje
                ):
                    continue

                fecha_texto = fila.get(
                    "fecha_hora",
                    ""
                )

                try:

                    fecha_alerta = datetime.strptime(
                        fecha_texto,
                        "%Y-%m-%d %H:%M:%S"
                    )

                    diferencia = ahora - fecha_alerta

                    if diferencia.total_seconds() < cooldown_minutos * 60:
                        return True

                except Exception:
                    continue

    except Exception:
        return False

    return False


def registrar_alerta_kcd(
    alerta,
    metricas,
    chrome
):

    nombre_archivo = "alertas_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha_hora",
        "tipo",
        "nivel",
        "mensaje",
        "valor",
        "umbral",
        "sugerencia",
        "estado",
        "cpu",
        "ram",
        "disco",
        "espacio_libre_pct",
        "ivk",
        "chrome_procesos",
        "chrome_ram_mb"
    ]

    fila = [
        alerta.get(
            "fecha_hora",
            ""
        ),
        alerta.get(
            "tipo",
            ""
        ),
        alerta.get(
            "nivel",
            ""
        ),
        alerta.get(
            "mensaje",
            ""
        ),
        alerta.get(
            "valor",
            ""
        ),
        alerta.get(
            "umbral",
            ""
        ),
        alerta.get(
            "sugerencia",
            ""
        ),
        alerta.get(
            "estado",
            ""
        ),
        metricas.get(
            "cpu",
            0
        ),
        metricas.get(
            "ram",
            0
        ),
        metricas.get(
            "disco",
            0
        ),
        metricas.get(
            "espacio_libre_pct",
            0
        ),
        metricas.get(
            "ivk",
            0
        ),
        chrome.get(
            "chrome_procesos",
            0
        ),
        chrome.get(
            "chrome_ram_mb",
            0
        )
    ]

    with open(
        nombre_archivo,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        if not existe_archivo:

            escritor.writerow(
                encabezados
            )

        escritor.writerow(
            fila
        )

    try:

        registrar_accion_kcd(
            "ALERTA_MONITOREO",
            alerta.get(
                "nivel",
                "SIN_NIVEL"
            ),
            alerta.get(
                "mensaje",
                ""
            )
        )

    except Exception:
        pass


def preparar_accion_bloque10_desde_alerta_kcd(
    alerta,
    metricas,
    chrome
):

    nombre_archivo = "acciones_preparadas_bloque10_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha_hora",
        "origen",
        "tipo_alerta",
        "nivel",
        "problema",
        "accion_sugerida",
        "estado",
        "cpu",
        "ram",
        "disco",
        "espacio_libre_pct",
        "ivk",
        "chrome_procesos",
        "chrome_ram_mb"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "BLOQUE_12_MONITOREO",
        alerta.get(
            "tipo",
            ""
        ),
        alerta.get(
            "nivel",
            ""
        ),
        alerta.get(
            "mensaje",
            ""
        ),
        alerta.get(
            "sugerencia",
            ""
        ),
        "PENDIENTE_BLOQUE_10",
        metricas.get(
            "cpu",
            0
        ),
        metricas.get(
            "ram",
            0
        ),
        metricas.get(
            "disco",
            0
        ),
        metricas.get(
            "espacio_libre_pct",
            0
        ),
        metricas.get(
            "ivk",
            0
        ),
        chrome.get(
            "chrome_procesos",
            0
        ),
        chrome.get(
            "chrome_ram_mb",
            0
        )
    ]

    with open(
        nombre_archivo,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        if not existe_archivo:

            escritor.writerow(
                encabezados
            )

        escritor.writerow(
            fila
        )


def detectar_anomalias_kcd(
    metricas,
    chrome,
    config
):

    alertas = []

    cpu = metricas.get(
        "cpu",
        0
    )

    ram = metricas.get(
        "ram",
        0
    )

    disco = metricas.get(
        "disco",
        0
    )

    espacio_libre = metricas.get(
        "espacio_libre_pct",
        100
    )

    ivk = metricas.get(
        "ivk",
        100
    )

    chrome_ram = chrome.get(
        "chrome_ram_mb",
        0
    )

    chrome_procesos = chrome.get(
        "chrome_procesos",
        0
    )

    if cpu >= config["cpu_critico"]:

        alertas.append(
            crear_alerta_kcd(
                "CPU",
                "CRITICO",
                f"CPU en nivel critico ({cpu}%).",
                cpu,
                config["cpu_critico"],
                "Revisar procesos activos antes de ejecutar acciones correctivas."
            )
        )

    elif cpu >= config["cpu_alerta"]:

        alertas.append(
            crear_alerta_kcd(
                "CPU",
                "ALTO",
                f"CPU elevada ({cpu}%).",
                cpu,
                config["cpu_alerta"],
                "Monitorear consumo de CPU y preparar revision preventiva."
            )
        )

    if ram >= config["ram_critico"]:

        alertas.append(
            crear_alerta_kcd(
                "RAM",
                "CRITICO",
                f"RAM en nivel critico ({ram}%).",
                ram,
                config["ram_critico"],
                "Preparar plan de liberacion de memoria para Bloque 10."
            )
        )

    elif ram >= config["ram_alerta"]:

        alertas.append(
            crear_alerta_kcd(
                "RAM",
                "ALTO",
                f"RAM elevada ({ram}%).",
                ram,
                config["ram_alerta"],
                "Monitorear aplicaciones de alto consumo."
            )
        )

    if disco >= config["disco_critico"]:

        alertas.append(
            crear_alerta_kcd(
                "DISCO",
                "CRITICO",
                f"Disco en nivel critico ({disco}% usado).",
                disco,
                config["disco_critico"],
                "Preparar limpieza segura de temporales y cache para Bloque 10."
            )
        )

    elif disco >= config["disco_alerta"]:

        alertas.append(
            crear_alerta_kcd(
                "DISCO",
                "ALTO",
                f"Disco elevado ({disco}% usado).",
                disco,
                config["disco_alerta"],
                "Programar limpieza preventiva de almacenamiento."
            )
        )

    if espacio_libre <= config["espacio_libre_critico"]:

        alertas.append(
            crear_alerta_kcd(
                "ESPACIO_LIBRE",
                "CRITICO",
                f"Espacio libre critico ({espacio_libre}%).",
                espacio_libre,
                config["espacio_libre_critico"],
                "Preparar accion de liberacion de espacio para Bloque 10."
            )
        )

    elif espacio_libre <= config["espacio_libre_alerta"]:

        alertas.append(
            crear_alerta_kcd(
                "ESPACIO_LIBRE",
                "ALTO",
                f"Espacio libre reducido ({espacio_libre}%).",
                espacio_libre,
                config["espacio_libre_alerta"],
                "Revisar almacenamiento antes de que llegue a nivel critico."
            )
        )

    if ivk <= 45:

        alertas.append(
            crear_alerta_kcd(
                "IVK",
                "CRITICO",
                f"IVK bajo ({ivk}%).",
                ivk,
                45,
                "Preparar remediacion con Bloque 10 y validar con Bloque 11."
            )
        )

    elif ivk <= 65:

        alertas.append(
            crear_alerta_kcd(
                "IVK",
                "MODERADO",
                f"IVK medio ({ivk}%).",
                ivk,
                65,
                "Mantener seguimiento preventivo."
            )
        )

    if chrome_ram >= config["chrome_ram_critico_mb"]:

        alertas.append(
            crear_alerta_kcd(
                "CHROME_RAM",
                "CRITICO",
                f"Chrome consume RAM critica ({chrome_ram} MB).",
                chrome_ram,
                config["chrome_ram_critico_mb"],
                "Avisar al usuario para revisar pestanas, extensiones o reiniciar Chrome con autorizacion."
            )
        )

    elif chrome_ram >= config["chrome_ram_alerta_mb"]:

        alertas.append(
            crear_alerta_kcd(
                "CHROME_RAM",
                "ALTO",
                f"Chrome consume RAM elevada ({chrome_ram} MB).",
                chrome_ram,
                config["chrome_ram_alerta_mb"],
                "Monitorear uso de Chrome y preparar recomendacion preventiva."
            )
        )

    if chrome_procesos >= config["chrome_procesos_critico"]:

        alertas.append(
            crear_alerta_kcd(
                "CHROME_PROCESOS",
                "CRITICO",
                f"Chrome tiene demasiados procesos ({chrome_procesos}).",
                chrome_procesos,
                config["chrome_procesos_critico"],
                "Avisar al usuario para revisar extensiones y pestanas abiertas."
            )
        )

    elif chrome_procesos >= config["chrome_procesos_alerta"]:

        alertas.append(
            crear_alerta_kcd(
                "CHROME_PROCESOS",
                "ALTO",
                f"Chrome tiene procesos elevados ({chrome_procesos}).",
                chrome_procesos,
                config["chrome_procesos_alerta"],
                "Monitorear Chrome y preparar recomendacion para el usuario."
            )
        )

    return alertas


def escalar_riesgo_alertas_kcd(
    alertas
):

    if not alertas:
        return "BAJO"

    niveles = [
        alerta.get(
            "nivel",
            "BAJO"
        )
        for alerta in alertas
    ]

    if "CRITICO" in niveles:
        return "CRITICO"

    if "ALTO" in niveles:
        return "ALTO"

    if "MODERADO" in niveles:
        return "MODERADO"

    return "BAJO"


def procesar_alertas_monitoreo_kcd(
    alertas,
    metricas,
    chrome,
    config
):

    alertas_registradas = []

    for alerta in alertas:

        tipo = alerta.get(
            "tipo",
            ""
        )

        mensaje = alerta.get(
            "mensaje",
            ""
        )

        if alerta_reciente_kcd(
            tipo,
            mensaje,
            config["cooldown_alertas_minutos"]
        ):

            print(
                f"[KCD ALERTA] Omitida por cooldown: {mensaje}"
            )

            continue

        registrar_alerta_kcd(
            alerta,
            metricas,
            chrome
        )

        preparar_accion_bloque10_desde_alerta_kcd(
            alerta,
            metricas,
            chrome
        )

        alertas_registradas.append(
            alerta
        )

        print(
            f"[KCD ALERTA {alerta['nivel']}] {alerta['mensaje']}"
        )

    return alertas_registradas


def generar_resumen_diario_alertas_kcd(
    fecha=None
):

    if fecha is None:

        fecha = datetime.now().strftime(
            "%Y-%m-%d"
        )

    archivo_alertas = "alertas_kcd.csv"

    archivo_resumen = "resumen_diario_alertas_kcd.csv"

    if not os.path.exists(
        archivo_alertas
    ):

        print(
            "\n[KCD RESUMEN] No hay alertas registradas."
        )

        return None

    total = 0
    criticas = 0
    altas = 0
    moderadas = 0
    bajas = 0

    tipos = {}

    try:

        with open(
            archivo_alertas,
            mode="r",
            encoding="utf-8"
        ) as archivo:

            lector = csv.DictReader(
                archivo
            )

            for fila in lector:

                fecha_alerta = fila.get(
                    "fecha_hora",
                    ""
                )[:10]

                if fecha_alerta != fecha:
                    continue

                total += 1

                nivel = fila.get(
                    "nivel",
                    "BAJO"
                )

                tipo = fila.get(
                    "tipo",
                    "SIN_TIPO"
                )

                tipos[tipo] = tipos.get(
                    tipo,
                    0
                ) + 1

                if nivel == "CRITICO":
                    criticas += 1

                elif nivel == "ALTO":
                    altas += 1

                elif nivel == "MODERADO":
                    moderadas += 1

                else:
                    bajas += 1

    except Exception as error:

        print(
            f"\n[KCD ERROR] No se pudo generar resumen diario: {error}"
        )

        return None

    if criticas > 0:
        riesgo_dia = "CRITICO"

    elif altas > 0:
        riesgo_dia = "ALTO"

    elif moderadas > 0:
        riesgo_dia = "MODERADO"

    else:
        riesgo_dia = "BAJO"

    existe_resumen = os.path.exists(
        archivo_resumen
    )

    encabezados = [
        "fecha",
        "total_alertas",
        "criticas",
        "altas",
        "moderadas",
        "bajas",
        "riesgo_dia",
        "tipos_alerta"
    ]

    fila = [
        fecha,
        total,
        criticas,
        altas,
        moderadas,
        bajas,
        riesgo_dia,
        " | ".join(
            [
                f"{clave}:{valor}"
                for clave, valor in tipos.items()
            ]
        )
    ]

    with open(
        archivo_resumen,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(
            archivo
        )

        if not existe_resumen:

            escritor.writerow(
                encabezados
            )

        escritor.writerow(
            fila
        )

    print(
        "\n[KCD RESUMEN DIARIO]"
    )

    print(
        f"Fecha: {fecha}"
    )

    print(
        f"Total alertas: {total}"
    )

    print(
        f"Riesgo del dia: {riesgo_dia}"
    )

    return {
        "fecha": fecha,
        "total_alertas": total,
        "criticas": criticas,
        "altas": altas,
        "moderadas": moderadas,
        "bajas": bajas,
        "riesgo_dia": riesgo_dia,
        "tipos_alerta": tipos
    }


def ejecutar_monitoreo_continuo_kcd(
    ciclos=5,
    intervalo_segundos=10,
    config=None
):

    print(
        "\n[KCD BLOQUE 12] MONITOREO CONTINUO Y ALERTAS"
    )

    if config is None:

        config = obtener_config_monitoreo_kcd()

    try:

        ciclos = int(
            ciclos
        )

    except Exception:

        ciclos = 5

    try:

        intervalo_segundos = int(
            intervalo_segundos
        )

    except Exception:

        intervalo_segundos = 10

    if ciclos < 1:

        ciclos = 1

    if ciclos > 288:

        ciclos = 288

    if intervalo_segundos < 5:

        intervalo_segundos = 5

    print(
        f"Ciclos programados: {ciclos}"
    )

    print(
        f"Intervalo: {intervalo_segundos} segundos"
    )

    print(
        "Modo seguro: no se cierran procesos, no se cambian servicios, no se eliminan archivos."
    )

    historial_alertas = []

    for ciclo in range(
        1,
        ciclos + 1
    ):

        print(
            f"\n[KCD MONITOREO] Ciclo {ciclo}/{ciclos}"
        )

        metricas = medir_recursos_monitoreo_kcd()

        chrome = monitorear_chrome_kcd()

        print(
            f"CPU: {metricas['cpu']}% | RAM: {metricas['ram']}% | Disco: {metricas['disco']}% | IVK: {metricas['ivk']}%"
        )

        print(
            f"Chrome: {chrome['chrome_procesos']} procesos | {chrome['chrome_ram_mb']} MB"
        )

        alertas = detectar_anomalias_kcd(
            metricas,
            chrome,
            config
        )

        riesgo = escalar_riesgo_alertas_kcd(
            alertas
        )

        print(
            f"Riesgo del ciclo: {riesgo}"
        )

        alertas_registradas = procesar_alertas_monitoreo_kcd(
            alertas,
            metricas,
            chrome,
            config
        )

        historial_alertas.extend(
            alertas_registradas
        )

        if ciclo < ciclos:

            time.sleep(
                intervalo_segundos
            )

    resumen = {
        "ciclos": ciclos,
        "alertas_registradas": len(
            historial_alertas
        ),
        "riesgo_final": escalar_riesgo_alertas_kcd(
            historial_alertas
        )
    }

    print(
        "\n[KCD MONITOREO FINALIZADO]"
    )

    print(
        f"Ciclos ejecutados: {resumen['ciclos']}"
    )

    print(
        f"Alertas registradas: {resumen['alertas_registradas']}"
    )

    print(
        f"Riesgo final: {resumen['riesgo_final']}"
    )

    generar_resumen_diario_alertas_kcd()

    return resumen