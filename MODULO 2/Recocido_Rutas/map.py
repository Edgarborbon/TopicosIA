import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import contextily as cx
import os

def crearMapa(input_path, output_dir):
    """
    Genera un mapa con todos los puntos de distribución y lo guarda.
    """
    try:
        distribucionTiendas = pd.read_excel(input_path)
        #La variable geometry sirve para interpretar la longitud y latitud gracias a la biblioteca shapely. Cada par de xy (longitud/latitud) se almacena como un objeto geométrico
        #de "punto", objetos que GeoPandas puede entender y utilizar. 
        geometry = [Point(xy) for xy in zip(distribucionTiendas['Longitud_WGS84'], distribucionTiendas['Latitud_WGS84'])]
        #Aquí le decimos a GeoPandas que tome la tabla distirbucionTiendas y le agregue la columna geometry.
        #La variable crs define el estándar a utilizar, en este caso es el estandar global latitud/longitud
        gdf = gpd.GeoDataFrame(distribucionTiendas, geometry=geometry, crs='EPSG:4326') 
        #El concepto mercator viene de Web Mercator. GeoPandas utiliza OpenStreetMap el cual dibuja el mapa con información sacada de la red 
        #Esta conversión a epsg=3857 hace que las coordenadas almacenadas encajen con el mapa de fondo que nos genera GeoPandas 
        gdf_mercator = gdf.to_crs(epsg=3857)

        fig, ax = plt.subplots(figsize=(15, 15)) #Creamos el lienzo sobre el cual se dibujará el mapa que vamos a utilizar
        
        #Separamos los nodos en las 2 categorías que utilizamos, Centros de Distribución y Tiendas
        centros = gdf_mercator[gdf_mercator['Tipo'] == 'Centro de Distribución'] 
        tiendas = gdf_mercator[gdf_mercator['Tipo'] == 'Tienda']


        #Específicamos las propiedades de cada punto como color y etiqueta
        centros.plot(ax=ax, color='blue', markersize=130, label='Centro de Distribución', zorder=3)
        tiendas.plot(ax=ax, color='red', markersize=50, label='Tienda', zorder=2)

        #Añadimos al lienzo el mapa sacado de la red
        cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zorder=1)
        #Información de la imagen final, como el título
        ax.set_title('Distribución de Tiendas y Centros', fontsize=16)
        ax.set_axis_off() #No nos interesan los ejes de coordenadas en este caso así que se apaga
        ax.legend()
        #Nombre del archivo generado se concatena con la ruta donde se guardará en este caso en mi computadora, en una carpeta dedicada a los mapas
        output_path = os.path.join(output_dir, 'mapa_distribucion_general.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight') #la varaible dpi afecta la resolucion de la imagen generada y bbox_inches el tipo de borde
        print(f"Mapa de distribución general guardado en: {output_path}")
    except Exception as e:
        print(f"Error al crear el mapa general: {e}")


def crearMapaDeRutas(mejorSolucion, dfInfo, mapaNombres, output_dir):
    """
    Genera mapas individuales y uno con todas las rutas.
    
    """
    try:
        #Igual que el metodo anterior, se toman los datos necesarios para el mapa
        geometry = [Point(xy) for xy in zip(dfInfo['Longitud_WGS84'], dfInfo['Latitud_WGS84'])]
        gdf = gpd.GeoDataFrame(dfInfo, geometry=geometry, crs='EPSG:4326')
        gdf_mercator = gdf.to_crs(epsg=3857)

        #
        print("\n--- Generando mapas individuales por ruta ---")
        for nodoCentro, ruta in mejorSolucion.items():
            if not ruta:
                print(f"Saltando mapa para {mapaNombres[nodoCentro]} (sin tiendas asignadas).")
                continue

            figindividual, axIndividual = plt.subplots(figsize=(12, 12)) #Creamos el lienzo del mapa
            nombreCentro = mapaNombres[nodoCentro] #Tomamos el nombre del centro al que pertenece el mapa que estamos generando

            # Dibujar nodos de fondo y ruta. Se dibujan todos grises inicialmente para indicar los que no están siendo representados en este mapa pero 
            # nos importa que estén ahí igual para tener como referencia. Más adelante se resaltan de otro color los que nos importan por mapa individual
            gdf_mercator[gdf_mercator['Tipo'] == 'Centro de Distribución'].plot(ax=axIndividual, color='gray', markersize=100, zorder=2, alpha=0.4, marker='s')
            gdf_mercator[gdf_mercator['Tipo'] == 'Tienda'].plot(ax=axIndividual, color='gray', markersize=30, zorder=2, alpha=0.4) 
            rutaCompleta = [nodoCentro] + ruta + [nodoCentro] #Definimos la ruta completa, nodoCentro representa el nodo del centro actual
            puntosRuta = [gdf_mercator.loc[nodo].geometry for nodo in rutaCompleta] #Le decimos a GeoPandas qué nodos son los de la ruta actual
            
            #La biblioteca Shapely se encarga por nosotros de dibujar las lineas entre nodos con la información proporcionada
            linea = LineString(puntosRuta) 
            gpd.GeoSeries([linea], crs='EPSG:3857').plot(ax=axIndividual, color='darkorange', linewidth=2.5, zorder=3, label=f"Ruta: {nombreCentro}")

            # Creamos un DataFrame con los nodos de la ruta actual y los resaltamos con GeoPandas
            nodosRutaActual = gdf_mercator.loc[rutaCompleta]
            nodosRutaActual[nodosRutaActual['Tipo'] == 'Centro de Distribución'].plot(ax=axIndividual, color='blue', markersize=200, zorder=4, edgecolor='white', marker='s')
            nodosRutaActual[nodosRutaActual['Tipo'] == 'Tienda'].plot(ax=axIndividual, color='red', markersize=60, zorder=4, edgecolor='black')

            

            # Este ciclo le indica a GeoPandas que etiquete cada nodo. 
            # Así se nombrarán en el mapa como "T23", "T1", "CD4", etc
            for idx, row in gdf_mercator.iterrows(): #El método iterrows recorre el dataframe fila por fila
                numeroNodo = int(idx.split('_')[1]) #El numero del nodo, tomado del indiice obtenido en el archivo 

                # Como tenemos 100 nodos pero los primeros 10 son Centros de Distribución, tenemos este if para diferenciar Centros de Tiendas
                # el Nodo 11 por ejemplo, no sería la Tienda 11, sino la Tienda 1, ya que los primeros 10 nodos son Centros de distribucion
                if numeroNodo > 10:
                    etiqueta = f"T{numeroNodo - 10}" 
                else:
                    etiqueta = f"CD{numeroNodo}"
                
                #Esta linea es la que escribe la etiqueta, y + 150 para que esté un poco por encima del punto
                axIndividual.text(row.geometry.x, row.geometry.y + 150, etiqueta, fontsize=8, ha='center', va='bottom',
                        color='black', weight='bold', bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2', ec='none')) 

            # Codigo de configuracion del guardado de cada mapa, seguimos siguiendo la nomenclatura de GeoPandas 
            cx.add_basemap(axIndividual, source=cx.providers.OpenStreetMap.Mapnik, zorder=1)
            axIndividual.set_title(f'Ruta Óptima para: {nombreCentro}', fontsize=18) 
            axIndividual.set_axis_off()
            nombreFotoCentroIndividual = nombreCentro.replace(" ", "_").replace(".", "") 
            output_dirIndividual = os.path.join(output_dir, f'mapa_ruta_{nombreFotoCentroIndividual}.png')
            plt.savefig(output_dirIndividual, dpi=300, bbox_inches='tight')
            plt.close(figindividual) # Liberamos memoria después de guardar cada mapa individual
            print(f"Mapa individual guardado en: {output_dirIndividual}")
        
        
        print("\n--- Generando mapa combinado con todas las rutas ---")
        fig, ax = plt.subplots(figsize=(15, 15))

        # Repetimos partes del codigo anterior para generar todas las rutas, una por una, por encima de otra, creando así
        # un mapa que contenga absolutamente todas las rutas generadas, como una telaraña
        colores = plt.cm.get_cmap('tab10', len(mejorSolucion)) #Generamos una paleta de colores para representar cada ruta usando Matplotlib
        for i, (nodoCentro, ruta) in enumerate(mejorSolucion.items()): 
            if not ruta: continue
            colorRuta = colores(i)
            rutaCompleta = [nodoCentro] + ruta + [nodoCentro]
            puntosRuta = [gdf_mercator.loc[nodo].geometry for nodo in rutaCompleta]
            linea = LineString(puntosRuta)
            gpd.GeoSeries([linea], crs='EPSG:3857').plot(ax=ax, color=colorRuta, linewidth=2.0, zorder=2, label=mapaNombres[nodoCentro])
        gdf_mercator[gdf_mercator['Tipo'] == 'Centro de Distribución'].plot(ax=ax, color='blue', markersize=200, zorder=3, edgecolor='white', marker='s')
        gdf_mercator[gdf_mercator['Tipo'] == 'Tienda'].plot(ax=ax, color='red', markersize=60, zorder=3, edgecolor='black')

        
        for idx, row in gdf_mercator.iterrows(): 
            numeroNodo = int(idx.split('_')[1])
            if numeroNodo > 10:
                etiqueta = f"T{numeroNodo - 10}"
            else:
                etiqueta = f"CD{numeroNodo}"

            ax.text(row.geometry.x, row.geometry.y + 150, etiqueta, fontsize=8, ha='center', va='bottom',
                    color='black', weight='bold', bbox=dict(facecolor='white', alpha=0.6, boxstyle='round,pad=0.2', ec='none'))

        # Personalizar y guardar mapa 
        cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zorder=1)
        ax.set_title('Rutas Óptimas de Distribución (Consolidado)', fontsize=20)
        ax.set_axis_off()
        ax.legend(title='Rutas por Centro de Distribución', loc='upper right')
        output_Ruta = os.path.join(output_dir, 'mapa_rutas_optimas_consolidado.png')
        plt.savefig(output_Ruta, dpi=300, bbox_inches='tight')
        print(f"Mapa de rutas consolidado guardado en: {output_Ruta}")

    except Exception as e:
        print(f"Error al crear el mapa de rutas: {e}")