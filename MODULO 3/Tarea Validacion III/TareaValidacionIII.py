import random
import numpy as np
import operator

################################# CLASES #################################

class Municipio:
    """
    Representa un solo municipio/gen con coordenadas x - y
    """
    def __init__(self, x, y):
        """
        x: Coordenada en el eje X 
        y: Coordenada en el eje Y 

        Constructor de la clase. Inicializa un municipio
        con sus coordenadas  'x' e 'y'
        """
        self.x = x
        self.y = y
    
    def distancia(self, siguienteMunicipio):
        """
        siguienteMunicipio: Otro objeto de la clase 'Municipio'

        Calcula la distancia entre
        este municipio (self) y el 'siguienteMunicipio' proporcionado

        Returns:
         La distancia calculada
        """
        distanciaX = abs(self.x - siguienteMunicipio.x)
        distanciaY = abs(self.y - siguienteMunicipio.y)
        distancia = np.sqrt((distanciaX ** 2) + (distanciaY ** 2))
        return distancia

    def __repr__(self):
        """
        Devuelve la representación oficial en string del objeto municipio, para la impresión final

        Returns:
         Una cadena con el formato "(x.xx, y.yy)"
        """
        return f"({self.x:.2f}, {self.y:.2f})"


class Individuo:
    """
    Modificación principal del codigo original.
    Representa una solución candidata
    Calcula y almacena su propia distancia y aptitud 
    """
    def __init__(self, ruta):
        """
        ruta: Una lista de objetos 'Municipio' que representa una posible solución

        Constructor de la clase. Inicializa un objeto Individuo para una 
        ruta específica, y calcula automáticamente su distancia y aptitud
        """
        self.ruta = ruta
        self.distancia = 0.0
        self.aptitud = 0.0
        # A diferencia de la implementación original, calculamos la aptitud al momento de crear 
        # la ruta, y se almacena como parametro del objeto
        self.distanciaRuta()
        self.rutaApta()

    def distanciaRuta(self):
        """
        Usa self.ruta

        Calcula la distancia total de la ruta almacenada
        Suma la distancia entre cada municipio, en orden, y al final 
        suma la distancia de regreso al punto inicial
        Guarda el resultado en 'self.distancia'

        Returns:
         La distancia total de la ruta
        """
        if self.distancia == 0:
            distanciaTotal = 0
            for i in range(len(self.ruta)):
                puntoInicial = self.ruta[i]
                puntoFinal = None
                if i + 1 < len(self.ruta):
                    puntoFinal = self.ruta[i + 1]
                else:
                    # Regreso al inicio
                    puntoFinal = self.ruta[0]
                distanciaTotal += puntoInicial.distancia(puntoFinal)
            self.distancia = distanciaTotal
        return self.distancia

    def rutaApta(self):
        """
        Usa self.distancia.

        Calcula la aptitud(fitness) de la ruta
        Define la aptitud como 1 / (distancia total).
        Entre más bajo sea el valor de la distancia, la aptitud es mayor

        Returns:
         El valor de aptitud
        """
        if self.aptitud == 0:
            # Asegura que la distancia esté calculada
            self.distanciaRuta()
            self.aptitud = 1.0 / float(self.distancia)
        return self.aptitud
    
    def __repr__(self):
        """
        Devuelve la representación en string del objeto Individuo.

        Returns:
         Una cadena mostrando la Distancia y Aptitud
        """
        return f"[Dist: {self.distancia:.2f} | Apt: {self.aptitud:.6e}]"


class AlgoritmoGenetico:
    """
    Clase principal que ejecuta toda la lógica del algoritmo
    """
    def __init__(self, listaMunicipios, tamañoPoblacion, indivSelecionados, razonMutacion):
        """
        listaMunicipios: La lista completa de objetos 'Municipio' a visitar.
        tamañoPoblacion: El número de individuos (rutas) en cada generación.
        indivSelecionados: El número de mejores individuos que pasan directo.
        razonMutacion: La probabilidad de mutación 

        Constructor de la clase. Inicializa el algoritmo con sus parámetros.
        """
        # Parámetros del algoritmo
        self.listaMunicipios = listaMunicipios
        self.tamañoPoblacion = tamañoPoblacion
        self.indivSelecionados = indivSelecionados
        self.razonMutacion = razonMutacion
        
        # Almacén de la población actual
        self.poblacion = []

    def _crearRuta(self):
        """
        Usa self.listaMunicipios.

        Crea una ruta aleatoria mezclando aleatoriamente
        la lista de municipios base.

        Returns:
         Una nueva lista con los municipios en orden aleatorio (list).
        """
        ruta = random.sample(self.listaMunicipios, len(self.listaMunicipios))
        return ruta

    def _poblacionInicial(self):
        """
        Usa self.tamañoPoblacion.

        Crea la población inicial llamando a 
        '_crearRuta' n cantidad de veces.
        """
        for _ in range(self.tamañoPoblacion):
            rutaAleatoria = self._crearRuta()
            self.poblacion.append(Individuo(rutaAleatoria))

    def _clasificacionRutas(self):
        """
        Usa self.poblacion.

        Ordena la población actual de mejor
        (mayor aptitud) a peor (menor aptitud)

        Returns:
         Una lista de 'Individuo' ordenada descendentemente
        """
        return sorted(self.poblacion, key=lambda i: i.aptitud, reverse=True) #Ordenamos de forma descendente usando el propio [sorted] de Python. La función lamda le indica que solo los ordene según su aptitud

    def _seleccionRutas(self, poblacionClasificada):
        """
        poblacionClasificada: La lista ordenada de 'Individuo'.

        Selecciona los individuos que pasarán a la siguiente generación
        usando el concepto de "elitismo" y selección aleatoria para aquellos clasificados como "no elites"

        Returns:
         Una lista de 'Individuo' seleccionados para el apareamiento
        """
        grupoApareamiento = []
        
        # Selección de la "elite"
        for i in range(self.indivSelecionados):
            grupoApareamiento.append(poblacionClasificada[i])
        
        # Los restantes, se seleccionan de manera aleatoria
        totalAptitud = sum(i.aptitud for i in poblacionClasificada)
        
        for _ in range(self.tamañoPoblacion - self.indivSelecionados):
            puntoAleatorio = random.uniform(0, totalAptitud)
            sumaActual = 0
            for individuo in poblacionClasificada:
                sumaActual += individuo.aptitud
                if sumaActual > puntoAleatorio:
                    grupoApareamiento.append(individuo)
                    break
                    
        return grupoApareamiento

    def _cruce(self, progenitor1, progenitor2):
        """
        progenitor1: Un objeto 'Individuo'
        progenitor2: Otro objeto 'Individuo'

        Realiza el cruce entre dos progenitores.
        
        Returns:
         El hijo, un nuevo objeto 'Individuo'
        """
        hijo = []
        hijoP1 = []
        
        generacionX = int(random.random() * len(progenitor1.ruta))
        generacionY = int(random.random() * len(progenitor1.ruta))
        
        generacionInicial = min(generacionX, generacionY)
        generacionFinal = max(generacionX, generacionY)

        for i in range(generacionInicial, generacionFinal):
            hijoP1.append(progenitor1.ruta[i])
            
        hijoP2 = [gen for gen in progenitor2.ruta if gen not in hijoP1]
        hijo = hijoP1 + hijoP2
        
        return Individuo(hijo)

    def _reproduccionPoblacion(self, grupoApareamiento):
        """
        grupoApareamiento: Las rutas 'Individuo' que se van a reproducir.

        Crea la nueva población
        Los 'indivSelecionados' mejores pasan directamente
        El resto se genera cruzando individuos del grupo de apareamiento

        Returns:
         La nueva generación de 'Individuo' 
        """
        hijos = []
        
        # Seleccion de los "elite"
        for i in range(self.indivSelecionados):
            hijos.append(grupoApareamiento[i])
        
        # Cruce
        espacio = random.sample(grupoApareamiento, len(grupoApareamiento))
        
        for i in range(self.indivSelecionados, self.tamañoPoblacion):
            progenitor1 = espacio[i]
            progenitor2 = espacio[len(grupoApareamiento) - i - 1]
            
            hijo = self._cruce(progenitor1, progenitor2)
            hijos.append(hijo)
            
        return hijos

    def _mutacion(self, individuo):
        """
        individuo: Un objeto 'Individuo'.

        Aplica una mutación de "intercambio" (Swap) a la ruta del individuo
        basado en 'self.razonMutacion'.
        Si muta, recalcula la aptitud del individuo.

        Returns:
         El individuo mutado
        """
        mutado = False
        for i in range(len(individuo.ruta)):
            if random.random() < self.razonMutacion:
                j = int(random.random() * len(individuo.ruta))
                
                # Swap
                municipio1 = individuo.ruta[i]
                municipio2 = individuo.ruta[j]
                
                individuo.ruta[i] = municipio2
                individuo.ruta[j] = municipio1
                mutado = True
        
        # Si la ruta cambió, recalcular distancia y aptitud
        if mutado:
            individuo.distancia = 0.0 
            individuo.aptitud = 0.0
            individuo.distanciaRuta()
            individuo.rutaApta()
        
        return individuo

    def _mutacionPoblacion(self, poblacionHijos):
        """
        poblacionHijos: La nueva generación de 'Individuo'.

        Recorre toda la nueva población y aplica la función '_mutacion' a cada uno.

        Returns:
         La población mutada 
        """
        poblacionMutada = []
        for individuo in poblacionHijos:
            individuoMutado = self._mutacion(individuo)
            poblacionMutada.append(individuoMutado)
        return poblacionMutada

    def _nuevaGeneracion(self):
        """
        Creamos una nueva generación, siguiendo el procedimiento del algoritmo genético:
        Clasificar -> Seleccionar -> Reproducir -> Mutar
        Actualiza 'self.poblacion' con la nueva generación
        """
        poblacionClasificada = self._clasificacionRutas()
        grupoApareamiento = self._seleccionRutas(poblacionClasificada)
        hijos = self._reproduccionPoblacion(grupoApareamiento)
        nuevaGeneracion = self._mutacionPoblacion(hijos)
        self.poblacion = nuevaGeneracion

    # --- Método Público de Ejecución ---
    
    def iniciarAlgoritmoGenetico(self, generaciones):
        """
        generaciones: El número de generaciones a crear

        Función principal que ejecuta el algoritmo
        -Crea la población inicial
        -Itera según las generaciones especificadas
        -Devuelve la mejor ruta

        Returns:
         La solucion final
        """
        print("Iniciando Algoritmo Genético")
        
        self._poblacionInicial()
        
        solucionInicial = self._clasificacionRutas()[0]
        print(f"Mejor distancia inicial (Gen 0): {solucionInicial.distancia:.2f}")
        
        for i in range(generaciones):
            self._nuevaGeneracion()
            
            if (i+1) % 50 == 0:
                solucionActual = self._clasificacionRutas()[0]
                print(f"Generación {i+1:4}: Mejor distancia = {solucionActual.distancia:.2f}")

        print("\nEvolución finalizada.")
        solucionFinal = self._clasificacionRutas()[0]
        
        print(f"Mejor distancia final: {solucionFinal.distancia:.2f}")
        return solucionFinal

# -----------------------------------------------------------------
# PRUEBAS Y EJECUCIÓN
# -----------------------------------------------------------------

def prueba():
    """
    Ponemos a prueba el algoritmo con una situación ficticia.
    En este caso, creamos un 'cuadro' y definimos
    """
    print("\n[Iniciando Prueba]")
    m1 = Municipio(0, 0)
    m2 = Municipio(0, 10)
    m3 = Municipio(10, 10)
    m4 = Municipio(10, 0)
    
    rutaPrueba = [m1, m2, m3, m4]
    distanciaEsperada = 40.0
    
    indivPrueba = Individuo(rutaPrueba)
    distanciaFinal = indivPrueba.distancia
    
    print(f"Distancia Esperada: {distanciaEsperada} | Calculada: {distanciaFinal}")
    
    if abs(distanciaFinal - distanciaEsperada) < 0.001:
        print("Prueba de lógica (Individuo) superada")
    else:
        print("Error en la lógica (Individuo)")
    print("-------------------------------------------------")


if __name__ == '__main__':
    
    # 1. Ejecutar la prueba unitaria formal
    prueba()

    # 2. Definir los municipios para el problema
    listaMunicipios = [
        Municipio(x=40.4168, y=-3.7038),  # Madrid
        Municipio(x=41.3784, y=2.1925),   # Barcelona
        Municipio(x=43.2630, y=-2.9350),  # Bilbao
        Municipio(x=39.4699, y=-0.3763),  # Valencia
        Municipio(x=37.3891, y=-5.9845),  # Sevilla
        Municipio(x=36.7213, y=-4.4214),  # Málaga
        Municipio(x=42.8468, y=-2.6716),  # Vitoria
        Municipio(x=38.3452, y=-0.4815)   # Alicante
    ]
    
    # 3. Instanciar y configurar el Algoritmo Genético
    ag = AlgoritmoGenetico(
        listaMunicipios=listaMunicipios,
        tamañoPoblacion=10,
        indivSelecionados=1,
        razonMutacion=0.05
    )
    
    # 4. Ejecutar la evolución
    mejorSolucion = ag.iniciarAlgoritmoGenetico(generaciones=500)
    
    # 5. Imprimir resultados finales
    print("\n-------------------------------------------------")
    print("Mejor ruta encontrada: ")
    ruta_str = " -> ".join([str(individuo) for individuo in mejorSolucion.ruta])
    print(ruta_str + f" -> {mejorSolucion.ruta[0]}") # Regreso al inicio
    print(f"Distancia total: {mejorSolucion.distancia}")