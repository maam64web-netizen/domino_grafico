'''
Domino

Juego de Domino en terminal.
'''
#
from queue import Queue
import random as rd
from imagen_ficha import *
from constantes import *
#
def crear_fichas(root=None):
    # Carga todas las imagenes de las fichas y las guarda en un diccionario.
    # La clave es "00", "01" ... "66" y el valor la imagen (ImageTk.PhotoImage).
    #
    # ImageTk.PhotoImage necesita una raiz de Tkinter creada. Si no se pasa
    # ninguna, se crea una oculta para poder generar las imagenes.
    if root is None:
        root = tk.Tk()
        root.withdraw()
    #
    imagen_ficha = {}                           # Diccionario con las imagenes de las fichas
    for i in range(7):                          # Bucle externo para el primer numero (de 0 a 6)
        for j in range(i,7):                    # Bucle interno que empieza en 'i' para evitar duplicados
            ficha = ImagenFicha(i,j)            # Creamos la ficha (carga su imagen)
            imagen_ficha[ficha.clave] = ficha.imagen
    #
    # Terminado el bucle, generamos tambien la "99": la ficha vuelta
    ruta_vuelta = os.path.join(RUTA_IMAGENES,"99.png")
    imagen_ficha["99"] = ImageTk.PhotoImage(Image.open(ruta_vuelta))
    #
    return imagen_ficha
#
def repartir_fichas(fichas):
    fichas_mezcladas = list(fichas)             # Copia para no modificar la lista original
    rd.shuffle(fichas_mezcladas)                # Mezclamos las fichas aleatoriamente
    jugador = sorted(fichas_mezcladas[0:7])     # Primeras 7 fichas para el jugador (ordenadas)
    cpu = sorted(fichas_mezcladas[7:14])        # Siguientes 7 fichas para la cpu (ordenadas)
    mazo = fichas_mezcladas[14:]                # El resto queda en el mazo
    return jugador,cpu,mazo
#
def buscar_ficha_inicial(mano):
    # Devuelve la mejor ficha para empezar de una mano y un valor de prioridad.
    # Un doble siempre tiene prioridad sobre cualquier ficha no doble.
    mejor_ficha = None
    mejor_valor = -1          # Prioridad de la mejor ficha encontrada
    for ficha in mano:
        a = ficha[0]
        b = ficha[1]
        if a == b:                    # Es un doble
            valor = 100 + a           # Los dobles tienen prioridad alta (100 + su valor)
        else:                         # No es un doble
            valor = a + b             # Prioridad = suma de sus dos valores
        if valor > mejor_valor:
            mejor_valor = valor
            mejor_ficha = ficha
    return mejor_ficha,mejor_valor
#
def extremo_izq(tablero):
    # Valor libre del extremo izquierdo del tablero.
    return tablero[0][0]
#
def extremo_der(tablero):
    # Valor libre del extremo derecho del tablero.
    return tablero[-1][1]
#
def ficha_encaja(ficha,tablero):
    # Devuelve una lista con los extremos ("izq"/"der") donde encaja la ficha.
    a = ficha[0]
    b = ficha[1]
    izq = extremo_izq(tablero)
    der = extremo_der(tablero)
    extremos = []
    if a == izq or b == izq:      # Encaja por el extremo izquierdo
        extremos.append("izq")
    if a == der or b == der:      # Encaja por el extremo derecho
        extremos.append("der")
    return extremos
#
def colocar_ficha(tablero,ficha,extremo):
    # Coloca la ficha en el extremo indicado, orientandola correctamente,
    # y la guarda en el tablero como una tupla (izq,der).
    a = ficha[0]
    b = ficha[1]
    if extremo == "izq":
        valor_extremo = extremo_izq(tablero)
        # El valor que casa con el tablero va hacia adentro (a la derecha de la tupla);
        # el otro queda como nuevo extremo (a la izquierda de la tupla).
        nuevo_extremo = b if a == valor_extremo else a
        tablero.insert(0,(nuevo_extremo,valor_extremo))
    else:  # extremo == "der"
        valor_extremo = extremo_der(tablero)
        # El valor que casa va hacia adentro (izquierda de la tupla); el otro queda como extremo.
        nuevo_extremo = b if a == valor_extremo else a
        tablero.append((valor_extremo,nuevo_extremo))
#
def tiene_jugada(mano,tablero):
    # Comprueba si en la mano hay alguna ficha que se pueda colocar.
    for ficha in mano:
        if ficha_encaja(ficha,tablero):
            return True
    return False
#
def buscar_jugada_cpu(cpu,tablero):
    # Busca la ficha mas alta (mayor suma) que la cpu pueda colocar en algun extremo.
    # Devuelve (ficha, extremo, valor) o (None, None, -1) si no puede jugar.
    mejor_ficha = None
    mejor_extremo = None
    mejor_valor = -1
    for ficha in cpu:
        extremos = ficha_encaja(ficha,tablero)
        if extremos:                          # La ficha se puede colocar
            valor = ficha[0] + ficha[1]       # Suma de sus valores
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_ficha = ficha
                mejor_extremo = extremos[0]   # Cualquiera de los extremos validos
    return mejor_ficha,mejor_extremo,mejor_valor
#
def turno_cpu(cpu,mazo,tablero):
    # La cpu juega la ficha mas alta posible. Si no puede, roba del mazo hasta
    # poder colocar una. Si no puede y el mazo esta vacio, pasa turno.
    while True:
        ficha,extremo,valor = buscar_jugada_cpu(cpu,tablero)
        if ficha is not None:                 # Puede colocar una ficha
            cpu.remove(ficha)
            colocar_ficha(tablero,ficha,extremo)
            cpu.sort()                        # Reclasificamos (ordenamos) la mano de la cpu
            print("La CPU coloca la ficha",ficha,"por el extremo",extremo)
            return False                      # No pasa turno
        # No puede colocar: intenta robar del mazo
        if mazo:
            robada = mazo.pop(0)              # Coge la primera del mazo
            cpu.append(robada)
            cpu.sort()                        # Volvemos a clasificar las fichas de la cpu
            print("La CPU roba una ficha del mazo")
        else:
            print("La CPU no puede jugar y no hay fichas en el mazo: pasa turno")
            return True                       # Pasa turno
#
def turno_jugador(jugador,mazo,tablero):
    # Si el jugador no tiene ficha colocable, roba hasta encontrar una (o hasta
    # que el mazo se agote). Luego se le pregunta que ficha quiere poner.
    while not tiene_jugada(jugador,tablero):
        if mazo:
            robada = mazo.pop(0)              # Roba la primera del mazo
            jugador.append(robada)
            jugador.sort()
            print("No tienes ficha para colocar. Robas del mazo:",robada)
        else:
            print("No puedes jugar y no hay fichas en el mazo: pasas turno")
            return True                       # Pasa turno
    # El jugador tiene al menos una ficha colocable: le preguntamos cual
    while True:
        print("Tablero:",tablero)
        print("Tus fichas:")
        for i in range(len(jugador)):
            print(" ",i + 1,"->",jugador[i])   # Mostramos con indice basado en 1
        eleccion = input("Que ficha quieres poner? (numero): ")
        if not eleccion.isdigit():
            print("Entrada no valida. Introduce un numero.")
            continue
        indice = int(eleccion) - 1               # El usuario elige indice de la lista - 1
        if indice < 0 or indice >= len(jugador):
            print("Numero fuera de rango. Intentalo de nuevo.")
            continue
        ficha = jugador[indice]
        extremos = ficha_encaja(ficha,tablero)
        if not extremos:
            print("Esa ficha no se puede colocar. Elige otra.")
            continue
        # Si encaja en los dos extremos, preguntamos por que lado
        if len(extremos) == 2:
            lado = input("Por que extremo? (izq/der): ").strip().lower()
            if lado not in ("izq","der"):
                print("Extremo no valido. Intentalo de nuevo.")
                continue
        else:
            lado = extremos[0]
        jugador.remove(ficha)
        colocar_ficha(tablero,ficha,lado)
        print("Colocas la ficha",ficha,"por el extremo",lado)
        return False                             # No pasa turno
#
def iniciar_juego(jugador,cpu):
    # Buscamos la mejor ficha de inicio en cada mano
    ficha_jugador,valor_jugador = buscar_ficha_inicial(jugador)
    ficha_cpu,valor_cpu = buscar_ficha_inicial(cpu)
    # Empieza quien tenga la ficha con mayor prioridad
    if valor_jugador >= valor_cpu:
        quien_empieza = "jugador"
        ficha_inicial = ficha_jugador
        jugador.remove(ficha_inicial)     # Quitamos la ficha de la mano del jugador
    else:
        quien_empieza = "cpu"
        ficha_inicial = ficha_cpu
        cpu.remove(ficha_inicial)         # Quitamos la ficha de la mano de la cpu
    # El tablero es una lista de fichas (tuplas) ya orientadas en cadena
    tablero = [(ficha_inicial[0],ficha_inicial[1])]
    # El turno pasa al otro jugador
    turno = "cpu" if quien_empieza == "jugador" else "jugador"
    return tablero,quien_empieza,turno
#
def sumar_puntos(mano):
    # Suma los puntos de todas las fichas de una mano.
    total = 0
    for ficha in mano:
        total += ficha[0] + ficha[1]
    return total
#
def generar_fichas():
    # Genera las 28 fichas jugables del domino como tuplas de ENTEROS (a,b),
    # con a <= b. No incluye la ficha vuelta "99" (esa es solo para la imagen).
    fichas = []
    for i in range(7):                          # Primer numero (0 a 6)
        for j in range(i,7):                    # Segundo numero (evita duplicados)
            fichas.append((i,j))
    return fichas
#
def main():
    # Bucle principal del juego: reparte, inicia y alterna turnos hasta que
    # alguien se quede sin fichas o la partida quede cerrada (ambos pasan).
    # OJO: crear_fichas() devuelve un diccionario de IMAGENES con claves de
    # texto ("00", "01".."66", "99"); usarlo aqui hacia que las fichas fueran
    # cadenas y provocaba "not supported between instances of 'str' and 'int'".
    # Para la logica del juego necesitamos tuplas de enteros.
    fichas = generar_fichas()
    jugador,cpu,mazo = repartir_fichas(fichas)
    print("Reparto inicial:")
    print("Jugador:",jugador,"->",len(jugador),"fichas")
    print("CPU:    ",cpu,"->",len(cpu),"fichas")
    print("Mazo:   ",len(mazo),"fichas")
    #
    tablero,quien_empieza,turno = iniciar_juego(jugador,cpu)
    print()
    print("Empieza:",quien_empieza)
    print("Tablero:",tablero)
    #
    pasos_seguidos = 0        # Cuenta cuantos jugadores pasan seguidos
    # Si el que empieza se quedo sin fichas con la ficha inicial, gana ya
    if not jugador:
        print("\nEl jugador se ha quedado sin fichas. GANA EL JUGADOR!")
        return
    if not cpu:
        print("\nLa CPU se ha quedado sin fichas. GANA LA CPU!")
        return
    #
    while True:
        print()
        print("=== Turno de:",turno,"===")
        if turno == "cpu":
            paso = turno_cpu(cpu,mazo,tablero)
        else:
            paso = turno_jugador(jugador,mazo,tablero)
        print("Tablero:",tablero)
        print("Fichas -> Jugador:",len(jugador),"| CPU:",len(cpu),"| Mazo:",len(mazo))
        #
        # Comprobamos si el jugador actual se quedo sin fichas (ha ganado)
        if turno == "jugador" and not jugador:
            print("\nEl jugador se ha quedado sin fichas. GANA EL JUGADOR!")
            return
        if turno == "cpu" and not cpu:
            print("\nLa CPU se ha quedado sin fichas. GANA LA CPU!")
            return
        #
        # Control de partida cerrada: si ambos pasan seguidos, se cierra el juego
        if paso:
            pasos_seguidos += 1
        else:
            pasos_seguidos = 0
        if pasos_seguidos >= 2:
            print("\nJuego cerrado: ninguno puede jugar y no hay fichas en el mazo.")
            puntos_jugador = sumar_puntos(jugador)
            puntos_cpu = sumar_puntos(cpu)
            print("Puntos del jugador:",puntos_jugador)
            print("Puntos de la CPU:  ",puntos_cpu)
            if puntos_jugador < puntos_cpu:
                print("GANA EL JUGADOR! (menos puntos)")
            elif puntos_cpu < puntos_jugador:
                print("GANA LA CPU! (menos puntos)")
            else:
                print("EMPATE!")
            return
        #
        # Pasamos el turno al otro jugador
        turno = "cpu" if turno == "jugador" else "jugador"
#
if __name__ == "__main__":
    main()
#