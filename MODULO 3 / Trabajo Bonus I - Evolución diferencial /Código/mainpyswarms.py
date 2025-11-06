import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('qt5agg') #Framework necesario para mostrar la animación en otra ventana en mi sistema operativo
import numpy as np
import pyswarms as ps
from pyswarms.utils.plotters import plot_contour #Esta funcion se encarga de generar la animación utilizando el historial que guarda PySwarms al optimizar un enjambre. Funciona solamente con 2 dimensiones
from pyswarms.utils.plotters.formatters import (
    Mesher,    #Para dibujar el fondo (las curvas de nivel)
    Designer,  #Para configurar el diseño
    Animator,  #Para generar la animación
)
# PySwarms ya cuenta con algunas funciones definidas, en este caso decidimos poner a prueba el PSO para resolver la llamada función esfera (f(x,y) = x^2 + y^2)
# fx.sphere es la forma con la que la invocaremos desde la biblioteca de pyswarms, el objetivo en esta ejecución es minimizar, es decir, optimizar la función debería darnos un resultado cercano o igual a cero
from pyswarms.utils.functions import single_obj as fx

################################# CONFIGURAR Y EJECUTAR EL ALGORITMO PSO #################################

print("Ejecutando optimización de función esfera con Pyswarms")

#Opciones básicas del enjambre
#c1 es el coeficiente personal, que tanto confía en si misma una particula del enjambre
#c2 es el coeficiente social, que tanto se deja influenciar por el resto
#w es la inercia
parametrosEnjambre = {"c1": 1.5, "c2": 1.5, "w": 0.5}

# Definimos el "mapa" o "área de búsqueda"
limiteInferior = -10  # El límite más bajo (izquierda y abajo)
limiteSuperior = 10   # El límite más alto (derecha y arriba)


#Almacenamos en una variable dos arreglos de la biblioteca numpy
#Un arreglo contendrá los limites inferiores y otro los superiores tanto de x como de y
#Esto es necesario para PySwarms
limitesBusqueda = (
    np.array([limiteInferior, limiteInferior]),  
    np.array([limiteSuperior, limiteSuperior]),  
)

#GlobalBestPSO es el encargado de la creación del enjambre, facilitado por la biblioteca PySwarms que aprendimos a utilizar en el proyecto de esta unidad
#Se le manda el tamaño que esperamos del enjambre, sus dimensiones, sus parametros (c1, c2 e inercia) y los limites que queremos que cada particula respete
#A diferencia de el proyecto de la unidad, este enjambre es de 2 dimensiones (variables) lo que nos facilita mucho las cosas y nos permite ahora sí aprovechar al máximo
#el metodo optimize en n iteraciones en lugar de la forma manual empleada por nosotros en el trabajo de la unidad
optimizador = ps.single.GlobalBestPSO(
    n_particles=50,  
    dimensions=2,    
    options=parametrosEnjambre, 
    bounds=limitesBusqueda, 
)

# Llamamos al optimizador, enviandole nuestra ecuación (la función esfera)
# Almacenaremos el mejor costo y la posición que lo representa

costoFinal, posicionFinal = optimizador.optimize(
    objective_func=fx.sphere, iters=50
)

print("Optimización finalizada. Creando animación:")

################################# PREPARAR LOS OBJETOS PARA LA ANIMACIÓN #################################

# pos_history es un registro guardado por PySwarms que contiene el historial de todo el movimiento realizado por el enjambre. Necesitamos esto para animarlo
historial = optimizador.pos_history

# Creamos el mesher, el cual es el encargado de dibujar el plano/fondo y le pasamos la ecuación que estamos usando. Ya con esta información el mesher ys sabe que se necesita dibujar
m = Mesher(func=fx.sphere)

# El designer es el encargado de dibujar la gráfica, le pasamos los limites definidos
d = Designer(limits=[(-10, 10), (-10, 10)])

# El animator se encarga de animar vaya el historial de movimientos del enjambre, es necesario definirle el intervalo en milisegundos en el que se va a actualizar
a = Animator(interval=500)

################################# CREAR LA ANIMACIÓN #################################

# LLamamos la función plot_contour que tomará los objetos definidos anteriormente 
anim = plot_contour(
    pos_history=historial,  # El historial de movimientos
    mesher=m,       # El fondo
    designer=d,     # La gráfica
    animator=a,     # El animador, los milisegundos que tarda en actualizar
    title="Enjambre animado.", 
)

#Mostrar animación en otra ventana
plt.show()

print("\n--- Resultados ---")
print(f"Mejor posición encontrada (x, y): {posicionFinal}")
print(f"Mejor costo encontrado f(x,y): {costoFinal}")
