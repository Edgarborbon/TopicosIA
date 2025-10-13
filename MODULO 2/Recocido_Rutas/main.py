import pandas as pd 
import os
import time
import threading
import sys
# Se importa la nueva función para dibujar rutas y la función del algoritmo
from map import crearMapaDeRutas 
from recocido import recocido
from interfaz import MiApp, TextViewWriter, ventanaMain

def main(app,gui_ready_event):
  
  # Se crearon archivos IDÉNTICOS a las matrices xlsx pero en formatos .csv. Esto debido a problemas de la biblioteca pandas al querer 
  # interpretar la información, pero el orden de los datos y su estructura es la misma a los proporcionados para el ejercicio.
  archivoDistribucion = os.path.expanduser('~/Documents/Zuriel/data/datos_distribucion_tiendas.xlsx')
  archivoCombustible = os.path.expanduser('~/Documents/Zuriel/data/matriz_costos_combustible.csv') 
  archivoDistancia = os.path.expanduser('~/Documents/Zuriel/data/matriz_distancias.csv')   
  output_dir = os.path.expanduser('~/Documents/Zuriel/mapas')

  # Parámetros para el recocido
  costoPorDistancia = 4.5
  tempInicial = 2000
  tasaEnfriamiento = 0.995
  numIteraciones = 20000
  
  #Este bloque de codigo funciona como un semáforo para que el algoritmo no empiece hasta que no se haya generado la interfaz
  #Sin esto, el algoritmo empezará a trabajar antes que exista la interfaz, haciendo que el programa deje de funcionar
  gui_ready_event.wait()  
  #También con esta variable redirigimos los print de la terminal a la caja de texto de la interfaz haciendo uso de la biblioteca sys
  #Y un método definido en el archivo interfaz.py
  text_buffer = app.window.text_buffer 
  writer = TextViewWriter(text_buffer)
  sys.stdout = writer

  # Se montan los datos en DataFrames gracias a la biblioteca Pandas. 
  print("Cargando y preparando datos...")

  

  try:
    #Este archivo sirve para saber qué nodos corresponden a centros de distribución o tiendas. Además, de aquí sacamos las coordenadas para la generación del mapa 
    #Todo se hace siguiendo la documentación de la biblioteca pandas para lectura de archivos xlsx/csv y el proceso de crear DataFrames con esos datos
    dfInfoXLSX = pd.read_excel(archivoDistribucion, sheet_name="Sheet1") 
    numeroNodos = len(dfInfoXLSX)
    nombreNodos = [f'Nodo_{i+1}' for i in range(numeroNodos)]
    
    # Se cargan las matrices con las distancias y el costo de combustible entre nodos
    dfDistanciaCSV = pd.read_csv(archivoDistancia, header=None)
    dfCombustibleCSV = pd.read_csv(archivoCombustible, header=None)

    # Tomamos los nombres de los nodos del archivo datos_distribucion_tiendas y lo asignamos como indice y columna a ambas matrices. 
    # Todo este procedimiento nació por muchos problemas que estaba teniendo a la hora de interpretar las matrices en sus formatos xlsx. 
    dfDistancia = dfDistanciaCSV.copy()
    dfDistancia.index = nombreNodos
    dfDistancia.columns = nombreNodos
    dfCombustible = dfCombustibleCSV.copy()
    dfCombustible.index = nombreNodos
    dfCombustible.columns = nombreNodos
    
    dfInfo = dfInfoXLSX.copy()
    dfInfo['Nodo'] = nombreNodos
    dfInfo = dfInfo.set_index('Nodo')
    print("Datos cargados y limpiados correctamente.")
  except Exception as e:
    print(f"Error crítico al cargar los datos: {e}")
    return

  # Se llama al metodo que ejecutará todo el código del recocido simulado, enviando los datos necesarios.
  
  mejorSolucion, mapaNombres = recocido(
      dfInfo=dfInfo,
      dfCombustible=dfCombustible,
      dfDistancia=dfDistancia,
      costoPorDistancia=costoPorDistancia,
      tempinicial=tempInicial,
      tasaEnfriamiento=tasaEnfriamiento,
      numIteraciones=numIteraciones
  )
  """
  # Ya con la solución obtenida gracias al metodo anterior, generamos el mapa y lo guardamos.
  if mejorSolucion:
      print("\nGenerando mapa de la ruta óptima...")
      crearMapaDeRutas(
          mejorSolucion=mejorSolucion,
          dfInfo=dfInfo,
          mapaNombres=mapaNombres,
          output_dir=output_dir
      )
      print("Mapa de rutas guardado.")
  """
if __name__ == "__main__":
    gui_ready_event = threading.Event() #Definimos la variable semáforo
    #La biblioteca necesaria para la interfaz de prueba que usamos (GTK) tiene una serie de "reglas" a la hora de asignar ids de aplicación
    #Esta, en específico, requiere 2 palabras separadas por punto mínimamente. 
    #Esta id debe ser única ya que interactua con el sistema operativo, y en caso de haber ids idénticas habrán conflictos. 
    app = MiApp(gui_ready_event,application_id="recocido.simulado") 
    #Se crea el hilo que interactua con el semáforo y separa la salida de la terminal en "hilos", de no hacer esto, en la interfaz gráfica
    #en lugar de salir en tiempo real los print, se esperará a que termine el programa y pondrá toda la terminal de golpe.
    main_logic_thread = threading.Thread(target=main, args=(app,gui_ready_event))
    main_logic_thread.daemon = True
    main_logic_thread.start()
    
    #Codigo de ejecución de aplicación, pasa la información a la [app] la cual es la interfaz gráfica sin detener el proceso de fondo
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

