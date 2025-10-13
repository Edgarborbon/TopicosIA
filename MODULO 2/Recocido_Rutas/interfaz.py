import gi
import sys
import os
import threading
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gio, Gdk, GLib


#Esta clase es una template básica para imprimir la terminal en la aplicación, hay
#muchas formas de hacer esto pero para la necesidad de este proyecto optamos por tomar esta
#ya que simplemente diseñamos la interfaz para facilidad de mostrar el resultado para la documentación
#Para esta interfaz utilizamos el framework GTK, es un toolkit de Gimp de código abierto que sirve para crear
#Aplicaciones gráficas principalmente para Linux
#Como la computadora que sí o sí podemos llevar a clase funciona con Linux, la decidimos utilizar porque es bastante sencilla y hay 
#mucha documentación/ejemplos de donde basarse. 
#Por lo tanto, este código dará error de no ser ejecutado bajo Linux con las librerias y paquetes necesarios, cosa que
#no debería ser un problema en este contexto.
class TextViewWriter:
    def __init__(self, text_buffer):
        self.text_buffer = text_buffer

    def write(self, text):
        GLib.idle_add(self.text_buffer.insert_at_cursor, text)

    def flush(self):
        pass

class ventanaMain(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Sistema de enrutamiento para tiendas de autoservicio")  #Título de la ventana. No se mira por mi sistema operativo
        self.set_default_size(800, 700)

        #Las aplicaciones gráficas diseñadas con el framework GTK se manejan por el concepto de "cajas", algo similar a los divs de html
        #Todos los objetos/widgets de GTK deben ir dentro de cajas, y todos los objetos de GTK tienen propiedades similares a 
        #cualquier lenguaje de diseño, véase HTML, CSS, etc. 
        #Aquí creamos la caja principal, la que vendría siendo toda la ventana
        cajaPrincipal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        cajaPrincipal.set_margin_top(10)
        cajaPrincipal.set_margin_bottom(10)
        cajaPrincipal.set_margin_start(10)
        cajaPrincipal.set_margin_end(10)
        self.set_child(cajaPrincipal)

        #Optamos por utilizar el concepto de "notebook" para organizar un poco el resultado. 
        #Aquí deefinimos la "libreta" y a esta libreta se agregan con [append] las hojas/pestañas para no tener toda la información
        #en un mismo lado
        notebook = Gtk.Notebook()
        notebook.set_vexpand(True) 
        cajaPrincipal.append(notebook) #Agregamos la libreta a la caja/ventana principal

        #Primer pestaña: La consola
        #Creamos una caja que usaremos para tener un cuadro de texto de solo lectura que usaremos como reemplazo de la terminal de Visual Studio Code

        cajaImpresion = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        cajaImpresion.set_margin_top(10)
        cajaImpresion.set_margin_bottom(10)
        cajaImpresion.set_margin_start(10)
        cajaImpresion.set_margin_end(10)

        #Creamos un objeto ScrolledWindow que como su nombre indica, sirve para darle la propiedad a la caja de permitir usar una barra lateral/horizontal para 
        #que quepa toda la información sin tener que hacer el texto más chico
        scrolled_window = Gtk.ScrolledWindow() 
        scrolled_window.set_vexpand(True)
        #Creamos el TextView que mostrará el resultado
        textoTerminal = Gtk.TextView()
        textoTerminal.set_editable(False) #Lo definimos como solo lectura
        self.text_buffer = textoTerminal.get_buffer() #Usando la variable declarada en el archivo principal, le pasamos las impresiones al TextView
        scrolled_window.set_child(textoTerminal) #Definimos que el TextView será objeto hijo de la ventana 

        # --- MODIFICACIÓN --- Se cambia la lógica del botón.
        #boton_ejecutar = Gtk.Button(label="Proceso controlado desde main.py") # --- MODIFICACIÓN --- Se cambia el texto para mayor claridad.
        #boton_ejecutar.set_sensitive(False) # --- AGREGADO --- Se desactiva el botón, ya que la lógica se inicia automáticamente.

        cajaImpresion.append(scrolled_window) #Asignamos la ventana deslizable a la caja correspondiente        
        labelConsola = Gtk.Label(label="Consola de Salida") 
        #Creamos una pestaña de la libreta con la caja recién creada y su etiqueta correspondiente
        notebook.append_page(cajaImpresion, labelConsola) 

        #Segunda pestaña: Los mapas

        #Mismo procedimiento que la pestaña anterior
        cajaMapas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        cajaMapas.set_margin_top(10)
        cajaMapas.set_margin_bottom(10)
        cajaMapas.set_margin_start(10)
        cajaMapas.set_margin_end(10)

        scrolled_window_mapas = Gtk.ScrolledWindow()
        scrolled_window_mapas.set_vexpand(True)

        #Creamos una caja que contendrá los mapas generados de las rutas optimas
        cajaListaImagenes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        scrolled_window_mapas.set_child(cajaListaImagenes)

        #Creamos un arreglo con los nombres de los mapas generados en cada ejecución
        #Los nommbres nunca cambian y cada ejecución del algoritmo simplemente reemplaza las imagenes en caso de existir 
        #sin necesidad de darle autorización. 
        #Esto con la finalidad de hacer más rápido el proceso
        self.nombreMapas = [
          'mapa_ruta_Centro_de_Distribución_1.png',
          'mapa_ruta_Centro_de_Distribución_2.png',
          'mapa_ruta_Centro_de_Distribución_3.png',
          'mapa_ruta_Centro_de_Distribución_4.png',
          'mapa_ruta_Centro_de_Distribución_5.png',
          'mapa_ruta_Centro_de_Distribución_6.png',
          'mapa_ruta_Centro_de_Distribución_7.png',
          'mapa_ruta_Centro_de_Distribución_8.png',
          'mapa_ruta_Centro_de_Distribución_9.png',
          'mapa_ruta_Centro_de_Distribución_10.png',
          'mapa_rutas_optimas_consolidado.png',
        ]
        self.visoresMapas = [] #Lista vacía donde guardaremos cada objeto Picture que contendrá cada uno un mapa

        #Este ciclo recorrerá el arreglo con el nombre de cada mapa y por cada uno creará un widget/objeto Picture donde lo mostrará
        
        for nombre in self.nombreMapas:
          visor = Gtk.Picture()
          visor.set_keep_aspect_ratio(True)
          visor.set_can_shrink(True)
          visor.set_size_request(-1,800)

          #Cada objeto generado se va agregando a la caja que los mostrará todos al final
          cajaListaImagenes.append(visor)
          self.visoresMapas.append(visor)

        #Para optimizar memoria, no cargamos las impágenes hasta no oprimir un botón
        botonCargar = Gtk.Button(label="Mostrar mapas de rutas óptimas")
        botonCargar.connect("clicked", self.onButtonPressed)
        #Se agrega la ventana deslizable con los mapas y el botón que los carga a la caja correspondiente
        cajaMapas.append(scrolled_window_mapas)
        cajaMapas.append(botonCargar)    
        labelMapa = Gtk.Label(label="Mapas generados")
        notebook.append_page(cajaMapas, labelMapa)

        
      
    #Función que determina el comportamiento del botón
    def onButtonPressed(self, widget):
        #Definimos la ruta donde se encuentran los mapas
        rutaMapa = os.path.expanduser('~/Documents/Zuriel/mapas')

        #Recorremos el arreglo con los nombres de los mapas 
        #Le concatenamos a la ruta el nombre del archivo 
        for i, nombreMapa in enumerate(self.nombreMapas):
            visorActual = self.visoresMapas[i] # Obtenemos el widget correspondiente
            rutaCompleta = os.path.join(rutaMapa, nombreMapa) #Creamos la ruta completa del mapa

            #Este if es un verificador usado durante el debuggeo en caso de que no existiese dicho archivo
            #La forma del algoritmo garantiza que siempre existan todos los mapas, pero por si acaso, 
            #por la naturaleza de la probabilidad, se deja
            if os.path.exists(rutaCompleta):
                mapa = Gio.File.new_for_path(rutaCompleta) #Gio.File pertenece a GTK y es simplemente una forma de manipulación de archivos y directorios
                visorActual.set_file(mapa)
            else:
                #Si no hay foto, se avisa
                visorActual.set_file(None)
                print(f"No existe el archivo: {nombreMapa}")
        
        print("Mapas generados")

#Esta clase inicializa la interfaz
class MiApp(Gtk.Application):
    def __init__(self, ready_event, **kwargs):
        super().__init__(**kwargs)
        self.window = None #Se tiene que declarar la propiedad [window] de lo contrario da error
        self.ready_event = ready_event #El semaforo declarado en el archivo principal, se declara por defecto como falso

    def do_activate(self):
        self.window = ventanaMain(application=self) #Se asigna la ventana de la aplicación con la id recibida en el archivo principal
        self.window.present() #Se necesita declarar como present de lo contrario no funciona, reglas de GTK

        #Se declara el ready_event como activado/verdadero
        #Esto le avisará al archivo pricipal que ya existe una ventana a la cual mandar los argumentos necesarios para mostrar
        #la información de la terminal en el TextView de esta interfaz        
        self.ready_event.set()