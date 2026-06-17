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


# ==============================================================================
# BLOQUE 13.0 - INTELIGENCIA PREDICTIVA KCD
# ==============================================================================
#
# 13.1 Lectura de historicos KCD
# 13.2 Analisis de tendencias
# 13.3 Prediccion de riesgo
# 13.4 Mantenimiento predictivo
# 13.5 Registro de evidencia predictiva
# 13.6 Factores estructurales directos
#
# ==============================================================================

def leer_historico_csv_kcd(
    nombre_archivo
):

    if not os.path.exists(
        nombre_archivo
    ):

        print(
            f"\n[KCD PREDICTIVO] No existe historico: {nombre_archivo}"
        )

        return []

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

                registros.append(
                    fila
                )

    except Exception as error:

        print(
            f"\n[KCD ERROR] No se pudo leer {nombre_archivo}: {error}"
        )

        return []

    return registros


def convertir_float_kcd(
    valor,
    defecto=0
):

    try:

        return float(
            valor
        )

    except Exception:

        return defecto


def promedio_lista_kcd(
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


def parsear_fecha_kcd(
    fecha_texto
):

    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y"
    ]

    for formato in formatos:

        try:

            return datetime.strptime(
                fecha_texto,
                formato
            )

        except Exception:

            continue

    return None


def calcular_tendencia_kcd(
    valores,
    margen=1
):

    if len(
        valores
    ) < 2:

        return {
            "tendencia": "SIN_DATOS",
            "cambio": 0,
            "promedio_inicial": 0,
            "promedio_final": 0
        }

    mitad = max(
        1,
        len(
            valores
        ) // 2
    )

    bloque_inicial = valores[
        :mitad
    ]

    bloque_final = valores[
        mitad:
    ]

    if not bloque_final:

        bloque_final = valores[
            -1:
        ]

    promedio_inicial = promedio_lista_kcd(
        bloque_inicial
    )

    promedio_final = promedio_lista_kcd(
        bloque_final
    )

    cambio = round(
        promedio_final - promedio_inicial,
        2
    )

    if cambio > margen:

        tendencia = "SUBE"

    elif cambio < -margen:

        tendencia = "BAJA"

    else:

        tendencia = "SE_MANTIENE"

    return {
        "tendencia": tendencia,
        "cambio": cambio,
        "promedio_inicial": promedio_inicial,
        "promedio_final": promedio_final
    }


def obtener_factores_estructurales_actuales_kcd():

    try:

        ram_total_gb = round(
            psutil.virtual_memory().total / (1024 ** 3),
            2
        )

    except Exception:

        ram_total_gb = 0

    try:

        disco = psutil.disk_usage(
            "/"
        )

        espacio_libre_pct = round(
            (disco.free / disco.total) * 100,
            2
        )

    except Exception:

        espacio_libre_pct = 0

    factores = {
        "ram_total_gb": ram_total_gb,
        "espacio_libre_pct": espacio_libre_pct,
        "ram_estructural": ram_total_gb < 4,
        "ram_limitada": ram_total_gb < 8,
        "espacio_critico": espacio_libre_pct < 15,
        "espacio_limitado": espacio_libre_pct < 25
    }

    print(
        "\n[KCD PREDICTIVO] Factores estructurales actuales"
    )

    print(
        f"RAM instalada: {factores['ram_total_gb']} GB"
    )

    print(
        f"Espacio libre actual: {factores['espacio_libre_pct']}%"
    )

    return factores


def analizar_bitacora_predictiva_kcd(
    registros
):

    print(
        "\n[KCD PREDICTIVO] Analizando bitacora_kcd.csv"
    )

    cpu = []
    ram = []
    disco = []
    ivk = []

    for fila in registros:

        cpu.append(
            convertir_float_kcd(
                fila.get(
                    "cpu",
                    0
                )
            )
        )

        ram.append(
            convertir_float_kcd(
                fila.get(
                    "ram",
                    0
                )
            )
        )

        disco.append(
            convertir_float_kcd(
                fila.get(
                    "disco",
                    0
                )
            )
        )

        ivk.append(
            convertir_float_kcd(
                fila.get(
                    "ivk",
                    0
                )
            )
        )

    analisis = {
        "registros": len(
            registros
        ),
        "cpu_promedio": promedio_lista_kcd(
            cpu
        ),
        "ram_promedio": promedio_lista_kcd(
            ram
        ),
        "disco_promedio": promedio_lista_kcd(
            disco
        ),
        "ivk_promedio": promedio_lista_kCD(
            ivk
        ) if False else promedio_lista_kcd(
            ivk
        ),
        "tendencia_cpu": calcular_tendencia_kcd(
            cpu
        ),
        "tendencia_ram": calcular_tendencia_kcd(
            ram
        ),
        "tendencia_disco": calcular_tendencia_kcd(
            disco
        ),
        "tendencia_ivk": calcular_tendencia_kcd(
            ivk
        )
    }

    print(
        f"Registros bitacora: {analisis['registros']}"
    )

    print(
        f"IVK tendencia: {analisis['tendencia_ivk']['tendencia']}"
    )

    print(
        f"RAM tendencia: {analisis['tendencia_ram']['tendencia']}"
    )

    print(
        f"Disco tendencia: {analisis['tendencia_disco']['tendencia']}"
    )

    return analisis


def analizar_alertas_predictivas_kcd(
    registros
):

    print(
        "\n[KCD PREDICTIVO] Analizando alertas_kcd.csv"
    )

    registros_ordenados = []

    for fila in registros:

        fecha = parsear_fecha_kcd(
            fila.get(
                "fecha_hora",
                ""
            )
        )

        if fecha is None:

            continue

        fila["_fecha_parseada"] = fecha

        registros_ordenados.append(
            fila
        )

    registros_ordenados.sort(
        key=lambda item: item["_fecha_parseada"]
    )

    total = len(
        registros_ordenados
    )

    criticas = 0
    altas = 0
    moderadas = 0
    bajas = 0

    tipos = {}

    pesos_temporales = []

    for fila in registros_ordenados:

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
            peso = 4

        elif nivel == "ALTO":

            altas += 1
            peso = 3

        elif nivel == "MODERADO":

            moderadas += 1
            peso = 2

        else:

            bajas += 1
            peso = 1

        pesos_temporales.append(
            peso
        )

    if total < 2:

        tendencia_alertas = {
            "tendencia": "SIN_DATOS",
            "cambio": 0,
            "promedio_inicial": 0,
            "promedio_final": 0
        }

    else:

        tendencia_alertas = calcular_tendencia_kcd(
            pesos_temporales,
            margen=0.5
        )

        if tendencia_alertas["tendencia"] == "SUBE":

            tendencia_alertas["tendencia"] = "AUMENTAN"

        elif tendencia_alertas["tendencia"] == "BAJA":

            tendencia_alertas["tendencia"] = "DISMINUYEN"

        else:

            tendencia_alertas["tendencia"] = "SE_MANTIENEN"

    analisis = {
        "total_alertas": total,
        "criticas": criticas,
        "altas": altas,
        "moderadas": moderadas,
        "bajas": bajas,
        "tipos": tipos,
        "tendencia_alertas": tendencia_alertas
    }

    print(
        f"Total alertas con fecha valida: {total}"
    )

    print(
        f"Alertas criticas: {criticas}"
    )

    print(
        f"Tendencia temporal de alertas: {tendencia_alertas['tendencia']}"
    )

    return analisis


def analizar_validaciones_predictivas_kcd(
    registros
):

    print(
        "\n[KCD PREDICTIVO] Analizando validacion_resultados_kcd.csv"
    )

    total = len(
        registros
    )

    efectivos = 0
    parciales = 0
    no_efectivos = 0
    requieren_hardware = 0

    ultimo_ram_total = 0
    ultimo_espacio_libre = 0

    for fila in registros:

        certificacion = fila.get(
            "certificacion",
            ""
        )

        resultado = fila.get(
            "resultado",
            ""
        )

        ram_total = convertir_float_kcd(
            fila.get(
                "despues_ram_total_gb",
                fila.get(
                    "antes_ram_total_gb",
                    0
                )
            )
        )

        espacio_libre = convertir_float_kcd(
            fila.get(
                "despues_espacio_libre",
                fila.get(
                    "antes_espacio_libre",
                    0
                )
            )
        )

        if ram_total > 0:

            ultimo_ram_total = ram_total

        if espacio_libre > 0:

            ultimo_espacio_libre = espacio_libre

        if certificacion == "EFECTIVO":

            efectivos += 1

        elif certificacion == "PARCIALMENTE EFECTIVO":

            parciales += 1

        elif certificacion == "REQUIERE HARDWARE":

            requieren_hardware += 1

        elif (
            certificacion == "NO EFECTIVO"
            or resultado == "SIN CAMBIO"
            or resultado == "EMPEORO"
        ):

            no_efectivos += 1

    analisis = {
        "total_validaciones": total,
        "efectivos": efectivos,
        "parciales": parciales,
        "no_efectivos": no_efectivos,
        "requieren_hardware": requieren_hardware,
        "ultimo_ram_total_gb": ultimo_ram_total,
        "ultimo_espacio_libre_pct": ultimo_espacio_libre
    }

    print(
        f"Validaciones registradas: {total}"
    )

    print(
        f"Efectivas: {efectivos}"
    )

    print(
        f"No efectivas: {no_efectivos}"
    )

    print(
        f"Requieren hardware: {requieren_hardware}"
    )

    return analisis


def calcular_puntaje_riesgo_predictivo_kcd(
    bitacora,
    alertas,
    validaciones,
    estructural
):

    puntaje = 0
    factores = []

    if bitacora["registros"] > 0:

        if bitacora["ivk_promedio"] <= 45:

            puntaje += 5

            factores.append(
                "IVK promedio en zona critica."
            )

        elif bitacora["ivk_promedio"] <= 65:

            puntaje += 2

            factores.append(
                "IVK promedio en zona preventiva."
            )

        if bitacora["tendencia_ivk"]["tendencia"] == "BAJA":

            puntaje += 2

            factores.append(
                "El IVK presenta tendencia descendente."
            )

        if bitacora["ram_promedio"] >= 85:

            puntaje += 3

            factores.append(
                "RAM promedio elevada."
            )

        elif bitacora["ram_promedio"] >= 75:

            puntaje += 2

            factores.append(
                "RAM promedio en nivel de alerta."
            )

        if bitacora["tendencia_ram"]["tendencia"] == "SUBE":

            puntaje += 2

            factores.append(
                "La RAM presenta tendencia de aumento."
            )

        if bitacora["disco_promedio"] >= 90:

            puntaje += 3

            factores.append(
                "Disco promedio en zona critica."
            )

        elif bitacora["disco_promedio"] >= 80:

            puntaje += 2

            factores.append(
                "Disco promedio en zona de alerta."
            )

        if bitacora["tendencia_disco"]["tendencia"] == "SUBE":

            puntaje += 2

            factores.append(
                "El uso de disco presenta tendencia de aumento."
            )

    if alertas["total_alertas"] > 0:

        if alertas["criticas"] > 0:

            puntaje += 4

            factores.append(
                "Existen alertas criticas registradas."
            )

        elif alertas["altas"] > 0:

            puntaje += 2

            factores.append(
                "Existen alertas altas registradas."
            )

        if alertas["tendencia_alertas"]["tendencia"] == "AUMENTAN":

            puntaje += 2

            factores.append(
                "Las alertas aumentan temporalmente segun fecha y severidad."
            )

    if validaciones["total_validaciones"] > 0:

        if validaciones["requieren_hardware"] > 0:

            puntaje += 4

            factores.append(
                "Hay validaciones que requieren hardware."
            )

        if validaciones["no_efectivos"] > 0:

            puntaje += 2

            factores.append(
                "Hay acciones no efectivas o sin mejora."
            )

    if estructural.get(
        "ram_estructural",
        False
    ):

        puntaje += 4

        factores.append(
            f"RAM instalada estructuralmente baja ({estructural['ram_total_gb']} GB)."
        )

    elif estructural.get(
        "ram_limitada",
        False
    ):

        puntaje += 2

        factores.append(
            f"RAM instalada limitada ({estructural['ram_total_gb']} GB)."
        )

    if estructural.get(
        "espacio_critico",
        False
    ):

        puntaje += 4

        factores.append(
            f"Espacio libre actual critico ({estructural['espacio_libre_pct']}%)."
        )

    elif estructural.get(
        "espacio_limitado",
        False
    ):

        puntaje += 2

        factores.append(
            f"Espacio libre actual limitado ({estructural['espacio_libre_pct']}%)."
        )

    return {
        "puntaje": puntaje,
        "factores": factores
    }


def clasificar_riesgo_predictivo_kcd(
    puntaje
):

    if puntaje >= 14:

        return "CRITICO"

    if puntaje >= 9:

        return "ALTO"

    if puntaje >= 4:

        return "MODERADO"

    return "BAJO"


def estimar_plazo_predictivo_kcd(
    riesgo
):

    if riesgo == "CRITICO":

        return "Atender en menos de 24 horas."

    if riesgo == "ALTO":

        return "Atender en 24 a 72 horas."

    if riesgo == "MODERADO":

        return "Atender durante los proximos 7 dias."

    return "Mantener monitoreo preventivo mensual."


def generar_mantenimiento_predictivo_kcd(
    bitacora,
    alertas,
    validaciones,
    estructural,
    riesgo,
    factores
):

    posibles_fallas = []
    prioridades = []

    if bitacora["registros"] > 0:

        if (
            bitacora["ram_promedio"] >= 75
            or bitacora["tendencia_ram"]["tendencia"] == "SUBE"
        ):

            posibles_fallas.append(
                "Saturacion progresiva de memoria RAM."
            )

            prioridades.append(
                "Revisar consumo de RAM y aplicaciones en segundo plano."
            )

        if (
            bitacora["disco_promedio"] >= 80
            or bitacora["tendencia_disco"]["tendencia"] == "SUBE"
        ):

            posibles_fallas.append(
                "Disco acercandose a nivel critico."
            )

            prioridades.append(
                "Programar limpieza preventiva y revision de almacenamiento."
            )

        if bitacora["tendencia_ivk"]["tendencia"] == "BAJA":

            posibles_fallas.append(
                "Degradacion del rendimiento general del equipo."
            )

            prioridades.append(
                "Preparar acciones del Bloque 10 y validar con Bloque 11."
            )

    if alertas["total_alertas"] > 0:

        if alertas["criticas"] > 0:

            posibles_fallas.append(
                "Reincidencia de alertas criticas."
            )

            prioridades.append(
                "Atender primero las alertas criticas registradas por Bloque 12."
            )

        if alertas["tendencia_alertas"]["tendencia"] == "AUMENTAN":

            posibles_fallas.append(
                "Incremento temporal de eventos anormales."
            )

            prioridades.append(
                "Reducir recurrencia de alertas antes de que escalen."
            )

    if validaciones["requieren_hardware"] > 0:

        posibles_fallas.append(
            "Limitacion previamente certificada como no corregible por software."
        )

        prioridades.append(
            "Evaluar ampliacion o intervencion de hardware."
        )

    if estructural.get(
        "ram_estructural",
        False
    ):

        posibles_fallas.append(
            "Rendimiento limitado por RAM fisica insuficiente."
        )

        prioridades.append(
            "Priorizar ampliacion fisica de RAM si el equipo lo permite."
        )

    if estructural.get(
        "espacio_critico",
        False
    ):

        posibles_fallas.append(
            "Riesgo de bloqueo por almacenamiento insuficiente."
        )

        prioridades.append(
            "Liberar espacio, respaldar archivos grandes o ampliar almacenamiento."
        )

    if not posibles_fallas:

        posibles_fallas.append(
            "No se identifican fallas probables con el historico disponible."
        )

    if not prioridades:

        prioridades.append(
            "Continuar monitoreo preventivo con Bloque 12."
        )

    plazo = estimar_plazo_predictivo_kcd(
        riesgo
    )

    plan = {
        "que_puede_fallar": posibles_fallas,
        "que_atender_primero": prioridades,
        "plazo_aproximado": plazo,
        "factores": factores
    }

    return plan


def registrar_prediccion_riesgo_kcd(
    prediccion
):

    nombre_archivo = "prediccion_riesgo_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha_hora",
        "riesgo_predictivo",
        "puntaje",
        "plazo_aproximado",
        "ram_total_gb",
        "espacio_libre_pct",
        "que_puede_fallar",
        "que_atender_primero",
        "factores",
        "registros_bitacora",
        "total_alertas",
        "total_validaciones"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        prediccion.get(
            "riesgo_predictivo",
            "SIN_DATOS"
        ),
        prediccion.get(
            "puntaje",
            0
        ),
        prediccion.get(
            "plazo_aproximado",
            ""
        ),
        prediccion.get(
            "ram_total_gb",
            0
        ),
        prediccion.get(
            "espacio_libre_pct",
            0
        ),
        " | ".join(
            prediccion.get(
                "que_puede_fallar",
                []
            )
        ),
        " | ".join(
            prediccion.get(
                "que_atender_primero",
                []
            )
        ),
        " | ".join(
            prediccion.get(
                "factores",
                []
            )
        ),
        prediccion.get(
            "registros_bitacora",
            0
        ),
        prediccion.get(
            "total_alertas",
            0
        ),
        prediccion.get(
            "total_validaciones",
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
            "PREDICCION_RIESGO",
            prediccion.get(
                "riesgo_predictivo",
                "SIN_DATOS"
            ),
            prediccion.get(
                "plazo_aproximado",
                ""
            )
        )

    except Exception:

        pass

    print(
        "\n[KCD PREDICTIVO] Evidencia registrada en prediccion_riesgo_kcd.csv"
    )


def ejecutar_inteligencia_predictiva_kcd():

    print(
        "\n[KCD BLOQUE 13] INTELIGENCIA PREDICTIVA KCD"
    )

    bitacora_registros = leer_historico_csv_kcd(
        "bitacora_kcd.csv"
    )

    alertas_registros = leer_historico_csv_kcd(
        "alertas_kcd.csv"
    )

    validaciones_registros = leer_historico_csv_kcd(
        "validacion_resultados_kcd.csv"
    )

    estructural = obtener_factores_estructurales_actuales_kcd()

    if (
        not bitacora_registros
        and not alertas_registros
        and not validaciones_registros
    ):

        prediccion = {
            "riesgo_predictivo": "SIN_HISTORICO",
            "puntaje": 0,
            "plazo_aproximado": "No disponible por falta de historico.",
            "ram_total_gb": estructural.get(
                "ram_total_gb",
                0
            ),
            "espacio_libre_pct": estructural.get(
                "espacio_libre_pct",
                0
            ),
            "que_puede_fallar": [
                "No se puede predecir sin datos historicos."
            ],
            "que_atender_primero": [
                "Ejecutar Bloque 12 para generar monitoreo historico."
            ],
            "factores": [
                "No existe historico suficiente."
            ],
            "registros_bitacora": 0,
            "total_alertas": 0,
            "total_validaciones": 0
        }

        registrar_prediccion_riesgo_kcd(
            prediccion
        )

        print(
            "\n[KCD PREDICTIVO] No hay historico suficiente para predecir riesgo."
        )

        return prediccion

    bitacora = analizar_bitacora_predictiva_kcd(
        bitacora_registros
    )

    alertas = analizar_alertas_predictivas_kcd(
        alertas_registros
    )

    validaciones = analizar_validaciones_predictivas_kcd(
        validaciones_registros
    )

    riesgo = calcular_puntaje_riesgo_predictivo_kcd(
        bitacora,
        alertas,
        validaciones,
        estructural
    )

    riesgo_predictivo = clasificar_riesgo_predictivo_kcd(
        riesgo["puntaje"]
    )

    mantenimiento = generar_mantenimiento_predictivo_kcd(
        bitacora,
        alertas,
        validaciones,
        estructural,
        riesgo_predictivo,
        riesgo["factores"]
    )

    prediccion = {
        "riesgo_predictivo": riesgo_predictivo,
        "puntaje": riesgo["puntaje"],
        "plazo_aproximado": mantenimiento["plazo_aproximado"],
        "ram_total_gb": estructural.get(
            "ram_total_gb",
            0
        ),
        "espacio_libre_pct": estructural.get(
            "espacio_libre_pct",
            0
        ),
        "que_puede_fallar": mantenimiento["que_puede_fallar"],
        "que_atender_primero": mantenimiento["que_atender_primero"],
        "factores": mantenimiento["factores"],
        "registros_bitacora": bitacora["registros"],
        "total_alertas": alertas["total_alertas"],
        "total_validaciones": validaciones["total_validaciones"],
        "detalle_bitacora": bitacora,
        "detalle_alertas": alertas,
        "detalle_validaciones": validaciones,
        "detalle_estructural": estructural
    }

    registrar_prediccion_riesgo_kcd(
        prediccion
    )

    print(
        "\n[KCD PREDICCION FINAL]"
    )

    print(
        f"Riesgo predictivo: {prediccion['riesgo_predictivo']}"
    )

    print(
        f"Puntaje: {prediccion['puntaje']}"
    )

    print(
        f"RAM instalada: {prediccion['ram_total_gb']} GB"
    )

    print(
        f"Espacio libre actual: {prediccion['espacio_libre_pct']}%"
    )

    print(
        f"Plazo aproximado: {prediccion['plazo_aproximado']}"
    )

    print(
        "\nQue puede fallar:"
    )

    for item in prediccion["que_puede_fallar"]:

        print(
            f"- {item}"
        )

    print(
        "\nQue atender primero:"
    )

    for item in prediccion["que_atender_primero"]:

        print(
            f"- {item}"
        )

    return prediccion

# ==============================================================================
# BLOQUE 14.0 - ORQUESTACION INTELIGENTE KCD
# ==============================================================================
#
# 14.1 Consolidacion de evidencias
# 14.2 Priorizacion automatica
# 14.3 Motor de decisiones KCD
# 14.4 Plan automatico de mantenimiento
# 14.5 Indice de Prioridad KCD - IPK
# 14.6 Generador de agenda tecnica
# 14.7 Resumen ejecutivo automatico
# 14.8 Evidencia de orquestacion
#
# ==============================================================================

def leer_csv_orquestacion_kcd(
    nombre_archivo
):

    if not os.path.exists(
        nombre_archivo
    ):

        return []

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

                registros.append(
                    fila
                )

    except Exception as error:

        print(
            f"\n[KCD ORQUESTADOR ERROR] No se pudo leer {nombre_archivo}: {error}"
        )

        return []

    return registros


def convertir_numero_orquestacion_kcd(
    valor,
    defecto=0
):

    try:

        return float(
            valor
        )

    except Exception:

        return defecto


def ultimo_registro_orquestacion_kcd(
    registros
):

    if not registros:

        return {}

    return registros[
        -1
    ]


def consolidar_evidencias_kcd():

    print(
        "\n[KCD ORQUESTADOR] Consolidando evidencias KCD..."
    )

    bitacora = leer_csv_orquestacion_kcd(
        "bitacora_kcd.csv"
    )

    alertas = leer_csv_orquestacion_kcd(
        "alertas_kcd.csv"
    )

    acciones_preparadas = leer_csv_orquestacion_kcd(
        "acciones_preparadas_bloque10_kcd.csv"
    )

    validaciones = leer_csv_orquestacion_kcd(
        "validacion_resultados_kcd.csv"
    )

    predicciones = leer_csv_orquestacion_kcd(
        "prediccion_riesgo_kcd.csv"
    )

    evidencias = {
        "bitacora": bitacora,
        "alertas": alertas,
        "acciones_preparadas": acciones_preparadas,
        "validaciones": validaciones,
        "predicciones": predicciones,
        "ultima_bitacora": ultimo_registro_orquestacion_kcd(
            bitacora
        ),
        "ultima_validacion": ultimo_registro_orquestacion_kcd(
            validaciones
        ),
        "ultima_prediccion": ultimo_registro_orquestacion_kcd(
            predicciones
        )
    }

    print(
        f"Registros bitacora: {len(bitacora)}"
    )

    print(
        f"Alertas: {len(alertas)}"
    )

    print(
        f"Acciones preparadas: {len(acciones_preparadas)}"
    )

    print(
        f"Validaciones: {len(validaciones)}"
    )

    print(
        f"Predicciones: {len(predicciones)}"
    )

    return evidencias


def contar_alertas_por_nivel_kcd(
    alertas
):

    conteo = {
        "CRITICO": 0,
        "ALTO": 0,
        "MODERADO": 0,
        "BAJO": 0
    }

    for alerta in alertas:

        nivel = alerta.get(
            "nivel",
            "BAJO"
        )

        if nivel in conteo:

            conteo[nivel] += 1

        else:

            conteo["BAJO"] += 1

    return conteo


def clasificar_ipk_kcd(
    ipk
):

    if ipk >= 76:

        return "CRITICO"

    if ipk >= 51:

        return "ALTO"

    if ipk >= 26:

        return "MODERADO"

    return "BAJO"


def calcular_ipk_kcd(
    evidencias
):

    ultima_bitacora = evidencias.get(
        "ultima_bitacora",
        {}
    )

    ultima_prediccion = evidencias.get(
        "ultima_prediccion",
        {}
    )

    ultima_validacion = evidencias.get(
        "ultima_validacion",
        {}
    )

    alertas = evidencias.get(
        "alertas",
        []
    )

    conteo_alertas = contar_alertas_por_nivel_kcd(
        alertas
    )

    cpu = convertir_numero_orquestacion_kcd(
        ultima_bitacora.get(
            "cpu",
            0
        )
    )

    ram = convertir_numero_orquestacion_kcd(
        ultima_bitacora.get(
            "ram",
            0
        )
    )

    disco = convertir_numero_orquestacion_kcd(
        ultima_bitacora.get(
            "disco",
            0
        )
    )

    ivk = convertir_numero_orquestacion_kcd(
        ultima_bitacora.get(
            "ivk",
            100
        ),
        100
    )

    riesgo_predictivo = ultima_prediccion.get(
        "riesgo_predictivo",
        "BAJO"
    )

    espacio_libre = convertir_numero_orquestacion_kcd(
        ultima_prediccion.get(
            "espacio_libre_pct",
            100
        ),
        100
    )

    ram_total = convertir_numero_orquestacion_kcd(
        ultima_prediccion.get(
            "ram_total_gb",
            0
        )
    )

    certificacion = ultima_validacion.get(
        "certificacion",
        ""
    )

    resultado_validacion = ultima_validacion.get(
        "resultado",
        ""
    )

    ipk = 0
    factores = []

    if ivk <= 45:

        ipk += 25

        factores.append(
            "IVK critico"
        )

    elif ivk <= 65:

        ipk += 15

        factores.append(
            "IVK preventivo"
        )

    elif ivk <= 80:

        ipk += 7

        factores.append(
            "IVK moderado"
        )

    if conteo_alertas["CRITICO"] > 0:

        ipk += 20

        factores.append(
            "Alertas criticas"
        )

    elif conteo_alertas["ALTO"] > 0:

        ipk += 12

        factores.append(
            "Alertas altas"
        )

    elif conteo_alertas["MODERADO"] > 0:

        ipk += 6

        factores.append(
            "Alertas moderadas"
        )

    if riesgo_predictivo == "CRITICO":

        ipk += 20

        factores.append(
            "Prediccion critica"
        )

    elif riesgo_predictivo == "ALTO":

        ipk += 15

        factores.append(
            "Prediccion alta"
        )

    elif riesgo_predictivo == "MODERADO":

        ipk += 8

        factores.append(
            "Prediccion moderada"
        )

    if ram >= 90:

        ipk += 15

        factores.append(
            "RAM en nivel critico"
        )

    elif ram >= 80:

        ipk += 10

        factores.append(
            "RAM alta"
        )

    elif ram >= 70:

        ipk += 5

        factores.append(
            "RAM moderada"
        )

    if ram_total > 0 and ram_total < 4:

        ipk += 15

        factores.append(
            "RAM fisica insuficiente"
        )

    elif ram_total >= 4 and ram_total < 8:

        ipk += 8

        factores.append(
            "RAM fisica limitada"
        )

    if disco >= 90:

        ipk += 15

        factores.append(
            "Disco critico"
        )

    elif disco >= 80:

        ipk += 10

        factores.append(
            "Disco alto"
        )

    if espacio_libre <= 15:

        ipk += 15

        factores.append(
            "Espacio libre critico"
        )

    elif espacio_libre <= 25:

        ipk += 8

        factores.append(
            "Espacio libre limitado"
        )

    if certificacion == "REQUIERE HARDWARE":

        ipk += 15

        factores.append(
            "Validacion requiere hardware"
        )

    elif (
        certificacion == "NO EFECTIVO"
        or resultado_validacion == "SIN CAMBIO"
        or resultado_validacion == "EMPEORO"
    ):

        ipk += 10

        factores.append(
            "Validacion no efectiva"
        )

    if cpu >= 90:

        ipk += 10

        factores.append(
            "CPU critica"
        )

    elif cpu >= 75:

        ipk += 5

        factores.append(
            "CPU alta"
        )

    if ipk > 100:

        ipk = 100

    nivel = clasificar_ipk_kcd(
        ipk
    )

    return {
        "ipk": ipk,
        "nivel": nivel,
        "factores": factores,
        "cpu": cpu,
        "ram": ram,
        "disco": disco,
        "ivk": ivk,
        "espacio_libre_pct": espacio_libre,
        "ram_total_gb": ram_total,
        "riesgo_predictivo": riesgo_predictivo,
        "certificacion": certificacion,
        "alertas": conteo_alertas
    }


def crear_item_decision_kcd(
    prioridad,
    accion,
    origen,
    plazo,
    categoria
):

    return {
        "fecha": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "prioridad": prioridad,
        "accion": accion,
        "origen": origen,
        "plazo": plazo,
        "categoria": categoria,
        "estado": "PENDIENTE"
    }


def priorizar_acciones_kcd(
    evidencias,
    ipk
):

    print(
        "\n[KCD ORQUESTADOR] Priorizando acciones..."
    )

    acciones = []

    ram_total = ipk.get(
        "ram_total_gb",
        0
    )

    espacio_libre = ipk.get(
        "espacio_libre_pct",
        100
    )

    ram = ipk.get(
        "ram",
        0
    )

    disco = ipk.get(
        "disco",
        0
    )

    cpu = ipk.get(
        "cpu",
        0
    )

    ivk = ipk.get(
        "ivk",
        100
    )

    riesgo_predictivo = ipk.get(
        "riesgo_predictivo",
        "BAJO"
    )

    if ram_total > 0 and ram_total < 4:

        acciones.append(
            crear_item_decision_kcd(
                "CRITICO",
                "Evaluar ampliacion fisica de memoria RAM.",
                "BLOQUE_13_PREDICTIVO",
                "INMEDIATO",
                "HARDWARE"
            )
        )

    if espacio_libre <= 15 or disco >= 90:

        acciones.append(
            crear_item_decision_kcd(
                "CRITICO",
                "Liberar espacio en disco mediante limpieza segura autorizada.",
                "BLOQUE_12_13",
                "INMEDIATO",
                "SOFTWARE"
            )
        )

    elif espacio_libre <= 25 or disco >= 80:

        acciones.append(
            crear_item_decision_kcd(
                "ALTO",
                "Programar limpieza preventiva de almacenamiento.",
                "BLOQUE_12_13",
                "24 HORAS",
                "SOFTWARE"
            )
        )

    if ivk <= 45:

        acciones.append(
            crear_item_decision_kcd(
                "CRITICO",
                "Preparar optimizacion preventiva con Bloque 10 y validar con Bloque 11.",
                "BLOQUE_13_PREDICTIVO",
                "INMEDIATO",
                "SOFTWARE"
            )
        )

    elif ivk <= 65:

        acciones.append(
            crear_item_decision_kcd(
                "ALTO",
                "Programar optimizacion general del sistema.",
                "BLOQUE_13_PREDICTIVO",
                "7 DIAS",
                "SOFTWARE"
            )
        )

    if ram >= 90:

        acciones.append(
            crear_item_decision_kcd(
                "CRITICO",
                "Revisar saturacion de RAM y preparar plan de remediacion.",
                "BLOQUE_12_MONITOREO",
                "INMEDIATO",
                "SOFTWARE"
            )
        )

    elif ram >= 75:

        acciones.append(
            crear_item_decision_kcd(
                "ALTO",
                "Revisar aplicaciones de alto consumo de memoria.",
                "BLOQUE_12_MONITOREO",
                "24 HORAS",
                "USUARIO"
            )
        )

    if cpu >= 90:

        acciones.append(
            crear_item_decision_kcd(
                "CRITICO",
                "Revisar procesos de alto consumo de CPU sin cerrarlos automaticamente.",
                "BLOQUE_12_MONITOREO",
                "INMEDIATO",
                "SOFTWARE"
            )
        )

    elif cpu >= 75:

        acciones.append(
            crear_item_decision_kcd(
                "ALTO",
                "Monitorear CPU y revisar aplicaciones activas.",
                "BLOQUE_12_MONITOREO",
                "24 HORAS",
                "VIGILANCIA"
            )
        )

    if riesgo_predictivo == "CRITICO":

        acciones.append(
            crear_item_decision_kcd(
                "CRITICO",
                "Atender riesgo predictivo critico y preparar plan de mantenimiento.",
                "BLOQUE_13_PREDICTIVO",
                "INMEDIATO",
                "ORQUESTACION"
            )
        )

    elif riesgo_predictivo == "ALTO":

        acciones.append(
            crear_item_decision_kcd(
                "ALTO",
                "Atender riesgo predictivo alto durante la ventana de mantenimiento.",
                "BLOQUE_13_PREDICTIVO",
                "24 HORAS",
                "ORQUESTACION"
            )
        )

    for alerta in evidencias.get(
        "alertas",
        []
    ):

        tipo = alerta.get(
            "tipo",
            ""
        )

        nivel = alerta.get(
            "nivel",
            ""
        )

        mensaje = alerta.get(
            "mensaje",
            ""
        )

        if (
            "CHROME" in tipo
            and nivel in [
                "CRITICO",
                "ALTO"
            ]
        ):

            acciones.append(
                crear_item_decision_kcd(
                    nivel,
                    "Revisar Chrome: pestanas, extensiones y consumo de memoria.",
                    "BLOQUE_12_CHROME",
                    "24 HORAS",
                    "USUARIO"
                )
            )

        elif (
            nivel == "CRITICO"
            and mensaje
        ):

            acciones.append(
                crear_item_decision_kcd(
                    "CRITICO",
                    f"Atender alerta critica: {mensaje}",
                    "BLOQUE_12_ALERTAS",
                    "INMEDIATO",
                    "VIGILANCIA"
                )
            )

    for accion_preparada in evidencias.get(
        "acciones_preparadas",
        []
    ):

        accion_sugerida = accion_preparada.get(
            "accion_sugerida",
            ""
        )

        nivel = accion_preparada.get(
            "nivel",
            "MODERADO"
        )

        if accion_sugerida:

            plazo = "24 HORAS"

            if nivel == "CRITICO":

                plazo = "INMEDIATO"

            acciones.append(
                crear_item_decision_kcd(
                    nivel,
                    accion_sugerida,
                    "BLOQUE_10_PREPARADO",
                    plazo,
                    "PLANIFICACION"
                )
            )

    acciones.append(
        crear_item_decision_kcd(
            "BAJO",
            "Realizar auditoria preventiva general KCD.",
            "BLOQUE_14_ORQUESTACION",
            "30 DIAS",
            "AUDITORIA"
        )
    )

    return eliminar_acciones_duplicadas_kcd(
        acciones
    )


def eliminar_acciones_duplicadas_kcd(
    acciones
):

    vistas = set()
    depuradas = []

    for accion in acciones:

        clave = (
            accion.get(
                "accion",
                ""
            ),
            accion.get(
                "plazo",
                ""
            )
        )

        if clave in vistas:

            continue

        vistas.add(
            clave
        )

        depuradas.append(
            accion
        )

    orden = {
        "CRITICO": 1,
        "ALTO": 2,
        "MODERADO": 3,
        "BAJO": 4
    }

    depuradas.sort(
        key=lambda item: orden.get(
            item.get(
                "prioridad",
                "BAJO"
            ),
            4
        )
    )

    return depuradas


def motor_decisiones_kcd(
    acciones
):

    atender_primero = []
    puede_esperar = []
    debe_vigilarse = []
    requiere_hardware = []

    for accion in acciones:

        categoria = accion.get(
            "categoria",
            ""
        )

        prioridad = accion.get(
            "prioridad",
            "BAJO"
        )

        if categoria == "HARDWARE":

            requiere_hardware.append(
                accion
            )

        elif prioridad in [
            "CRITICO",
            "ALTO"
        ]:

            atender_primero.append(
                accion
            )

        elif categoria == "VIGILANCIA":

            debe_vigilarse.append(
                accion
            )

        else:

            puede_esperar.append(
                accion
            )

    return {
        "atender_primero": atender_primero,
        "puede_esperar": puede_esperar,
        "debe_vigilarse": debe_vigilarse,
        "requiere_hardware": requiere_hardware
    }


def generar_plan_mantenimiento_kcd(
    acciones
):

    plan = {
        "INMEDIATO": [],
        "24 HORAS": [],
        "7 DIAS": [],
        "30 DIAS": []
    }

    for accion in acciones:

        plazo = accion.get(
            "plazo",
            "30 DIAS"
        )

        if plazo not in plan:

            plazo = "30 DIAS"

        plan[plazo].append(
            accion
        )

    return plan


def agenda_item_existe_kcd(
    accion,
    origen,
    estado
):

    archivo = "agenda_mantenimiento_kcd.csv"

    if not os.path.exists(
        archivo
    ):

        return False

    try:

        with open(
            archivo,
            mode="r",
            encoding="utf-8"
        ) as archivo_csv:

            lector = csv.DictReader(
                archivo_csv
            )

            for fila in lector:

                if (
                    fila.get(
                        "accion",
                        ""
                    ) == accion
                    and fila.get(
                        "origen",
                        ""
                    ) == origen
                    and fila.get(
                        "estado",
                        ""
                    ) == estado
                ):

                    return True

    except Exception:

        return False

    return False


def generar_agenda_mantenimiento_kcd(
    acciones
):

    nombre_archivo = "agenda_mantenimiento_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "prioridad",
        "accion",
        "origen",
        "estado"
    ]

    nuevas = 0

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

        for item in acciones:

            accion = item.get(
                "accion",
                ""
            )

            origen = item.get(
                "origen",
                ""
            )

            estado = item.get(
                "estado",
                "PENDIENTE"
            )

            if agenda_item_existe_kcd(
                accion,
                origen,
                estado
            ):

                continue

            escritor.writerow([
                item.get(
                    "fecha",
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ),
                item.get(
                    "prioridad",
                    "BAJO"
                ),
                accion,
                origen,
                estado
            ])

            nuevas += 1

    print(
        f"\n[KCD ORQUESTADOR] Agenda generada/actualizada: {nombre_archivo}"
    )

    print(
        f"Acciones nuevas en agenda: {nuevas}"
    )

    return nuevas


def registrar_orquestacion_kcd(
    ipk,
    resumen
):

    nombre_archivo = "orquestacion_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "IPK",
        "riesgo_actual",
        "riesgo_futuro",
        "accion_principal",
        "nivel_prioridad"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        ipk.get(
            "ipk",
            0
        ),
        resumen.get(
            "riesgo_actual",
            "BAJO"
        ),
        resumen.get(
            "riesgo_futuro",
            "BAJO"
        ),
        resumen.get(
            "accion_recomendada",
            ""
        ),
        resumen.get(
            "nivel_prioridad",
            "BAJO"
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
            "ORQUESTACION_KCD",
            resumen.get(
                "nivel_prioridad",
                "BAJO"
            ),
            resumen.get(
                "accion_recomendada",
                ""
            )
        )

    except Exception:

        pass

    print(
        f"\n[KCD ORQUESTADOR] Evidencia registrada: {nombre_archivo}"
    )


def generar_resumen_ejecutivo_orquestador_kcd(
    ipk,
    acciones,
    decisiones
):

    if acciones:

        accion_principal = acciones[0].get(
            "accion",
            "Sin accion principal"
        )

        nivel_prioridad = acciones[0].get(
            "prioridad",
            "BAJO"
        )

    else:

        accion_principal = "Continuar monitoreo preventivo."
        nivel_prioridad = "BAJO"

    riesgo_actual = ipk.get(
        "nivel",
        "BAJO"
    )

    riesgo_futuro = ipk.get(
        "riesgo_predictivo",
        "BAJO"
    )

    if ipk.get(
        "ipk",
        0
    ) >= 76:

        estado_general = "ATENCION INMEDIATA"

    elif ipk.get(
        "ipk",
        0
    ) >= 51:

        estado_general = "RIESGO ALTO"

    elif ipk.get(
        "ipk",
        0
    ) >= 26:

        estado_general = "VIGILANCIA PREVENTIVA"

    else:

        estado_general = "ESTABLE"

    resumen = {
        "estado_general": estado_general,
        "riesgo_actual": riesgo_actual,
        "riesgo_futuro": riesgo_futuro,
        "prioridad_principal": nivel_prioridad,
        "accion_recomendada": accion_principal,
        "nivel_prioridad": nivel_prioridad,
        "atender_primero": len(
            decisiones.get(
                "atender_primero",
                []
            )
        ),
        "requiere_hardware": len(
            decisiones.get(
                "requiere_hardware",
                []
            )
        )
    }

    print(
        "\n[KCD ORQUESTADOR]"
    )

    print(
        f"Estado general: {resumen['estado_general']}"
    )

    print(
        f"IPK: {ipk['ipk']} / 100"
    )

    print(
        f"Riesgo actual: {resumen['riesgo_actual']}"
    )

    print(
        f"Riesgo futuro: {resumen['riesgo_futuro']}"
    )

    print(
        f"Prioridad principal: {resumen['prioridad_principal']}"
    )

    print(
        f"Accion recomendada: {resumen['accion_recomendada']}"
    )

    print(
        f"Acciones para atender primero: {resumen['atender_primero']}"
    )

    print(
        f"Acciones que requieren hardware: {resumen['requiere_hardware']}"
    )

    return resumen


def ejecutar_orquestacion_inteligente_kcd():

    print(
        "\n[KCD BLOQUE 14] ORQUESTACION INTELIGENTE KCD"
    )

    print(
        "Modo seguro: solo lee, analiza, prioriza, agenda y registra evidencia."
    )

    evidencias = consolidar_evidencias_kcd()

    ipk = calcular_ipk_kcd(
        evidencias
    )

    acciones = priorizar_acciones_kcd(
        evidencias,
        ipk
    )

    decisiones = motor_decisiones_kcd(
        acciones
    )

    plan = generar_plan_mantenimiento_kcd(
        acciones
    )

    generar_agenda_mantenimiento_kcd(
        acciones
    )

    resumen = generar_resumen_ejecutivo_orquestador_kcd(
        ipk,
        acciones,
        decisiones
    )

    registrar_orquestacion_kcd(
        ipk,
        resumen
    )

    print(
        "\n[KCD PLAN AUTOMATICO DE MANTENIMIENTO]"
    )

    for plazo, items in plan.items():

        print(
            f"\n{plazo}"
        )

        if not items:

            print(
                "- Sin acciones programadas."
            )

        for item in items:

            print(
                f"- [{item['prioridad']}] {item['accion']}"
            )

    return {
        "ipk": ipk,
        "acciones": acciones,
        "decisiones": decisiones,
        "plan": plan,
        "resumen": resumen
    }


# ==============================================================================
# BLOQUE 15.0 - GESTION DE INCIDENTES Y CASOS KCD
# ==============================================================================
#
# 15.1 Apertura automatica de incidentes
# 15.2 Registro maestro de incidentes
# 15.3 Clasificacion de incidentes
# 15.4 Priorizacion
# 15.5 Seguimiento de incidentes
# 15.6 Cierre tecnico
# 15.7 Tiempo de resolucion
# 15.8 Evidencia de incidentes
# 15.9 Integracion KCD
# 15.10 Resumen ejecutivo de incidentes
#
# ==============================================================================

def leer_csv_incidentes_kcd(
    nombre_archivo
):

    if not os.path.exists(
        nombre_archivo
    ):

        return []

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

                registros.append(
                    fila
                )

    except Exception as error:

        print(
            f"\n[KCD INCIDENTES ERROR] No se pudo leer {nombre_archivo}: {error}"
        )

        return []

    return registros


def convertir_fecha_incidente_kcd(
    fecha_texto
):

    try:

        return datetime.strptime(
            fecha_texto,
            "%Y-%m-%d %H:%M:%S"
        )

    except Exception:

        return None


def generar_id_incidente_kcd():

    registros = leer_csv_incidentes_kcd(
        "incidentes_kcd.csv"
    )

    mayor = 0

    for fila in registros:

        id_incidente = fila.get(
            "id_incidente",
            ""
        )

        try:

            numero = int(
                id_incidente.replace(
                    "INC-KCD-",
                    ""
                )
            )

            if numero > mayor:

                mayor = numero

        except Exception:

            continue

    nuevo = mayor + 1

    return f"INC-KCD-{nuevo:06d}"


def clasificar_categoria_incidente_kcd(
    texto
):

    texto = str(
        texto
    ).lower()

    if (
        "ram" in texto
        or "memoria" in texto
    ):

        return "MEMORIA"

    if (
        "disco" in texto
        or "espacio" in texto
        or "almacenamiento" in texto
    ):

        return "DISCO"

    if "cpu" in texto:

        return "CPU"

    if "chrome" in texto:

        return "CHROME"

    if (
        "red" in texto
        or "network" in texto
        or "internet" in texto
    ):

        return "RED"

    if (
        "servicio" in texto
        or "servicios" in texto
    ):

        return "SERVICIOS"

    if (
        "hardware" in texto
        or "fisica" in texto
        or "ampliacion" in texto
    ):

        return "HARDWARE"

    if (
        "software" in texto
        or "optimizacion" in texto
        or "aplicacion" in texto
    ):

        return "SOFTWARE"

    return "GENERAL"


def convertir_numero_incidente_kcd(
    valor,
    defecto=0
):

    try:

        return float(
            valor
        )

    except Exception:

        return defecto


def clasificar_prioridad_incidente_kcd(
    descripcion,
    datos=None
):

    if datos is None:

        datos = {}

    texto = str(
        descripcion
    ).lower()

    nivel = str(
        datos.get(
            "nivel",
            ""
        )
    ).upper()

    riesgo = str(
        datos.get(
            "riesgo_predictivo",
            ""
        )
    ).upper()

    certificacion = str(
        datos.get(
            "certificacion",
            ""
        )
    ).upper()

    resultado = str(
        datos.get(
            "resultado",
            ""
        )
    ).upper()

    ivk = convertir_numero_incidente_kcd(
        datos.get(
            "ivk",
            100
        ),
        100
    )

    ram_total = convertir_numero_incidente_kcd(
        datos.get(
            "ram_total_gb",
            0
        )
    )

    espacio_libre = convertir_numero_incidente_kcd(
        datos.get(
            "espacio_libre_pct",
            datos.get(
                "despues_espacio_libre",
                datos.get(
                    "antes_espacio_libre",
                    100
                )
            )
        ),
        100
    )

    chrome_ram = convertir_numero_incidente_kcd(
        datos.get(
            "chrome_ram_mb",
            0
        )
    )

    if (
        nivel == "CRITICO"
        or riesgo == "CRITICO"
        or certificacion == "REQUIERE HARDWARE"
        or resultado == "EMPEORO"
        or "critico" in texto
        or "crítico" in texto
        or ivk <= 45
        or (
            ram_total > 0
            and ram_total < 4
        )
        or espacio_libre < 15
    ):

        return "CRITICO"

    if (
        nivel == "ALTO"
        or riesgo == "ALTO"
        or resultado == "SIN CAMBIO"
        or certificacion == "NO EFECTIVO"
        or chrome_ram >= 1000
        or "alto" in texto
        or "no efectivo" in texto
    ):

        return "ALTO"

    if (
        nivel == "MODERADO"
        or riesgo == "MODERADO"
        or "moderado" in texto
        or "parcial" in texto
    ):

        return "MODERADO"

    return "BAJO"


def incidente_duplicado_kcd(
    origen,
    descripcion
):

    registros = leer_csv_incidentes_kcd(
        "incidentes_kcd.csv"
    )

    for fila in registros:

        if (
            fila.get(
                "origen",
                ""
            ) == origen
            and fila.get(
                "descripcion",
                ""
            ) == descripcion
            and fila.get(
                "estado",
                ""
            ) != "CERRADO"
        ):

            return True

    return False


def escribir_incidente_maestro_kcd(
    incidente
):

    nombre_archivo = "incidentes_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "id_incidente",
        "fecha_apertura",
        "origen",
        "categoria",
        "prioridad",
        "estado",
        "descripcion",
        "fecha_cierre",
        "resultado",
        "validacion",
        "responsable",
        "tiempo_resolucion_horas"
    ]

    with open(
        nombre_archivo,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=encabezados
        )

        if not existe_archivo:

            escritor.writeheader()

        escritor.writerow({
            "id_incidente": incidente.get(
                "id_incidente",
                ""
            ),
            "fecha_apertura": incidente.get(
                "fecha_apertura",
                ""
            ),
            "origen": incidente.get(
                "origen",
                ""
            ),
            "categoria": incidente.get(
                "categoria",
                "GENERAL"
            ),
            "prioridad": incidente.get(
                "prioridad",
                "BAJO"
            ),
            "estado": incidente.get(
                "estado",
                "PENDIENTE"
            ),
            "descripcion": incidente.get(
                "descripcion",
                ""
            ),
            "fecha_cierre": "",
            "resultado": "",
            "validacion": "",
            "responsable": "",
            "tiempo_resolucion_horas": ""
        })


def registrar_seguimiento_incidente_kcd(
    id_incidente,
    estado,
    observacion
):

    estados_validos = [
        "EN_ANALISIS",
        "EN_PROCESO",
        "PENDIENTE",
        "VALIDANDO",
        "CERRADO"
    ]

    if estado not in estados_validos:

        estado = "PENDIENTE"

    nombre_archivo = "seguimiento_incidentes_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "id_incidente",
        "estado",
        "observacion"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        id_incidente,
        estado,
        observacion
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


def abrir_incidente_kcd(
    origen,
    descripcion,
    datos=None
):

    if datos is None:

        datos = {}

    if incidente_duplicado_kcd(
        origen,
        descripcion
    ):

        print(
            f"[KCD INCIDENTES] Incidente duplicado omitido: {descripcion}"
        )

        return None

    categoria = clasificar_categoria_incidente_kcd(
        descripcion
    )

    prioridad = clasificar_prioridad_incidente_kcd(
        descripcion,
        datos
    )

    incidente = {
        "id_incidente": generar_id_incidente_kcd(),
        "fecha_apertura": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "origen": origen,
        "categoria": categoria,
        "prioridad": prioridad,
        "estado": "PENDIENTE",
        "descripcion": descripcion
    }

    escribir_incidente_maestro_kcd(
        incidente
    )

    registrar_seguimiento_incidente_kcd(
        incidente["id_incidente"],
        "PENDIENTE",
        "Incidente abierto por KCD."
    )

    try:

        registrar_accion_kcd(
            "INCIDENTE_ABIERTO",
            prioridad,
            f"{incidente['id_incidente']} | {descripcion}"
        )

    except Exception:

        pass

    print(
        f"[KCD INCIDENTES] Abierto {incidente['id_incidente']} - {prioridad}"
    )

    return incidente


def abrir_incidentes_desde_alertas_kcd():

    alertas = leer_csv_incidentes_kcd(
        "alertas_kcd.csv"
    )

    creados = []

    for alerta in alertas:

        nivel = alerta.get(
            "nivel",
            ""
        )

        tipo = alerta.get(
            "tipo",
            "GENERAL"
        )

        mensaje = alerta.get(
            "mensaje",
            ""
        )

        if nivel not in [
            "CRITICO",
            "ALTO"
        ]:

            continue

        descripcion = (
            f"Alerta {nivel} detectada en {tipo}: {mensaje}"
        )

        incidente = abrir_incidente_kcd(
            "BLOQUE_12_ALERTAS",
            descripcion,
            alerta
        )

        if incidente:

            creados.append(
                incidente
            )

    return creados


def abrir_incidentes_desde_predicciones_kcd():

    predicciones = leer_csv_incidentes_kcd(
        "prediccion_riesgo_kcd.csv"
    )

    creados = []

    for prediccion in predicciones:

        riesgo = prediccion.get(
            "riesgo_predictivo",
            ""
        )

        if riesgo not in [
            "CRITICO",
            "ALTO"
        ]:

            continue

        descripcion = (
            f"Prediccion de riesgo {riesgo}: {prediccion.get('que_puede_fallar', '')}"
        )

        incidente = abrir_incidente_kcd(
            "BLOQUE_13_PREDICTIVO",
            descripcion,
            prediccion
        )

        if incidente:

            creados.append(
                incidente
            )

    return creados


def abrir_incidentes_desde_validaciones_kcd():

    validaciones = leer_csv_incidentes_kcd(
        "validacion_resultados_kcd.csv"
    )

    creados = []

    for validacion in validaciones:

        resultado = validacion.get(
            "resultado",
            ""
        )

        certificacion = validacion.get(
            "certificacion",
            ""
        )

        if (
            resultado not in [
                "SIN CAMBIO",
                "EMPEORO"
            ]
            and certificacion not in [
                "NO EFECTIVO",
                "REQUIERE HARDWARE"
            ]
        ):

            continue

        descripcion = (
            f"Validacion no favorable: resultado={resultado}, certificacion={certificacion}."
        )

        incidente = abrir_incidente_kcd(
            "BLOQUE_11_VALIDACION",
            descripcion,
            validacion
        )

        if incidente:

            creados.append(
                incidente
            )

    return creados


def abrir_incidentes_desde_acciones_preparadas_kcd():

    acciones = leer_csv_incidentes_kcd(
        "acciones_preparadas_bloque10_kcd.csv"
    )

    creados = []

    for accion in acciones:

        nivel = accion.get(
            "nivel",
            ""
        )

        problema = accion.get(
            "problema",
            ""
        )

        accion_sugerida = accion.get(
            "accion_sugerida",
            ""
        )

        if nivel not in [
            "CRITICO",
            "ALTO"
        ]:

            continue

        descripcion = (
            f"Accion preparada de prioridad {nivel}: {problema} | {accion_sugerida}"
        )

        incidente = abrir_incidente_kcd(
            "BLOQUE_10_PREPARADO",
            descripcion,
            accion
        )

        if incidente:

            creados.append(
                incidente
            )

    return creados


def abrir_incidentes_desde_orquestacion_kcd():

    orquestaciones = leer_csv_incidentes_kcd(
        "orquestacion_kcd.csv"
    )

    creados = []

    for item in orquestaciones:

        riesgo_actual = item.get(
            "riesgo_actual",
            ""
        )

        riesgo_futuro = item.get(
            "riesgo_futuro",
            ""
        )

        prioridad = item.get(
            "nivel_prioridad",
            ""
        )

        if (
            riesgo_actual not in [
                "CRITICO",
                "ALTO"
            ]
            and riesgo_futuro not in [
                "CRITICO",
                "ALTO"
            ]
            and prioridad not in [
                "CRITICO",
                "ALTO"
            ]
        ):

            continue

        descripcion = (
            f"Orquestacion KCD requiere atencion: IPK={item.get('IPK', '')}, accion={item.get('accion_principal', '')}"
        )

        datos = {
            "nivel": prioridad,
            "riesgo_predictivo": riesgo_futuro
        }

        incidente = abrir_incidente_kcd(
            "BLOQUE_14_ORQUESTACION",
            descripcion,
            datos
        )

        if incidente:

            creados.append(
                incidente
            )

    return creados


def actualizar_estado_incidente_kcd(
    id_incidente,
    estado,
    observacion="Actualizacion de estado."
):

    registros = leer_csv_incidentes_kcd(
        "incidentes_kcd.csv"
    )

    if not registros:

        print(
            "\n[KCD INCIDENTES] No existen incidentes para actualizar."
        )

        return False

    encontrado = False

    for fila in registros:

        if fila.get(
            "id_incidente",
            ""
        ) == id_incidente:

            fila["estado"] = estado

            encontrado = True

            break

    if not encontrado:

        print(
            f"\n[KCD INCIDENTES] No se encontro el incidente {id_incidente}."
        )

        return False

    guardar_incidentes_actualizados_kcd(
        registros
    )

    registrar_seguimiento_incidente_kcd(
        id_incidente,
        estado,
        observacion
    )

    print(
        f"\n[KCD INCIDENTES] {id_incidente} actualizado a {estado}."
    )

    return True


def guardar_incidentes_actualizados_kcd(
    registros
):

    nombre_archivo = "incidentes_kcd.csv"

    encabezados = [
        "id_incidente",
        "fecha_apertura",
        "origen",
        "categoria",
        "prioridad",
        "estado",
        "descripcion",
        "fecha_cierre",
        "resultado",
        "validacion",
        "responsable",
        "tiempo_resolucion_horas"
    ]

    with open(
        nombre_archivo,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=encabezados
        )

        escritor.writeheader()

        for fila in registros:

            escritor.writerow({
                "id_incidente": fila.get(
                    "id_incidente",
                    ""
                ),
                "fecha_apertura": fila.get(
                    "fecha_apertura",
                    ""
                ),
                "origen": fila.get(
                    "origen",
                    ""
                ),
                "categoria": fila.get(
                    "categoria",
                    "GENERAL"
                ),
                "prioridad": fila.get(
                    "prioridad",
                    "BAJO"
                ),
                "estado": fila.get(
                    "estado",
                    "PENDIENTE"
                ),
                "descripcion": fila.get(
                    "descripcion",
                    ""
                ),
                "fecha_cierre": fila.get(
                    "fecha_cierre",
                    ""
                ),
                "resultado": fila.get(
                    "resultado",
                    ""
                ),
                "validacion": fila.get(
                    "validacion",
                    ""
                ),
                "responsable": fila.get(
                    "responsable",
                    ""
                ),
                "tiempo_resolucion_horas": fila.get(
                    "tiempo_resolucion_horas",
                    ""
                )
            })


def cerrar_incidente_kcd(
    id_incidente,
    resultado,
    validacion,
    responsable="KCD"
):

    resultados_validos = [
        "RESUELTO",
        "PARCIAL",
        "NO_RESUELTO"
    ]

    if resultado not in resultados_validos:

        resultado = "NO_RESUELTO"

    registros = leer_csv_incidentes_kcd(
        "incidentes_kcd.csv"
    )

    if not registros:

        print(
            "\n[KCD INCIDENTES] No existen incidentes para cerrar."
        )

        return False

    encontrado = False

    fecha_cierre = datetime.now()

    for fila in registros:

        if fila.get(
            "id_incidente",
            ""
        ) == id_incidente:

            fecha_apertura = convertir_fecha_incidente_kcd(
                fila.get(
                    "fecha_apertura",
                    ""
                )
            )

            if fecha_apertura:

                tiempo_horas = round(
                    (fecha_cierre - fecha_apertura).total_seconds() / 3600,
                    2
                )

            else:

                tiempo_horas = ""

            fila["estado"] = "CERRADO"
            fila["fecha_cierre"] = fecha_cierre.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            fila["resultado"] = resultado
            fila["validacion"] = validacion
            fila["responsable"] = responsable
            fila["tiempo_resolucion_horas"] = tiempo_horas

            encontrado = True

            break

    if not encontrado:

        print(
            f"\n[KCD INCIDENTES] No se encontro el incidente {id_incidente}."
        )

        return False

    guardar_incidentes_actualizados_kcd(
        registros
    )

    registrar_seguimiento_incidente_kcd(
        id_incidente,
        "CERRADO",
        f"Cierre tecnico: {resultado} | Validacion: {validacion} | Responsable: {responsable}"
    )

    try:

        registrar_accion_kcd(
            "INCIDENTE_CERRADO",
            resultado,
            id_incidente
        )

    except Exception:

        pass

    print(
        f"\n[KCD INCIDENTES] Incidente cerrado: {id_incidente}"
    )

    return True


def calcular_metricas_incidentes_kcd():

    registros = leer_csv_incidentes_kcd(
        "incidentes_kcd.csv"
    )

    abiertos = 0
    cerrados = 0
    tiempos = []

    prioridad_maxima = "BAJO"
    incidente_principal = ""
    estado_principal = ""

    orden_prioridad = {
        "CRITICO": 4,
        "ALTO": 3,
        "MODERADO": 2,
        "BAJO": 1
    }

    mayor_prioridad = 0

    for fila in registros:

        estado = fila.get(
            "estado",
            "PENDIENTE"
        )

        prioridad = fila.get(
            "prioridad",
            "BAJO"
        )

        if estado == "CERRADO":

            cerrados += 1

            tiempo = convertir_numero_incidente_kcd(
                fila.get(
                    "tiempo_resolucion_horas",
                    0
                )
            )

            if tiempo > 0:

                tiempos.append(
                    tiempo
                )

        else:

            abiertos += 1

        valor_prioridad = orden_prioridad.get(
            prioridad,
            1
        )

        if (
            estado != "CERRADO"
            and valor_prioridad > mayor_prioridad
        ):

            mayor_prioridad = valor_prioridad
            prioridad_maxima = prioridad
            incidente_principal = fila.get(
                "id_incidente",
                ""
            )
            estado_principal = estado

    if tiempos:

        promedio = round(
            sum(
                tiempos
            ) / len(
                tiempos
            ),
            2
        )

        maximo = max(
            tiempos
        )

        minimo = min(
            tiempos
        )

    else:

        promedio = 0
        maximo = 0
        minimo = 0

    metricas = {
        "incidentes_abiertos": abiertos,
        "incidentes_cerrados": cerrados,
        "promedio_resolucion": promedio,
        "maximo_resolucion": maximo,
        "minimo_resolucion": minimo,
        "prioridad_maxima": prioridad_maxima,
        "incidente_principal": incidente_principal,
        "estado_principal": estado_principal
    }

    return metricas


def registrar_estadisticas_incidentes_kcd(
    metricas
):

    nombre_archivo = "estadisticas_incidentes_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "incidentes_abiertos",
        "incidentes_cerrados",
        "promedio_resolucion",
        "maximo_resolucion",
        "minimo_resolucion",
        "prioridad_maxima",
        "incidente_principal"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        metricas.get(
            "incidentes_abiertos",
            0
        ),
        metricas.get(
            "incidentes_cerrados",
            0
        ),
        metricas.get(
            "promedio_resolucion",
            0
        ),
        metricas.get(
            "maximo_resolucion",
            0
        ),
        metricas.get(
            "minimo_resolucion",
            0
        ),
        metricas.get(
            "prioridad_maxima",
            "BAJO"
        ),
        metricas.get(
            "incidente_principal",
            ""
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

    print(
        "\n[KCD INCIDENTES] Estadisticas registradas."
    )


def resumen_ejecutivo_incidentes_kcd(
    metricas
):

    print(
        "\n[KCD INCIDENTES]"
    )

    print(
        f"Incidentes abiertos: {metricas.get('incidentes_abiertos', 0)}"
    )

    print(
        f"Incidentes cerrados: {metricas.get('incidentes_cerrados', 0)}"
    )

    print(
        f"Prioridad maxima: {metricas.get('prioridad_maxima', 'BAJO')}"
    )

    print(
        f"Incidente principal: {metricas.get('incidente_principal', '')}"
    )

    print(
        f"Estado: {metricas.get('estado_principal', '')}"
    )

    print(
        f"Tiempo promedio de resolucion: {metricas.get('promedio_resolucion', 0)} horas"
    )

    return metricas


def ejecutar_gestion_incidentes_kcd():

    print(
        "\n[KCD BLOQUE 15] GESTION DE INCIDENTES Y CASOS KCD"
    )

    print(
        "Modo seguro: no cierra incidentes automaticamente, no remedia y no modifica Windows."
    )

    creados = []

    creados.extend(
        abrir_incidentes_desde_alertas_kcd()
    )

    creados.extend(
        abrir_incidentes_desde_predicciones_kcd()
    )

    creados.extend(
        abrir_incidentes_desde_validaciones_kcd()
    )

    creados.extend(
        abrir_incidentes_desde_acciones_preparadas_kcd()
    )

    creados.extend(
        abrir_incidentes_desde_orquestacion_kcd()
    )

    metricas = calcular_metricas_incidentes_kcd()

    registrar_estadisticas_incidentes_kcd(
        metricas
    )

    resumen_ejecutivo_incidentes_kcd(
        metricas
    )

    print(
        f"\n[KCD INCIDENTES] Nuevos incidentes abiertos: {len(creados)}"
    )

    return {
        "nuevos_incidentes": creados,
        "metricas": metricas
    }

# ==============================================================================
# BLOQUE 16.0 - CENTRO DE CONTROL Y MADUREZ KCD
# ==============================================================================
#
# 16.1 Consolidacion global de evidencias
# 16.2 Indice de Madurez KCD
# 16.3 Estado global del sistema
# 16.4 Efectividad de remediaciones
# 16.5 Nivel de incidentes
# 16.6 Riesgo acumulado
# 16.7 Salud operativa
# 16.8 Trazabilidad documental
# 16.9 Dashboard CSV
#
# ==============================================================================

def leer_csv_madurez_kcd(
    nombre_archivo
):

    if not os.path.exists(
        nombre_archivo
    ):

        return []

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

                registros.append(
                    fila
                )

    except Exception as error:

        print(
            f"\n[KCD MADUREZ ERROR] No se pudo leer {nombre_archivo}: {error}"
        )

        return []

    return registros


def convertir_numero_madurez_kcd(
    valor,
    defecto=0
):

    try:

        return float(
            valor
        )

    except Exception:

        return defecto


def limitar_indice_kcd(
    valor
):

    if valor < 0:

        return 0

    if valor > 100:

        return 100

    return round(
        valor,
        2
    )


def ultimo_registro_madurez_kcd(
    registros
):

    if not registros:

        return {}

    return registros[
        -1
    ]


def consolidar_evidencias_madurez_kcd():

    print(
        "\n[KCD MADUREZ] Consolidando evidencias globales..."
    )

    archivos = {
        "bitacora": "bitacora_kcd.csv",
        "acciones": "acciones_kcd.csv",
        "alertas": "alertas_kcd.csv",
        "prediccion": "prediccion_riesgo_kcd.csv",
        "orquestacion": "orquestacion_kcd.csv",
        "incidentes": "incidentes_kcd.csv",
        "seguimiento_incidentes": "seguimiento_incidentes_kcd.csv",
        "estadisticas_incidentes": "estadisticas_incidentes_kcd.csv",
        "validaciones": "validacion_resultados_kcd.csv"
    }

    evidencias = {}

    for clave, archivo in archivos.items():

        registros = leer_csv_madurez_kcd(
            archivo
        )

        evidencias[clave] = registros

        print(
            f"{archivo}: {len(registros)} registros"
        )

    return evidencias


def calcular_trazabilidad_documental_kcd(
    evidencias
):

    total_fuentes = len(
        evidencias
    )

    fuentes_con_datos = 0

    for registros in evidencias.values():

        if registros:

            fuentes_con_datos += 1

    if total_fuentes == 0:

        return 0

    indice = (
        fuentes_con_datos / total_fuentes
    ) * 100

    return limitar_indice_kcd(
        indice
    )


def calcular_salud_operativa_kcd(
    evidencias
):

    bitacora = evidencias.get(
        "bitacora",
        []
    )

    if not bitacora:

        return {
            "indice": 50,
            "estado": "SIN_DATOS",
            "ivk": 0,
            "cpu": 0,
            "ram": 0,
            "disco": 0
        }

    ultimo = ultimo_registro_madurez_kcd(
        bitacora
    )

    ivk = convertir_numero_madurez_kcd(
        ultimo.get(
            "ivk",
            50
        ),
        50
    )

    cpu = convertir_numero_madurez_kcd(
        ultimo.get(
            "cpu",
            0
        )
    )

    ram = convertir_numero_madurez_kcd(
        ultimo.get(
            "ram",
            0
        )
    )

    disco = convertir_numero_madurez_kcd(
        ultimo.get(
            "disco",
            0
        )
    )

    penalizacion = 0

    if cpu >= 90:

        penalizacion += 20

    elif cpu >= 75:

        penalizacion += 10

    if ram >= 90:

        penalizacion += 25

    elif ram >= 75:

        penalizacion += 12

    if disco >= 90:

        penalizacion += 25

    elif disco >= 80:

        penalizacion += 12

    indice = limitar_indice_kcd(
        ivk - penalizacion
    )

    if indice >= 76:

        estado = "SALUDABLE"

    elif indice >= 51:

        estado = "ACEPTABLE"

    elif indice >= 26:

        estado = "EN_RIESGO"

    else:

        estado = "CRITICO"

    return {
        "indice": indice,
        "estado": estado,
        "ivk": ivk,
        "cpu": cpu,
        "ram": ram,
        "disco": disco
    }


def calcular_efectividad_remediaciones_kcd(
    evidencias
):

    validaciones = evidencias.get(
        "validaciones",
        []
    )

    if not validaciones:

        return {
            "indice": 50,
            "estado": "SIN_DATOS",
            "efectivas": 0,
            "parciales": 0,
            "no_efectivas": 0,
            "requieren_hardware": 0
        }

    efectivas = 0
    parciales = 0
    no_efectivas = 0
    requieren_hardware = 0

    puntaje = 0

    for fila in validaciones:

        certificacion = fila.get(
            "certificacion",
            ""
        )

        resultado = fila.get(
            "resultado",
            ""
        )

        if certificacion == "EFECTIVO":

            efectivas += 1
            puntaje += 100

        elif certificacion == "PARCIALMENTE EFECTIVO":

            parciales += 1
            puntaje += 65

        elif certificacion == "REQUIERE HARDWARE":

            requieren_hardware += 1
            puntaje += 45

        elif (
            certificacion == "NO EFECTIVO"
            or resultado == "SIN CAMBIO"
            or resultado == "EMPEORO"
        ):

            no_efectivas += 1
            puntaje += 20

        else:

            puntaje += 50

    indice = limitar_indice_kcd(
        puntaje / len(
            validaciones
        )
    )

    if indice >= 76:

        estado = "EFECTIVA"

    elif indice >= 51:

        estado = "PARCIAL"

    elif indice >= 26:

        estado = "BAJA"

    else:

        estado = "NO_EFECTIVA"

    return {
        "indice": indice,
        "estado": estado,
        "efectivas": efectivas,
        "parciales": parciales,
        "no_efectivas": no_efectivas,
        "requieren_hardware": requieren_hardware
    }


def calcular_nivel_incidentes_kcd(
    evidencias
):

    incidentes = evidencias.get(
        "incidentes",
        []
    )

    if not incidentes:

        return {
            "indice": 100,
            "estado": "SIN_INCIDENTES",
            "abiertos": 0,
            "cerrados": 0,
            "criticos_abiertos": 0
        }

    abiertos = 0
    cerrados = 0
    criticos_abiertos = 0
    altos_abiertos = 0

    for fila in incidentes:

        estado = fila.get(
            "estado",
            "PENDIENTE"
        )

        prioridad = fila.get(
            "prioridad",
            "BAJO"
        )

        if estado == "CERRADO":

            cerrados += 1

        else:

            abiertos += 1

            if prioridad == "CRITICO":

                criticos_abiertos += 1

            elif prioridad == "ALTO":

                altos_abiertos += 1

    penalizacion = (
        criticos_abiertos * 30
        + altos_abiertos * 18
        + abiertos * 5
    )

    indice = limitar_indice_kcd(
        100 - penalizacion
    )

    if criticos_abiertos > 0:

        estado = "CRITICO"

    elif altos_abiertos > 0:

        estado = "ALTO"

    elif abiertos > 0:

        estado = "CONTROLADO"

    else:

        estado = "CERRADO"

    return {
        "indice": indice,
        "estado": estado,
        "abiertos": abiertos,
        "cerrados": cerrados,
        "criticos_abiertos": criticos_abiertos
    }


def calcular_riesgo_acumulado_kcd(
    evidencias
):

    alertas = evidencias.get(
        "alertas",
        []
    )

    predicciones = evidencias.get(
        "prediccion",
        []
    )

    orquestaciones = evidencias.get(
        "orquestacion",
        []
    )

    puntaje_riesgo = 0

    for alerta in alertas:

        nivel = alerta.get(
            "nivel",
            "BAJO"
        )

        if nivel == "CRITICO":

            puntaje_riesgo += 6

        elif nivel == "ALTO":

            puntaje_riesgo += 4

        elif nivel == "MODERADO":

            puntaje_riesgo += 2

        else:

            puntaje_riesgo += 1

    ultima_prediccion = ultimo_registro_madurez_kcd(
        predicciones
    )

    riesgo_predictivo = ultima_prediccion.get(
        "riesgo_predictivo",
        "BAJO"
    )

    if riesgo_predictivo == "CRITICO":

        puntaje_riesgo += 25

    elif riesgo_predictivo == "ALTO":

        puntaje_riesgo += 18

    elif riesgo_predictivo == "MODERADO":

        puntaje_riesgo += 10

    ultima_orquestacion = ultimo_registro_madurez_kcd(
        orquestaciones
    )

    ipk = convertir_numero_madurez_kcd(
        ultima_orquestacion.get(
            "IPK",
            0
        )
    )

    puntaje_riesgo += ipk * 0.4

    if puntaje_riesgo >= 80:

        estado = "CRITICO"

    elif puntaje_riesgo >= 50:

        estado = "ALTO"

    elif puntaje_riesgo >= 25:

        estado = "MODERADO"

    else:

        estado = "BAJO"

    indice_salud_riesgo = limitar_indice_kcd(
        100 - puntaje_riesgo
    )

    return {
        "indice": indice_salud_riesgo,
        "estado": estado,
        "puntaje_riesgo": round(
            puntaje_riesgo,
            2
        ),
        "riesgo_predictivo": riesgo_predictivo,
        "ipk": ipk
    }


def calcular_actividad_mantenimiento_kcd(
    evidencias
):

    acciones = evidencias.get(
        "acciones",
        []
    )

    alertas = evidencias.get(
        "alertas",
        []
    )

    validaciones = evidencias.get(
        "validaciones",
        []
    )

    preventivas = 0
    correctivas = 0
    auditorias = 0

    for fila in acciones:

        accion = str(
            fila.get(
                "accion",
                ""
            )
        ).lower()

        detalle = str(
            fila.get(
                "detalle",
                ""
            )
        ).lower()

        texto = accion + " " + detalle

        if (
            "prevent" in texto
            or "monitoreo" in texto
            or "auditoria" in texto
        ):

            preventivas += 1

        if (
            "correc" in texto
            or "remediacion" in texto
            or "validacion" in texto
            or "incidente" in texto
        ):

            correctivas += 1

        if "auditoria" in texto:

            auditorias += 1

    total_actividad = (
        len(
            acciones
        )
        + len(
            alertas
        )
        + len(
            validaciones
        )
    )

    return {
        "acciones_registradas": len(
            acciones
        ),
        "alertas_registradas": len(
            alertas
        ),
        "validaciones_registradas": len(
            validaciones
        ),
        "preventivas": preventivas,
        "correctivas": correctivas,
        "auditorias": auditorias,
        "actividad_total": total_actividad
    }


def clasificar_madurez_kcd(
    indice
):

    if indice >= 85:

        return "MADUREZ_OPTIMA"

    if indice >= 70:

        return "MADURO"

    if indice >= 50:

        return "GESTIONADO"

    if indice >= 30:

        return "BASICO"

    return "INICIAL"


def clasificar_estado_global_kcd(
    indice_madurez,
    riesgo,
    incidentes
):

    if (
        riesgo.get(
            "estado",
            "BAJO"
        ) == "CRITICO"
        or incidentes.get(
            "estado",
            ""
        ) == "CRITICO"
    ):

        return "CRITICO"

    if indice_madurez >= 85:

        return "ESTABLE_OPTIMO"

    if indice_madurez >= 70:

        return "ESTABLE"

    if indice_madurez >= 50:

        return "CONTROLADO"

    if indice_madurez >= 30:

        return "EN_RIESGO"

    return "CRITICO"


def calcular_indice_madurez_kcd(
    trazabilidad,
    salud,
    efectividad,
    incidentes,
    riesgo
):

    indice = (
        trazabilidad * 0.20
        + salud.get(
            "indice",
            0
        ) * 0.25
        + efectividad.get(
            "indice",
            0
        ) * 0.20
        + incidentes.get(
            "indice",
            0
        ) * 0.20
        + riesgo.get(
            "indice",
            0
        ) * 0.15
    )

    return limitar_indice_kcd(
        indice
    )


def registrar_madurez_kcd(
    resultado
):

    nombre_archivo = "madurez_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "indice_madurez",
        "clasificacion_madurez",
        "estado_global",
        "salud_operativa",
        "efectividad_remediaciones",
        "nivel_incidentes",
        "riesgo_acumulado",
        "trazabilidad_documental",
        "acciones_registradas",
        "alertas_registradas",
        "validaciones_registradas"
    ]

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        resultado.get(
            "indice_madurez",
            0
        ),
        resultado.get(
            "clasificacion_madurez",
            ""
        ),
        resultado.get(
            "estado_global",
            ""
        ),
        resultado.get(
            "salud_operativa",
            {}
        ).get(
            "estado",
            ""
        ),
        resultado.get(
            "efectividad_remediaciones",
            {}
        ).get(
            "estado",
            ""
        ),
        resultado.get(
            "nivel_incidentes",
            {}
        ).get(
            "estado",
            ""
        ),
        resultado.get(
            "riesgo_acumulado",
            {}
        ).get(
            "estado",
            ""
        ),
        resultado.get(
            "trazabilidad_documental",
            0
        ),
        resultado.get(
            "actividad_mantenimiento",
            {}
        ).get(
            "acciones_registradas",
            0
        ),
        resultado.get(
            "actividad_mantenimiento",
            {}
        ).get(
            "alertas_registradas",
            0
        ),
        resultado.get(
            "actividad_mantenimiento",
            {}
        ).get(
            "validaciones_registradas",
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

    print(
        "\n[KCD MADUREZ] Registro guardado en madurez_kcd.csv"
    )


def registrar_dashboard_kcd(
    resultado
):

    nombre_archivo = "dashboard_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "indicador",
        "valor",
        "estado",
        "detalle"
    ]

    filas = [
        [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Indice de Madurez KCD",
            resultado.get(
                "indice_madurez",
                0
            ),
            resultado.get(
                "clasificacion_madurez",
                ""
            ),
            "Indice global 0-100"
        ],
        [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Estado Global",
            resultado.get(
                "estado_global",
                ""
            ),
            resultado.get(
                "estado_global",
                ""
            ),
            "Estado consolidado del sistema"
        ],
        [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Salud Operativa",
            resultado.get(
                "salud_operativa",
                {}
            ).get(
                "indice",
                0
            ),
            resultado.get(
                "salud_operativa",
                {}
            ).get(
                "estado",
                ""
            ),
            "IVK, CPU, RAM y disco"
        ],
        [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Efectividad Remediaciones",
            resultado.get(
                "efectividad_remediaciones",
                {}
            ).get(
                "indice",
                0
            ),
            resultado.get(
                "efectividad_remediaciones",
                {}
            ).get(
                "estado",
                ""
            ),
            "Resultados del Bloque 11"
        ],
        [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Nivel de Incidentes",
            resultado.get(
                "nivel_incidentes",
                {}
            ).get(
                "indice",
                0
            ),
            resultado.get(
                "nivel_incidentes",
                {}
            ).get(
                "estado",
                ""
            ),
            "Incidentes abiertos y cerrados"
        ],
        [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Riesgo Acumulado",
            resultado.get(
                "riesgo_acumulado",
                {}
            ).get(
                "puntaje_riesgo",
                0
            ),
            resultado.get(
                "riesgo_acumulado",
                {}
            ).get(
                "estado",
                ""
            ),
            "Alertas, prediccion e IPK"
        ],
        [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Trazabilidad Documental",
            resultado.get(
                "trazabilidad_documental",
                0
            ),
            "AUDITABLE",
            "Fuentes CSV disponibles"
        ]
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

        for fila in filas:

            escritor.writerow(
                fila
            )

    print(
        "\n[KCD DASHBOARD] Registro guardado en dashboard_kcd.csv"
    )


def mostrar_resumen_madurez_kcd(
    resultado
):

    print(
        "\n[KCD CENTRO DE CONTROL]"
    )

    print(
        f"Indice de Madurez KCD: {resultado['indice_madurez']} / 100"
    )

    print(
        f"Clasificacion: {resultado['clasificacion_madurez']}"
    )

    print(
        f"Estado global: {resultado['estado_global']}"
    )

    print(
        f"Salud operativa: {resultado['salud_operativa']['estado']} ({resultado['salud_operativa']['indice']})"
    )

    print(
        f"Efectividad remediaciones: {resultado['efectividad_remediaciones']['estado']} ({resultado['efectividad_remediaciones']['indice']})"
    )

    print(
        f"Nivel incidentes: {resultado['nivel_incidentes']['estado']} ({resultado['nivel_incidentes']['indice']})"
    )

    print(
        f"Riesgo acumulado: {resultado['riesgo_acumulado']['estado']} ({resultado['riesgo_acumulado']['puntaje_riesgo']})"
    )

    print(
        f"Trazabilidad documental: {resultado['trazabilidad_documental']}%"
    )

    print(
        f"Acciones registradas: {resultado['actividad_mantenimiento']['acciones_registradas']}"
    )

    print(
        f"Alertas registradas: {resultado['actividad_mantenimiento']['alertas_registradas']}"
    )

    print(
        f"Validaciones registradas: {resultado['actividad_mantenimiento']['validaciones_registradas']}"
    )


def ejecutar_centro_madurez_kcd():

    print(
        "\n[KCD BLOQUE 16] CENTRO DE CONTROL Y MADUREZ KCD"
    )

    print(
        "Modo seguro: solo lee evidencias, calcula indicadores y registra dashboard."
    )

    evidencias = consolidar_evidencias_madurez_kcd()

    trazabilidad = calcular_trazabilidad_documental_kcd(
        evidencias
    )

    salud = calcular_salud_operativa_kcd(
        evidencias
    )

    efectividad = calcular_efectividad_remediaciones_kcd(
        evidencias
    )

    incidentes = calcular_nivel_incidentes_kcd(
        evidencias
    )

    riesgo = calcular_riesgo_acumulado_kcd(
        evidencias
    )

    actividad = calcular_actividad_mantenimiento_kcd(
        evidencias
    )

    indice_madurez = calcular_indice_madurez_kcd(
        trazabilidad,
        salud,
        efectividad,
        incidentes,
        riesgo
    )

    clasificacion = clasificar_madurez_kcd(
        indice_madurez
    )

    estado_global = clasificar_estado_global_kcd(
        indice_madurez,
        riesgo,
        incidentes
    )

    resultado = {
        "fecha": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "indice_madurez": indice_madurez,
        "clasificacion_madurez": clasificacion,
        "estado_global": estado_global,
        "salud_operativa": salud,
        "efectividad_remediaciones": efectividad,
        "nivel_incidentes": incidentes,
        "riesgo_acumulado": riesgo,
        "trazabilidad_documental": trazabilidad,
        "actividad_mantenimiento": actividad
    }

    registrar_madurez_kcd(
        resultado
    )

    registrar_dashboard_kcd(
        resultado
    )

    try:

        registrar_accion_kcd(
            "CENTRO_MADUREZ_KCD",
            estado_global,
            f"Indice de Madurez KCD: {indice_madurez}"
        )

    except Exception:

        pass

    mostrar_resumen_madurez_kcd(
        resultado
    )

    return resultado


# ==============================================================================
# BLOQUE 17.0 - INVESTIGACION AUTOMATICA DE ESPACIO RECUPERABLE KCD
# ==============================================================================
#
# 17.1 Analisis de carpetas grandes del usuario
# 17.2 Analisis profundo de AppData
# 17.3 Deteccion de aplicaciones grandes
# 17.4 Analisis especializado de Chrome
# 17.5 Clasificacion de carpetas
# 17.6 Calculo de espacio recuperable
# 17.7 Recomendaciones de espacio
# 17.8 Evidencia CSV
# 17.9 Resumen ejecutivo de espacio
#
# ==============================================================================

def obtener_rutas_usuario_espacio_kcd():

    usuario = os.path.expanduser(
        "~"
    )

    rutas = {
        "AppData": os.path.join(
            usuario,
            "AppData"
        ),
        "AppData_Local": os.environ.get(
            "LOCALAPPDATA",
            os.path.join(
                usuario,
                "AppData",
                "Local"
            )
        ),
        "AppData_Roaming": os.environ.get(
            "APPDATA",
            os.path.join(
                usuario,
                "AppData",
                "Roaming"
            )
        ),
        "AppData_LocalLow": os.path.join(
            usuario,
            "AppData",
            "LocalLow"
        ),
        "Documents": os.path.join(
            usuario,
            "Documents"
        ),
        "Downloads": os.path.join(
            usuario,
            "Downloads"
        ),
        "PycharmProjects": os.path.join(
            usuario,
            "PycharmProjects"
        )
    }

    return rutas


def convertir_bytes_a_mb_kcd(
    bytes_valor
):

    return round(
        bytes_valor / (1024 ** 2),
        2
    )


def convertir_mb_a_gb_kcd(
    mb_valor
):

    return round(
        mb_valor / 1024,
        2
    )


def calcular_tamano_ruta_kcd(
    ruta,
    limite_archivos=200000
):

    total_bytes = 0
    archivos_contados = 0
    errores = 0

    if not os.path.exists(
        ruta
    ):

        return {
            "existe": False,
            "tamano_mb": 0,
            "archivos_contados": 0,
            "errores": 0
        }

    if os.path.isfile(
        ruta
    ):

        try:

            total_bytes = os.path.getsize(
                ruta
            )

            return {
                "existe": True,
                "tamano_mb": convertir_bytes_a_mb_kcd(
                    total_bytes
                ),
                "archivos_contados": 1,
                "errores": 0
            }

        except Exception:

            return {
                "existe": True,
                "tamano_mb": 0,
                "archivos_contados": 0,
                "errores": 1
            }

    for raiz, carpetas, archivos in os.walk(
        ruta
    ):

        for archivo in archivos:

            try:

                ruta_archivo = os.path.join(
                    raiz,
                    archivo
                )

                total_bytes += os.path.getsize(
                    ruta_archivo
                )

                archivos_contados += 1

                if archivos_contados >= limite_archivos:

                    return {
                        "existe": True,
                        "tamano_mb": convertir_bytes_a_mb_kcd(
                            total_bytes
                        ),
                        "archivos_contados": archivos_contados,
                        "errores": errores
                    }

            except Exception:

                errores += 1

                continue

    return {
        "existe": True,
        "tamano_mb": convertir_bytes_a_mb_kcd(
            total_bytes
        ),
        "archivos_contados": archivos_contados,
        "errores": errores
    }


def clasificar_ruta_espacio_kcd(
    ruta,
    aplicacion="GENERAL"
):

    ruta_min = str(
        ruta
    ).lower()

    if (
        "cache" in ruta_min
        or "code cache" in ruta_min
        or "gpucache" in ruta_min
        or "cachestorage" in ruta_min
        or "temporary" in ruta_min
        or "temp" in ruta_min
    ):

        return "POSIBLE_LIMPIEZA"

    if (
        "user data" in ruta_min
        or "profile" in ruta_min
        or "default" in ruta_min
        or "documents" in ruta_min
        or "downloads" in ruta_min
        or "pycharmprojects" in ruta_min
    ):

        return "REQUIERE_AUTORIZACION"

    if (
        "appdata" in ruta_min
        and aplicacion in [
            "Chrome",
            "Google",
            "Microsoft",
            "Adobe",
            "JetBrains",
            "Docker",
            "Zoom",
            "Mozilla"
        ]
    ):

        return "SEGURO_ANALIZAR"

    if (
        "windows" in ruta_min
        or "system32" in ruta_min
        or "program files" in ruta_min
    ):

        return "NO_TOCAR"

    return "SEGURO_ANALIZAR"


def estimar_recuperable_kcd(
    clasificacion,
    tamano_mb
):

    if clasificacion == "POSIBLE_LIMPIEZA":

        return round(
            tamano_mb * 0.85,
            2
        )

    if clasificacion == "SEGURO_ANALIZAR":

        return round(
            tamano_mb * 0.10,
            2
        )

    return 0


def detectar_aplicacion_por_ruta_kcd(
    ruta
):

    ruta_min = str(
        ruta
    ).lower()

    aplicaciones = {
        "Chrome": "chrome",
        "Google": "google",
        "Microsoft": "microsoft",
        "Adobe": "adobe",
        "JetBrains": "jetbrains",
        "Docker": "docker",
        "Zoom": "zoom",
        "Mozilla": "mozilla"
    }

    for nombre, patron in aplicaciones.items():

        if patron in ruta_min:

            return nombre

    return "GENERAL"


def crear_registro_espacio_kcd(
    origen,
    ruta,
    tipo,
    aplicacion,
    tamano_mb,
    clasificacion,
    recomendacion
):

    recuperable_mb = estimar_recuperable_kcd(
        clasificacion,
        tamano_mb
    )

    return {
        "fecha": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "origen": origen,
        "ruta": ruta,
        "tipo": tipo,
        "aplicacion": aplicacion,
        "tamano_mb": tamano_mb,
        "tamano_gb": convertir_mb_a_gb_kcd(
            tamano_mb
        ),
        "clasificacion": clasificacion,
        "recuperable_mb": recuperable_mb,
        "recuperable_gb": convertir_mb_a_gb_kcd(
            recuperable_mb
        ),
        "recomendacion": recomendacion
    }


def analizar_carpetas_usuario_kcd():

    print(
        "\n[KCD ESPACIO] Analizando carpetas principales del usuario..."
    )

    rutas = obtener_rutas_usuario_espacio_kcd()

    registros = []

    for nombre, ruta in rutas.items():

        resultado = calcular_tamano_ruta_kcd(
            ruta
        )

        if not resultado["existe"]:

            continue

        aplicacion = detectar_aplicacion_por_ruta_kcd(
            ruta
        )

        clasificacion = clasificar_ruta_espacio_kcd(
            ruta,
            aplicacion
        )

        recomendacion = "Analizar contenido antes de cualquier accion."

        if nombre == "Downloads":

            recomendacion = "Revisar descargas antiguas, duplicados o instaladores."

        elif nombre == "Documents":

            recomendacion = "Revisar documentos grandes antes de mover o respaldar."

        elif nombre == "PycharmProjects":

            recomendacion = "Revisar proyectos grandes, entornos virtuales y archivos temporales."

        elif "AppData" in nombre:

            recomendacion = "Analizar consumo de aplicaciones. No borrar carpetas manualmente."

        registro = crear_registro_espacio_kcd(
            nombre,
            ruta,
            "CARPETA_USUARIO",
            aplicacion,
            resultado["tamano_mb"],
            clasificacion,
            recomendacion
        )

        registros.append(
            registro
        )

        print(
            f"{nombre}: {registro['tamano_gb']} GB"
        )

    return registros


def analizar_aplicaciones_appdata_kcd():

    print(
        "\n[KCD ESPACIO] Analizando aplicaciones grandes en AppData..."
    )

    rutas = obtener_rutas_usuario_espacio_kcd()

    bases_appdata = [
        rutas.get(
            "AppData_Local",
            ""
        ),
        rutas.get(
            "AppData_Roaming",
            ""
        ),
        rutas.get(
            "AppData_LocalLow",
            ""
        )
    ]

    aplicaciones = [
        "Chrome",
        "Google",
        "Microsoft",
        "Adobe",
        "JetBrains",
        "Docker",
        "Zoom",
        "Mozilla"
    ]

    registros = []

    for base in bases_appdata:

        if not os.path.exists(
            base
        ):

            continue

        for raiz, carpetas, archivos in os.walk(
            base
        ):

            nivel_relativo = raiz.replace(
                base,
                ""
            ).count(
                os.sep
            )

            if nivel_relativo > 2:

                carpetas[:] = []

                continue

            aplicacion_detectada = detectar_aplicacion_por_ruta_kcd(
                raiz
            )

            if aplicacion_detectada not in aplicaciones:

                continue

            resultado = calcular_tamano_ruta_kcd(
                raiz,
                limite_archivos=80000
            )

            clasificacion = clasificar_ruta_espacio_kcd(
                raiz,
                aplicacion_detectada
            )

            recomendacion = (
                "Aplicacion detectada en AppData. Revisar antes de cualquier limpieza."
            )

            if clasificacion == "POSIBLE_LIMPIEZA":

                recomendacion = (
                    "Posible cache o temporal. Preparar limpieza autorizada con Bloque 10."
                )

            registro = crear_registro_espacio_kcd(
                "AppData",
                raiz,
                "APLICACION_APPDATA",
                aplicacion_detectada,
                resultado["tamano_mb"],
                clasificacion,
                recomendacion
            )

            registros.append(
                registro
            )

            carpetas[:] = []

    registros.sort(
        key=lambda item: item["tamano_mb"],
        reverse=True
    )

    return registros[
        :30
    ]


def rutas_chrome_kcd():

    local_appdata = os.environ.get(
        "LOCALAPPDATA",
        ""
    )

    base_chrome = os.path.join(
        local_appdata,
        "Google",
        "Chrome",
        "User Data"
    )

    return base_chrome


def analizar_chrome_kcd():

    print(
        "\n[KCD ESPACIO] Analizando Chrome sin cerrar procesos..."
    )

    base_chrome = rutas_chrome_kcd()

    registros = []

    if not os.path.exists(
        base_chrome
    ):

        print(
            "[KCD ESPACIO] Chrome User Data no encontrado."
        )

        return registros

    total_chrome = calcular_tamano_ruta_kcd(
        base_chrome
    )

    registros.append(
        crear_registro_espacio_kcd(
            "Chrome",
            base_chrome,
            "CHROME_TOTAL",
            "Chrome",
            total_chrome["tamano_mb"],
            "REQUIERE_AUTORIZACION",
            "No borrar User Data. Contiene perfiles, historial, sesiones y datos del usuario."
        )
    )

    perfiles = []

    try:

        for item in os.listdir(
            base_chrome
        ):

            ruta_item = os.path.join(
                base_chrome,
                item
            )

            if not os.path.isdir(
                ruta_item
            ):

                continue

            nombre = item.lower()

            if (
                nombre == "default"
                or nombre.startswith(
                    "profile"
                )
                or nombre == "guest profile"
            ):

                perfiles.append(
                    ruta_item
                )

    except Exception:

        perfiles = []

    for perfil in perfiles:

        resultado_perfil = calcular_tamano_ruta_kcd(
            perfil
        )

        registros.append(
            crear_registro_espacio_kcd(
                "Chrome",
                perfil,
                "CHROME_PERFIL",
                "Chrome",
                resultado_perfil["tamano_mb"],
                "NO_TOCAR",
                "Perfil de usuario. No borrar manualmente."
            )
        )

        rutas_cache = [
            (
                "CHROME_CACHE",
                os.path.join(
                    perfil,
                    "Cache"
                ),
                "Cache de Chrome. Posible limpieza con autorizacion."
            ),
            (
                "CHROME_CODE_CACHE",
                os.path.join(
                    perfil,
                    "Code Cache"
                ),
                "Code Cache de Chrome. Posible limpieza con autorizacion."
            ),
            (
                "CHROME_GPUCACHE",
                os.path.join(
                    perfil,
                    "GPUCache"
                ),
                "GPUCache de Chrome. Posible limpieza con autorizacion."
            ),
            (
                "CHROME_SERVICE_WORKER_CACHE",
                os.path.join(
                    perfil,
                    "Service Worker",
                    "CacheStorage"
                ),
                "Service Worker CacheStorage. Revisar antes de limpiar."
            )
        ]

        for tipo, ruta_cache, recomendacion in rutas_cache:

            if not os.path.exists(
                ruta_cache
            ):

                continue

            resultado_cache = calcular_tamano_ruta_kcd(
                ruta_cache
            )

            registros.append(
                crear_registro_espacio_kcd(
                    "Chrome",
                    ruta_cache,
                    tipo,
                    "Chrome",
                    resultado_cache["tamano_mb"],
                    "POSIBLE_LIMPIEZA",
                    recomendacion
                )
            )

    return registros


def registrar_investigacion_espacio_kcd(
    registros
):

    nombre_archivo = "investigacion_espacio_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "origen",
        "ruta",
        "tipo",
        "aplicacion",
        "tamano_mb",
        "tamano_gb",
        "clasificacion",
        "recuperable_mb",
        "recuperable_gb",
        "recomendacion"
    ]

    with open(
        nombre_archivo,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=encabezados
        )

        if not existe_archivo:

            escritor.writeheader()

        for registro in registros:

            escritor.writerow(
                registro
            )

    print(
        "\n[KCD ESPACIO] Evidencia registrada en investigacion_espacio_kcd.csv"
    )


def registrar_recomendaciones_espacio_kcd(
    resumen,
    recomendaciones
):

    nombre_archivo = "recomendaciones_espacio_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "nivel_riesgo",
        "accion_recomendada",
        "espacio_recuperable_mb",
        "espacio_recuperable_gb",
        "detalle"
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

        for recomendacion in recomendaciones:

            escritor.writerow([
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                resumen.get(
                    "nivel_riesgo",
                    "BAJO"
                ),
                recomendacion,
                resumen.get(
                    "recuperable_total_mb",
                    0
                ),
                resumen.get(
                    "recuperable_total_gb",
                    0
                ),
                resumen.get(
                    "accion_recomendada",
                    ""
                )
            ])


def preparar_datos_bloque10_espacio_kcd(
    resumen
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

    problema = (
        f"Espacio recuperable estimado: {resumen.get('recuperable_total_gb', 0)} GB."
    )

    accion = resumen.get(
        "accion_recomendada",
        "Revisar espacio recuperable antes de cualquier limpieza."
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

        escritor.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "BLOQUE_17_INVESTIGACION_ESPACIO",
            "ESPACIO_RECUPERABLE",
            resumen.get(
                "nivel_riesgo",
                "BAJO"
            ),
            problema,
            accion,
            "PENDIENTE_BLOQUE_10",
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ])


def generar_resumen_espacio_kcd(
    registros
):

    if not registros:

        return {
            "carpeta_mas_pesada": "SIN_DATOS",
            "aplicacion_mas_pesada": "SIN_DATOS",
            "recuperable_total_mb": 0,
            "recuperable_total_gb": 0,
            "nivel_riesgo": "SIN_DATOS",
            "accion_recomendada": "No hay datos suficientes para recomendar."
        }

    carpeta_mas_pesada = max(
        registros,
        key=lambda item: item.get(
            "tamano_mb",
            0
        )
    )

    acumulado_aplicaciones = {}

    recuperable_total_mb = 0

    for registro in registros:

        aplicacion = registro.get(
            "aplicacion",
            "GENERAL"
        )

        acumulado_aplicaciones[aplicacion] = acumulado_aplicaciones.get(
            aplicacion,
            0
        ) + registro.get(
            "tamano_mb",
            0
        )

        recuperable_total_mb += registro.get(
            "recuperable_mb",
            0
        )

    aplicacion_mas_pesada = max(
        acumulado_aplicaciones,
        key=acumulado_aplicaciones.get
    )

    recuperable_total_mb = round(
        recuperable_total_mb,
        2
    )

    recuperable_total_gb = convertir_mb_a_gb_kcd(
        recuperable_total_mb
    )

    if recuperable_total_gb >= 10:

        nivel_riesgo = "CRITICO"

    elif recuperable_total_gb >= 5:

        nivel_riesgo = "ALTO"

    elif recuperable_total_gb >= 1:

        nivel_riesgo = "MODERADO"

    else:

        nivel_riesgo = "BAJO"

    if aplicacion_mas_pesada == "Chrome" and recuperable_total_gb >= 1:

        accion_recomendada = (
            "Limpiar cache de Chrome solo con autorizacion. No borrar perfiles."
        )

    elif "PycharmProjects" in carpeta_mas_pesada.get(
        "ruta",
        ""
    ):

        accion_recomendada = (
            "Revisar proyectos grandes, entornos virtuales y archivos temporales."
        )

    elif "AppData" in carpeta_mas_pesada.get(
        "ruta",
        ""
    ):

        accion_recomendada = (
            "Revisar AppData Local y caches de aplicaciones. No borrar carpetas manualmente."
        )

    else:

        accion_recomendada = (
            "Revisar carpetas grandes y preparar limpieza autorizada con Bloque 10."
        )

    return {
        "carpeta_mas_pesada": carpeta_mas_pesada.get(
            "ruta",
            ""
        ),
        "aplicacion_mas_pesada": aplicacion_mas_pesada,
        "recuperable_total_mb": recuperable_total_mb,
        "recuperable_total_gb": recuperable_total_gb,
        "nivel_riesgo": nivel_riesgo,
        "accion_recomendada": accion_recomendada
    }


def generar_recomendaciones_espacio_kcd(
    registros,
    resumen
):

    recomendaciones = []

    hay_chrome_cache = False
    hay_appdata = False
    hay_pycharm = False

    for registro in registros:

        tipo = registro.get(
            "tipo",
            ""
        )

        ruta = registro.get(
            "ruta",
            ""
        )

        if (
            registro.get(
                "aplicacion",
                ""
            ) == "Chrome"
            and "CACHE" in tipo
        ):

            hay_chrome_cache = True

        if "AppData" in ruta:

            hay_appdata = True

        if "PycharmProjects" in ruta:

            hay_pycharm = True

    if hay_chrome_cache:

        recomendaciones.append(
            "Limpiar cache de Chrome solo con autorizacion del usuario."
        )

        recomendaciones.append(
            "No borrar perfiles de Chrome manualmente."
        )

    if hay_appdata:

        recomendaciones.append(
            "Revisar AppData Local antes de limpiar. Priorizar caches, no datos del usuario."
        )

    if hay_pycharm:

        recomendaciones.append(
            "Revisar proyectos grandes, entornos virtuales y carpetas temporales."
        )

    if resumen.get(
        "recuperable_total_gb",
        0
    ) >= 1:

        recomendaciones.append(
            "Preparar accion segura para Bloque 10 sin ejecutar limpieza automatica."
        )

    if not recomendaciones:

        recomendaciones.append(
            "No se detecta espacio recuperable significativo."
        )

    return recomendaciones


def mostrar_resumen_espacio_kcd(
    resumen,
    recomendaciones
):

    print(
        "\n[KCD INVESTIGACION ESPACIO]"
    )

    print(
        f"Carpeta mas pesada: {resumen.get('carpeta_mas_pesada', '')}"
    )

    print(
        f"Aplicacion mas pesada: {resumen.get('aplicacion_mas_pesada', '')}"
    )

    print(
        f"Espacio recuperable estimado: {resumen.get('recuperable_total_gb', 0)} GB"
    )

    print(
        f"Nivel de riesgo: {resumen.get('nivel_riesgo', '')}"
    )

    print(
        f"Accion recomendada: {resumen.get('accion_recomendada', '')}"
    )

    print(
        "\nRecomendaciones:"
    )

    for recomendacion in recomendaciones:

        print(
            f"- {recomendacion}"
        )


def ejecutar_investigacion_espacio_kcd():

    print(
        "\n[KCD BLOQUE 17] INVESTIGACION AUTOMATICA DE ESPACIO RECUPERABLE"
    )

    print(
        "Modo seguro: no borra archivos, no cierra Chrome, no limpia caches y no modifica Windows."
    )

    registros = []

    registros.extend(
        analizar_carpetas_usuario_kcd()
    )

    registros.extend(
        analizar_aplicaciones_appdata_kcd()
    )

    registros.extend(
        analizar_chrome_kcd()
    )

    registros = [
        registro
        for registro in registros
        if registro.get(
            "tamano_mb",
            0
        ) > 0
    ]

    registros.sort(
        key=lambda item: item.get(
            "tamano_mb",
            0
        ),
        reverse=True
    )

    resumen = generar_resumen_espacio_kcd(
        registros
    )

    recomendaciones = generar_recomendaciones_espacio_kcd(
        registros,
        resumen
    )

    registrar_investigacion_espacio_kcd(
        registros
    )

    registrar_recomendaciones_espacio_kcd(
        resumen,
        recomendaciones
    )

    if resumen.get(
        "recuperable_total_gb",
        0
    ) >= 1:

        preparar_datos_bloque10_espacio_kcd(
            resumen
        )

    try:

        registrar_accion_kcd(
            "INVESTIGACION_ESPACIO",
            resumen.get(
                "nivel_riesgo",
                "BAJO"
            ),
            resumen.get(
                "accion_recomendada",
                ""
            )
        )

    except Exception:

        pass

    mostrar_resumen_espacio_kcd(
        resumen,
        recomendaciones
    )

    return {
        "registros": registros,
        "resumen": resumen,
        "recomendaciones": recomendaciones
    }

# ==============================================================================
# BLOQUE 18.0 - REMEDIACION INTELIGENTE AUTORIZADA KCD
# ==============================================================================
#
# 18.1 Lectura de recomendaciones
# 18.2 Clasificacion de acciones candidatas
# 18.3 Solicitud de autorizacion explicita
# 18.4 Ejecucion segura autorizada
# 18.5 Medicion ANTES y DESPUES
# 18.6 Evidencia de remediacion
# 18.7 Validacion con Bloque 11
#
# ==============================================================================

def leer_csv_remediacion_kcd(
    nombre_archivo
):

    if not os.path.exists(
        nombre_archivo
    ):

        return []

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

                registros.append(
                    fila
                )

    except Exception as error:

        print(
            f"\n[KCD REMEDIACION ERROR] No se pudo leer {nombre_archivo}: {error}"
        )

        return []

    return registros


def convertir_numero_remediacion_kcd(
    valor,
    defecto=0
):

    try:

        return float(
            valor
        )

    except Exception:

        return defecto


def obtener_chrome_user_data_kcd():

    local_appdata = os.environ.get(
        "LOCALAPPDATA",
        ""
    )

    return os.path.join(
        local_appdata,
        "Google",
        "Chrome",
        "User Data"
    )


def ruta_segura_cache_chrome_kcd(
    ruta
):

    ruta_abs = os.path.abspath(
        ruta
    ).lower()

    base_chrome = os.path.abspath(
        obtener_chrome_user_data_kcd()
    ).lower()

    if not ruta_abs.startswith(
        base_chrome
    ):

        return False

    permitidos = [
        "cache",
        "code cache",
        "gpucache",
        "cachestorage"
    ]

    for permitido in permitidos:

        if permitido in ruta_abs:

            return True

    bloqueados = [
        "login data",
        "cookies",
        "history",
        "preferences",
        "local state",
        "password",
        "sessions"
    ]

    for bloqueado in bloqueados:

        if bloqueado in ruta_abs:

            return False

    return False


def medir_estado_remediacion_kcd(
    etapa
):

    try:

        medicion = medir_estado_validacion_kcd(
            etapa,
            muestras=3
        )

        return medicion

    except Exception:

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

        return {
            "etapa": etapa,
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


def clasificar_accion_remediacion_kcd(
    texto
):

    texto = str(
        texto
    ).lower()

    if (
        "perfil" in texto
        or "password" in texto
        or "contraseña" in texto
        or "cookies" in texto
        or "historial" in texto
        or "documents" in texto
        or "documentos" in texto
        or "downloads" in texto
        or "descargas" in texto
        or "appdata completo" in texto
        or "user data" in texto
    ):

        return "NO_RECOMENDADA"

    if (
        "proyecto" in texto
        or "pycharmprojects" in texto
        or "archivos grandes" in texto
        or "revisar appdata" in texto
        or "revisar carpeta" in texto
    ):

        return "SOLO_MANUAL"

    if (
        "cache de chrome" in texto
        or "caché de chrome" in texto
        or "chrome cache" in texto
        or "code cache" in texto
        or "gpucache" in texto
        or "cachestorage" in texto
    ):

        return "REQUIERE_AUTORIZACION"

    if (
        "temporal" in texto
        or "temporales kcd" in texto
        or "kcd temp" in texto
    ):

        return "SEGURA"

    return "REQUIERE_AUTORIZACION"


def crear_candidata_remediacion_kcd(
    origen,
    accion,
    impacto_estimado_mb=0
):

    clasificacion = clasificar_accion_remediacion_kcd(
        accion
    )

    return {
        "origen": origen,
        "accion": accion,
        "clasificacion": clasificacion,
        "impacto_estimado_mb": round(
            impacto_estimado_mb,
            2
        ),
        "impacto_estimado_gb": round(
            impacto_estimado_mb / 1024,
            2
        )
    }


def leer_candidatas_bloque10_kcd():

    registros = leer_csv_remediacion_kcd(
        "acciones_preparadas_bloque10_kcd.csv"
    )

    candidatas = []

    for fila in registros:

        accion = fila.get(
            "accion_sugerida",
            ""
        )

        if not accion:

            continue

        candidatas.append(
            crear_candidata_remediacion_kcd(
                "BLOQUE_10",
                accion,
                0
            )
        )

    return candidatas


def leer_candidatas_bloque14_kcd():

    registros = leer_csv_remediacion_kcd(
        "agenda_mantenimiento_kcd.csv"
    )

    candidatas = []

    for fila in registros:

        accion = fila.get(
            "accion",
            ""
        )

        if not accion:

            continue

        candidatas.append(
            crear_candidata_remediacion_kcd(
                "BLOQUE_14",
                accion,
                0
            )
        )

    return candidatas


def leer_candidatas_bloque17_kcd():

    recomendaciones = leer_csv_remediacion_kcd(
        "recomendaciones_espacio_kcd.csv"
    )

    investigacion = leer_csv_remediacion_kcd(
        "investigacion_espacio_kcd.csv"
    )

    candidatas = []

    for fila in recomendaciones:

        accion = fila.get(
            "accion_recomendada",
            ""
        )

        impacto = convertir_numero_remediacion_kcd(
            fila.get(
                "espacio_recuperable_mb",
                0
            )
        )

        if accion:

            candidatas.append(
                crear_candidata_remediacion_kcd(
                    "BLOQUE_17",
                    accion,
                    impacto
                )
            )

    for fila in investigacion:

        clasificacion = fila.get(
            "clasificacion",
            ""
        )

        tipo = fila.get(
            "tipo",
            ""
        )

        ruta = fila.get(
            "ruta",
            ""
        )

        recuperable = convertir_numero_remediacion_kcd(
            fila.get(
                "recuperable_mb",
                0
            )
        )

        if (
            clasificacion == "POSIBLE_LIMPIEZA"
            and "CHROME" in tipo
        ):

            candidatas.append(
                crear_candidata_remediacion_kcd(
                    "BLOQUE_17_CHROME",
                    f"Limpiar cache de Chrome autorizada: {ruta}",
                    recuperable
                )
            )

    return candidatas


def generar_candidatas_remediacion_kcd():

    candidatas = []

    candidatas.append(
        crear_candidata_remediacion_kcd(
            "KCD_BASE",
            "Limpiar temporales KCD.",
            0
        )
    )

    candidatas.extend(
        leer_candidatas_bloque10_kcd()
    )

    candidatas.extend(
        leer_candidatas_bloque14_kcd()
    )

    candidatas.extend(
        leer_candidatas_bloque17_kcd()
    )

    base_chrome = obtener_chrome_user_data_kcd()

    if os.path.exists(
        base_chrome
    ):

        candidatas.append(
            crear_candidata_remediacion_kcd(
                "KCD_CHROME",
                "Limpiar cache de Chrome autorizada.",
                0
            )
        )

    depuradas = []
    vistas = set()

    for candidata in candidatas:

        clave = (
            candidata.get(
                "origen",
                ""
            ),
            candidata.get(
                "accion",
                ""
            )
        )

        if clave in vistas:

            continue

        vistas.add(
            clave
        )

        depuradas.append(
            candidata
        )

    return depuradas


def mostrar_candidatas_remediacion_kcd(
    candidatas
):

    print(
        "\n[KCD REMEDIACION] Acciones candidatas:"
    )

    if not candidatas:

        print(
            "No hay acciones candidatas."
        )

        return

    for numero, candidata in enumerate(
        candidatas,
        start=1
    ):

        print(
            f"\n{numero}. {candidata['accion']}"
        )

        print(
            f"   Origen: {candidata['origen']}"
        )

        print(
            f"   Clasificacion: {candidata['clasificacion']}"
        )

        print(
            f"   Impacto estimado: {candidata['impacto_estimado_gb']} GB"
        )


def solicitar_autorizacion_kcd(
    candidata
):

    if candidata.get(
        "clasificacion",
        ""
    ) in [
        "NO_RECOMENDADA",
        "SOLO_MANUAL"
    ]:

        print(
            f"\n[KCD REMEDIACION] No ejecutable automaticamente: {candidata['accion']}"
        )

        return "NO"

    print(
        "\n[KCD AUTORIZACION]"
    )

    print(
        f"Accion: {candidata['accion']}"
    )

    print(
        f"Clasificacion: {candidata['clasificacion']}"
    )

    print(
        "Escriba SI para autorizar o NO para omitir."
    )

    respuesta = input(
        "Autorizacion: "
    ).strip().upper()

    if respuesta == "SI":

        return "SI"

    return "NO"


def borrar_contenido_directorio_seguro_kcd(
    ruta
):

    liberado_bytes = 0
    eliminados = 0
    errores = 0

    if not os.path.exists(
        ruta
    ):

        return {
            "liberado_mb": 0,
            "eliminados": 0,
            "errores": 0,
            "resultado": "RUTA_NO_EXISTE"
        }

    for raiz, carpetas, archivos in os.walk(
        ruta,
        topdown=False
    ):

        for archivo in archivos:

            ruta_archivo = os.path.join(
                raiz,
                archivo
            )

            try:

                tamano = os.path.getsize(
                    ruta_archivo
                )

                os.remove(
                    ruta_archivo
                )

                liberado_bytes += tamano
                eliminados += 1

            except Exception:

                errores += 1

        for carpeta in carpetas:

            ruta_carpeta = os.path.join(
                raiz,
                carpeta
            )

            try:

                if not os.listdir(
                    ruta_carpeta
                ):

                    os.rmdir(
                        ruta_carpeta
                    )

            except Exception:

                errores += 1

    return {
        "liberado_mb": convertir_bytes_a_mb_kcd(
            liberado_bytes
        ),
        "eliminados": eliminados,
        "errores": errores,
        "resultado": "EJECUTADO"
    }


def limpiar_temporales_kcd_autorizado():

    carpeta_temp = tempfile.gettempdir()

    liberado_bytes = 0
    eliminados = 0
    errores = 0

    try:

        elementos = os.listdir(
            carpeta_temp
        )

    except Exception:

        elementos = []

    for elemento in elementos:

        nombre = elemento.lower()

        if (
            not nombre.startswith(
                "kcd"
            )
            and "kcd" not in nombre
        ):

            continue

        ruta = os.path.join(
            carpeta_temp,
            elemento
        )

        try:

            if os.path.isfile(
                ruta
            ):

                tamano = os.path.getsize(
                    ruta
                )

                os.remove(
                    ruta
                )

                liberado_bytes += tamano
                eliminados += 1

            elif os.path.isdir(
                ruta
            ):

                resultado = borrar_contenido_directorio_seguro_kcd(
                    ruta
                )

                liberado_bytes += resultado.get(
                    "liberado_mb",
                    0
                ) * 1024 * 1024

                try:

                    if not os.listdir(
                        ruta
                    ):

                        os.rmdir(
                            ruta
                        )

                except Exception:

                    pass

                eliminados += resultado.get(
                    "eliminados",
                    0
                )
                errores += resultado.get(
                    "errores",
                    0
                )

        except Exception:

            errores += 1

    return {
        "liberado_mb": convertir_bytes_a_mb_kcd(
            liberado_bytes
        ),
        "eliminados": eliminados,
        "errores": errores,
        "resultado": "EJECUTADO"
    }


def obtener_rutas_cache_chrome_autorizadas_kcd():

    base_chrome = obtener_chrome_user_data_kcd()

    rutas = []

    if not os.path.exists(
        base_chrome
    ):

        return rutas

    try:

        perfiles = os.listdir(
            base_chrome
        )

    except Exception:

        return rutas

    for perfil in perfiles:

        ruta_perfil = os.path.join(
            base_chrome,
            perfil
        )

        if not os.path.isdir(
            ruta_perfil
        ):

            continue

        nombre = perfil.lower()

        if not (
            nombre == "default"
            or nombre.startswith(
                "profile"
            )
            or nombre == "guest profile"
        ):

            continue

        posibles = [
            os.path.join(
                ruta_perfil,
                "Cache"
            ),
            os.path.join(
                ruta_perfil,
                "Code Cache"
            ),
            os.path.join(
                ruta_perfil,
                "GPUCache"
            ),
            os.path.join(
                ruta_perfil,
                "Service Worker",
                "CacheStorage"
            )
        ]

        for ruta in posibles:

            if (
                os.path.exists(
                    ruta
                )
                and ruta_segura_cache_chrome_kcd(
                    ruta
                )
            ):

                rutas.append(
                    ruta
                )

    return rutas


def limpiar_cache_chrome_autorizada_kcd(
    accion
):

    rutas = []

    if ":" in accion:

        posible_ruta = accion.split(
            ":",
            1
        )[1].strip()

        if (
            os.path.exists(
                posible_ruta
            )
            and ruta_segura_cache_chrome_kcd(
                posible_ruta
            )
        ):

            rutas.append(
                posible_ruta
            )

    if not rutas:

        rutas = obtener_rutas_cache_chrome_autorizadas_kcd()

    liberado_mb = 0
    eliminados = 0
    errores = 0

    for ruta in rutas:

        if not ruta_segura_cache_chrome_kcd(
            ruta
        ):

            continue

        resultado = borrar_contenido_directorio_seguro_kcd(
            ruta
        )

        liberado_mb += resultado.get(
            "liberado_mb",
            0
        )

        eliminados += resultado.get(
            "eliminados",
            0
        )

        errores += resultado.get(
            "errores",
            0
        )

    return {
        "liberado_mb": round(
            liberado_mb,
            2
        ),
        "eliminados": eliminados,
        "errores": errores,
        "resultado": "EJECUTADO"
    }


def ejecutar_accion_remediacion_kcd(
    candidata
):

    accion = candidata.get(
        "accion",
        ""
    ).lower()

    if (
        "temporales kcd" in accion
        or "limpiar temporales" in accion
    ):

        return limpiar_temporales_kcd_autorizado()

    if (
        "cache de chrome" in accion
        or "caché de chrome" in accion
        or "chrome autorizada" in accion
    ):

        return limpiar_cache_chrome_autorizada_kcd(
            candidata.get(
                "accion",
                ""
            )
        )

    return {
        "liberado_mb": 0,
        "eliminados": 0,
        "errores": 0,
        "resultado": "SOLO_REGISTRO_MANUAL"
    }


def registrar_remediacion_autorizada_kcd(
    candidata,
    autorizacion,
    resultado,
    antes,
    despues
):

    nombre_archivo = "remediacion_autorizada_kcd.csv"

    existe_archivo = os.path.exists(
        nombre_archivo
    )

    encabezados = [
        "fecha",
        "origen",
        "accion",
        "clasificacion",
        "autorizacion",
        "ejecutada",
        "resultado",
        "liberado_mb",
        "eliminados",
        "errores",
        "antes_cpu",
        "antes_ram",
        "antes_disco",
        "antes_espacio_libre",
        "antes_ivk",
        "despues_cpu",
        "despues_ram",
        "despues_disco",
        "despues_espacio_libre",
        "despues_ivk"
    ]

    ejecutada = "SI" if autorizacion == "SI" else "NO"

    fila = [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        candidata.get(
            "origen",
            ""
        ),
        candidata.get(
            "accion",
            ""
        ),
        candidata.get(
            "clasificacion",
            ""
        ),
        autorizacion,
        ejecutada,
        resultado.get(
            "resultado",
            ""
        ),
        resultado.get(
            "liberado_mb",
            0
        ),
        resultado.get(
            "eliminados",
            0
        ),
        resultado.get(
            "errores",
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
            "ivk",
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


def ejecutar_remediacion_autorizada_kcd():

    print(
        "\n[KCD BLOQUE 18] REMEDIACION INTELIGENTE AUTORIZADA"
    )

    print(
        "Modo seguro: no ejecuta nada sin autorizacion explicita."
    )

    print(
        "No borra perfiles, cookies, contrasenas, documentos, descargas ni AppData completo."
    )

    candidatas = generar_candidatas_remediacion_kcd()

    mostrar_candidatas_remediacion_kcd(
        candidatas
    )

    if not candidatas:

        return {
            "ejecutadas": 0,
            "omitidas": 0,
            "resultados": []
        }

    antes = medir_estado_remediacion_kcd(
        "ANTES"
    )

    resultados = []
    ejecutadas = 0
    omitidas = 0

    for candidata in candidatas:

        autorizacion = solicitar_autorizacion_kcd(
            candidata
        )

        if autorizacion != "SI":

            resultado = {
                "liberado_mb": 0,
                "eliminados": 0,
                "errores": 0,
                "resultado": "NO_AUTORIZADA"
            }

            despues_parcial = medir_estado_remediacion_kcd(
                "DESPUES"
            )

            registrar_remediacion_autorizada_kcd(
                candidata,
                autorizacion,
                resultado,
                antes,
                despues_parcial
            )

            omitidas += 1

            continue

        resultado = ejecutar_accion_remediacion_kcd(
            candidata
        )

        despues_parcial = medir_estado_remediacion_kcd(
            "DESPUES"
        )

        registrar_remediacion_autorizada_kcd(
            candidata,
            autorizacion,
            resultado,
            antes,
            despues_parcial
        )

        try:

            registrar_accion_kcd(
                "REMEDIACION_AUTORIZADA",
                resultado.get(
                    "resultado",
                    ""
                ),
                candidata.get(
                    "accion",
                    ""
                )
            )

        except Exception:

            pass

        resultados.append({
            "candidata": candidata,
            "resultado": resultado
        })

        ejecutadas += 1

    print(
        "\n[KCD REMEDIACION] Ejecutadas:"
    )

    print(
        ejecutadas
    )

    print(
        "[KCD REMEDIACION] Omitidas:"
    )

    print(
        omitidas
    )

    validacion = None

    try:

        validacion = validar_resultados_kcd(
            antes,
            "REMEDIACION_AUTORIZADA_KCD"
        )

    except Exception as error:

        print(
            f"\n[KCD REMEDIACION] No se pudo ejecutar validacion Bloque 11: {error}"
        )

    return {
        "ejecutadas": ejecutadas,
        "omitidas": omitidas,
        "resultados": resultados,
        "validacion": validacion
    }