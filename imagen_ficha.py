'''
Clase Ficha

Crea (carga) las imagenes de las fichas del domino.
- El parametro a es el primer numero y b el segundo (de 0 a 6).
- La imagen a cargar se basa en esos dos numeros: 00.png, 01.png ... 66.png
- Las imagenes cargadas se guardan en un diccionario cuya clave es
  "00", "01" ... "66" y cuyo valor es la imagen (ImageTk.PhotoImage).
- Al terminar el bucle se genera tambien la "99", que es la ficha vuelta
  (una ficha boca abajo en la que no se ven sus valores).
'''
import os
import tkinter as tk
from PIL import Image,ImageTk
from constantes import *
#
class ImagenFicha():
    def __init__(self,a,b):
        self.a = a                              # Primer numero de la ficha (0 a 6)
        self.b = b                              # Segundo numero de la ficha (0 a 6)
        menor = min(a,b)    # El nombre del fichero usa el menor primero para coincidir con
        mayor = max(a,b)    # las imagenes existentes (00.png, 01.png ... 66.png)
        self.clave = f"{menor}{mayor}"          # Clave del diccionario: "00", "01" ... "66"
        self.nombre = f"{self.clave}.png"       # Nombre del fichero de imagen
        self.ruta = os.path.join(RUTA_IMAGENES,self.nombre)
        self.imagen = ImageTk.PhotoImage(Image.open(self.ruta))
#
def crear_fichas(root=None):
    # Carga todas las imagenes de las fichas y las guarda en un diccionario.
    # La clave es "00", "01" ... "66" y el valor la imagen (ImageTk.PhotoImage).
    # Retorna un diccionario con las imagenes cargadas
#
    # ImageTk.PhotoImage necesita una raiz de Tkinter creada. Si no se pasa
    # ninguna, necesitamos crear una (oculta) para poder generar las imagenes.
    if root is None:
        root = tk.Tk()
        root.withdraw()
#
    imagen_ficha = {}                           # Creamos el diccionario vacio
    for i in range(7):                          # Bucle externo para el primer numero (de 0 a 6)
        for j in range(i,7):                    # Bucle interno que empieza en 'i' para evitar duplicados
            ficha = ImagenFicha(i,j)            # Creamos la ficha (carga su imagen)
            imagen_ficha[ficha.clave] = ficha.imagen    # Insertamos la ficha en el diccionario
#
    # Terminado el bucle, generamos tambien la "99": la ficha vuelta
    ruta_vuelta = os.path.join(RUTA_IMAGENES,"99.png")
    imagen_ficha["99"] = ImageTk.PhotoImage(Image.open(ruta_vuelta))
#
    # Retornamos el diccionario con las imagenes
    return imagen_ficha
#
def pintar_fichas(root,imagen_ficha):
    # Pinta en la ventana todas las fichas contenidas en el diccionario.
    # Se colocan en una rejilla ordenada por su clave ("00", "01" ... "66", "99").
    COLUMNAS = 8                                 # Numero de fichas por fila
#
    # Marco contenedor con algo de margen alrededor
    contenedor = tk.Frame(root,bg=TAPETE)    # Fondo verde tipo tapete
    contenedor.pack(padx=10,pady=10)
#
    claves = sorted(imagen_ficha.keys())        # Orden: "00","01"..."66","99"
    for indice,clave in enumerate(claves):
        fila = indice // COLUMNAS
        columna = indice % COLUMNAS
        # Cada ficha se muestra en un Label con un pequeno relieve
        etiqueta = tk.Label(contenedor,image=imagen_ficha[clave],
                            bg=TAPETE,bd=1,relief="solid")
        etiqueta.grid(row=fila,column=columna,padx=4,pady=4)
#
def main():
    # Creamos la ventana principal
    root = tk.Tk()
    root.title(TITULO)
    root.configure(bg=TAPETE)
    centrar_ventana(root,ANCHO,ALTO)
    root.iconbitmap(ICONO)
    #root.state('zoomed')
#
    # Creamos (cargamos) las fichas usando esta misma ventana
    imagen_ficha = crear_fichas(root)
    #print("Fichas cargadas:",len(imagen_ficha))
    #print("Claves:",sorted(imagen_ficha.keys()))
#
    # Una vez creadas las fichas, las pintamos en la ventana
    pintar_fichas(root,imagen_ficha)
#
    root.mainloop()
#
if __name__ == "__main__":
    main()
#