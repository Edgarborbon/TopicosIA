import pandas as pd
import numpy as np
import random
import math

def generarMatrizCosto(dfDistancias, dfCombustible, costoPorDistancia):
    """
    Multiplicamos la matriz de distancias con la variable costoPorDistancia definida por el usuario.
    Esta forma de "cuantificar" que movimiento conviene mas utilizando ambas matrices puede ser reemplazada por cualquiera
    que el usuario desee. Nosotros nos quedamos con esta porque era algo sencillo y entendible de tener en cuenta distancia
    y combustible a la hora de decidir a qué nodo nos moveremos.
    """
    print(f"Calculando matriz de costo con ${costoPorDistancia:.2f}/km...")
    costoTotal = dfCombustible + (dfDistancias * costoPorDistancia)
    np.fill_diagonal(costoTotal.values, np.inf)
    return costoTotal

def calcularCostoRuta(ruta, matrizCosto):
    """
    Tomamos la ruta ya definida en su respectivo método y le calculamos el costo.
    Decidimos interpretar el costo como la cantidad de dinero requerido para movernos de un lado a otro, teniendo en cuenta
    cuanto nos cuesta viajar x cantidad de kilometros.

    """
    costo = 0
    for i in range(len(ruta) - 1):
        origen = ruta[i] #origen almacenará el nodo actual dentro del ciclo, por ejemplo el nodo 1 de esta ruta puede ser el Centro 4
        destino = ruta[i+1] #destino representa el movimiento siguiente, tomando el indice actual del ciclo +1. Por ejemplo, si i=1 es Centro 4,
                            #i+1 = i=2 puede ser la Tienda 20, el destino de el movimiento i
        costo += matrizCosto.loc[origen, destino] #Al costo actual se le suma el costo de trazladarnos de origen a destino, por ejemplo
                                                  #movernos de C4 a T20 puede costar $200, y ese 200 se le suma al costo actual
    return costo

def calcularCostoSolucion(solucion, matrizCosto, mapaTiendaCentroIdeal, PENALIDAD_GEOGRAFICA):
    """
        Calculamos el costo total de la solución. 
        [ruta] es la lista con la ruta definida en la solucion. La recorremos con un for donde
        [centro] es el índice. Por cada indice, sumamos ese indice a la ruta + el costo de regresar al centro donde empezó.
        Ya teniendo la ruta completa (Centro de Distribución, todas las tiendas y al final de nuevo al centro de distribución)
        mandamos esa ruta completa al método anterior que calculará su costo.
        La variable [Penalidad] y el [mapaTiendaCentroideal] nos ayudan a darle una penalización al costo en el caso de que
        la solución haya realizado movimientos muy largos y costosos. De esta forma agregamos más costo a la solución, haciendola 
        "peor" ante los ojos del recocido.
        
    """
    costoTotal = 0
    for centro, ruta in solucion.items():
        if ruta:
            rutaCompleta = [centro] + ruta + [centro]
            costoTotal += calcularCostoRuta(rutaCompleta, matrizCosto)
            for tienda in ruta:
                if mapaTiendaCentroIdeal[tienda] != centro:
                    costoTotal += PENALIDAD_GEOGRAFICA
    return costoTotal

def generarSolucionInicial(centros, tiendas, mapaTiendaCentrosCercanos, porcentajeError=0.15):
    """
    Generamos aleatoriamente una solución errónea para usarla como punto de comparación inicial durante el recocido simulado.

    """
    print(f"Generando solución inicial con un {porcentajeError*100}% de error intencional...")
    solucion = {centro: [] for centro in centros} #Diccionario(un tipo de lista) de Python, establece cada centro como una clave
    for tienda in tiendas: #Por cada tienda, definimos los centros más cercanos para calcular cual convendría más usar
        centros_cercanos_para_tienda = mapaTiendaCentrosCercanos[tienda] # ^ 
        if random.random() < porcentajeError and len(centros_cercanos_para_tienda) > 1: #Generamos un numero entre el 0 y el 1, teniendo en cuenta el porcentaje de error, la idea de todo esto es tener un inicio erroneo
            centro_asignado = random.choice(centros_cercanos_para_tienda[1:])  # Se asigna a un centro que nunca será el mśa cercano gracias al [1:]. Tomamos el indice 1 en lugar del 0, que vendría siendo el más cercano             
        else:   #Este else significa que sí se asignará el centro más cercano. Esto es para que no todas las posiciones de esta solucion sean erroneas, teniendo así un punto de comparación inicial medianamente realista.
            centro_asignado = centros_cercanos_para_tienda[0]
        solucion[centro_asignado].append(tienda) #Se agrega la tienda a la ruta 
    for centro in centros:
        random.shuffle(solucion[centro]) #Ya generado todo, revolvemos la solucion para darle más cosas al algoritmo que optimizar. 
    return solucion

def generarVecino(solucion, mapaTiendaCentrosCercanos):
    """
   Generamos el vecino
    """
    vecinoGenerado = {k: list(v) for k, v in solucion.items()} #Los diccionarios en Python tienen CLAVES e OBJETOS, los cuales tienen asignados una clave respectivamente
    #Este ciclo explora todo el diccionario "solucion", yendo de par en par
    #En el ciclo, k funciona como el indice (La Clave, o Key) y v sería el objeto. Siguiendo esta lógica, tomaremos cada par del diccionario, osea tomar una Clave (Centro)
    #y sus objetos (Tiendas). Estos datos se asignan de la siguiente manera:
    #k:list(v) significa que k será la clave del nuevo diccionario vecinoGenerado y le asignaremos todos los datos que tomamos en v como lista, v siendo las tiendas. 
    #Todo eso genera una copia de la solucion con sus propios indices. Por la forma que opera Python, si no hacemos este proceso tan rebuscado, al modificar una ruta en
    #la solucion recibida que le pasamos a vecinoGenerado, también se modificaría en la [solucion] original que recibimos, rompiendo el recocido.
    #En pocas palabras, sin todo eso, la máquina y la memoria no podrían diferenciar [vecinoGenerado] de [solucion], cosa que nos rompió mucho la cabeza hasta que encontramos
    #esta solución 
    probabilidadRuta = 0.80  #Variable que define el margen de error que le daremos al algoritmo, puede tener cualquier valor dependiendo de si queremos que el algoritmo batalle o no
    if random.random() < probabilidadRuta:
        rutasElegibles = [centro for centro, ruta in vecinoGenerado.items() if len(ruta) >= 2] #Recorre cada ruta en el vecino generado. Si la ruta tiene 2 o mas tiendas, añade su centro a la lista de rutas elegibles para no intercambiar el orden en una ruta con menos de 2 paradas
        if not rutasElegibles: return vecinoGenerado #Si la ruta está vacia, no hay suficientes movimientos para un intercambio, por lo tanto salimos
        centroAOptimizar = random.choice(rutasElegibles) #Sacamos un centro aleatorio para optimizar
        rutaAOptimizar = vecinoGenerado[centroAOptimizar] #Buscamos en el diccionario vecinoGenerado el id del centro que acabamos de sacar, para traer las tiendas que puede abarcar
        idx1, idx2 = random.sample(range(len(rutaAOptimizar)), 2) #Elegimos 2 posiciones aleatorias de la ruta para un swap
        rutaAOptimizar[idx1], rutaAOptimizar[idx2] = rutaAOptimizar[idx2], rutaAOptimizar[idx1] #El swap en cuestión
    else:
        centrosConTiendas = [c for c, r in vecinoGenerado.items() if r]  #Creamos una lista con todos los centros con rutas no vacías, para garantizar que tenemos de donde sacar informacion
        if not centrosConTiendas: return vecinoGenerado #Salida de emergencia, si las rutas están vacías, no hay nada que mover
        centroOrigen = random.choice(centrosConTiendas) #Elegimos ruta al azar
        tiendaAMover = vecinoGenerado[centroOrigen].pop(random.randrange(len(vecinoGenerado[centroOrigen]))) #.pop elimina una posicion de la lista. Nos aseguramos que sea aleatoria y la sacamos para moverla
        centrosPermitidos = mapaTiendaCentrosCercanos[tiendaAMover] #Sacamos los centros más cercanos de la tienda que acabamos de sacar 
        centroDestino = random.choice(centrosPermitidos) #Garantizamos que la tienda se asigne solamente al centro más lógico
        puntoInsercion = random.randint(0, len(vecinoGenerado[centroDestino])) #Generamos una posicion aleatoria en la ruta del centro destino
        vecinoGenerado[centroDestino].insert(puntoInsercion, tiendaAMover) #Tomamos la tienda y la ponemos en la posicion generada dentro de la ruta
    return vecinoGenerado

def recocido(dfInfo, dfCombustible, dfDistancia, costoPorDistancia, tempinicial, tasaEnfriamiento, numIteraciones):
    """."""
    
    listaCentros = dfInfo[dfInfo['Tipo'] == 'Centro de Distribución'].index.tolist() #Se agregan los centros a una lista para separarlos de las tiendas
    listaTiendas = dfInfo[dfInfo['Tipo'] == 'Tienda'].index.tolist()
    nombreNodo = dfInfo['Nombre'].to_dict() #Guardamos el nombre de cada nodo en un diccionario.

    penalidadGeografica = 20000  #Variable que penaliza si el viaje es demasiado largo
    centrosCercanosPermitidos = 3 #Variable para ayudar al algoritmo a intentar que todos los centros tengan viajes

    print("Pre-calculando 'Centro Ideal' y 'Centros Permitidos' para cada tienda...")
    mapaTiendaCentroIdeal = {} #Se crean listas para almacenar la informacion de los centros con la que interactuaremos en el recocido
    mapaTiendaCentrosCercanos = {}
    for tienda in listaTiendas:
        distancias = dfDistancia.loc[tienda, listaCentros] #Por cada tienda, se guarda la distancia que tiene hacia los centros y se guarda en una lista
        centrosOrdenados = distancias.sort_values().index.tolist() #Se ordenan los centros de acuerdo a la distancia
        mapaTiendaCentroIdeal[tienda] = centrosOrdenados[0] # Se le asigna a la tienda actual del ciclo el centro más cercano 
        mapaTiendaCentrosCercanos[tienda] = centrosOrdenados[:centrosCercanosPermitidos] #Y se guardan una vez definidos

    matrizCosto = generarMatrizCosto(dfDistancia, dfCombustible, costoPorDistancia) #Generamos la matriz costo
    
    solucionActual = generarSolucionInicial(listaCentros, listaTiendas, mapaTiendaCentrosCercanos, porcentajeError=0.15) #Generamos la solucion inicial que vamos a intentar optimizar. 
    
    solucionInicial = {k: list(v) for k, v in solucionActual.items()} # Guardamos una copia de la solucion inicial que no se modificará, solo para comparación
    
    costoActual = calcularCostoSolucion(solucionActual, matrizCosto, mapaTiendaCentroIdeal, penalidadGeografica) #Calculo de costo
    
    #Valores iniciales del algoritmo. El punto de partida completo, incluyendo la temperatura
    mejorSolucion = solucionActual
    mejorCosto = costoActual
    temp = tempinicial


    print("--- Generando solución inicial ---")
    print(f"\nCosto de la solución inicial: {costoActual:,.2f}")

    for i in range(numIteraciones):
        vecinoGenerado = generarVecino(solucionActual, mapaTiendaCentrosCercanos) #Se genera un vecino nuevo y se le calcula el costo para luego compararlo con el costo actual 
        costoVecino = calcularCostoSolucion(vecinoGenerado, matrizCosto, mapaTiendaCentroIdeal, penalidadGeografica)
        costoDiff = costoVecino - costoActual #Generamos el delta, si la diferencia de ambos costos es negativa, quiere decir que el costo del vecino nuevo es menor que el actual, osea, que es mejor.  
        if costoDiff < 0 or random.random() < math.exp(-costoDiff / temp): #Criterio de aceptación. Si el vecino nuevo es mejor que la solucion actual O, en caso de ser peor, se cumple la ecuación de la probabilidad (la cual es más probable se cumpla si la temperatura es alta) también se acepta
            solucionActual = vecinoGenerado #Como se aceptó, nuestro vecino generado se vuelve la solución actual
            costoActual = costoVecino #Y el costo de dicho vecino se vuelve el costo actual, esto para estar comparando
        if costoActual < mejorCosto: #Si el costo actual es menor que el mejor costo, se vuelve nuestro nuevo mejor costo, y dicha solucion se vuelve la mejor solucion actual, con la que compararemos los proximos vecinos
            mejorSolucion = solucionActual
            mejorCosto = costoActual
        temp *= tasaEnfriamiento #Enfriamos gradualmente el sistema
        if (i + 1) % 2000 == 0:  #Impresión para debuggeo en terminal.
            print(f"Iteración {i+1}/{numIteraciones}  Mejor costo hasta ahora: {mejorCosto:,.2f}")

    print("\n--- Recocido completado ---")
    print(f"Mejor costo de ruta encontrado: {mejorCosto:,.2f}")
    

    print("\n--- Rutas generadas ---")
    costoVerificacion = 0
    for nodoCentroDist, nodosRutaFinal in mejorSolucion.items(): #Iteramos por encima de cada mejor solucion para imprimirla textualmente 
        centroNombre = nombreNodo[nodoCentroDist]  #Sacamos el nombre del centro actual, para aclarar que se está imprimiendo su ruta
        
        # Obtener la ruta inicial para este centro
        nodosRutaInicial = solucionInicial[nodoCentroDist]
        
        # Calcular costo inicial de esta ruta específica
        costoInicialRuta = 0
        if nodosRutaInicial:
            rutaCompleta = [nodoCentroDist] + nodosRutaInicial + [nodoCentroDist] #Se imprime la ruta, aclarando que termina con el camión regresando al centro donde inicio
            costoInicialRuta = calcularCostoRuta(rutaCompleta, matrizCosto) 
            # Si la ruta cuenta con un error, como un viaje claramente no optimo, se realiza una penalizacion definida por el usuario
            for tienda in nodosRutaInicial:
                if mapaTiendaCentroIdeal[tienda] != nodoCentroDist:
                    costoInicialRuta += penalidadGeografica
        
        # Calculamos el costo final, mismo procedimiendo que el anterior
        costoFinalRuta = 0
        if nodosRutaFinal:
            rutaCompletaFinal = [nodoCentroDist] + nodosRutaFinal + [nodoCentroDist]
            costoFinalRuta = calcularCostoRuta(rutaCompletaFinal, matrizCosto)
            
            for tienda in nodosRutaFinal:
                if mapaTiendaCentroIdeal[tienda] != nodoCentroDist:
                    costoFinalRuta += penalidadGeografica
        
        costoVerificacion += costoFinalRuta  #Sumamos los costos para determinar si la ruta mejoró o empeoró el precio. 
        mejora = costoInicialRuta - costoFinalRuta

            #En algunos casos, veremos rutas con pérdidas en lugar de mejoras. Esto es porque el algoritmo calcula si vale la pena sacrificar la eficiencia de una ruta
            #para reducir muchísimo el costo de otra, logrando así un costo TOTAL que sea considerado mejora, con algunos sacrificios por así decirlo



        #Impresión final de la ruta y qué nodos viajó
        print(f"\n{centroNombre} ({len(nodosRutaFinal)} tiendas):")
        nombre_rutas_finales = [nombreNodo[nodo] for nodo in nodosRutaFinal]
        if nombre_rutas_finales:
             print(f"  Ruta final:   {' -> '.join(nombre_rutas_finales)}")
        else:
             print("  Ruta final:   (Sin tiendas asignadas)")   #En algunos casos, el algoritmo me generaba centros que no sacaban camion
                                                                #Lo modificamos para que no ocurra, pero por si acaso queda esta linea
        print(f"  Costo Inicial:  ${costoInicialRuta:,.2f}")
        print(f"  Costo Final:    ${costoFinalRuta:,.2f} (Mejora: ${mejora:,.2f})")
    
    print("\n-------------------------------------------")
    print(f"Costo total: ${costoVerificacion:,.2f}")  #Costo final definitivo de todo el viaje de todos los centros

    return mejorSolucion, nombreNodo