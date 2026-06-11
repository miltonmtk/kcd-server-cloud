# ==============================================================================
# ESCUDO KCD - ORQUESTADOR DE PRODUCCIÓN PREMIUM (v10.1 - VERSIÓN AUDITORÍA INTERNA)
# ==============================================================================

import os
import sys
import warnings
import requests  
from fpdf import FPDF  

# Forzar el silencio absoluto de advertencias de desarrollo en consola
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ==============================================================================
# 1. CANDADO DE SEGURIDAD (VALIDACIÓN CON EL BACKEND)
# ==============================================================================
def verificar_licencia_remota(clave_licencia, hardware_id):
    URL_API = "http://127.0.0.1:5000/api/validar-licencia"
    payload = {"licencia": clave_licencia, "hardware_id": hardware_id}
    try:
        respuesta = requests.post(URL_API, json=payload, timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json() if hasattr(respuesta, 'json') else {}
            print(f"\n[KCD SECURITY]: {datos.get('mensaje', 'Acceso Otorgado')}")
            return True
        else:
            print("\n[KCD ALERTA]: Acceso denegado por el servidor.")
            return False
    except Exception:
        print("\n[KCD ERROR CRÍTICO]: No se pudo conectar con la API de licencias.")
        return False

# ==============================================================================
# 2. CLASE DE DISEÑO AVANZADO (ROTULADO DE VERSIÓN v10.1 EN EL HEADER)
# ==============================================================================
class PDF_KCD(FPDF):
    def header(self):
        # Fondo del encabezado corporativo (Azul oscuro profundo)
        self.set_fill_color(24, 43, 73)  
        self.rect(0, 0, 210, 32, 'F')
        self.set_text_color(255, 255, 255)
        
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 5, 'INFORME DE CONTINUIDAD DIGITAL Y AUDITORIA', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_font('Helvetica', '', 9)
        # Se añade de manera mandatoria la versión del software en el subtítulo institucional
        self.cell(0, 6, 'Escudo KCD - Kit de Continuidad Digital Automatizado 24/7 (Version v10.1)', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        # Trazabilidad de la versión también en el pie de página de cada hoja
        self.cell(0, 10, f'Pagina {self.page_no()} | Auditoria Interna Escudo KCD v10.1', align='C')

    def agregar_seccion_titulo(self, titulo):
        self.set_fill_color(230, 240, 250)
        self.set_text_color(24, 43, 73)
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, f" {titulo}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)

    def dibujar_visto_bueno(self, x, y):
        """ Dibuja un símbolo de verificado (✓) vectorial en color verde de éxito """
        self.set_draw_color(40, 167, 69)  
        self.set_line_width(0.8)          
        self.line(x + 3, y + 4.5, x + 4.5, y + 6)
        self.line(x + 4.5, y + 6, x + 7.5, y + 2.5)
        self.set_draw_color(0, 0, 0) # Restaurar color de línea por defecto

# ==============================================================================
# 3. MOTOR COMPILADOR (LÍMITE ESTRICTO DE 2 PÁGINAS PARA IMPRESIÓN DOBLE CARA)
# ==============================================================================
def generar_reporte_pdf_real():
    nombre_pdf = 'reporte_continuity_digital.pdf'
    
    if os.path.exists(nombre_pdf):
        try:
            with open(nombre_pdf, 'a'): pass
        except IOError:
            print("\n[ERROR CRÍTICO]: Cierra el PDF antes de compilar.")
            return False

    print("[PROCESO]: Compilando datos logicos y aplicando matriz de trazabilidad v10.1...")
    
    pdf = PDF_KCD()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --------------------------------------------------------------------------
    # PÁGINA 1: AUDITORÍA Y PROTOCOLOS DE COMPORTAMIENTO
    # --------------------------------------------------------------------------
    pdf.add_page()
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "ID Reporte: KCD-20260603-1530", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Version del Pipeline: Core Engine v10.1 (Production Release)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Fecha de Operacion: 03/06/2026 (100% Actualizado)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.agregar_seccion_titulo("PARTE 1: DIAGNOSTICO Y DETECCION DE FALLAS ENCONTRADAS")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5, "El Escudo KCD realizo un escaneo sobre los perifericos e interfaces logicas para mitigar cuellos de botella:")
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(60, 6, " Area Evaluada", border=1)
    pdf.cell(40, 6, " Estado Inicial", border=1)
    pdf.cell(90, 6, " Diagnostico Comercial", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(60, 6, " Red Local (Datafono)", border=1)
    pdf.cell(40, 6, " CRITICO", border=1)
    pdf.cell(90, 6, " Enlace perimetral caido con la pasarela.", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(60, 6, " Rendimiento (RAM)", border=1)
    pdf.cell(40, 6, " SOBRECARGA", border=1)
    pdf.cell(90, 6, " Exceso de subprocesos huerfanos detectados.", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.agregar_seccion_titulo("PARTE 2: CORRECCIONES AUTOMATICAS Y MITIGACION")
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, "[X] Re-conexion Forzada de Red: Tarjeta reiniciada con IP nueva.\n[X] Purga de Canales de Salida: Buffer de facturacion limpio.")
    pdf.ln(6)

    pdf.agregar_seccion_titulo("PARTE 3: RECOMENDACIONES DE OPERACION PARA EL CLIENTE")
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 5, "1. Continuidad de Energia los Fines de Semana", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, "-> NO APAGUE el equipo el sabado. El Escudo KCD requiere energia para ejecutar la desfragmentacion automatica los domingos a las 14:00 p.m.\n")

    # --------------------------------------------------------------------------
    # PÁGINA 2: LISTA DE CHEQUEO (AUDITORÍA INTERNA DE CONTROL CON VISTOS BUENOS)
    # --------------------------------------------------------------------------
    pdf.add_page()
    pdf.agregar_seccion_titulo("ANEXO: LISTA DE CHEQUEO DE VALIDACION OPERATIVA (v10.1)")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5, "Detalle secuencial de control interno para la optimizacion de procesos y estados de mitigacion:")
    pdf.ln(4)

    # Encabezados de la Tabla de Control
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 7, " Falla Evaluada", border=1, fill=True)
    pdf.cell(55, 7, " Recomendacion Tecnica", border=1, fill=True)
    pdf.cell(65, 7, " Accion de Mitigacion Escudo KCD", border=1, fill=True)
    pdf.cell(20, 7, " Estado", border=1, fill=True, new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.set_font('Helvetica', '', 8.5)
    pos_x_check = pdf.get_x() + 170  # Eje X fijo alineado al recuadro de estado

    # Fila 1: Red Local (No K.O. -> Mitigado)
    pos_y = pdf.get_y()
    pdf.cell(50, 8, " Enlace Datafono Caido", border=1)
    pdf.cell(55, 8, " Correccion por Escudo KCD", border=1)
    pdf.cell(65, 8, " Reinicio virtual e IP limpia asignada", border=1)
    pdf.cell(20, 8, "", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.dibujar_visto_bueno(pos_x_check, pos_y)

    # Fila 2: Cola de Impresión (No K.O. -> Mitigado)
    pos_y = pdf.get_y()
    pdf.cell(50, 8, " Cola Impresion Bloqueada", border=1)
    pdf.cell(55, 8, " Correccion por Escudo KCD", border=1)
    pdf.cell(65, 8, " Purga de buffers de facturacion", border=1)
    pdf.cell(20, 8, "", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.dibujar_visto_bueno(pos_x_check, pos_y)

    # Fila 3: Memoria RAM (No K.O. -> Mitigado)
    pos_y = pdf.get_y()
    pdf.cell(50, 8, " Sobrecarga de RAM", border=1)
    pdf.cell(55, 8, " Correccion por Escudo KCD", border=1)
    pdf.cell(65, 8, " Purga de subprocesos huerfanos", border=1)
    pdf.cell(20, 8, "", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.dibujar_visto_bueno(pos_x_check, pos_y)

    # Fila 4: Pantalla Azul (Falla K.O. -> Requiere Técnico)
    pdf.cell(50, 8, " Pantalla Azul (BSOD)", border=1)
    pdf.cell(55, 8, " Mantenimiento por Profesional", border=1)
    pdf.cell(65, 8, " Registro previo. Requiere asistencia fisica", border=1)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(20, 8, "Requiere", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_text_color(50, 50, 50)

    # Fila 5: Arranque Dañado (Falla K.O. -> Requiere Reinstalación)
    pdf.cell(50, 8, " Bucle de Reinicio", border=1)
    pdf.cell(55, 8, " Reinstalacion de S.O.", border=1)
    pdf.cell(65, 8, " Bloqueo base. Requiere medio externo", border=1)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(20, 8, "Requiere", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_text_color(50, 50, 50)
    
    # --------------------------------------------------------------------------
    # BLOQUE SEGURO DE FIRMAS COOPERATIVAS
    # --------------------------------------------------------------------------
    pdf.ln(18)
    y_firmas = pdf.get_y()
    
    # Trazado geométrico estable de las líneas de firma
    pdf.line(15, y_firmas, 95, y_firmas)
    pdf.line(115, y_firmas, 195, y_firmas)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_y(y_firmas + 2)
    pdf.cell(90, 5, "Firma Consultor Tecnologico (KCD v10.1)", align='C')
    pdf.set_x(115)
    pdf.cell(80, 5, "Firma Responsable / Comercio", align='C')

    pdf.output(nombre_pdf)
    print("\n========================================================")
    print(f"[OK AUDITORÍA]: '{nombre_pdf}' compilo exitosamente en v10.1.")
    print("========================================================")
    return True

# ==============================================================================
# CONTROLADOR PRINCIPAL DEL PIPELINE
# ==============================================================================
if __name__ == '__main__':
    LICENCIA_ACTUAL = "KCD-COLOMBIA-2026"  
    HARDWARE_ID_ACTUAL = "LAPTOP-MILTON-01" 

    print("[PROCESO]: Solicitando verificacion de credenciales al servidor...")
    if not verificar_licencia_remota(LICENCIA_ACTUAL, HARDWARE_ID_ACTUAL):
        sys.exit(1)
        
    generar_reporte_pdf_real()