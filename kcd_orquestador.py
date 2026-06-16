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
# BLOQUE 8.0 - REPORTES PDF
# ==============================================================================
#
# 8.1 Clase PDF KCD
# 8.2 Generador de informes
# 8.3 Diagnóstico Ejecutivo
#
# ==============================================================================

class PDF_KCD(FPDF):

    def header(self):

        self.set_fill_color(24, 43, 73)
        self.rect(0, 0, 210, 20, "F")

        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 14)

        self.cell(
            0,
            10,
            "INFORME DE CONTINUIDAD DIGITAL Y AUDITORIA",
            align="C"
        )

        self.ln(15)

    def footer(self):

        self.set_y(-15)

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
            190,
            8,
            titulo,
            border=0,
            ln=1,
            fill=True
        )

        self.ln(2)


def generar_reporte_pdf_real():

    print(
        "[PROCESO]: Compilando informe KCD..."
    )

    nombre_pdf = "reporte_continuity_digital.pdf"

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

    disco = psutil.disk_usage("/")

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

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.cell(
        0,
        6,
        "ID Reporte: KCD-LAB-01",
        ln=1
    )

    pdf.cell(
        0,
        6,
        "Modulo: Continuidad Digital",
        ln=1
    )

    pdf.ln(3)

    pdf.agregar_seccion_titulo(
        "PARTE 1 - MEDICION REAL DEL EQUIPO"
    )

    pdf.cell(
        0,
        6,
        f"CPU: {datos['cpu']}%",
        ln=1
    )

    pdf.cell(
        0,
        6,
        f"RAM: {datos['ram']}%",
        ln=1
    )

    pdf.cell(
        0,
        6,
        f"DISCO: {datos['disco']}%",
        ln=1
    )

    pdf.cell(
        0,
        6,
        f"IVK: {ivk}%",
        ln=1
    )

    pdf.ln(3)

    pdf.agregar_seccion_titulo(
        "PARTE 2 - DIAGNOSTICO EJECUTIVO"
    )

    pdf.cell(
        0,
        6,
        f"Riesgo General: {diagnostico['riesgo']}",
        ln=1
    )

    pdf.cell(
        0,
        6,
        f"Hallazgo Principal: {diagnostico['hallazgo']}",
        ln=1
    )

    pdf.ln(3)

    pdf.agregar_seccion_titulo(
        "PARTE 3 - PLAN DE ACCION"
    )

    if ram_total < 4:

        pdf.cell(
            0,
            6,
            "- Ampliar memoria RAM.",
            ln=1
        )

    if espacio_libre_pct < 20:

        pdf.cell(
            0,
            6,
            "- Liberar espacio en disco.",
            ln=1
        )

    if ivk <= 45:

        pdf.cell(
            0,
            6,
            "- Ejecutar optimizacion preventiva.",
            ln=1
        )

    pdf.output(
        nombre_pdf
    )

    print("\n========================================================")
    print(f"[OK KCD]: '{nombre_pdf}' generado correctamente.")
    print(f"[IVK]: Indice de Velocidad KCD: {ivk}%")
    print("========================================================")

    return True


# ------------------------------------------------------------------------------
# 8.3 DIAGNOSTICO EJECUTIVO UNIFICADO
# ------------------------------------------------------------------------------

def diagnostico_ejecutivo_kcd(
    datos,
    ivk,
    ram_total,
    espacio_libre_pct
):

    print(
        "\n[KCD LAB-09A] DIAGNÓSTICO EJECUTIVO"
    )

    riesgo = "BAJO"

    if (
        ram_total < 4
        or espacio_libre_pct < 15
        or ivk <= 45
    ):
        riesgo = "ALTO"

    elif (
        ram_total < 8
        or espacio_libre_pct < 25
    ):
        riesgo = "MODERADO"

    if ram_total < 4:

        principal = (
            f"Memoria RAM insuficiente ({ram_total} GB)."
        )

    elif espacio_libre_pct < 15:

        principal = (
            f"Espacio libre reducido ({espacio_libre_pct}%)."
        )

    else:

        principal = (
            "No se detectan limitaciones críticas."
        )

    print(
        f"Riesgo general: {riesgo}"
    )

    print(
        f"Hallazgo principal: {principal}"
    )

    return {
        "riesgo": riesgo,
        "hallazgo": principal
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
# BLOQUE 10.0 - OPTIMIZACIÓN Y CORRECCIÓN
# ==============================================================================
#
# 10.1 Clasificación de problemas detectados
# 10.2 Plan de acción KCD
# 10.3 Evidencia de corrección
#
# ==============================================================================

def clasificar_problemas_kcd(
    ivk,
    ram_total,
    espacio_libre_pct
):

    print(
        "\n[KCD LAB-10A] CLASIFICACIÓN DE PROBLEMAS"
    )

    corregibles = []

    no_corregibles = []

    if espacio_libre_pct < 20:

        corregibles.append(
            "Liberación de espacio en disco"
        )

    if ivk <= 45:

        corregibles.append(
            "Optimización preventiva del sistema"
        )

    if ram_total < 4:

        no_corregibles.append(
            "Ampliación física de memoria RAM"
        )

    print("\nCORREGIBLES POR SOFTWARE:")

    if corregibles:

        for item in corregibles:

            print(
                f"- {item}"
            )

    else:

        print(
            "- Ninguno"
        )

    print("\nNO CORREGIBLES POR SOFTWARE:")

    if no_corregibles:

        for item in no_corregibles:

            print(
                f"- {item}"
            )

    else:

        print(
            "- Ninguno"
        )

    return {
        "corregibles": corregibles,
        "no_corregibles": no_corregibles
    }


def generar_plan_accion_kcd(
    clasificacion
):

    print(
        "\n[KCD LAB-10B] PLAN DE ACCIÓN"
    )

    acciones = []

    for problema in clasificacion["corregibles"]:

        if problema == "Liberación de espacio en disco":

            acciones.append(
                "Ejecutar limpieza preventiva."
            )

        elif problema == "Optimización preventiva del sistema":

            acciones.append(
                "Aplicar optimización recomendada."
            )

    if clasificacion["no_corregibles"]:

        acciones.append(
            "Programar intervención técnica."
        )

    if acciones:

        for numero, accion in enumerate(
            acciones,
            start=1
        ):

            print(
                f"{numero}. {accion}"
            )

    else:

        print(
            "No se requieren acciones."
        )

    return acciones


def registrar_plan_accion_kcd(
    acciones
):

    if not acciones:
        return

    for accion in acciones:

        registrar_accion_kcd(
            "PLAN_ACCION",
            "PENDIENTE",
            accion
        )

    print(
        "\n[KCD LAB-10C] PLAN REGISTRADO"
    )