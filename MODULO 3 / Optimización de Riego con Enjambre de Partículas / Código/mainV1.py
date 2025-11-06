import pandas as pd
import numpy as np
import pyswarms as ps
import matplotlib.pyplot as plt
import pathlib
#Biblioteca normalizadora de datos. La usamos para facilidad de comparación ya que es algo complejo comparar los datos ya que son totalmente distintos
#De esta manera, normalizamos la información para que a la hora de comparar coordenadas, altitud, temperatura y nivel de salinidad, los valores son del 0 a 1
#permitiendonos así medir los cambios en porcentajes. De esta manera, podremos identificar un cambio de temperaturas como "la temperatura aumentó un 40%" en lugar de decir
#la temperatura aumentó 6 grados. Todo esto para facilitar el uso de la biblioteca PySwarms.
from sklearn.preprocessing import MinMaxScaler

try:
    dfEnjambre = pd.read_csv('~/Documents/PSO_Riego/data/data.csv')
    
    #Definir las columnas que usaremos para medir la "similitud"
    columnasDatos = ['Latitud', 'Longitud', 'Elevacion (m)', 'Salinidad (dS/m)']
    
    # NORMALIZACIÓN DE DATOS
    #Crear el normalizador que convertirá todo a un rango de 0 a 1
    normalizador = MinMaxScaler()
    
    #El método fit_transform aprende de forma inteligente cual es el valor minimo y maximo de cada columna y los "aplasta"
    #de tal forma que todos los valores estén entre el 0 y el 1. De esta forma es más sencillo comparar el impacto en el costo que tiene cada variable. 
    dfValoresCrudosNormalizados = normalizador.fit_transform(dfEnjambre[columnasDatos])
    #dfValoresCrudosNormalizados es un dataframe con los valores "raw"/crudos, no tiene encabezados, solamente los datos numeros con los que interactua numpy, esto es necesario para la normalizacion
    
    #Recrear el DataFrame con los datos normalizados, ahora reincorporando las columnas de los datos para saber qué estamos comparando en el enjambre
    dfEnjambreNormalizado = pd.DataFrame(dfValoresCrudosNormalizados, columns=columnasDatos, index=dfEnjambre.index)
    
    #Añadir la columna 'Cultivo' de vuelta. La sacamos porque obviamente no queremos/podemos "comprimir" cadenas de texto a valores entre el 0 - 1
    dfEnjambreNormalizado['Cultivo'] = dfEnjambre['Cultivo']

    #Filtrar por cultivo (ahora con 4 columnas normalizadas)
    #Esta implementación del algoritmo crea 3 enjambres, uno por cultivo, para proponer soluciones que a la larga traten de satisfacer todos los cultivos al mismo tiempo 
    #Estos vectores ahora tienen 4 dimensiones: Latitud, Longitud, Elevación y Salinidad
    vectorPuntosMaiz = dfEnjambreNormalizado[dfEnjambreNormalizado['Cultivo'] == 'Maíz'][columnasDatos].values
    vectorPuntosChile = dfEnjambreNormalizado[dfEnjambreNormalizado['Cultivo'] == 'Chile'][columnasDatos].values
    vectorPuntosTomate = dfEnjambreNormalizado[dfEnjambreNormalizado['Cultivo'] == 'Tomate'][columnasDatos].values
    
    print(f"Datos cargados: {len(vectorPuntosMaiz)} puntos de Maíz.")
    print(f"Datos cargados: {len(vectorPuntosChile)} puntos de Chile.")
    print(f"Datos cargados: {len(vectorPuntosTomate)} puntos de Tomate.")

except FileNotFoundError:
    print("Error: No se encontró el archivo 'datos_cultivos.csv'")

#Definir las dimensiones que se compararán entre los sensores
dimensionesPorSensor = 4 # (Lat, Lon, Elev, Sal)

################################# --- FUNCIÓN FITNESS --- #################################


def fitness(solucionCand, vectorPuntos, numSensores):
    #En esta implementación, cada particula la definimos como un "explorador" que recorre el plano y propone 2 soluciones, 2 coordenadas. Cada particula tiene como objetivo proponer las 2 posiciones donde estaran
    #los 2 sensores para cada cultivo. Algo así como que cada particula es un dron que va sobrevolando el campo con sensores que detectan las propiedades del suelo. 
    #En terminos de programacion, cada particula es en realidad un vector de 2 soluciones. Esto podría interpretarse como que en realidad una solucion es un equipo de 2 particulas, pero la forma en la que la programamos
    #por facilidad, es representar una particula como un vector con 2 soluciones propuestas. 
    #Otras opciones de resolver este problema con el enjammbre pueden ser, por ejemplo:
    #       -Que cada particula represente un sensor y al final tomar las mejores n particulas y que esas sean la solucion
    #       -Tener un enjambre más pequeño y que directamente cada particula sea una solución definitiva
    #       -Tener un enjambre principal y simplemente ejecutar el enjambre predeterminado
    #Entre otros, hay tantas formas de implementar el PSO jugando con los valores, nosotros optamos por esta que es algo sencilla

    #'solucionCand' es un vector de 1 dimensión, usaremos reshape para darle formato de 2 dimensiones y pasarlo a otra matriz
    #Lo reformateamos a (numSensores, 4)
    #De esta forma, dividimos la solucion candidata en n partes, en este caso 4 dimensiones, para ir separando cada elemento de la solucion de 4 en 4, es decir, sus 4 variables a utilizar (Lat, Lon, Elev, Sal)
    #Por ejemplo, si nuestra solución candidata es [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], con este método, se convierte en:
    #[ [0.1, 0.2, 0.3, 0.4],  # Fila 1 = Sensor 1
    #[0.5, 0.6, 0.7, 0.8] ]   # Fila 2 = Sensor 2
    #Generando así una matriz que nos permite interactuar con los datos de manera más sencilla para este problema.
    coordsSensores = solucionCand.reshape(numSensores, dimensionesPorSensor)
    
    costoTotal = 0.0
    for punto in vectorPuntos: 
        
        #El método np.linalg.norm funciona como el encargado de calcular la distancia o similitud en linea recta entre 2 puntos
        #En condiciones normales, calcular la distancia entre 2 puntos es bastante sencillo pero en este problema se complica ya que nuestra implementación toma en cuenta más de 2 variables
        # "punto" es un vector con las 4 variables que estamos comparando y se le resta a cada una de las filas de la matriz coordsSensores, generando así una matriz de diferencias (Deltas)
        #El argumento axis le indica a NumPy que calcule las distancias a lo largo de las filas, osea el eje 1
        #El resultado de todo eso es un vector de distancias, de cada punto a cada sensor
        distanciaSensores = np.linalg.norm(punto - coordsSensores, axis=1)
        sensorMasCerca = np.min(distanciaSensores) #Encontramos el valor minimo en dicho vector, es decir, el sensor más cercano al punto actual
        costoTotal += sensorMasCerca #El cual se suma por cada punto del enjambre, generando al final el costo total de distancias
    return costoTotal


#Define cuántos sensores queremos para CADA cultivo. Esto puede cambiar dependiendo de la necesidad del usuario, por cuestiones de facilidad de testeo, le daremos 2 a cada cultivo
numSensoresMaiz = 2
numSensoresChile = 2
numSensoresTomate = 2

#Calculo del fitness de cada cultivo 
#posicionEnjambre es un vector con las posiciones de las n particulas, en este caso 50

################################# --- CALCULO FITNESS POR CULTIVO --- #################################


def fitnessMaiz(posicionEnjambre):
    numParticulas = posicionEnjambre.shape[0] #Asignamos el numero de particulas de forma dinamica, de esta forma si ese numero cambia durante la implementación no hay necesidad de cambiar este metodo
    costoEnjambre = np.zeros(numParticulas) #Creamos un vector de 50 elementos vacios que llenaremos con el metodo fitness general para cada particula del enjambre en el siguiente ciclo for
    for i in range(numParticulas):
        costoEnjambre[i] = fitness(posicionEnjambre[i], vectorPuntosMaiz, numSensoresMaiz) 
    return costoEnjambre

def fitnessChile(posicionEnjambre):
    numParticulas = posicionEnjambre.shape[0]
    costoEnjambre = np.zeros(numParticulas)
    for i in range(numParticulas):
        costoEnjambre[i] = fitness(posicionEnjambre[i], vectorPuntosChile, numSensoresChile)
    return costoEnjambre

def fitnessTomate(posicionEnjambre):
    numParticulas = posicionEnjambre.shape[0]
    costoEnjambre = np.zeros(numParticulas)
    for i in range(numParticulas):
        costoEnjambre[i] = fitness(posicionEnjambre[i], vectorPuntosTomate, numSensoresTomate)
    return costoEnjambre

#Configurar y Ejecutar PySwarms

#Opciones básicas del enjambre
#c1 es el coeficiente personal, que tanto confía en si misma una particula del enjambre
#c2 es el coeficiente social, que tanto se deja influenciar por el resto
#w es la inercia
parametrosEnjambre = {'c1': 0.5, 'c2': 0.3, 'w': 0.9} 
totalIteraciones = 100 


################################# --- BUCLE MAIZ --- #################################


print(f"Optimizando {numSensoresMaiz} sensores para Maíz...")

#LÍMITES
#Como ahora todo está normalizado de 0 a 1, los límites son simples.
limiteMin = 0.0
limiteMax = 1.0

# DIMENSIONES
# El total de dimensiones es (sensores * 4)
dimensionesMaiz = numSensoresMaiz * dimensionesPorSensor # Ej: 2 * 4 = 8 dimensiones, es decir, cada particula debe proponer una solucion de 8 numeros, en este caso 
                                                          # Lat, Lon, Elev, Sal 1 y 2, ya que cada particula propone 2 opciones

# Crear los vectores de bordes (ej. 8 ceros y 8 unos)
bordesMinimosMaiz = np.tile(limiteMin, dimensionesMaiz)
bordesMaximosMaiz = np.tile(limiteMax, dimensionesMaiz)

#GlobalBestPSO es el encargado de la creación del enjambre, facilitado por la biblioteca PySwarms que se nos recomendó utilizar en las especificaciones del proyecto 
#Se le manda el tamaño que esperamos del enjambre, sus dimensiones, sus parametros (c1, c2 e inercia) y los limites que queremos que cada particula respete
optimizerMaiz = ps.single.GlobalBestPSO(n_particles=50,
                                        dimensions=dimensionesMaiz,
                                        options=parametrosEnjambre, 
                                        bounds=(bordesMinimosMaiz, bordesMaximosMaiz)) 


progreso_dir_maiz = pathlib.Path("progreso_maiz") # Nueva carpeta
progreso_dir_maiz.mkdir(exist_ok=True)

#PySwarms cuenta con una forma de hacer todo totalmente automático, con el método optimize. Sin embargo, esto no nos permitiría desplegar los resultados al final de la forma que queremos debido a las dimensiones
#del problema. Por lo tanto, en lugar de realizar el metodo optimize 100 veces de golpe, se ejecuta de uno por uno dentro de un for para facilitar el dibujo final en el plano
for i in range(totalIteraciones):
    optimizerMaiz.optimize(fitnessMaiz, iters=1)
    #Optimize es el método encargado de lidiar con todo el trabajo pesado del algoritmo. Toma las 50 particulas, registra y compara los mejores locales y sociales, actualiza y lleva un historial
    #Una vez actualizados los mejores personales de cada particula, y el mejor del enjambre, y luego de actualizar todos los valores toca mover las particulas para la siguiente Iteración
    #En circunstancias normales, configurando el optimize para que realice las iteraciones necesarias, una sola ejecución de este metodo realiza todo el movimiento del enjambre y registra los resultados
    #para ya el usuario interactuar con ellos. En este caso, se hace manual para la graficacion
    
    if (i + 1) % 10 == 0: 
        print(f"Guardando imagen de progreso (Iteración {i+1})") #Guardamos un mapa cada 10 iteraciones para monitorear el progreso del enjambre
        
        plt.figure(figsize=(12, 8))
        
        
        #Obtener la mejor solución (Normalizada)
        mejorPosicionActualNorm = optimizerMaiz.swarm.best_pos #swarm.best_pos de PySwarms nos da la mejor posicion, en este caso de 1 sola iteracion 
        #Reformatear a (numSensores, 4). Con esto lo convertimos en una matriz 2x4, 2 sensores, 4 dimensiones
        mejorPosicionActualNorm = mejorPosicionActualNorm.reshape(numSensoresMaiz, dimensionesPorSensor)
        #Revertimos la normalización para recuperar los valores originales. Necesario para obtener las coordenadas
        mejorPosicionActualReal = normalizador.inverse_transform(mejorPosicionActualNorm)
        #Extraer solo Lat/Lon (columnas 0 y 1) para graficar
        mejorPosicionCoord = mejorPosicionActualReal[:, 0:2] # Forma (numSensores, 2)
        
        #Revertimos la normalización de nuevo para los puntos de fondo para el gráfico
        vectorPuntosMaizReal = normalizador.inverse_transform(vectorPuntosMaiz)
        
        #(Omitimos graficar TODAS las partículas grises porque des-normalizar
        #50x2 sensores es más complejo y lento dentro del bucle)
        
        mejorCostoActual = optimizerMaiz.swarm.best_cost #swarm.best_cost de PySwarms nos da el mejor costo calculado en el metodo .optimize, como estamos yendo de 1 por 1, es necesario hacer esto manualmente
        #De lo contrario, con una vez que llamemos este método ya obtenemos el mejor costo automáticamente sin necesidad de esta operación manual
        
        #Graficar los puntos de Maíz 
        plt.scatter(vectorPuntosMaizReal[:, 1], vectorPuntosMaizReal[:, 0], #[:, 1] y [:, 0] definen que X será la Longitud y Y la Latitud, el resto son propiedades de diseño
                    color='red', label='Maíz', alpha=0.3, s=30)
        
        #Graficar la 'X', con marker definimos la forma del punto,s=250 es el tamaño, y zorder define a que "nivel" está sobre los otros puntos dibujados, asegurandonos que siempre esté por encima
        plt.scatter(mejorPosicionCoord[:, 1], mejorPosicionCoord[:, 0], 
                    marker='X', color='red', s=250, 
                    label=f'Mejor Posición (Iter {i+1})', zorder=10,
                    edgecolors='black', linewidth=1.5)
        
        #Título
        plt.title(f'Progreso(Maíz) - Iteración {i+1}\nMejor Costo Actual: {mejorCostoActual:.2f}')
        #Etiquetas 
        plt.xlabel('Longitud')
        plt.ylabel('Latitud')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5)) 
        plt.grid(True)
        #Usar límites reales(no normalizados) para el gráfico
        latitudMin, latitudMax = vectorPuntosMaizReal[:, 0].min(), vectorPuntosMaizReal[:, 0].max()
        longitudMin, longitudMax = vectorPuntosMaizReal[:, 1].min(), vectorPuntosMaizReal[:, 1].max()
        plt.xlim(longitudMin, longitudMax) 
        plt.ylim(latitudMin, latitudMax)   
        plt.gca().set_aspect('equal', adjustable='box')
        
        output_filename_progreso = progreso_dir_maiz / f"maiz_iter_{i+1:03d}.png"
        plt.savefig(output_filename_progreso, bbox_inches='tight')
        plt.close()

#Guardar la solución final
mejorCostoMaiz = optimizerMaiz.swarm.best_cost
solucionOptimaMaiz = optimizerMaiz.swarm.best_pos 
print(f"Costo Maíz: {mejorCostoMaiz}")

#Repetimos todo lo anterior para los cultivos restantes

################################# --- BUCLE CHILE --- #################################


print(f"Optimizando {numSensoresChile} sensores para Chile")


dimensionesChile = numSensoresChile * dimensionesPorSensor 
bordesMinimosChile = np.tile(limiteMin, dimensionesChile)
bordesMaximosChile = np.tile(limiteMax, dimensionesChile)

optimizerChile = ps.single.GlobalBestPSO(n_particles=50,
                                         dimensions=dimensionesChile,
                                         options=parametrosEnjambre, 
                                         bounds=(bordesMinimosChile, bordesMaximosChile)) 


progreso_dir_chile = pathlib.Path("progreso_chile")
progreso_dir_chile.mkdir(exist_ok=True)

for i in range(totalIteraciones):
    optimizerChile.optimize(fitnessChile, iters=1)
    
    if (i + 1) % 10 == 0:
        print(f"Guardando imagen de progreso (Iteración {i+1})")
        
        plt.figure(figsize=(12, 8))
        
        
        mejorPosicionActualNorm = optimizerChile.swarm.best_pos 
        mejorPosicionActualNorm = mejorPosicionActualNorm.reshape(numSensoresChile, dimensionesPorSensor)
        mejorPosicionActualReal = normalizador.inverse_transform(mejorPosicionActualNorm)
        mejorPosicionCoord = mejorPosicionActualReal[:, 0:2]
        
        vectorPuntosChileReal = normalizador.inverse_transform(vectorPuntosChile)
        mejorCostoActual = optimizerChile.swarm.best_cost
        
        plt.scatter(vectorPuntosChileReal[:, 1], vectorPuntosChileReal[:, 0], 
                    color='blue', label='Chile', alpha=0.3, s=30)
        
        plt.scatter(mejorPosicionCoord[:, 1], mejorPosicionCoord[:, 0], 
                    marker='X', color='blue', s=250, 
                    label=f'Mejor Posición (Iter {i+1})', zorder=10,
                    edgecolors='black', linewidth=1.5)
        
        plt.title(f'Progreso(Chile) - Iteración {i+1}\nMejor Costo Actual: {mejorCostoActual:.2f}')
        plt.xlabel('Longitud')
        plt.ylabel('Latitud')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.grid(True)
        latitudMin, latitudMax = vectorPuntosChileReal[:, 0].min(), vectorPuntosChileReal[:, 0].max()
        longitudMin, longitudMax = vectorPuntosChileReal[:, 1].min(), vectorPuntosChileReal[:, 1].max()
        plt.xlim(longitudMin, longitudMax) 
        plt.ylim(latitudMin, latitudMax)   
        plt.gca().set_aspect('equal', adjustable='box')
        
        output_filename_progreso = progreso_dir_chile / f"chile_iter_{i+1:03d}.png"
        plt.savefig(output_filename_progreso, bbox_inches='tight')
        plt.close()

mejorCostoChile = optimizerChile.swarm.best_cost
solucionOptimaChile = optimizerChile.swarm.best_pos
print(f"Costo Chile: {mejorCostoChile}")


################################# --- BUCLE TOMATE --- #################################


print(f"Optimizando {numSensoresTomate} sensores para Tomate")


dimensionesTomate = numSensoresTomate * dimensionesPorSensor 
bordesMinimosTomate = np.tile(limiteMin, dimensionesTomate)
bordesMaximosTomate = np.tile(limiteMax, dimensionesTomate)

optimizerTomate = ps.single.GlobalBestPSO(n_particles=50,
                                          dimensions=dimensionesTomate, 
                                          options=parametrosEnjambre, 
                                          bounds=(bordesMinimosTomate, bordesMaximosTomate)) 


progreso_dir_tomate = pathlib.Path("progreso_tomate")
progreso_dir_tomate.mkdir(exist_ok=True)

for i in range(totalIteraciones):
    optimizerTomate.optimize(fitnessTomate, iters=1)
    
    if (i + 1) % 10 == 0:
        print(f"Guardando imagen de progreso (Iteración {i+1})")
        
        plt.figure(figsize=(12, 8))
        
        
        mejorPosicionActualNorm = optimizerTomate.swarm.best_pos 
        mejorPosicionActualNorm = mejorPosicionActualNorm.reshape(numSensoresTomate, dimensionesPorSensor)
        mejorPosicionActualReal = normalizador.inverse_transform(mejorPosicionActualNorm)
        mejorPosicionCoord = mejorPosicionActualReal[:, 0:2]
        
        vectorPuntosTomateReal = normalizador.inverse_transform(vectorPuntosTomate)
        mejorCostoActual = optimizerTomate.swarm.best_cost
        
        plt.scatter(vectorPuntosTomateReal[:, 1], vectorPuntosTomateReal[:, 0], 
                    color='green', label='Tomate', alpha=0.3, s=30)
        
        plt.scatter(mejorPosicionCoord[:, 1], mejorPosicionCoord[:, 0], 
                    marker='X', color='green', s=250, 
                    label=f'Mejor Posición (Iter {i+1})', zorder=10,
                    edgecolors='black', linewidth=1.5)
        
        plt.title(f'Progreso(Tomate) - Iteración {i+1}\nMejor Costo Actual: {mejorCostoActual:.2f}')
        plt.xlabel('Longitud')
        plt.ylabel('Latitud')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.grid(True)
        latitudMin, latitudMax = vectorPuntosTomateReal[:, 0].min(), vectorPuntosTomateReal[:, 0].max()
        longitudMin, longitudMax = vectorPuntosTomateReal[:, 1].min(), vectorPuntosTomateReal[:, 1].max()
        plt.xlim(longitudMin, longitudMax) 
        plt.ylim(latitudMin, latitudMax)   
        plt.gca().set_aspect('equal', adjustable='box')
        
        output_filename_progreso = progreso_dir_tomate / f"tomate_iter_{i+1:03d}.png"
        plt.savefig(output_filename_progreso, bbox_inches='tight')
        plt.close()

mejorCostoTomate = optimizerTomate.swarm.best_cost
solucionOptimaTomate = optimizerTomate.swarm.best_pos
print(f"Costo Tomate: {mejorCostoTomate}")


print(f"\nCosto total: {mejorCostoMaiz + mejorCostoChile + mejorCostoTomate}")

################################# --- GRAFICACIÓN DE DATOS FINALES --- #################################

#Reformatear las 3 posiciones óptimas (que están en 4 dimensiones y normalizadas)
solucionMaiz4DNormalizada = solucionOptimaMaiz.reshape(numSensoresMaiz, dimensionesPorSensor)
solucionChile4DNormalizada = solucionOptimaChile.reshape(numSensoresChile, dimensionesPorSensor)
solucionTomate4DNormalizada = solucionOptimaTomate.reshape(numSensoresTomate, dimensionesPorSensor)

#Revertir la normalizacion
solucionMaizReal = normalizador.inverse_transform(solucionMaiz4DNormalizada)
solucionChileReal = normalizador.inverse_transform(solucionChile4DNormalizada)
solucionTomateReal = normalizador.inverse_transform(solucionTomate4DNormalizada)

#Extraer solo Lat/Lon para graficar
solucionMaizFormateada = solucionMaizReal[:, 0:2]
solucionChileFormateada = solucionChileReal[:, 0:2]
solucionTomateFormateada = solucionTomateReal[:, 0:2]

plt.figure(figsize=(12, 8)) 

#Graficar los puntos de datos reales
vectorPuntosMaizReal = normalizador.inverse_transform(vectorPuntosMaiz)
vectorPuntosChileReal = normalizador.inverse_transform(vectorPuntosChile)
vectorPuntosTomateReal = normalizador.inverse_transform(vectorPuntosTomate)


#Dibujamos con matplotlib los puntos de cada cultivo, asignando un color diferente a cada uno siguiendo el ejemplo proporcionado por el profesor en la documentación

plt.scatter(vectorPuntosMaizReal[:, 1], vectorPuntosMaizReal[:, 0], 
            color='red', label='Maíz', alpha=0.7, s=30)
plt.scatter(vectorPuntosChileReal[:, 1], vectorPuntosChileReal[:, 0], 
            color='blue', label='Chile', alpha=0.7, s=30)
plt.scatter(vectorPuntosTomateReal[:, 1], vectorPuntosTomateReal[:, 0], 
            color='green', label='Tomate', alpha=0.7, s=30)

#Graficar las soluciones, con forma de X y siempre por encima de otros puntos

plt.scatter(solucionMaizFormateada[:, 1], solucionMaizFormateada[:, 0], 
            marker='X', color='red', s=250, 
            label=f'Sensor Maíz (N={numSensoresMaiz})', zorder=10,
            edgecolors='black', linewidth=1.5) 
plt.scatter(solucionChileFormateada[:, 1], solucionChileFormateada[:, 0], 
            marker='X', color='blue', s=250, 
            label=f'Sensor Chile (N={numSensoresChile})', zorder=10,
            edgecolors='black', linewidth=1.5) 
plt.scatter(solucionTomateFormateada[:, 1], solucionTomateFormateada[:, 0], 
            marker='X', color='green', s=250, 
            label=f'Sensor Tomate (N={numSensoresTomate})', zorder=10,
            edgecolors='black', linewidth=1.5) 


################################# --- GENERACIÓN DE ARCHIVO FINAL --- #################################


plt.title('Mapa con Sensores Optimizados')
plt.xlabel('Longitud')
plt.ylabel('Latitud')

plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True)
plt.gca().set_aspect('equal', adjustable='box') 

# Guardar el archivo final
base_name = "Mapa de sensores final"
extension = ".png"
counter = 1
output_path = pathlib.Path(f"{base_name}{extension}")
while output_path.exists():
    output_path = pathlib.Path(f"{base_name}({counter}){extension}")
    counter += 1 
output_filename = str(output_path)

plt.savefig(output_filename, bbox_inches='tight')

print(f"\nGráfico de resultados guardado como: {output_filename}")
