'''
Domino grafico

Version grafica (Tkinter) del juego de domino contenido en domino.py.

Flujo:
1. Al iniciar, se muestran en pantalla TODAS las fichas del domino.
2. Un menu permite elegir "Jugar" o "Salir".
3. Al elegir "Jugar" se reparten las fichas:
   - En la parte lateral derecha se ven las fichas del JUGADOR (visibles).
   - En la parte lateral izquierda se ven las fichas de la CPU (ocultas, boca abajo).
   - En la parte inferior se ve el MAZO (tambien oculto, boca abajo).
4. "Salir" cierra la aplicacion.
'''
import os
#import time as tm
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image,ImageTk
import pygame as py
#
from constantes import *
# Carga de imagenes de las fichas (diccionario clave -> ImageTk.PhotoImage)
from imagen_ficha import crear_fichas
# Logica del juego ya existente en domino.py
from domino import (
    repartir_fichas,
    iniciar_juego,
    ficha_encaja,
    colocar_ficha,
    tiene_jugada,
    buscar_jugada_cpu,
    sumar_puntos,
)
#
class JuegoDomino:
    '''Ventana principal del juego de domino grafico.'''
    def __init__(self,root):
        self.root = root
        self.root.title(TITULO)
        self.root.configure(bg=TAPETE)
        self.root.geometry(f'{ANCHO}x{ALTO}')
        self.root.update()
        self.root.state('zoomed')
        w = self.root.winfo_width() + self.root.winfo_rootx()
        h = self.root.winfo_height() + self.root.winfo_rooty() - 30 # Barra de tareas
        try:
            self.root.iconbitmap(ICONO)
        except Exception:
            # Si no se encuentra el icono, seguimos sin el
            pass
        self.root.state('normal')
        self.root.geometry(f'{w}x{h}+0+0')
        self.root.resizable(False,False)
#
        # Cargamos los sonidos para el juego
        self.sonido_repartir = py.mixer.Sound(RUTA_SONIDOS + "repartir.mp3")
        self.sonido_poner = py.mixer.Sound(RUTA_SONIDOS + "poner.mp3")
        self.sonido_robar = py.mixer.Sound(RUTA_SONIDOS + "robar.mp3")
#
        # Totales de puntos a 0
        self.puntos_cpu = 0
        self.puntos_jugador = 0
#
        # Cargamos todas las imagenes de las fichas usando esta misma ventana.
        # El diccionario tiene claves "00".."66" y "99" (ficha vuelta / oculta).
        self.imagen_ficha = crear_fichas(self.root)
        # Lista de todas las claves de fichas jugables (sin la "99")
        self.claves_fichas = sorted(k for k in self.imagen_ficha if k != "99")
        # Version HORIZONTAL (girada 90 grados) de cada ficha, con el valor
        # menor a la izquierda. Se usa en las manos de CPU y jugador.
        self.imagen_ficha_h = self.crear_fichas_horizontales()
        # Imagenes de cada ficha en sus 4 orientaciones (0, 90, 180, 270),
        # usadas para dibujar la serpiente del tablero girando las fichas.
        self.imagen_ficha_orientada = self.crear_fichas_orientadas()
#
        # Barra de menu de la aplicacion (Juego / Ayuda)
        self.crear_menu()
#
        # Contenedor unico donde iremos dibujando cada pantalla.
        # Al cambiar de pantalla, se destruye y se vuelve a crear.
        self.contenedor = tk.Frame(self.root,bg=TAPETE)
        self.contenedor.pack(fill="both",expand=True)
#
        # Mostramos la primera pantalla: todas las fichas + menu
        self.pantalla_inicio()
#
    # Barra de menu de la aplicacion
    def crear_menu(self):
        '''Crea la barra de menu superior con los menus Juego y Ayuda.'''
        barra_menu = tk.Menu(self.root)
#
        # Menu "Juego": Nuevo / Salir
        menu_juego = tk.Menu(barra_menu,tearoff=0)
        menu_juego.add_command(label="Nuevo",command=self.pantalla_juego)
        menu_juego.add_separator()
        menu_juego.add_command(label="Salir",command=self.salir)
        barra_menu.add_cascade(label="Juego",menu=menu_juego)
        # Guardamos el menu para poder activar/desactivar "Nuevo" durante el juego
        self.menu_juego = menu_juego
#
        # Menu "Ayuda": Ayuda / Acerca de ...
        menu_ayuda = tk.Menu(barra_menu,tearoff=0)
        menu_ayuda.add_command(label="Ayuda",command=self.mostrar_ayuda)
        menu_ayuda.add_command(label="Acerca de ...",command=self.acerca_de)
        barra_menu.add_cascade(label="Ayuda",menu=menu_ayuda)
#
        # Asignamos la barra de menu a la ventana principal
        self.root.config(menu=barra_menu)
#
    # Activa o desactiva la entrada de menu "Nuevo"
    def activar_menu_nuevo(self,activar):
        '''Habilita o deshabilita la opcion "Nuevo" del menu Juego.

        Se desactiva al iniciar una partida y se vuelve a activar cuando la
        partida ha finalizado.
        '''
        estado = "normal" if activar else "disabled"
        self.menu_juego.entryconfig("Nuevo",state=estado)
#
    # Utilidades
    def limpiar_contenedor(self):
        '''Elimina todos los widgets de la pantalla actual.'''
        for widget in self.contenedor.winfo_children():
            widget.destroy()
#
    def clave_de_ficha(self,ficha):
        '''Devuelve la clave de imagen ("00".."66") para una ficha (a, b).'''
        menor = min(ficha[0],ficha[1])
        mayor = max(ficha[0],ficha[1])
        return f"{menor}{mayor}"
#
    def crear_fichas_horizontales(self):
        '''Crea un diccionario clave -> imagen GIRADA a horizontal.

        Las imagenes originales son verticales con el valor menor arriba.
        Al rotarlas 90 grados en sentido antihorario, ese valor menor queda
        a la izquierda, que es como queremos ver las fichas en las manos.
        Incluye tambien la ficha vuelta "99".
        '''
        imagenes = {}
        claves = self.claves_fichas + ["99"]
        for clave in claves:
            ruta = os.path.join(RUTA_IMAGENES,f"{clave}.png")
            imagen = Image.open(ruta)
            # rotate(90, expand=True): antihorario -> el borde de arriba
            # (valor menor) pasa a la izquierda
            imagen_girada = imagen.rotate(90,expand=True)
            imagenes[clave] = ImageTk.PhotoImage(imagen_girada)
        return imagenes
#
    def crear_fichas_orientadas(self):
        '''Crea un diccionario clave -> {angulo: imagen} con 4 orientaciones.

        La imagen base es VERTICAL (60x121) con el valor menor arriba.
        Para cada ficha se guardan sus rotaciones antihorarias:
          -   0 : vertical, menor arriba  / mayor abajo
          -  90 : horizontal, menor a la IZQUIERDA / mayor a la derecha
          - 180 : vertical, mayor arriba  / menor abajo
          - 270 : horizontal, mayor a la izquierda / menor a la DERECHA
        Esto permite orientar cada ficha para que su numero coincida con el
        de la ficha anterior en la serpiente del tablero.
        '''
        imagenes = {}
        for clave in self.claves_fichas:
            ruta = os.path.join(RUTA_IMAGENES,f"{clave}.png")
            base = Image.open(ruta)
            imagenes[clave] = {
                angulo: ImageTk.PhotoImage(base.rotate(angulo,expand=True))
                for angulo in (0,90,180,270)
            }
        return imagenes
#
    def crear_zona_scroll_vertical(self,parent,lado_barra="right"):
        '''Crea una zona con SCROLL VERTICAL y devuelve el Frame interior.

        Se usa para las manos de la CPU y del jugador: si hay mas fichas de
        las que caben en la pantalla, se activa una barra de desplazamiento
        vertical y se puede desplazar con la rueda del raton.

        - lado_barra: "right" coloca la barra de scroll a la DERECHA de las
          fichas (por defecto, para el jugador); "left" la coloca a la
          IZQUIERDA de las fichas (para la CPU, en el lateral izquierdo).

        Estructura creada dentro de "parent":
          Frame contenedor
            +-- Canvas (con scrollregion) + Scrollbar vertical
                  +-- Frame interior  <-- se devuelve (aqui van las fichas)

        Devuelve el Frame interior, de modo que el resto del codigo puede
        seguir empaquetando fichas en el como si fuera un Frame normal.
        '''
        # Contenedor que agrupa el Canvas y la barra de scroll
        contenedor = tk.Frame(parent,bg=TAPETE)
        contenedor.pack(fill="both",expand=True)
        # Ancho de una ficha horizontal (girada) mas el margen lateral de las
        # fichas (padx=4 a cada lado). Se usa como ancho inicial del Canvas
        # para que la columna se vea bien antes de dibujar las fichas.
        ancho_ficha = self.imagen_ficha_h["99"].width() + 12
        # Canvas donde "vive" el contenido desplazable
        lienzo = tk.Canvas(
            contenedor,bg=TAPETE,highlightthickness=0,bd=0,width=ancho_ficha
        )
        barra = tk.Scrollbar(
            contenedor,orient="vertical",command=lienzo.yview
        )
        lienzo.configure(yscrollcommand=barra.set)
        # La barra puede ir a la izquierda o a la derecha de las fichas.
        if lado_barra == "left":
            barra.pack(side="left",fill="y")
            lienzo.pack(side="right",fill="both",expand=True)
        else:
            barra.pack(side="right",fill="y")
            lienzo.pack(side="left",fill="both",expand=True)
        # Frame interior donde se colocaran realmente las fichas
        interior = tk.Frame(lienzo,bg=TAPETE)
        ventana = lienzo.create_window((0,0),window=interior,anchor="nw")
#
        def _ajustar_scrollregion(evento):
            '''Actualiza la region desplazable al tamano del contenido.'''
            lienzo.configure(scrollregion=lienzo.bbox("all"))
        interior.bind("<Configure>",_ajustar_scrollregion)
#
        def _ajustar_ancho(evento):
            '''Hace que el frame interior ocupe el ancho del Canvas.'''
            lienzo.itemconfigure(ventana,width=evento.width)
        lienzo.bind("<Configure>",_ajustar_ancho)
#
        def _rueda(evento):
            '''Desplaza el contenido con la rueda del raton.'''
            # Solo hay scroll si el contenido es mas alto que el Canvas
            if lienzo.bbox("all") is None:
                return
            _,_,_,alto_contenido = lienzo.bbox("all")
            if alto_contenido <= lienzo.winfo_height():
                return
            # En Windows evento.delta es multiplo de 120
            lienzo.yview_scroll(int(-evento.delta / 120),"units")
        # Activamos la rueda solo cuando el cursor esta sobre la zona
        def _activar_rueda(evento):
            lienzo.bind_all("<MouseWheel>",_rueda)
        def _desactivar_rueda(evento):
            lienzo.unbind_all("<MouseWheel>")
        lienzo.bind("<Enter>",_activar_rueda)
        lienzo.bind("<Leave>",_desactivar_rueda)
        interior.bind("<Enter>",_activar_rueda)
        interior.bind("<Leave>",_desactivar_rueda)
        return interior
#
    def crear_columna_fichas_h(self,parent,claves,ocultas=False):
        '''Crea una columna (una debajo de otra) de fichas HORIZONTALES.

        - claves: lista de claves ("00".."66").
        - ocultas: si es True, se dibuja siempre la ficha vuelta ("99").
        '''
        contenedor = tk.Frame(parent,bg=TAPETE)
        for clave in claves:
            clave_imagen = "99" if ocultas else clave
            etiqueta = tk.Label(
                contenedor,
                image=self.imagen_ficha_h[clave_imagen],
                bg=TAPETE,
                bd=1,
                relief="solid",
            )
            etiqueta.pack(side="top",padx=4,pady=3)
        return contenedor
#
    def crear_fila_fichas(self,parent,claves,ocultas=False,vertical=False):
        '''Crea un Frame con las fichas dibujadas en Labels.

        - claves: lista de claves ("00".."66"). Cada una se dibuja con su imagen.
        - ocultas: si es True, se dibuja siempre la ficha vuelta ("99").
        - vertical: si es True, las fichas se apilan en columna (para laterales);
          si es False, se colocan en fila (para arriba/abajo).
        '''
        contenedor = tk.Frame(parent,bg=TAPETE)
        lado = "top" if vertical else "left"
        for clave in claves:
            clave_imagen = "99" if ocultas else clave
            etiqueta = tk.Label(
                contenedor,
                image=self.imagen_ficha[clave_imagen],
                bg=TAPETE,
                bd=1,
                relief="solid",
            )
            etiqueta.pack(side=lado,padx=4,pady=4)
        return contenedor
#
    def crear_rejilla_fichas(self,parent,claves,columnas,ocultas=False):
        '''Crea una rejilla de fichas SEPARADAS (sin solaparse).

        Las fichas se colocan en una cuadricula con el numero de columnas
        indicado, dejando espacio entre ellas para que se vean por separado
        (evita el efecto de "rectangulo negro" al apilar fichas vueltas).
        - claves: lista de claves ("00".."66").
        - columnas: numero de columnas de la cuadricula.
        - ocultas: si es True, se dibuja siempre la ficha vuelta ("99").
        '''
        contenedor = tk.Frame(parent,bg=TAPETE)
        for indice,clave in enumerate(claves):
            fila = indice // columnas
            columna = indice % columnas
            clave_imagen = "99" if ocultas else clave
            etiqueta = tk.Label(
                contenedor,
                image=self.imagen_ficha[clave_imagen],
                bg=TAPETE,
                bd=1,
                relief="solid",
            )
            etiqueta.grid(row=fila,column=columna,padx=5,pady=5)
        return contenedor
#
    # Pantalla 1: todas las fichas + menu
    def pantalla_inicio(self):
        '''Muestra todas las fichas del domino (pantalla de presentacion).

        Para empezar a jugar se usa el menu Juego > Nuevo.'''
        self.limpiar_contenedor()
#
        # Titulo de la pantalla
        titulo = tk.Label(
            self.contenedor,
            text="DOMINO",
            font=("Arial",28,"bold"),
            fg="white",
            bg=TAPETE,
        )
        titulo.pack(pady=(20,10))
#
        # Rejilla con las 28 fichas (sin la ficha vuelta "99"),
        # dispuestas en 4 filas de 7 columnas.
        rejilla = tk.Frame(self.contenedor,bg=TAPETE)
        rejilla.pack(pady=10)
#
        columnas_inicio = 7                          # 28 fichas -> 4 filas x 7 columnas
        claves = self.claves_fichas                  # "00".."66" (sin "99")
        for indice,clave in enumerate(claves):
            fila = indice // columnas_inicio
            columna = indice % columnas_inicio
            etiqueta = tk.Label(
                rejilla,
                image=self.imagen_ficha[clave],
                bg=TAPETE,
                bd=1,
                relief="solid",
            )
            etiqueta.grid(row=fila,column=columna,padx=4,pady=4)
#
        # Texto guia: se juega desde el menu superior
        tk.Label(
            self.contenedor,
            text="Menu  Juego > Nuevo  para comenzar una partida",
            font=("Arial",14,"bold"),
            fg="white",
            bg=TAPETE,
        ).pack(pady=20)
#
    # Pantalla de juego (jugador visible, cpu y mazo ocultos)
    def pantalla_juego(self):
        '''Inicia una nueva partida (opcion de menu Juego > Nuevo).

        Si venimos de una partida anterior, primero BORRA de forma visible la
        zona de las fichas, luego reproduce el sonido de repartir y, tras un
        retardo de segundo y medio (sin bloquear la ventana), monta la nueva
        pantalla de juego. En la primera partida se monta directamente.
        '''
        # Al iniciar la partida, desactivamos la opcion "Nuevo" del menu
        self.activar_menu_nuevo(False)
        # Detectamos si venimos de una partida anterior (ya se jugo antes).
        partida_anterior = getattr(self,"tablero",None) is not None
        if partida_anterior:
            # Borramos la zona de las fichas ANTES de emitir el sonido y
            # forzamos el repintado para que el borrado se vea en pantalla.
            self.limpiar_contenedor()
            self.contenedor.update_idletasks()
            # Sonido de repartir y retardo de segundo y medio (no bloqueante),
            # igual que al robar la CPU y el jugador.
            self.sonido_repartir.play()
            self.root.after(1500,self._montar_pantalla_juego)
        else:
            # Primera partida: montamos directamente tras el sonido.
            self.sonido_repartir.play()
            #self._montar_pantalla_juego()
            self.root.after(1500,self._montar_pantalla_juego)
#
    def _montar_pantalla_juego(self):
        '''Reparte las fichas, monta el tablero y arranca la partida.

        - Izquierda: fichas de la CPU (ocultas).
        - Derecha: fichas del jugador (visibles y clicables).
        - Centro: mensajes y tablero donde se colocan las fichas.
        - Abajo: mazo (oculto) y su numero de fichas.'''
        self.limpiar_contenedor()
#
        # Repartimos con la logica de domino.py. Las claves son "ab" (texto);
        # las convertimos a tuplas de enteros (a, b) para que las operaciones
        # de domino.py (sumas, comparaciones) funcionen correctamente.
        jugador,cpu,mazo = repartir_fichas(self.claves_fichas)
        self.jugador = [(int(f[0]),int(f[1])) for f in jugador]
        self.cpu = [(int(f[0]),int(f[1])) for f in cpu]
        self.mazo = [(int(f[0]),int(f[1])) for f in mazo]
#
        # Zona superior: puntos CPU (izq), "DOMINO" (centro), puntos jugador (der)
        zona_superior = tk.Frame(self.contenedor,bg=TAPETE)
        zona_superior.pack(side="top",fill="x",pady=(10,5))
        # Tres columnas de igual peso para alinear izquierda / centro / derecha
        zona_superior.columnconfigure(0,weight=1)
        zona_superior.columnconfigure(1,weight=1)
        zona_superior.columnconfigure(2,weight=1)
        # Puntos de la CPU (encima de su columna, a la izquierda)
        self.etiqueta_puntos_cpu = tk.Label(
            zona_superior,
            text=f"CPU: {self.puntos_cpu}",
            font=("Arial",14,"bold"),
            fg="white",
            bg=TAPETE,
        )
        self.etiqueta_puntos_cpu.grid(row=0,column=0)
        # Titulo "DOMINO" en el centro
        tk.Label(
            zona_superior,
            text="DOMINO",
            font=("Arial",24,"bold"),
            fg="white",
            bg=TAPETE,
        ).grid(row=0,column=1)
        # Puntos del jugador (encima de su columna, a la derecha)
        self.etiqueta_puntos_jugador = tk.Label(
            zona_superior,
            text=f"Jugador: {self.puntos_jugador}",
            font=("Arial",14,"bold"),
            fg="white",
            bg=TAPETE,
        )
        self.etiqueta_puntos_jugador.grid(row=0,column=2)
#
        # Zona inferior: MAZO (oculto)
        zona_mazo = tk.Frame(self.contenedor,bg=TAPETE)
        zona_mazo.pack(side="bottom",pady=(5,15))
        self.etiqueta_mazo = tk.Label(
            zona_mazo,
            text=f"Mazo ({len(self.mazo)})",
            font=("Arial",14,"bold"),
            fg="white",
            bg=TAPETE,
        )
        self.etiqueta_mazo.pack()
        self.zona_mazo_fichas = tk.Frame(zona_mazo,bg=TAPETE)
        self.zona_mazo_fichas.pack()
#
        # Zona media: CPU (izq), jugador (der) y tablero (centro)
        zona_media = tk.Frame(self.contenedor,bg=TAPETE)
        zona_media.pack(side="top",fill="both",expand=True)
#
        # Lateral izquierdo: fichas de la CPU (ocultas)
        zona_cpu = tk.Frame(zona_media,bg=TAPETE)
        zona_cpu.pack(side="left",fill="y",padx=(10,5),pady=(70,10))
        self.etiqueta_cpu = tk.Label(
            zona_cpu,
            text=f"CPU ({len(self.cpu)})",
            font=("Arial",14,"bold"),
            fg="white",
            bg=TAPETE,
        )
        self.etiqueta_cpu.pack(pady=(0,5))
        # Scroll vertical a la izquierda de las fichas
        # por si hay mas de las que caben en pantalla
        self.zona_cpu_fichas = self.crear_zona_scroll_vertical(zona_cpu,
                                                               lado_barra="left"
        )
#
        # Lateral derecho: fichas del JUGADOR (visibles y clicables)
        zona_jugador = tk.Frame(zona_media,bg=TAPETE)
        zona_jugador.pack(side="right",fill="y",padx=(5,10),pady=(70,10))
        self.etiqueta_jugador = tk.Label(
            zona_jugador,
            text=f"Jugador ({len(self.jugador)})",
            font=("Arial",14,"bold"),
            fg="white",
            bg=TAPETE,
        )
        self.etiqueta_jugador.pack(pady=(0,5))
        # Scroll vertical a la derecha de las fichas
        # por si hay mas de las que caben en pantalla
        self.zona_jugador_fichas = self.crear_zona_scroll_vertical(zona_jugador)
#
        # Centro: mensajes y TABLERO donde se colocan las fichas
        zona_centro = tk.Frame(zona_media,bg=TAPETE)
        zona_centro.pack(side="left",fill="both",expand=True,pady=10)
        self.etiqueta_info = tk.Label(
            zona_centro,
            text="",
            font=("Arial",16,"bold"),
            fg="white",
            bg=TAPETE,
        )
        self.etiqueta_info.pack(pady=(10,5))
        # Panel FIJO con los botones para elegir el extremo. Estan SIEMPRE
        # visibles. Desactivados cuando no hay que decidir y activos solo
        # cuando la ficha pulsada encaja por los dos extremos del tablero.
        self.panel_extremos = tk.Frame(zona_centro,bg=TAPETE)
        self.panel_extremos.pack(pady=(0,5))
        self.btn_izq = tk.Button(
            self.panel_extremos,
            text="◀ Izquierda",
            font=("Arial",12,"bold"),
            bg="#f0c000",
            activebackground="#ffd633",
            disabledforeground="#7a7a7a",
            cursor="hand2",
            state="disabled",
            command=lambda: self.elegir_extremo("izq"),
        )
        self.btn_izq.pack(side="left",padx=6)
        self.btn_der = tk.Button(
            self.panel_extremos,
            text="Derecha ▶",
            font=("Arial",12,"bold"),
            bg="#f0c000",
            activebackground="#ffd633",
            disabledforeground="#7a7a7a",
            cursor="hand2",
            state="disabled",
            command=lambda: self.elegir_extremo("der"),
        )
        self.btn_der.pack(side="left",padx=6)
        self.btn_cancelar = tk.Button(
            self.panel_extremos,
            text="Cancelar",
            font=("Arial",12,"bold"),
            bg="#d0d0d0",
            activebackground="#e6e6e6",
            disabledforeground="#7a7a7a",
            cursor="hand2",
            state="disabled",
            command=self.cancelar_extremo,
        )
        self.btn_cancelar.pack(side="left",padx=6)
        # El tablero es un Canvas para poder colocar las fichas por coordenadas
        # y dibujar la serpiente (giros y fichas orientadas).
        self.zona_tablero = tk.Canvas(
            zona_centro,bg=TAPETE,highlightthickness=0,bd=0
        )
        self.zona_tablero.pack(fill="both",expand=True)
#
        # Arrancamos la partida con la logica de domino.py
        self.iniciar_partida()
#
    # Logica de la partida (usa domino.py)
    def iniciar_partida(self):
        '''Decide quien empieza y coloca la primera ficha en el tablero.'''
        self.tablero,quien_empieza,self.turno = iniciar_juego(
            self.jugador,self.cpu
        )
        # Indice de la PRIMERA ficha jugada dentro de self.tablero. Sirve de
        # ancla para dibujar: la serpiente crece hacia los extremos sin mover
        # las fichas ya colocadas. Se actualiza en _colocar_ficha.
        self.indice_inicial = 0
        # Reiniciamos el ancho/alto de referencia del tablero para esta partida
        self._ancho_tablero_ref = None
        self._alto_tablero_ref = None
        self.pasos_seguidos = 0     # Turnos pasados seguidos (para cierre)
        self.fin_partida = False
        # Estado de la eleccion de extremo (cuando una ficha encaja por los dos
        # lados y el jugador debe elegir con el raton donde colocarla).
        self.eligiendo_extremo = False
        self.ficha_a_elegir = None
        self.habilitar_botones_extremo(False)
        self.refrescar_pantalla()
        if self.turno == "cpu":
            self.mostrar_info("Empieza la CPU...")
            self.root.after(800,self.turno_cpu_grafico)
        else:
            # Empieza el jugador (la CPU ya coloco su ficha inicial, p.ej. un
            # doble). Si el jugador no tiene jugada, robara del mazo o pasara.
            self.mostrar_info("Empiezas tu: pulsa una ficha para colocarla")
            self.preparar_turno_jugador()
#
    def mostrar_info(self,texto):
        '''Actualiza la etiqueta de mensajes del centro.'''
        self.etiqueta_info.config(text=texto)
#
    def actualizar_contadores(self):
        '''Refresca los rotulos con el numero de fichas y la puntuacion.'''
        self.etiqueta_cpu.config(text=f"CPU ({len(self.cpu)})")
        self.etiqueta_jugador.config(text=f"Jugador ({len(self.jugador)})")
        self.etiqueta_mazo.config(text=f"Mazo ({len(self.mazo)})")
        self.etiqueta_puntos_cpu.config(text=f"CPU: {self.puntos_cpu}")
        self.etiqueta_puntos_jugador.config(text=f"Jugador: {self.puntos_jugador}"
        )
#
    def refrescar_pantalla(self):
        '''Redibuja manos, mazo y tablero segun el estado actual.'''
        self.actualizar_contadores()
        for zona in (
            self.zona_cpu_fichas,
            self.zona_jugador_fichas,
            self.zona_mazo_fichas,
        ):
            for widget in zona.winfo_children():
                widget.destroy()
        # El tablero es un Canvas: se limpia borrando sus elementos dibujados
        self.zona_tablero.delete("all")
        # Al terminar la partida se descubren las fichas de la CPU y del mazo;
        # mientras se juega permanecen ocultas (boca abajo).
        descubrir = getattr(self,"fin_partida",False)
        # CPU: fichas ocultas durante la partida, visibles al terminar
        claves_cpu = [self.clave_de_ficha(f) for f in self.cpu]
        self.crear_columna_fichas_h(
            self.zona_cpu_fichas,claves_cpu,ocultas=not descubrir
        ).pack()
        # Mazo: fichas ocultas durante la partida, visibles al terminar
        claves_mazo = [self.clave_de_ficha(f) for f in self.mazo]
        self.crear_fila_fichas(
            self.zona_mazo_fichas,claves_mazo,ocultas=not descubrir
        ).pack()
        # Jugador: fichas visibles y clicables
        self.dibujar_mano_jugador()
        # Tablero: fichas colocadas
        self.dibujar_tablero()
#
    def dibujar_mano_jugador(self):
        '''Dibuja la mano del jugador con fichas clicables (en columna).'''
        # Guardamos las etiquetas de cada ficha para poder resaltarlas cuando
        # el jugador deba elegir el extremo (encaja por los dos lados).
        self.etiquetas_jugador = {}
        for ficha in self.jugador:
            clave = self.clave_de_ficha(ficha)
            etiqueta = tk.Label(
                self.zona_jugador_fichas,
                image=self.imagen_ficha_h[clave],
                bg=TAPETE,
                bd=1,
                relief="solid",
                cursor="hand2",
            )
            etiqueta.pack(side="top",padx=4,pady=3)
            self.etiquetas_jugador[ficha] = etiqueta
            etiqueta.bind(
                "<Button-1>",
                lambda evento,f=ficha: self.click_ficha_jugador(f),
            )
#
    def dibujar_tablero(self):
        '''Dibuja la serpiente de fichas del tablero sobre el Canvas.

        Reglas de dibujo (como en un domino real):
        - La PRIMERA ficha (ancla) se coloca ARRIBA, centrada horizontalmente.
        - Al colocar nuevas fichas, las YA colocadas NO se mueven: la serpiente
          crece hacia sus extremos (rama derecha y rama izquierda) partiendo
          del ancla.
        - El recorrido es un zig-zag descendente: horizontal (este-oeste) hasta
          el limite lateral, luego VERTICAL bajando por el lateral hasta el
          limite inferior, y de nuevo horizontal en sentido contrario, etc.
        - Cada ficha se ORIENTA (gira) para que su numero coincida con el de la
          ficha anterior en la cadena.
        - Las fichas DOBLES se dibujan PERPENDICULARES al tramo en curso, salvo
          la ficha de la esquina (1a de un cambio de orientacion), que se alinea
          con el nuevo tramo.

        El tablero (self.tablero) es una lista de tuplas (izq, der) ya
        encadenada: tablero[i][1] == tablero[i+1][0].
        '''
        if not self.tablero:
            return
        # Medidas de una ficha (imagen base vertical 60x120)
        largo = self.imagen_ficha["99"].height()    # Lado largo  (~120)
        corto = self.imagen_ficha["99"].width()      # Lado corto  (~60)
        sep = 4                                       # Separacion entre fichas
        # Ancho disponible del tablero (si aun no esta renderizado, usamos req)
        self.zona_tablero.update_idletasks()
        ancho_canvas = self.zona_tablero.winfo_width()
        if ancho_canvas <= 1:
            ancho_canvas = self.zona_tablero.winfo_reqwidth() or 600
        alto_canvas = self.zona_tablero.winfo_height()
        if alto_canvas <= 1:
            alto_canvas = self.zona_tablero.winfo_reqheight() or 400
        # El ancho/alto de referencia se FIJA en el primer dibujo para que las
        # fichas ya colocadas NO se muevan cuando el Canvas crece. Solo se
        # recalcula si el ancho cambia mucho (redimension real de la ventana).
        ancho_ref = getattr(self,"_ancho_tablero_ref",None)
        if ancho_ref is None or abs(ancho_ref - ancho_canvas) > corto:
            ancho_ref = ancho_canvas
            self._ancho_tablero_ref = ancho_ref
        alto_ref = getattr(self,"_alto_tablero_ref",None)
        if alto_ref is None or alto_ref < alto_canvas:
            alto_ref = max(alto_canvas,3 * largo)     # Al menos 3 filas
            self._alto_tablero_ref = alto_ref
        margen = largo // 2 + sep
        limites = {
            "der": ancho_ref - margen,
            "izq": margen,
            "inf": alto_ref - margen,
        }
        # Punto de partida: PRIMERA ficha ARRIBA y centrada horizontalmente
        x_centro = ancho_ref / 2
        y_inicial = largo / 2 + sep
        indice = getattr(self,"indice_inicial",0)
        if indice < 0 or indice >= len(self.tablero):
            indice = 0
        placements = []                               # (imagen, cx, cy)
        # --- Ficha inicial (ancla) arriba en el centro ---
        ficha0 = self.tablero[indice]
        clave0 = self.clave_de_ficha(ficha0)
        doble0 = ficha0[0] == ficha0[1]
        menor0 = min(ficha0[0],ficha0[1])
        imagen0 = self._imagen_orientada(
            clave0,doble0,menor0,ficha0[0],"H","der",False
        )
        paso0 = corto if doble0 else largo
        placements.append((imagen0,x_centro,y_inicial))
        # --- Rama DERECHA: fichas posteriores al ancla, crecen hacia la derecha ---
        borde_der = x_centro + paso0 / 2               # Extremo derecho ocupado
        self._extender_rama(
            self.tablero[indice + 1:],"der",borde_der,y_inicial,
            largo,corto,sep,limites,placements,
        )
        # --- Rama IZQUIERDA: fichas anteriores al ancla, crecen hacia la izq ---
        borde_izq = x_centro - paso0 / 2               # Extremo izquierdo ocupado
        # Fichas [indice-1, indice-2, ..., 0] (del ancla hacia afuera).
        # OJO: no usar [indice-1::-1] porque con indice=0 recorreria toda la
        # lista. Construimos la sublista explicita para evitar ese caso.
        rama_izquierda = self.tablero[:indice][::-1]
        self._extender_rama(
            rama_izquierda,"izq",borde_izq,y_inicial,
            largo,corto,sep,limites,placements,
        )
        # Ajustamos el Canvas para que quepa toda la serpiente verticalmente
        max_cy = max(cy for _,_,cy in placements)
        alto_necesario = int(max_cy + largo / 2 + sep)
        if self.zona_tablero.winfo_height() < alto_necesario:
            self.zona_tablero.config(height=alto_necesario)
        # Dibujamos todas las fichas
        for imagen,cx,cy in placements:
            self.zona_tablero.create_image(cx,cy,image=imagen)
#
    def _extender_rama(self,fichas,sentido_h,borde_x,borde_y,largo,corto,
                       sep,limites,placements):
        '''Coloca una rama de la serpiente con tramos horizontales y verticales.

        Recorrido en zig-zag descendente (como un domino real):
        - Tramo HORIZONTAL (H): las fichas van tumbadas (este-oeste) segun el
          sentido ("der" o "izq"). Al llegar al limite lateral, se pasa a...
        - Tramo VERTICAL (V): las fichas se ponen de pie y BAJAN por el lateral
          hasta el limite inferior. Alli se vuelve a HORIZONTAL, pero en sentido
          contrario, y asi sucesivamente.

        Regla de los DOBLES: se colocan al reves de la orientacion del tramo en
        curso (en H -> el doble va vertical; en V -> el doble va horizontal),
        SALVO cuando el doble es la PRIMERA ficha de un cambio de orientacion
        (la ficha de la esquina), que se alinea con el nuevo tramo.

        Parametros:
        - 'fichas': fichas de la rama, del ancla hacia afuera.
        - 'sentido_h': sentido horizontal inicial ("der" o "izq").
        - 'borde_x','borde_y': punto de conexion libre del extremo actual.
        '''
        # ---- Modelo geometrico ----
        # Cada ficha se dibuja centrada en (cx, cy). Segun su orientacion ocupa
        # un rectangulo (ancho x alto):
        #   - TUMBADA (horizontal): ancho=largo, alto=corto      -> angulos 90/270
        #   - DE PIE  (vertical)  : ancho=corto, alto=largo      -> angulos 0/180
        # Un DOBLE va PERPENDICULAR al tramo; una ficha NORMAL va ALINEADA con el
        # tramo. La ficha de ESQUINA (1a de un cambio de orientacion) se comporta
        # al reves: se alinea con el nuevo tramo aunque sea doble.
        #
        # Estado del recorrido:
        #   tramo   : "H" (horizontal) o "V" (vertical, bajando)
        #   sentido : en H, "der" o "izq" (hacia donde crece la fila)
        #   bx      : en H, X del borde EXTERIOR ocupado por la fila (por donde
        #             continua creciendo); en V, X (centro) del lateral que baja.
        #   by      : en H, Y de la LINEA CENTRAL de la fila; en V, borde INFERIOR
        #             ocupado (por donde continua bajando).
        #   fila_inf: Y mas bajo REAL de la fila H en curso (un doble de pie
        #             sobresale hasta by + largo/2). Evita que el giro hacia abajo
        #             se monte sobre ese doble.
        tramo = "H"
        sentido = sentido_h
        rama = sentido_h            # "der"/"izq": valor que conecta hacia el centro
        bx,by = borde_x,borde_y
        fila_inf = by + corto / 2
        # Extremos laterales REALES de la columna vertical en curso. Una ficha de
        # pie ocupa 'corto' de ancho, pero un DOBLE normal en V va TUMBADO y
        # sobresale 'largo/2' a cada lado. Guardamos hasta donde llega la columna
        # por la derecha y por la izquierda para que, al girar a horizontal, la
        # esquina no se monte sobre un doble que sobresalga.
        col_der = bx + corto / 2
        col_izq = bx - corto / 2
        # 'proxima_esquina' marca que la SIGUIENTE ficha inicia un nuevo tramo.
        proxima_esquina = False
        for ficha in fichas:
            clave = self.clave_de_ficha(ficha)
            es_doble = ficha[0] == ficha[1]
            menor = min(ficha[0],ficha[1])
            # Valor que CONECTA hacia el centro (ficha anterior de la cadena):
            # ficha[0] en la rama derecha, ficha[1] en la rama izquierda.
            vc = ficha[0] if rama == "der" else ficha[1]
            es_esquina = proxima_esquina
            proxima_esquina = False
            if tramo == "H":
                # Ancho que ocupa la ficha a lo largo de la fila:
                #   normal -> largo (tumbada) ; esquina -> largo (alineada al
                #   nuevo tramo H) ; doble normal -> corto (de pie, perpendicular).
                ancho = corto if (es_doble and not es_esquina) else largo
                limite = limites[sentido]
                cabe = (bx + ancho <= limite) if sentido == "der" \
                                              else (bx - ancho >= limite)
                if cabe:
                    # Ficha adosada al borde exterior de la fila.
                    cx = (bx + ancho / 2) if sentido == "der" else (bx - ancho / 2)
                    cy = by
                    imagen = self._imagen_orientada(
                        clave,es_doble,menor,vc,"H",sentido,es_esquina
                    )
                    placements.append((imagen,cx,cy))
                    bx = (bx + ancho) if sentido == "der" else (bx - ancho)
                    # Alto real por debajo de la linea central: de pie (doble
                    # normal) -> largo/2 ; tumbada -> corto/2. Lo registramos para
                    # que un giro hacia abajo posterior no se monte sobre el.
                    medio_alto = (largo / 2) if (es_doble and not es_esquina) \
                                             else (corto / 2)
                    fila_inf = max(fila_inf,cy + medio_alto)
                else:
                    # No cabe mas fila: GIRAMOS a tramo VERTICAL. La ficha actual
                    # es la esquina y baja por el lateral alineada al nuevo tramo.
                    tramo = "V"
                    es_esquina = True
                    imagen = self._imagen_orientada(
                        clave,es_doble,menor,vc,"V","abajo",True
                    )
                    # La esquina se ALINEA con el nuevo tramo V: SIEMPRE va DE PIE
                    # (tanto normal como doble), ocupando corto x largo.
                    med_ancho = corto / 2
                    med_alto = largo / 2
                    # Centro X retranqueado medio-ancho desde el borde exterior,
                    # de modo que la esquina quede alineada con el lateral.
                    cx = (bx - med_ancho) if sentido == "der" else (bx + med_ancho)
                    # Justo por debajo del punto mas bajo real de la fila.
                    cy = fila_inf + sep + med_alto
                    placements.append((imagen,cx,cy))
                    bx = cx                    # Bajamos por la columna centrada en cx
                    by = cy + med_alto         # Borde inferior ocupado
                    # Nueva columna: la esquina va de pie (ancho 'corto').
                    col_der = cx + corto / 2
                    col_izq = cx - corto / 2
                    # El siguiente tramo horizontal ira en sentido CONTRARIO.
                    sentido = "izq" if sentido == "der" else "der"
            else:  # tramo == "V" (bajando)
                # Alto que ocupa la ficha a lo largo de la columna:
                #   normal -> largo (de pie) ; esquina -> largo (alineada al nuevo
                #   tramo V) ; doble normal -> corto (tumbado, perpendicular).
                alto = corto if (es_doble and not es_esquina) else largo
                if by + alto <= limites["inf"]:
                    # Sigue bajando: ficha adosada por debajo del borde inferior.
                    cx = bx
                    cy = by + alto / 2
                    imagen = self._imagen_orientada(
                        clave,es_doble,menor,vc,"V","abajo",es_esquina
                    )
                    placements.append((imagen,cx,cy))
                    by = by + alto
                    # Ancho real de la ficha a cada lado del eje de la columna:
                    #   doble normal (tumbado) -> largo/2 ; de pie -> corto/2.
                    medio_ancho = (largo / 2) if (es_doble and not es_esquina) \
                                              else (corto / 2)
                    col_der = max(col_der,cx + medio_ancho)
                    col_izq = min(col_izq,cx - medio_ancho)
                else:
                    # No cabe mas abajo: GIRAMOS a tramo HORIZONTAL en el sentido
                    # ya invertido. La ficha actual es la esquina.
                    tramo = "H"
                    es_esquina = True
                    imagen = self._imagen_orientada(
                        clave,es_doble,menor,vc,"H",sentido,True
                    )
                    # La esquina se ALINEA con el nuevo tramo H: SIEMPRE va TUMBADA
                    # (tanto normal como doble), ocupando largo x corto.
                    med_ancho = largo / 2
                    med_alto = corto / 2
                    # La esquina se ALINEA con la nueva fila: su borde INFERIOR
                    # coincide con el de la columna (by), de modo que forma la
                    # base de la 'L'. Por tanto su centro sube 'med_alto'.
                    cy = by - med_alto
                    # Se coloca JUSTO al lado de la columna (mas la separacion),
                    # usando el extremo lateral REAL (col_der/col_izq) para no
                    # montarse sobre un DOBLE tumbado que sobresalga de la columna.
                    borde_col = col_der if sentido == "der" else col_izq
                    cx = (borde_col + sep + med_ancho) if sentido == "der" \
                                                       else (borde_col - sep - med_ancho)
                    placements.append((imagen,cx,cy))
                    # Nuevo estado horizontal: el borde exterior de la fila queda
                    # en el extremo mas alejado de la esquina.
                    bx = (cx + med_ancho) if sentido == "der" else (cx - med_ancho)
                    by = cy
                    # Reiniciamos el borde inferior real de la nueva fila.
                    fila_inf = cy + med_alto
#
    def _imagen_orientada(self,clave,es_doble,menor,vc,tramo,sentido,
                          es_esquina):
        '''Devuelve la imagen de la ficha con la orientacion adecuada.

        Parametros:
        - 'menor': el valor menor de la ficha (para elegir el giro).
        - 'vc': valor que CONECTA hacia la ficha vecina del centro.
        - 'tramo': "H" (horizontal) o "V" (vertical, bajando).
        - 'sentido': en H, "der" o "izq"; en V no se usa.
        - 'es_esquina': True si es la 1ª ficha de un cambio de orientacion.

        Angulos de la imagen base (vertical, menor arriba):
          0 -> menor arriba ; 180 -> mayor arriba ;
          90 -> menor izquierda ; 270 -> menor derecha.

        Fichas normales: se orientan para que 'vc' quede del lado que conecta
        (izquierda/derecha en H, arriba en V).
        Fichas DOBLES: van PERPENDICULARES al tramo, salvo si son esquina, en
        cuyo caso se alinean CON el tramo.
        '''
        variantes = self.imagen_ficha_orientada[clave]
        if es_doble:
            if tramo == "H":
                # Perpendicular a H = vertical (0). Esquina = alineada H (90).
                return variantes[90] if es_esquina else variantes[0]
            else:  # tramo == "V"
                # Perpendicular a V = horizontal (90). Esquina = alineada V (0).
                return variantes[0] if es_esquina else variantes[90]
        # Ficha normal: colocar 'vc' del lado que conecta
        if tramo == "H":
            if sentido == "der":
                # vc a la IZQUIERDA
                return variantes[90] if vc == menor else variantes[270]
            else:  # "izq": vc a la DERECHA
                return variantes[270] if vc == menor else variantes[90]
        # tramo == "V" (bajando): vc ARRIBA
        return variantes[0] if vc == menor else variantes[180]
#
    def _colocar_ficha(self,ficha,extremo):
        '''Coloca una ficha en el tablero manteniendo el ancla (indice_inicial).

        Al colocar por el extremo IZQUIERDO, domino.colocar_ficha inserta la
        ficha en la posicion 0, por lo que todos los indices se desplazan +1.
        Actualizamos indice_inicial para que siga apuntando a la MISMA ficha
        fisica y las fichas ya dibujadas no cambien de sitio.
        '''
        colocar_ficha(self.tablero,ficha,extremo)
        if extremo == "izq":
            self.indice_inicial += 1
        # Sonido al poner ficha (lo comparten la CPU y el jugador).
        self.sonido_poner.play()
#
    def click_ficha_jugador(self,ficha):
        '''Gestiona el clic sobre una ficha del jugador para colocarla.'''
        if self.fin_partida or self.turno != "jugador":
            return
        # Si el jugador ya esta eligiendo el extremo de otra ficha, ignoramos
        # nuevos clics hasta que decida (o cancele) la eleccion en curso.
        if getattr(self,"eligiendo_extremo",False):
            return
        extremos = ficha_encaja(ficha,self.tablero)
        if not extremos:
            self.mostrar_info("Esa ficha no encaja. Elige otra.")
            return
        # Si encaja por AMBOS extremos, normalmente dejamos que el jugador elija
        # el lado. Pero si los dos extremos libres del tablero tienen el MISMO
        # valor (p.ej. la primera ficha, cuando el ancla es un doble), colocar
        # por un lado u otro es indistinto: la ponemos por la izquierda sin
        # preguntar.
        if len(extremos) == 2:
            valor_izq = self.tablero[0][0]
            valor_der = self.tablero[-1][1]
            if valor_izq == valor_der:
                self.colocar_ficha_jugador(ficha,"izq")
                return
            # Los extremos son distintos: resaltamos la ficha y dejamos que el
            # jugador elija con el raton en que lado colocarla.
            self.pedir_extremo(ficha)
            return
        # Encaja por un solo extremo: se coloca directamente.
        self.colocar_ficha_jugador(ficha,extremos[0])
#
    def colocar_ficha_jugador(self,ficha,extremo):
        '''Coloca la ficha del jugador en el extremo indicado y pasa turno.'''
        self.jugador.remove(ficha)
        self._colocar_ficha(ficha,extremo)
        self.pasos_seguidos = 0
        self.refrescar_pantalla()
        if self.comprobar_fin("jugador"):
            return
        # Pasa el turno a la CPU tras un retardo de segundo y medio (sin
        # bloquear la ventana), para que se vea la ficha recien colocada.
        self.turno = "cpu"
        self.mostrar_info("Turno de la CPU...")
        self.root.after(1500,self.turno_cpu_grafico)
#
    def habilitar_botones_extremo(self,activar):
        '''Activa o desactiva los botones Izquierda / Derecha / Cancelar.

        Los botones estan siempre visibles: se activan solo cuando el jugador
        debe elegir en que extremo colocar una ficha que encaja por los dos
        lados; el resto del tiempo permanecen desactivados.
        '''
        estado = "normal" if activar else "disabled"
        for boton in (
            getattr(self,"btn_izq",None),
            getattr(self,"btn_der",None),
            getattr(self,"btn_cancelar",None),
        ):
            if boton is not None:
                boton.config(state=estado)
#
    def pedir_extremo(self,ficha):
        '''Resalta la ficha y activa los botones para elegir el extremo.

        Se usa cuando la ficha pulsada encaja por los dos extremos del tablero.
        El jugador elige con el raton "Izquierda" o "Derecha" (o "Cancelar").
        '''
        self.eligiendo_extremo = True
        self.ficha_a_elegir = ficha
        # Resaltamos la ficha elegida en la mano del jugador.
        etiqueta = self.etiquetas_jugador.get(ficha)
        if etiqueta is not None:
            etiqueta.config(
                bd=3,
                relief="raised",
                highlightthickness=3,
                highlightbackground="gold",
                highlightcolor="gold",
            )
        self.mostrar_info("Esa ficha encaja en los dos lados. Elige donde colocarla.")
        # Activamos los botones fijos para que el jugador decida el extremo.
        self.habilitar_botones_extremo(True)
#
    def cerrar_panel_extremos(self):
        '''Desactiva los botones de eleccion de extremo y limpia el estado.'''
        self.habilitar_botones_extremo(False)
        self.eligiendo_extremo = False
        self.ficha_a_elegir = None
#
    def cancelar_extremo(self):
        '''Cancela la eleccion de extremo: la ficha vuelve a su estado normal.'''
        self.cerrar_panel_extremos()
        # Al refrescar, la mano se redibuja sin el resaltado.
        self.refrescar_pantalla()
        self.mostrar_info("Tu turno: pulsa una ficha para colocarla")
#
    def elegir_extremo(self,extremo):
        '''Coloca la ficha pendiente en el extremo elegido con el raton.'''
        ficha = getattr(self,"ficha_a_elegir",None)
        self.cerrar_panel_extremos()
        if ficha is None or self.fin_partida or self.turno != "jugador":
            return
        self.colocar_ficha_jugador(ficha,extremo)
#
    def robar_jugador(self):
        '''El jugador roba del mazo si no tiene jugada; devuelve False si pasa.'''
        while not tiene_jugada(self.jugador,self.tablero):
            if self.mazo:
                self.jugador.append(self.mazo.pop(0))
                self.jugador.sort()
            else:
                return False        # No puede jugar ni robar: pasa turno
        return True                 # Ya tiene una ficha colocable
#
    def robar_jugador_paso(self):
        '''Roba UNA ficha del mazo para el jugador (paso a paso, con retardo).

        Si el jugador ya puede jugar, muestra el mensaje de su turno. Si no,
        roba una ficha (mostrando el mensaje) y programa el siguiente paso tras
        segundo y medio. Si no puede jugar ni robar, pasa el turno a la CPU. De
        este modo cada robo es visible en pantalla antes de continuar.
        '''
        if self.fin_partida:
            return
        if tiene_jugada(self.jugador,self.tablero):
            # Ya tiene una ficha colocable: le toca jugar.
            self.refrescar_pantalla()
            self.mostrar_info("Tu turno: pulsa una ficha para colocarla")
            return
        if self.mazo:
            # No tiene jugada pero queda mazo: roba una ficha y reintenta luego.
            self.mostrar_info("Robas del mazo")
            self.jugador.append(self.mazo.pop(0))
            self.jugador.sort()
            self.refrescar_pantalla()
            self.sonido_robar.play()
            self.root.after(1500,self.robar_jugador_paso)
            return
        # No puede jugar ni robar: pasa el turno a la CPU.
        self.refrescar_pantalla()
        self.pasos_seguidos += 1
        self.mostrar_info("No puedes jugar ni robar: pasas turno")
        if self.pasos_seguidos >= 2:
            self.root.after(1500,self.terminar_por_cierre)
            return
        self.turno = "cpu"
        self.root.after(1500,self.turno_cpu_grafico)
#
    def turno_cpu_grafico(self):
        '''Ejecuta el turno de la CPU usando la logica de domino.py.

        Cada accion (colocar, robar del mazo o pasar) muestra su mensaje y deja
        un retardo de segundo y medio antes de continuar, para que se vea en
        pantalla lo que ocurre. El robo del mazo se hace ficha a ficha con ese
        retardo.
        '''
        if self.fin_partida:
            return
        ficha,extremo,valor = buscar_jugada_cpu(self.cpu,self.tablero)
        if ficha is not None:
            # La CPU tiene jugada: coloca la ficha.
            self.cpu.remove(ficha)
            # Valor del tablero por el que conecta la ficha (ANTES de colocarla,
            # porque _colocar_ficha modifica self.tablero). Si conecta por el
            # extremo izquierdo es tablero[0][0]; si por el derecho, tablero[-1][1].
            valor_conexion = self.tablero[0][0] if extremo == "izq" \
                                                else self.tablero[-1][1]
            # Orientamos la ficha para el mensaje: el valor que CONECTA se muestra
            # primero (p.ej. si coloca la 3,5 por el 5, se muestra como 5,3).
            if ficha[0] == valor_conexion:
                ficha_mostrada = ficha
            else:
                ficha_mostrada = (ficha[1],ficha[0])
            self._colocar_ficha(ficha,extremo)
            self.cpu.sort()
            self.pasos_seguidos = 0
            self.refrescar_pantalla()
            self.mostrar_info(f"La CPU coloca {ficha_mostrada}")
            if self.comprobar_fin("cpu"):
                return
            # Tras mostrar el mensaje, esperamos segundo y medio antes de dar el
            # turno al jugador.
            self.root.after(1500,self.preparar_turno_jugador)
            return
        if self.mazo:
            # No puede jugar pero queda mazo: roba una ficha, muestra el mensaje
            # y vuelve a intentarlo tras segundo y medio.
            self.mostrar_info("La CPU roba del mazo")
            self.cpu.append(self.mazo.pop(0))
            self.cpu.sort()
            self.refrescar_pantalla()
            self.sonido_robar.play()
            self.root.after(1500,self.turno_cpu_grafico)
            return
        # No puede jugar y no hay mazo: pasa turno.
        self.pasos_seguidos += 1
        self.mostrar_info("La CPU pasa turno")
        if self.pasos_seguidos >= 2:
            self.root.after(1500,self.terminar_por_cierre)
            return
        # Turno del jugador: si no tiene jugada, roba automaticamente o pasa
        self.root.after(1500,self.preparar_turno_jugador)
#
    def preparar_turno_jugador(self):
        '''Prepara el turno del jugador.

        Si el jugador no tiene ninguna ficha colocable, roba del mazo
        automaticamente hasta poder jugar. Si no puede robar (mazo vacio),
        pasa el turno a la CPU. Este metodo se usa tanto tras el turno de la
        CPU como al iniciar la partida cuando empieza el jugador (por ejemplo,
        cuando la CPU sale con un doble y el jugador no puede encajar).
        '''
        if self.fin_partida:
            return
        self.turno = "jugador"
        # El robo (o el paso de turno) se hace paso a paso con un retardo de
        # segundo y medio por cada accion, para que se vea en pantalla lo que ocurre.
        self.robar_jugador_paso()
#
    def comprobar_fin(self,quien):
        '''Comprueba si 'quien' se quedo sin fichas (gana la partida).

        Al ganar, el ganador suma 100 puntos a su marcador mas
        los puntos de las fichas que le quedan al perdedor en la mano.
        '''
        if quien == "jugador" and not self.jugador:
            self.puntos_jugador += 100          # 100 puntos por ganar
            puntos = sumar_puntos(self.cpu)     # + los puntos de las fichas del perdedor (CPU)
            self.puntos_jugador += puntos
            self.fin_partida = True
            # La partida ha finalizado: reactivamos la opcion "Nuevo"
            self.activar_menu_nuevo(True)
            self.actualizar_contadores()
            # Al terminar, descubrimos las fichas de la CPU y del mazo
            self.refrescar_pantalla()
            self.mostrar_info(
                f"Te has quedado sin fichas. GANAS! (+{100+puntos} puntos)"
            )
            titulo = "Fin"
            mensaje = f"Te has quedado sin fichas.\nGANAS!\n"
            mensaje += f"Sumas {puntos} puntos de las fichas de la CPU."
            mostrar_mensaje(self.root,titulo,mensaje,tipo="info",ancho=400,alto=200,auto_cerrar=0)
            return True
        if quien == "cpu" and not self.cpu:
            self.puntos_cpu += 100                # 100 puntos por ganar
            puntos = sumar_puntos(self.jugador)   # + los puntos de las fichas del perdedor (jugador)
            self.puntos_cpu += puntos
            self.fin_partida = True
            # La partida ha finalizado: reactivamos la opcion "Nuevo"
            self.activar_menu_nuevo(True)
            self.actualizar_contadores()
            # Al terminar, descubrimos las fichas de la CPU y del mazo
            self.refrescar_pantalla()
            self.mostrar_info(
                f"La CPU se quedo sin fichas. Gana la CPU. (+{100+puntos} puntos)"
            )
            titulo = "Fin"
            mensaje = f"La CPU se ha quedado sin fichas.\nGana la CPU.\n"
            mensaje += f"La CPU suma {puntos} puntos de tus fichas."
            mostrar_mensaje(self.root,titulo,mensaje,tipo="info",ancho=400,alto=200,auto_cerrar=0)
            return True
        return False
#
    def terminar_por_cierre(self):
        '''Partida cerrada (ambos pasan): gana quien tenga menos puntos.'''
        self.fin_partida = True
        # La partida ha finalizado: reactivamos la opcion "Nuevo"
        self.activar_menu_nuevo(True)
        puntos_j = sumar_puntos(self.jugador)
        puntos_c = sumar_puntos(self.cpu)
        if puntos_j < puntos_c:
            # Gana el jugador (menos puntos): suma los puntos del perdedor (CPU)
            self.puntos_jugador += puntos_c
            self.puntos_cpu += puntos_j
            resultado = (
                f"Juego cerrado. GANAS tu (menos puntos).\n"
                f"Sumas {puntos_c} puntos de las fichas de la CPU.\n"
                f"La CPU suma {puntos_j} puntos de tus fichas."
            )
        elif puntos_c < puntos_j:
            # Gana la CPU (menos puntos): suma los puntos del perdedor (jugador)
            self.puntos_cpu += puntos_j
            self.puntos_jugador += puntos_c
            resultado = (
                f"Juego cerrado. Gana la CPU (menos puntos).\n"
                f"La CPU suma {puntos_j} puntos de tus fichas.\n"
                f"Sumas {puntos_c} puntos de las fichas de la CPU."
            )
        else:
            # Empate de puntos: se cruzan los puntos (cada uno recibe los del otro)
            self.puntos_jugador += puntos_c
            self.puntos_cpu += puntos_j
            resultado = (
                f"Juego cerrado. EMPATE: se cruzan los puntos.\n"
                f"Sumas {puntos_c} puntos y la CPU suma {puntos_j} puntos."
            )
        self.actualizar_contadores()
        # Al terminar, descubrimos las fichas de la CPU y del mazo
        self.refrescar_pantalla()
        self.mostrar_info(resultado)
        titulo = "Fin"
        mensaje = f"{resultado}\n\nTus puntos: {puntos_j}\nPuntos CPU: {puntos_c}"
        mostrar_mensaje(self.root,titulo,resultado,tipo="info",ancho=400,alto=200,auto_cerrar=0)
#
    # Cerrar aplicacion
    def salir(self):
        '''Cierra la aplicacion.'''
        self.root.destroy()
        py.quit()
#
    # Mostrar la ayuda del juego
    def mostrar_ayuda(self):
        """Muestra la ventana de ayuda del juego"""
        ayuda_ancho = 800
        ayuda_alto = 700
#
        ayuda_win = tk.Toplevel(self.root)
        ayuda_win.withdraw()
        ayuda_win.title(f"Ayuda - {TITULO}")
        ayuda_win.geometry(f"{ayuda_ancho}x{ayuda_alto}")
        ayuda_win.config(bg="white")
        ayuda_win.resizable(True,True)
        ayuda_win.iconbitmap(ICONO)
        ayuda_win.transient(self.root)
        centrar_ventana(ayuda_win,ayuda_ancho,ayuda_alto)
        ayuda_win.deiconify()
#
        # Frame principal
        frame_ayuda = tk.Frame(ayuda_win,bg="white")
        frame_ayuda.pack(fill="both",expand=True,padx=10,pady=10)
#
        # Título
        tk.Label(frame_ayuda,text=f"Ayuda - {TITULO}",
                 font="Arial 16 bold",bg="white",fg="#2196F3").pack(pady=10)
#
        # Área de texto con scroll
        text_area = scrolledtext.ScrolledText(frame_ayuda,wrap=tk.WORD,
                                              font="Consolas 14",
                                              bg="#f5f5f5",fg="black")
        text_area.pack(fill="both",expand=True,padx=5,pady=5)
#
        # Leer y mostrar el archivo de ayuda
        try:
            ruta_ayuda = RUTA_TXT + "ayuda.txt"
            with open(ruta_ayuda,'r',encoding='utf-8') as f:
                contenido = f.read()
                text_area.insert(1.0,contenido)
                text_area.config(state='disabled')  # Solo lectura
        except FileNotFoundError:
            text_area.insert(1.0,"Error: No se encontró el archivo de ayuda.")
            text_area.config(state='disabled')
#
        # Botón cerrar
        btn_cerrar = tk.Button(frame_ayuda,text="Cerrar",font="Arial 12 bold",
                               bg="#f44336",fg="white",command=ayuda_win.destroy)
        btn_cerrar.pack(pady=10)
        btn_cerrar.bind("<Return>",lambda event: ayuda_win.destroy())
        btn_cerrar.focus_set()
#
    # Mostrar Acerca de ...
    def acerca_de(self):
        """Muestra información sobre la aplicación"""
        # Crear ventana Acerca de
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()  # Ocultar temporalmente
        ventana.title("Acerca de")
        ventana.geometry("500x300")
        ventana.resizable(False,False)
        ventana.iconbitmap(RUTA_IMAGENES + "icono.ico")
#
        # Frame principal
        frame = ttk.Frame(ventana,padding="30")
        frame.pack(fill=tk.BOTH,expand=True)
#
        # Título
        ttk.Label(
            frame,
            text=f"🁫 {TITULO}",
            font=('Segoe UI',14,'bold')
        ).pack(pady=(0,20))
#
        # Información
        info_text = [
            f"Versión {VERSION}",
            "",
            "Desarrollado con Python y Tkinter",
            "",
            f"{AUTOR} © 2026"
        ]
#
        for linea in info_text:
            ttk.Label(
                frame,
                text=linea,
                font=('Segoe UI',9)
            ).pack(pady=2)
#
        # Botón cerrar
        ttk.Button(
            frame,
            text="Cerrar",
            command=ventana.destroy,
            width=15
        ).pack(pady=(20,0))
#
        # Centrar ventana respecto a la ventana padre
        ventana.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (ventana.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (ventana.winfo_height() // 2)
        ventana.geometry(f'+{x}+{y}')
#
        # Mostrar ventana ya centrada
        ventana.deiconify()
#
        # Hacer modal
        ventana.transient(self.root)
        ventana.grab_set()
#
# Bucle principal de la aplicacion
def main():
    py.init()
    py.mixer.init()
    root = tk.Tk()
    JuegoDomino(root)
    root.mainloop()
#
# Punto de entrada del programa
if __name__ == "__main__":
    main()
#