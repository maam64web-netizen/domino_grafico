# ----------------- #
# - Importaciones - #
# ----------------- #
#
import os
import string
from datetime import date
import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
from ctypes import windll
try:
    import winreg
except ImportError:
    winreg = None
#
import holidays
# Importación explícita para Nuitka
try:
    import holidays.countries
    import holidays.countries.spain
except ImportError:
    pass  # En caso de versiones antiguas de holidays
#
#import pygame as py
#
# ------------------------ #
# - Constantes de la App - #
# ------------------------ #
#
TITULO = "Domino"
VERSION = "1.0"
AUTOR = "Miguel Ángel Arellano Medrano"
ANNO = "2026"
EMAIL = "maam64@outlook.es"
TIEMPO_ACERCA_DE = 10000
#
ANCHO = 1400
ALTO = 900
#
TAPETE = "#0a6b2f"
#
# ------------------------------------------------ #
# - Corregir las '\' en la ruta por '/' para vsc - #
# ------------------------------------------------ #
#
def formatRuta(ruta):
    clean = ""
    for caracter in ruta:
        if caracter == '\\':
            clean = clean + '/'
        else:
            clean = clean + caracter
    return clean
#
# ---------------------------------------------------- #
# - Corregir las '/' en la ruta por '\' para Windows - #
# ---------------------------------------------------- #
#
def formatRutaWindows(ruta):
    clean = ""
    for caracter in ruta:
        if caracter == '/':
            clean = clean + '\\'
        else:
            clean = clean + caracter
    return clean
#
# ---------------------------------------- #
# - Ruta raiz                            - #
# -                                      - #
# - Ruta archivos en programa ejecutable - #
# ---------------------------------------- #
#
RUTA = os.getcwd()    # Obtiene el directorio actual
RUTA_RAIZ = formatRuta(RUTA)
RUTA_RAIZ += "/"
RUTA_IMAGENES = RUTA_RAIZ + "imagenes/"
RUTA_SONIDOS = RUTA_RAIZ + "sonidos/"
RUTA_TXT = RUTA_RAIZ + "txt/"
ICONO = RUTA_IMAGENES + "icono.ico"
ICONO_NAVEGADOR = RUTA_IMAGENES + "carpeta.ico"
#
# ------------------------------------------------------------------ #
# - Centra una ventana en la pantalla o dentro de su ventana padre - #
# ------------------------------------------------------------------ #
#
def centrar_ventana(ventana,ancho,alto):
    """
    Parámetros:
    -----------
    ventana : tk.Tk o tk.Toplevel
        La ventana que se desea centrar
    ancho : int
        Ancho deseado de la ventana en píxeles
    alto : int
        Alto deseado de la ventana en píxeles
    
    Ejemplo:
    --------
    >>> root = tk.Tk()
    >>> centrar_ventana(root,800,600)
    """
    # Verificar si es una ventana Toplevel con padre
    if isinstance(ventana,tk.Toplevel) and ventana.master:
        try:
            # Actualizar ventanas para obtener dimensiones correctas
            ventana.master.update_idletasks()
            ventana.update_idletasks()
#
            # Obtener dimensiones y posición de la ventana padre
            padre_ancho = ventana.master.winfo_width()
            padre_alto = ventana.master.winfo_height()
            padre_x = ventana.master.winfo_x()
            padre_y = ventana.master.winfo_y()
#
            # Calcular posición centrada respecto a la ventana padre
            x = padre_x + (padre_ancho - ancho) // 2
            y = padre_y + (padre_alto - alto) // 2
        except:
            # Si hay error, centrar en pantalla
            pantalla_ancho = ventana.winfo_screenwidth()
            pantalla_alto = ventana.winfo_screenheight()
            x = (pantalla_ancho - ancho) // 2
            y = (pantalla_alto - alto) // 2
    else:
        # Es una ventana principal (tk.Tk) o no tiene padre, centrar en pantalla
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
#
    # Asegurar que la ventana no quede fuera de los límites de la pantalla
    x = max(0,x)
    y = max(0,y)
#
    # Establecer la geometría de la ventana
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
#
# ---------------------------------------------------- #
# - Mostrar un mensaje en una ventana modal centrada - #
# ---------------------------------------------------- #
#
def mostrar_mensaje(parent,titulo,mensaje,tipo="info",ancho=400,alto=200,auto_cerrar=0):
    """
    Args:
        parent: Ventana padre
        titulo: Título de la ventana
        mensaje: Mensaje a mostrar
        tipo: Tipo de mensaje ('info','error','aviso','pregunta')
        ancho: Ancho de la ventana
        alto: Alto de la ventana
        auto_cerrar: Segundos para cerrar automáticamente (0 = no cerrar automáticamente)
#
    Returns:
        True si el usuario acepta (para tipo 'pregunta'), None en otros casos
    """
    ventana = tk.Toplevel(parent)
    ventana.withdraw()
    ventana.title(titulo)
    ventana.geometry(f"{ancho}x{alto}")
    ventana.resizable(False,False)
    try:
        ventana.iconbitmap(RUTA_IMAGENES + "icono.ico")
    except:
        pass  # Si no existe el icono, continuar sin él
#
    frame = ttk.Frame(ventana,padding="20")
    frame.pack(fill=tk.BOTH,expand=True)
#
    # Icono según el tipo
    iconos = {
        'info': 'ℹ️',
        'error': '❌',
        'aviso': '⚠️',
        'pregunta': '❓'
    }
    icono = iconos.get(tipo,'ℹ️')
#
    # Título con icono
    ttk.Label(
        frame,
        text=f"{icono} {titulo}",
        font=('Segoe UI',12,'bold')
    ).pack(pady=(0,20))
#
    # Mensaje
    label_mensaje = ttk.Label(
        frame,
        text=mensaje,
        font=('Segoe UI',9),
        wraplength=ancho-60,
        justify=tk.LEFT
    )
    label_mensaje.pack(pady=10)
#
    # Variable para almacenar la respuesta y el timer
    respuesta = [None]
    timer_id = [None]
#
    def on_si():
        if timer_id[0]:
            ventana.after_cancel(timer_id[0])
        respuesta[0] = True
        ventana.destroy()
#
    def on_no():
        if timer_id[0]:
            ventana.after_cancel(timer_id[0])
        respuesta[0] = False
        ventana.destroy()
#
    def on_aceptar():
        if timer_id[0]:
            ventana.after_cancel(timer_id[0])
        ventana.destroy()
#
    def auto_cerrar_ventana():
        ventana.destroy()
#
    # Botones según el tipo
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=(20,0))
#
    if tipo == 'pregunta':
        ttk.Button(
            btn_frame,
            text="Sí",
            command=on_si,
            width=10
        ).pack(side=tk.LEFT,padx=5)
        ttk.Button(
            btn_frame,
            text="No",
            command=on_no,
            width=10
        ).pack(side=tk.LEFT,padx=5)
    else:
        ttk.Button(
            btn_frame,
            text="Aceptar",
            command=on_aceptar,
            width=15
        ).pack()
#
    # Centrar ventana respecto a la ventana padre
    ventana.update_idletasks()
    if parent.winfo_viewable():
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (ventana.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (ventana.winfo_height() // 2)
        ventana.geometry(f'+{x}+{y}')
#
    # Mostrar ventana ya centrada
    ventana.deiconify()
#
    # Programar cierre automático si se especificó (mayor que 0)
    if auto_cerrar > 0:
        timer_id[0] = ventana.after(int(auto_cerrar * 1000),auto_cerrar_ventana)
#
    # Hacer modal
    ventana.transient(parent)
    ventana.grab_set()
    ventana.wait_window()
#
    return respuesta[0]
#
# ---------------------------------------------------------------------------- #
# - Devuelve el día de la semana en texto de una fecha en formato YYYY-MM-DD - #
# ---------------------------------------------------------------------------- #
#
def obtener_dia_semana(fecha_str):
    """
    Args:
        fecha_str (str): Fecha en formato YYYY-MM-DD
        
    Returns:
        str: Día de la semana en español
    """
    dia_semana = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
#
    # Convertir la cadena a objeto date
    fecha_obj = date.fromisoformat(fecha_str)
    
    # Obtener el día de la semana (0=Lunes, 6=Domingo)
    return dia_semana[fecha_obj.weekday()]
#
# ---------------------------------------- #
# - Comprobar si un año es bisiesto o no - #
# ---------------------------------------- #
#
def bisiesto(texto):
    '''
    Parametros: Año en formato YYYY

    Retorna:
            None: Si el año es anterior al calendario gregoriano (1582)
            True: Si el año es bisiesto
            False: Si no es bisiesto
    '''
#
    anio = int(texto)
#    
    if anio < 1582:
        return None
#
    if (not anio % 4 and (anio % 100 or not anio % 400)):
        return True
#
    return False
#
# ------------------------------------------------------- #
# - Calcular los días laborables de un año-mes concreto - #
# ------------------------------------------------------- #
#
def laborables(texto,comunidad=None,excluir_festivos=True):
    '''
    Parametros:
        texto: Año y Mes en formato YYYYMM
        comunidad: Código de comunidad autónoma (opcional). Ejemplos:
                   'AN' = Andalucía, 'AR' = Aragón, 'AS' = Asturias,
                   'CB' = Cantabria, 'CE' = Ceuta, 'CL' = Castilla y León,
                   'CM' = Castilla-La Mancha, 'CN' = Canarias, 'CT' = Cataluña,
                   'EX' = Extremadura, 'GA' = Galicia, 'IB' = Islas Baleares,
                   'MC' = Murcia, 'MD' = Madrid, 'ML' = Melilla,
                   'NC' = Navarra, 'PV' = País Vasco, 'RI' = La Rioja,
                   'VC' = Comunidad Valenciana
                   Si es None, usa festivos nacionales de España
        excluir_festivos: Si True, excluye los festivos del conteo (por defecto True)
    
    Retorna:
            Número de días laborables (lunes a viernes, excluyendo festivos si se indica)
    '''
    # from datetime import date
    
#
    anio = int(texto[0:4])
    mes = int(texto[4:6])
#
    # Determinar el número de días del mes
    dias_meses = [0,31,28,31,30,31,30,31,31,30,31,30,31]
    num_dias = dias_meses[mes]
#
    # Ajustar febrero si es año bisiesto
    if mes == 2 and bisiesto(texto[0:4]):
        num_dias = 29
#
    # Obtener festivos de España (nacionales o por comunidad)
    if excluir_festivos:
        if comunidad:
            festivos_es = holidays.country_holidays('ES',subdiv=comunidad,years=anio)
        else:
            festivos_es = holidays.country_holidays('ES',years=anio)
#
    # Contar días laborables (lunes=0 a viernes=4)
    dias_lab = 0
    for dia in range(1, num_dias + 1):
        fecha = date(anio, mes, dia)
        # weekday() retorna 0=lunes, 1=martes, ..., 6=domingo
        if fecha.weekday() < 5:  # De lunes (0) a viernes (4)
            # Si excluir_festivos está activado, verificar que no sea festivo
            if excluir_festivos:
                if fecha not in festivos_es:
                    dias_lab += 1
            else:
                dias_lab += 1
#
    return dias_lab
#
# -------------------------------------------------------------------- #
# - Convertir Notación Anglosajona (. = decimal , = miles) a Europea - #
# -------------------------------------------------------------------- #
#
def formato_europeo(str_numero):
    return str_numero.replace(',','n').replace('.',',').replace('n','.')
#
# -------------------------------------------------------------------- #
# - Convertir Notación Europea (, = decimal . = miles) a Anglosajona - #
# -------------------------------------------------------------------- #
#
def formato_anglosajon(str_numero):
    return str_numero.replace('.','n').replace(',','.').replace('n',',')
#
# --------------------------------------------------------- #
# - Quitar puntuación de los miles y cambiar coma decimal - #
# - por punto (Viene de notación Europea)                 - #
# --------------------------------------------------------- #
#
def quitar_punto_miles(str_numero):
    return str_numero.replace('.','').replace(',','.')
#
# -------------------------------------------------------- #
# - Quitar puntuación de los miles y dejar punto decimal - #
# - Viene de notación Anglosajona)                       - #
# -------------------------------------------------------- #
#
def quitar_coma_miles(str_numero):
    return str_numero.replace(',','')
#
# ----------------------------------------------------------- #
# - Contar elementos (archivos) en una carpeta (directorio) - #
# ----------------------------------------------------------- #
#
def contar_elementos(directorio):
    return len(os.listdir(directorio))
#
# ------------------------------------------------------------------------------- #
# - Obtener los nombres de los elementos (archivos) de una carpeta (directorio) - #
# ------------------------------------------------------------------------------- #
#
def nombres_carpetas(directorio):
    return os.listdir(directorio)
#
# ------------------------------------------------- #
# - Convierte un número decimal a números romanos - #
# - Acepta números entre 1 y 3999                 - #
# ------------------------------------------------- #
#
def decimal_a_romano(numero):
    if not isinstance(numero,int):
        raise TypeError("El número debe ser un entero")
#
    if numero <= 0 or numero > 3999:
        raise ValueError("El número debe estar entre 1 y 3999")
#    
    # Valores y símbolos romanos
    valores = [1000,900,500,400,100,90,50,40,10,9,5,4,1]
    simbolos = ["M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"]
#
    resultado = ""
    i = 0
#
    # Construir el número romano
    while numero > 0:
        # Repetir el símbolo actual tantas veces como sea posible
        while numero >= valores[i]:
            resultado += simbolos[i]
            numero -= valores[i]
        i += 1
#
    return resultado
#
# ---------------------------------------- #
# - Convierte un número romano a decimal - #
# ---------------------------------------- #
#
def romano_a_decimal(romano):
    if not isinstance(romano,str):
        raise TypeError("El número romano debe ser una cadena de texto")
#
    # Validar que solo contenga caracteres romanos válidos
    caracteres_validos = "IVXLCDM"
    for char in romano.upper():
        if char not in caracteres_validos:
            raise ValueError(f"Carácter inválido '{char}' en el número romano")
#    
    # Valores de los símbolos romanos
    valores = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }
#    
    resultado = 0
    romano = romano.upper()
#    
    # Recorrer el número romano
    i = 0
    while i < len(romano):
        # Si es el último carácter o el valor actual es mayor o igual al siguiente
        if i == len(romano) - 1 or valores[romano[i]] >= valores[romano[i + 1]]:
            resultado += valores[romano[i]]
            i += 1
        else:
            # Si el valor actual es menor que el siguiente (notación sustractiva)
            resultado += valores[romano[i + 1]] - valores[romano[i]]
            i += 2
#    
    return resultado
#
# ----------------------- #
# - Favoritos a Binario - #
# ----------------------- #
#
def favs_a_binario(mun_decimal):
    """
    Convierte un número decimal a binario y almacena los dígitos en la lista favs_binario.
    
    Args:
        mun_decimal: Número decimal entre 0 y 67108863 a convertir (MAX_FAVS = 26 bits o favoritos)
        
    Returns:
        El número binario en forma de lista
    """
#
    # Numero máximo de favoritos (Viark Sat)
    MAX_FAVS = 26
#
    # Iniciar la lista favs_binario con ceros
    favs_binario = [0] * MAX_FAVS
#    
    # Convertir el número decimal a binario (sin el prefijo '0b')
    binario = bin(mun_decimal)[2:]
#
    # Rellenar con ceros a la izquierda si es necesario
    binario = binario.zfill(MAX_FAVS)
#
    # Almacenar cada dígito binario en la lista favs_binario
    # El bit menos significativo está en la posición 0
    for i in range(MAX_FAVS):
        favs_binario[25 - i] = int(binario[i])
#
    return favs_binario
#
# ----------------------- #
# - Binario a Favoritos - #
# ----------------------- #
#
def binario_a_favs(favs_binario):
    """
    Convierte la lista favs_binario con MAX_FAVS dígitos binarios a un número decimal.
    
    Args:
        favs_binario: Lista de MAX_FAVS dígitos binarios (0 o 1)
        
    Returns:
        El número decimal correspondiente
    """
#
    # Numero máximo de favoritos (Viark Sat)
    MAX_FAVS = 26
#
    # Verificar que la lista tenga MAX_FAVS elementos
    if len(favs_binario) != MAX_FAVS:
        raise ValueError(f"La lista favs_binario debe tener exactamente {MAX_FAVS} elementos")
#
    # Convertir de binario a decimal
    decimal = 0
    for i in range(MAX_FAVS):
        # Multiplicar cada dígito por la potencia de 2 correspondiente a su posición
        # Como el bit menos significativo está en la posición 0, usamos i como exponente
        decimal += favs_binario[i] * (2 ** i)
#
    return decimal
#
# --------------------------------------------------- #
# - Funcion encontrar_todas                         - #
# --------------------------------------------------- #
# - Devuelve una lista con todos los indices donde  - #
# - se ha encontrado la subcadena en la cadena      - #
# --------------------------------------------------- #
# - Parametros a pasar:                             - #
# - cadena es la cadena donde vamos a buscar la ... - #
# - subcadena a buscar en la cadena                 - #
# --------------------------------------------------- #
#
def encontrar_todas(cadena,subcadena):
	posiciones = []
	posicion = 0
#
	while posicion != -1:
		posicion = cadena.find(subcadena,posicion)
		if posicion != -1:
			posiciones.append(posicion)
			posicion += 1
#
	return posiciones
#
# ------------------------------------------------------ #
# - Funcion adyacentes                                 - #
# ------------------------------------------------------ #
# - Devuelve una lista de listas con las coordenadas X - #
# - e Y de las celdas adyacentes a una celda concreta  - #
# ------------------------------------------------------ #
# - Parametros a pasar:                                - #
# - filas y columnas son el tamaño de la matriz        - #
# - fila_origen y columna_origen es la celda a tratar  - #
# ------------------------------------------------------ #
#
def adyacentes(filas,columnas,fila_origen,columna_origen):
    if (not (fila_origen <= 0 and fila_origen >= (filas - 1)) and \
             columna_origen <= 0 and columna_origen >= (columnas - 1)):
        return None
#
    posiciones = []
    for i in range(-1,2):
        for j in range(-1,2):
            if (i != 0 or j != 0) and \
               (fila_origen + i) >= 0 and \
               (fila_origen + i) <= (filas - 1) and \
               (columna_origen + j) >= 0 and \
               (columna_origen + j) <= (columnas - 1):
                posiciones.append([fila_origen + i,columna_origen + j])
#
    return posiciones
#
# --------------------- #
# - Cargar una imagen - #
# --------------------- #
#
# def obtener_grafico(nombre_png,escala):
#     img = py.image.load(RUTA_IMAGENES + nombre_png)
#     image = escalar_imagen(img,escala)
#     return image
#
# ---------------------- #
# - Escalar una imagen - #
# ---------------------- #
#
# def escalar_imagen(imagen,escala):
#     w = imagen.get_width()
#     h = imagen.get_height()
#     nueva_imagen = py.transform.scale(imagen,(w*escala,h*escala))
#     return nueva_imagen
#
# ---------------------------------- #
# - Crear rectangulo de una imagen - #
# ---------------------------------- #
#
# def obtener_rect(image):
#     return image.get_rect()
#
# -------------------------------- #
# - Dibujar un texto en pantalla - #
# -------------------------------- #
#    
# def dibujar_texto(pantalla,texto,color,size,x,y):
#     font = py.font.SysFont("serif",size)
#     text_pantalla = font.render(texto,True,color)
#     text_rect = text_pantalla.get_rect()
#     text_rect.left = x
#     text_rect.top = y
#     pantalla.blit(text_pantalla,text_rect)
#
# ---------------------- #
# - navegador archivos - #
# ---------------------- #
#
# Función para obtener las unidades de disco disponibles en Windows
def obtener_unidades():
    """Obtener lista de unidades de disco disponibles
      (excluye ópticas y virtuales)"""
    unidades = []
    if os.name == 'nt':  # Windows
        # Obtener bitmask de unidades disponibles
        bitmask = windll.kernel32.GetLogicalDrives()
        # Verificar cada letra de unidad
        for letra in string.ascii_uppercase:
            if bitmask & 1:
                # Verificar el tipo de unidad
                ruta_unidad = f"{letra}:\\"
                tipo_unidad = windll.kernel32.GetDriveTypeW(ruta_unidad)
                # Tipos de unidad:
                # 0 = DRIVE_UNKNOWN (desconocido)
                # 1 = DRIVE_NO_ROOT_DIR (ruta inválida)
                # 2 = DRIVE_REMOVABLE (extraíble, ej: USB)
                # 3 = DRIVE_FIXED (disco fijo, ej: HDD/SSD)
                # 4 = DRIVE_REMOTE (unidad de red)
                # 5 = DRIVE_CDROM (unidad óptica CD/DVD)
                # 6 = DRIVE_RAMDISK (disco RAM virtual)
                # Solo incluir discos fijos (3) y removibles (2)
                if tipo_unidad in [2,3]:
                    unidades.append(letra)
            bitmask >>= 1
    else:
        # En Linux/Mac, usar punto de montaje raíz
        unidades = ['/']
    return unidades
#
# ------------------------------------------ #
# - Función para guardar la última carpeta - #
# - usada usando registro de Windows       - #
# ------------------------------------------ #
def _guardar_ultimo_directorio(ruta):
    """Guardar el último directorio usado en el registro de Windows"""
    if winreg and os.name == 'nt':
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU")
            winreg.SetValueEx(key,"NavegadorPython",0,winreg.REG_SZ,ruta)
            winreg.CloseKey(key)
        except:
            pass
#
# ----------------------------------------- #
# - Función para cargar la última carpeta - #
# - usada usando registro de Windows      - #
# ----------------------------------------- #
def _cargar_ultimo_directorio():
    """Cargar el último directorio usado desde el registro de Windows"""
    if winreg and os.name == 'nt':
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU")
            ruta,_ = winreg.QueryValueEx(key,"NavegadorPython")
            winreg.CloseKey(key)
            if ruta and os.path.exists(ruta):
                return ruta
        except:
            pass
    return None
#
# ------------------------------------------------------------- #
# - Clase para crear un navegador de archivos con 2 TreeViews - #
# ------------------------------------------------------------- #
class NavegadorArchivos:
    """
    Parámetros:
    - parent: ventana padre (tk.Tk o tk.Toplevel)
    - titulo: título de la ventana (default: "Navegador de Archivos")
    - ancho: ancho de la ventana (default: 1000)
    - alto: alto de la ventana (default: 600)
    - directorio_inicial: directorio donde iniciar (default: C:/ o /)
    - filtro_archivos: filtro para archivos, ej: "*.db" o None para todos (default: None)
    - ruta_imagenes: ruta a las imágenes para botones (default: None, usa texto)
    - icono: ruta al icono de la ventana (default: None)
    - monitorear_unidades: si True, comprueba cada segundo si hay nuevas unidades (default: True)
    
    Uso:
        navegador = NavegadorArchivos(root, filtro_archivos="*.db")
        resultado = navegador.obtener_seleccion()
        if resultado:
            print(f"Seleccionado: {resultado}")
    """
#
    def __init__(self,parent,titulo=None,ancho=1000,alto=600,
                 directorio_inicial=None,filtro_archivos=None,
                 ruta_imagenes=None,icono=None,
                 monitorear_unidades=True):
        self.parent = parent
        self.titulo_general = "Navegador de Archivos"
        self.ancho = ancho
        self.alto = alto
        self.filtro_archivos = filtro_archivos
        self.ruta_imagenes = ruta_imagenes
        self.seleccion = None
        self.cancelado = False
        self.monitorear_unidades = monitorear_unidades
        self.unidades_actuales = obtener_unidades()  # Lista de unidades actual
        self.monitor_id = None  # ID del after para poder cancelarlo
        self.carpeta_preview = None  # Carpeta en vista previa (para toggle)
#
        # Directorio inicial
        if directorio_inicial and os.path.exists(directorio_inicial):
            self.directorio_actual = formatRuta(directorio_inicial)
        else:
            # Intentar usar el último directorio visitado
            ultimo_dir = _cargar_ultimo_directorio()
            if ultimo_dir and os.path.exists(ultimo_dir):
                self.directorio_actual = formatRuta(ultimo_dir)
            else:
                # Usar primera unidad disponible o raíz
                unidades = obtener_unidades()
                if unidades:
                    self.directorio_actual = f"{unidades[0]}:/" if os.name == 'nt' else "/"
                else:
                    self.directorio_actual = "C:/" if os.name == 'nt' else "/"
#
        # Crear ventana
        self.ventana = tk.Toplevel(parent)
        self.ventana.title(self.titulo_general)
        self.ventana.geometry(f"{ancho}x{alto}")
        self.ventana.resizable(False,False)
        self.ventana.iconbitmap(ICONO_NAVEGADOR)
#
        self.ventana.transient(parent)
        self.ventana.grab_set()
#
        # Centrar ventana
        self.ventana.update_idletasks()
        centrar_ventana(self.ventana,ancho,alto)
#
        # Crear interfaz
        self.crear_interfaz(titulo)
#
        # Cargar contenido inicial
        self.cargar_contenido()
#
        # Protocolo de cierre
        self.ventana.protocol("WM_DELETE_WINDOW",self.cancelar)
#
        # Iniciar monitoreo de unidades si está habilitado
        if self.monitorear_unidades:
            self.iniciar_monitoreo_unidades()
#
    def crear_interfaz(self,titulo):
        """Crear la interfaz gráfica"""
        # Determinar título según filtro
        titulo_ventana = self.titulo_general + " - "
        if self.filtro_archivos:
            titulo_ventana += titulo + " (" + self.filtro_archivos + ")"
        elif not self.filtro_archivos and titulo:
            titulo_ventana += titulo
        else:
            titulo_ventana += "Seleccionar Carpeta"
#
        # Actualizar título de la ventana
        self.ventana.title(titulo_ventana)
#
        # Frame principal
        main_frame = tk.Frame(self.ventana,bg="#f5f5f5")
        main_frame.place(x=0,y=0,width=self.ancho,height=self.alto)
#
        # Barra de navegación superior
        nav_frame = tk.Frame(main_frame,bg="#ecf0f1",height=50)
        nav_frame.place(x=10,y=10,width=self.ancho-20,height=50)
#
        # Botón subir nivel (izquierda)
        x_pos_izq = 10
        if self.ruta_imagenes and os.path.exists(self.ruta_imagenes + "subir.png"):
            imagen_pil = Image.open(self.ruta_imagenes + "subir.png")
            imagen_resize = imagen_pil.resize((20,20))
            imagen_tk = ImageTk.PhotoImage(imagen_resize)
            btn_subir = tk.Button(nav_frame,text=" ↑ ",command=self.subir_nivel,
                                  bg="#0B7217",fg="white",font="Arial 9 bold", # 5dade2
                                  cursor="hand2",relief="flat")
            btn_subir.config(image=imagen_tk,compound=tk.LEFT)
            btn_subir.imagen = imagen_tk
        else:
            btn_subir = tk.Button(nav_frame,text="↑ Subir",command=self.subir_nivel,
                                  bg="#0B7217",fg="white",font="Arial 9 bold",
                                  cursor="hand2",relief="flat")
        btn_subir.place(x=x_pos_izq,y=10,width=60,height=30)
        x_pos_izq += 65
#
        # Frame para botones de unidades (dinámico, izquierda)
        self.frame_unidades = tk.Frame(nav_frame,bg="#ecf0f1")
        self.frame_unidades.place(x=x_pos_izq,y=10,width=300,height=30)
        self.actualizar_botones_unidades()
#
        # Label con ruta actual (alineado con TreeView de archivos, derecha)
        # Calcular posición: mitad de la ventana + 5px de separación
        x_pos_ruta = (self.ancho-20)//2+5
        ancho_ruta = self.ancho - x_pos_ruta - 20
        self.label_ruta = tk.Label(nav_frame,text=self.directorio_actual,
                                   bg="white",fg="#2980b9",font="Arial 10 bold",
                                   anchor="w",relief="solid",borderwidth=2)
        self.label_ruta.place(x=x_pos_ruta,y=8,width=ancho_ruta,height=34)
#
        # Frame para TreeViews
        tree_frame = tk.Frame(main_frame,bg="#f5f5f5")
        tree_frame.place(x=10,y=70,width=self.ancho-20,height=self.alto-150)
#
        # TreeView de carpetas (izquierda)
        frame_carpetas = tk.LabelFrame(tree_frame,text="📁 Carpetas",
                                       bg="#f5f5f5",fg="#2c3e50",font="Arial 10 bold")
        frame_carpetas.place(x=0,y=0,width=(self.ancho-30)//2,height=self.alto-150)
#
        scroll_carpetas_y = ttk.Scrollbar(frame_carpetas,orient=tk.VERTICAL)
        self.tree_carpetas = ttk.Treeview(frame_carpetas,columns=("Nombre",),
                                          show="headings",selectmode="browse",
                                          yscrollcommand=scroll_carpetas_y.set)
        scroll_carpetas_y.config(command=self.tree_carpetas.yview)
#
        self.tree_carpetas.heading("Nombre",text="Nombre")
        self.tree_carpetas.column("Nombre",width=400)
#
        self.tree_carpetas.pack(side=tk.LEFT,fill=tk.BOTH,expand=True,padx=5,pady=5)
        scroll_carpetas_y.pack(side=tk.RIGHT,fill=tk.Y)
#
        # Bind doble click en carpetas
        self.tree_carpetas.bind("<Double-Button-1>",self.navegar_carpeta)
        self.tree_carpetas.bind("<<TreeviewSelect>>",self.seleccionar_carpeta)
#
        # TreeView de archivos (derecha)
        frame_archivos = tk.LabelFrame(tree_frame,text="📄 Archivos",
                                       bg="#f5f5f5",fg="#2c3e50",font="Arial 10 bold")
        frame_archivos.place(x=(self.ancho-20)//2+5,y=0,
                             width=(self.ancho-30)//2,height=self.alto-150)
#
        scroll_archivos_y = ttk.Scrollbar(frame_archivos,orient=tk.VERTICAL)
        self.tree_archivos = ttk.Treeview(frame_archivos,columns=("Nombre","Tamano"),
                                          show="headings",selectmode="browse",
                                          yscrollcommand=scroll_archivos_y.set)
        scroll_archivos_y.config(command=self.tree_archivos.yview)
#
        self.tree_archivos.heading("Nombre",text="Nombre")
        self.tree_archivos.heading("Tamano",text="Tamaño")
        self.tree_archivos.column("Nombre",width=300)
        self.tree_archivos.column("Tamano",width=100)
#
        self.tree_archivos.pack(side=tk.LEFT,fill=tk.BOTH,expand=True,padx=5,pady=5)
        scroll_archivos_y.pack(side=tk.RIGHT,fill=tk.Y)
#
        # Bind selección y doble clic en archivos
        self.tree_archivos.bind("<<TreeviewSelect>>",self.seleccionar_archivo)
        self.tree_archivos.bind("<Double-Button-1>",self.navegar_desde_archivos)
#
        # Label de información (inicialmente vacío, se actualiza en cargar_contenido)
        self.label_info = tk.Label(main_frame,text="",
                                   bg="#f5f5f5",fg="#666666",font="Arial 9")
        self.label_info.place(x=10,y=self.alto-70,width=self.ancho-20,height=20)
#
        # Botones inferiores
        btn_ancho = 180
        btn_alto = 40
        espacio = (self.ancho - (btn_ancho * 2 + 20)) // 2
#
        # Botón Seleccionar
        btn_seleccionar = tk.Button(main_frame,text="✓ Seleccionar",command=self.aceptar,
                                    bg="#27ae60",fg="white",font="Arial 11 bold",
                                    cursor="hand2",relief="flat")
        btn_seleccionar.place(x=espacio,y=self.alto-45,width=btn_ancho,height=btn_alto)
#
        # Botón Cancelar
        btn_cancelar = tk.Button(main_frame,text="✗ Cancelar",command=self.cancelar,
                                 bg="#e74c3c",fg="white",font="Arial 11 bold",
                                 cursor="hand2",relief="flat")
        btn_cancelar.place(x=espacio+btn_ancho+20,y=self.alto-45,
                           width=btn_ancho,height=btn_alto)
#
    def formatear_tamaño(self,bytes):
        """Formatear tamaño de archivo en formato legible"""
        for unidad in ['B','KB','MB','GB','TB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unidad}"
            bytes /= 1024.0
        return f"{bytes:.1f} PB"
#
    def cargar_contenido(self):
        """Cargar carpetas y archivos del directorio actual"""
        # Limpiar TreeViews
        for item in self.tree_carpetas.get_children():
            self.tree_carpetas.delete(item)
        for item in self.tree_archivos.get_children():
            self.tree_archivos.delete(item)
#
        # Actualizar label de ruta
        ruta_mostrar = formatRutaWindows(self.directorio_actual) if os.name == 'nt' \
                                                                 else self.directorio_actual
        self.label_ruta.config(text=ruta_mostrar)
#
        # Actualizar UI inmediatamente
        self.ventana.update_idletasks()
#
        try:
            # Obtener elementos del directorio de forma más eficiente
            elementos = []
            try:
                elementos = os.listdir(self.directorio_actual)
            except PermissionError:
                self.label_info.config(text="⚠ Sin permisos para acceder a este directorio")
                return
            except Exception as e:
                self.label_info.config(text=f"⚠ Error: {str(e)}")
                return
#
            # Separar carpetas y archivos con límite
            carpetas = []
            archivos = []
            MAX_ITEMS = 1000  # Límite para evitar congelamiento
            contador = 0
#
            for elemento in elementos:
                if contador >= MAX_ITEMS:
                    self.label_info.config(text=f"⚠ Mostrando solo {MAX_ITEMS} elementos")
                    break
#
                ruta_completa = os.path.join(self.directorio_actual,elemento)
                try:
                    if os.path.isdir(ruta_completa):
                        carpetas.append((elemento,ruta_completa))
                        contador += 1
                    else:
                        # Aplicar filtro si existe
                        if self.filtro_archivos:
                            import fnmatch
                            if fnmatch.fnmatch(elemento.lower(),self.filtro_archivos.lower()):
                                archivos.append((elemento,ruta_completa))
                                contador += 1
                        else:
                            archivos.append((elemento,ruta_completa))
                            contador += 1
                except:
                    continue
#
            # Ordenar alfabéticamente
            carpetas.sort(key=lambda x: x[0].lower())
            archivos.sort(key=lambda x: x[0].lower())
#
            # Agregar carpetas al TreeView de carpetas (en lotes)
            BATCH_SIZE = 50
            for i in range(0, len(carpetas), BATCH_SIZE):
                batch = carpetas[i:i+BATCH_SIZE]
                for nombre,ruta_completa in batch:
                    ruta_mostrar = formatRutaWindows(ruta_completa) if os.name == 'nt' \
                                                                    else ruta_completa
                    self.tree_carpetas.insert("",tk.END,values=(f"📁 {nombre}",),
                                              tags=(ruta_completa,))
                # Actualizar UI cada 2 lotes
                if i % (BATCH_SIZE * 2) == 0:
                    self.ventana.update_idletasks()
#
            # Comportamiento del TreeView de archivos según el modo (en lotes)
            if self.filtro_archivos:
                # MODO SELECCIONAR ARCHIVO: Mostrar carpetas y archivos juntos
                # Primero las carpetas (en lotes)
                for i in range(0, len(carpetas), BATCH_SIZE):
                    batch = carpetas[i:i+BATCH_SIZE]
                    for nombre,ruta_completa in batch:
                        self.tree_archivos.insert("",tk.END,
                                                 values=(f"📁 {nombre}", "<DIR>"),
                                                 tags=(ruta_completa,"carpeta"))
                    if i % (BATCH_SIZE * 2) == 0:
                        self.ventana.update_idletasks()
#
                # Luego los archivos (en lotes)
                for i in range(0, len(archivos), BATCH_SIZE):
                    batch = archivos[i:i+BATCH_SIZE]
                    for nombre,ruta_completa in batch:
                        try:
                            tamaño = os.path.getsize(ruta_completa)
                            tamaño_formateado = self.formatear_tamaño(tamaño)
                        except:
                            tamaño_formateado = "N/A"
#
                        # Determinar icono según extensión
                        ext = os.path.splitext(nombre)[1].lower()
                        if ext in ['.db','.accdb']:
                            icono = "🗄️"
                        elif ext in ['.py','.pyw']:
                            icono = "🐍"
                        elif ext in ['.txt','.md','.log']:
                            icono = "📄"
                        elif ext in ['.jpg','.jpeg','.png','.gif','.bmp','.ico','psd']:
                            icono = "🖼️"
                        else:
                            icono = "📄"
#
                        self.tree_archivos.insert("",tk.END,
                                                  values=(f"{icono} {nombre}", tamaño_formateado),
                                                  tags=(ruta_completa,"archivo"))
                    if i % (BATCH_SIZE * 2) == 0:
                        self.ventana.update_idletasks()
            else:
                # MODO SELECCIONAR CARPETA: Mostrar carpetas y archivos del directorio actual
                # Primero las carpetas (en lotes)
                for i in range(0, len(carpetas), BATCH_SIZE):
                    batch = carpetas[i:i+BATCH_SIZE]
                    for nombre,ruta_completa in batch:
                        self.tree_archivos.insert("",tk.END,
                                                  values=(f"📁 {nombre}", "<DIR>"),
                                                  tags=(ruta_completa,"carpeta"))
                    if i % (BATCH_SIZE * 2) == 0:
                        self.ventana.update_idletasks()
#
                # Luego los archivos (en lotes)
                for i in range(0, len(archivos), BATCH_SIZE):
                    batch = archivos[i:i+BATCH_SIZE]
                    for nombre,ruta_completa in batch:
                        try:
                            tamaño = os.path.getsize(ruta_completa)
                            tamaño_formateado = self.formatear_tamaño(tamaño)
                        except:
                            tamaño_formateado = "N/A"
#
                        # Determinar icono según extensión
                        ext = os.path.splitext(nombre)[1].lower()
                        if ext in ['.db','.accdb']:
                            icono = "🗄️"
                        elif ext in ['.py','.pyw']:
                            icono = "🐍"
                        elif ext in ['.txt','.md','.log']:
                            icono = "📄"
                        elif ext in ['.jpg','.jpeg','.png','.gif','.bmp','.ico','psd']:
                            icono = "🖼️"
                        else:
                            icono = "📄"
#
                        self.tree_archivos.insert("",tk.END,
                                                  values=(f"{icono} {nombre}", tamaño_formateado),
                                                  tags=(ruta_completa,"archivo"))
                    if i % (BATCH_SIZE * 2) == 0:
                        self.ventana.update_idletasks()
#
            # Actualizar información
            if contador >= MAX_ITEMS:
                texto = f"⚠ Mostrando {len(carpetas)} carpetas y {len(archivos)} archivos (límite alcanzado)"
            else:
                texto = f"Carpetas: {len(carpetas)} | Archivos: {len(archivos)}"
            self.label_info.config(text=texto)
#
        except Exception as e:
            self.label_info.config(text=f"⚠ Error al cargar: {str(e)}")
#
    def navegar_carpeta(self,event):
        """Navegar a una carpeta al hacer doble clic"""
        seleccion = self.tree_carpetas.selection()
        if not seleccion:
            return
#
        item = seleccion[0]
        tags = self.tree_carpetas.item(item,"tags")
        if tags:
            ruta = tags[0]
            if os.path.isdir(ruta):
                self.directorio_actual = formatRuta(ruta)
                self.carpeta_preview = None  # Resetear preview al navegar
                self.cargar_contenido()
#
    def seleccionar_carpeta(self,event):
        """Marcar carpeta seleccionada con comportamiento toggle (ambos modos)"""
        seleccion = self.tree_carpetas.selection()
#
        # Deseleccionar archivos siempre
        self.tree_archivos.selection_remove(self.tree_archivos.selection())
#
        if seleccion:
            item = seleccion[0]
            tags = self.tree_carpetas.item(item,"tags")
            if tags:
                ruta_carpeta = tags[0]
#
                # Comportamiento toggle: si es la misma carpeta, deseleccionar
                if self.carpeta_preview == ruta_carpeta:
                    # Deseleccionar y volver a mostrar archivos del directorio actual
                    self.tree_carpetas.selection_remove(item)
                    self.carpeta_preview = None
                    # Usar after para no bloquear el hilo principal
                    self.ventana.after(1,
                         lambda: self.mostrar_archivos_carpeta(self.directorio_actual))
                else:
                    # Nueva carpeta seleccionada, mostrar sus archivos
                    self.carpeta_preview = ruta_carpeta
                    if os.path.isdir(ruta_carpeta):
                        # Usar after para no bloquear el hilo principal
                        self.ventana.after(1,
                             lambda r=ruta_carpeta: self.mostrar_archivos_carpeta(r))
        else:
            # Si no hay selección, resetear preview
            self.carpeta_preview = None
            # Usar after para no bloquear el hilo principal
            self.ventana.after(1,
                 lambda: self.mostrar_archivos_carpeta(self.directorio_actual))
#
    def mostrar_archivos_carpeta(self,ruta_carpeta):
        """Mostrar carpetas y archivos de una carpeta específica en el TreeView de archivos"""
        # Limpiar TreeView de archivos
        for item in self.tree_archivos.get_children():
            self.tree_archivos.delete(item)
#
        # Actualizar la interfaz inmediatamente
        self.ventana.update_idletasks()
#
        try:
            # Obtener elementos de la carpeta con límite de tiempo
            try:
                elementos = os.listdir(ruta_carpeta)
            except PermissionError:
                self.label_info.config(text="⚠ Sin permisos para acceder a esta carpeta")
                return
            except Exception as e:
                self.label_info.config(text=f"⚠ Error: {str(e)}")
                return
#
            carpetas = []
            archivos = []
            MAX_ITEMS = 1000  # Límite para evitar congelamiento
            contador = 0
#
            for elemento in elementos:
                if contador >= MAX_ITEMS:
                    self.label_info.config(text=f"⚠ Mostrando solo {MAX_ITEMS} elementos")
                    break
#
                ruta_completa = os.path.join(ruta_carpeta,elemento)
                try:
                    if os.path.isdir(ruta_completa):
                        carpetas.append((elemento,ruta_completa))
                        contador += 1
                    elif os.path.isfile(ruta_completa):
                        # Aplicar filtro si existe
                        if self.filtro_archivos:
                            import fnmatch
                            if fnmatch.fnmatch(elemento.lower(),self.filtro_archivos.lower()):
                                archivos.append((elemento,ruta_completa))
                                contador += 1
                        else:
                            archivos.append((elemento,ruta_completa))
                            contador += 1
                except:
                    continue
#
            # Ordenar alfabéticamente
            carpetas.sort(key=lambda x: x[0].lower())
            archivos.sort(key=lambda x: x[0].lower())
#
            # Agregar carpetas primero (en lotes para no bloquear)
            BATCH_SIZE = 50
            for i in range(0,len(carpetas),BATCH_SIZE):
                batch = carpetas[i:i+BATCH_SIZE]
                for nombre, ruta_completa in batch:
                    self.tree_archivos.insert("",tk.END,
                                              values=(f"📁 {nombre}", "<DIR>"),
                                              tags=(ruta_completa,"carpeta"))
                # Actualizar UI cada lote
                if i % (BATCH_SIZE * 2) == 0:
                    self.ventana.update_idletasks()
#
            # Agregar archivos después (en lotes)
            for i in range(0,len(archivos),BATCH_SIZE):
                batch = archivos[i:i+BATCH_SIZE]
                for nombre,ruta_completa in batch:
                    try:
                        tamaño = os.path.getsize(ruta_completa)
                        tamaño_formateado = self.formatear_tamaño(tamaño)
                    except:
                        tamaño_formateado = "N/A"
#
                    # Determinar icono según extensión
                    ext = os.path.splitext(nombre)[1].lower()
                    if ext in ['.db','.accdb']:
                        icono = "🗄️"
                    elif ext in ['.py','.pyw']:
                        icono = "🐍"
                    elif ext in ['.txt','.md','.log']:
                        icono = "📄"
                    elif ext in ['.jpg','.jpeg','.png','.gif','.bmp','.ico','psd']:
                        icono = "🖼️"
                    else:
                        icono = "📄"
#
                    self.tree_archivos.insert("",tk.END,
                                              values=(f"{icono} {nombre}", tamaño_formateado),
                                              tags=(ruta_completa,"archivo"))
                # Actualizar UI cada lote
                if i % (BATCH_SIZE * 2) == 0:
                    self.ventana.update_idletasks()
#
        except Exception as e:
            self.label_info.config(text=f"⚠ Error inesperado: {str(e)}")
#
    def seleccionar_archivo(self,event):
        """Marcar archivo seleccionado"""
        seleccion = self.tree_archivos.selection()
#
        if seleccion:
            item = seleccion[0]
            tags = self.tree_archivos.item(item,"tags")
#
            # Verificar si es una carpeta
            if tags and len(tags) > 1 and tags[1] == "carpeta":
                # Si es carpeta, deseleccionar (no se pueden seleccionar carpetas)
                self.tree_archivos.selection_remove(item)
                return
#
            # Si es archivo, deseleccionar carpetas del TreeView izquierdo
            self.tree_carpetas.selection_remove(self.tree_carpetas.selection())
#
        # Si no hay filtro (modo seleccionar carpeta), deshabilitar toda selección
        if not self.filtro_archivos:
            self.tree_archivos.selection_remove(self.tree_archivos.selection())
#
    def navegar_desde_archivos(self,event):
        """Navegar a una carpeta desde el TreeView de archivos al hacer doble clic"""
        seleccion = self.tree_archivos.selection()
        if not seleccion:
            return
#
        item = seleccion[0]
        tags = self.tree_archivos.item(item,"tags")
        if tags:
            ruta = tags[0]
            # Verificar si es una carpeta (segundo tag es "carpeta")
            if len(tags) > 1 and tags[1] == "carpeta":
                if os.path.isdir(ruta):
                    self.directorio_actual = formatRuta(ruta)
                    self.cargar_contenido()
#
    def subir_nivel(self):
        """Subir un nivel en la jerarquía de directorios"""
        directorio_padre = os.path.dirname(self.directorio_actual)
        if directorio_padre and directorio_padre != self.directorio_actual:
            self.directorio_actual = formatRuta(directorio_padre)
            self.carpeta_preview = None  # Resetear preview al subir nivel
            self.cargar_contenido()
#
    def ir_a_unidad(self,unidad):
        """Ir a la raíz de una unidad de disco"""
        if os.name == 'nt':
            ruta_unidad = f"{unidad}:/"
        else:
            ruta_unidad = unidad
#
        try:
            if os.path.exists(ruta_unidad):
                self.directorio_actual = formatRuta(ruta_unidad)
                self.carpeta_preview = None  # Resetear preview al cambiar de unidad
                self.cargar_contenido()
        except:
            pass
#
    def aceptar(self):
        """Aceptar selección"""
        # Detener monitoreo antes de cerrar
        if self.monitor_id:
            try:
                self.ventana.after_cancel(self.monitor_id)
                self.monitor_id = None
            except Exception as e:
                print(f"Error cancelando monitoreo en aceptar: {e}")
        
        # Si no hay filtro (modo seleccionar carpeta), siempre devolver carpeta
        if not self.filtro_archivos:
            # Verificar si hay carpeta seleccionada
            seleccion_carpeta = self.tree_carpetas.selection()
            if seleccion_carpeta:
                item = seleccion_carpeta[0]
                tags = self.tree_carpetas.item(item,"tags")
                if tags:
                    self.seleccion = formatRutaWindows(tags[0]) if os.name == 'nt' \
                                                                else tags[0]
                    # Guardar directorio para próxima vez
                    _guardar_ultimo_directorio(formatRuta(tags[0]))
                    try:
                        self.ventana.destroy()
                    except Exception as e:
                        print(f"Error destruyendo ventana (carpeta seleccionada): {e}")
                    return
#
            # Si no hay carpeta seleccionada, usar directorio actual
            self.seleccion = formatRutaWindows(self.directorio_actual) if os.name == 'nt' \
                                                                       else self.directorio_actual
            # Guardar directorio para próxima vez
            _guardar_ultimo_directorio(self.directorio_actual)
            try:
                self.ventana.destroy()
            except Exception as e:
                print(f"Error destruyendo ventana (directorio actual): {e}")
            return
#
        # Si hay filtro (modo seleccionar archivo), SOLO devolver archivos (no carpetas)
        seleccion_archivo = self.tree_archivos.selection()
        if seleccion_archivo:
            item = seleccion_archivo[0]
            tags = self.tree_archivos.item(item,"tags")
            if tags:
                # Verificar que sea un archivo y no una carpeta
                if len(tags) > 1 and tags[1] == "archivo":
                    self.seleccion = formatRutaWindows(tags[0]) if os.name == 'nt' else tags[0]
                    # Guardar el directorio del archivo para próxima vez
                    directorio_archivo = os.path.dirname(formatRuta(tags[0]))
                    _guardar_ultimo_directorio(directorio_archivo)
                    try:
                        self.ventana.destroy()
                    except Exception as e:
                        print(f"Error destruyendo ventana (archivo seleccionado): {e}")
                    return
#
        # Si no hay archivo seleccionado, no devolver nada (cancelar)
        self.cancelado = True
        self.seleccion = None
        try:
            self.ventana.destroy()
        except Exception as e:
            print(f"Error destruyendo ventana (sin selección): {e}")
#
    def cancelar(self):
        """Cancelar selección"""
        self.cancelado = True
        self.seleccion = None
        # Detener monitoreo de unidades
        if self.monitor_id:
            try:
                self.ventana.after_cancel(self.monitor_id)
                self.monitor_id = None
            except Exception as e:
                print(f"Error cancelando monitoreo en cancelar: {e}")
        # Destruir ventana
        try:
            self.ventana.destroy()
        except Exception as e:
            print(f"Error destruyendo ventana en cancelar: {e}")
#
    def iniciar_monitoreo_unidades(self):
        """Iniciar el monitoreo periódico de unidades cada segundo"""
        try:
            self.comprobar_unidades()
        except Exception as e:
            print(f"Error en monitoreo: {e}")
        finally:
            # Programar siguiente comprobación en 1000ms (1 segundo)
            # Solo si la ventana aún existe
            if self.ventana and self.ventana.winfo_exists():
                self.monitor_id = self.ventana.after(1000, self.iniciar_monitoreo_unidades)
#
    def comprobar_unidades(self):
        """Comprobar si hay cambios en las unidades disponibles"""
        try:
            unidades_nuevas = obtener_unidades()
        except Exception as e:
            print(f"Error obteniendo unidades: {e}")
            return
#
        # Verificar si hay cambios
        if set(unidades_nuevas) != set(self.unidades_actuales):
            # Detectar unidades añadidas
            unidades_agregadas = set(unidades_nuevas) - set(self.unidades_actuales)
            # Detectar unidades removidas
            unidades_removidas = set(self.unidades_actuales) - set(unidades_nuevas)
#
            # Actualizar lista de unidades
            self.unidades_actuales = unidades_nuevas
#
            # Actualizar botones de unidades en la interfaz
            try:
                self.actualizar_botones_unidades()
            except Exception as e:
                print(f"Error actualizando botones: {e}")
#
            # Mostrar información en el label
            try:
                if unidades_agregadas:
                    texto_agregadas = ", ".join([f"{u}:" for u in unidades_agregadas])
                    self.label_info.config(text=f"✓ Nueva(s) unidad(es) detectada(s): {texto_agregadas}")
                if unidades_removidas:
                    texto_removidas = ", ".join([f"{u}:" for u in unidades_removidas])
                    self.label_info.config(text=f"⚠ Unidad(es) removida(s): {texto_removidas}")
#
                    # Si el directorio actual está en una unidad removida, volver a la primera disponible
                    if os.name == 'nt':
                        letra_actual = self.directorio_actual[0].upper()
                        if letra_actual in unidades_removidas:
                            if self.unidades_actuales:
                                self.ir_a_unidad(self.unidades_actuales[0])
                            else:
                                self.directorio_actual = "C:/"
                                self.cargar_contenido()
            except Exception as e:
                print(f"Error mostrando información: {e}")
#
    def actualizar_botones_unidades(self):
        """Actualizar los botones de unidades en la interfaz"""
        # Limpiar frame de unidades
        for widget in self.frame_unidades.winfo_children():
            widget.destroy()
#
        # Crear botones para cada unidad
        x_pos = 0
        for unidad in self.unidades_actuales:
            texto_boton = f"{unidad}:" if os.name == 'nt' else "/"
            comando = lambda u=unidad: self.ir_a_unidad(u)
            btn_unidad = tk.Button(self.frame_unidades,text=texto_boton,command=comando,
                                   bg="#3498db",fg="white",font="Arial 9 bold",
                                   cursor="hand2",relief="flat")
            btn_unidad.place(x=x_pos,y=0,width=35,height=30)
            x_pos += 40
#
    def obtener_seleccion(self):
        """Esperar y obtener la selección del usuario"""
        self.ventana.wait_window()
        return self.seleccion if not self.cancelado else None
#
# Función de conveniencia para uso rápido
def selec_archivo(parent=None,titulo="Seleccionar Archivo",
                              filtro="*.*",directorio_inicial=None):
    """
    Función de conveniencia para seleccionar un archivo
    
    Retorna la ruta del archivo seleccionado o None si se canceló
    """
    if parent is None:
        parent = tk.Tk()
        parent.withdraw()
#
    navegador = NavegadorArchivos(parent,titulo=titulo,
                                  filtro_archivos=filtro,
                                  directorio_inicial=directorio_inicial)
    return navegador.obtener_seleccion()
#
def selec_carpeta(parent=None,titulo="Seleccionar Carpeta",
                              directorio_inicial=None):
    """
    Función de conveniencia para seleccionar una carpeta
    
    Retorna la ruta de la carpeta seleccionada o None si se canceló
    """
    if parent is None:
        parent = tk.Tk()
        parent.withdraw()
#
    navegador = NavegadorArchivos(parent,titulo=titulo,
                                  directorio_inicial=directorio_inicial)
    return navegador.obtener_seleccion()
#