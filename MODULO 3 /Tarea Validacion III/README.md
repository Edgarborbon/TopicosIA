# Tarea Validación III

Este proyecto documenta el estudio y modificación de un script de Algoritmo Genético (AG) diseñado para resolver el Problema del Vendedor Viajero (TSP).

El script original (`AG.py`) fue reparado y agilizado, resultando en el nuevo script (`TareaValidacionIII.py`). Los cambios se centraron en mejorar la eficiencia, la documentación y la organización del código.

## Cambios de `AG.py` a `TareaValidacionIII.py`


### 1. Modificación a Programación Orientada a Objetos

* **Cambio: (`TareaValidacionIII.py`):** Toda la lógica del algoritmo se ha reestructurado dentro de una clase principal: `AlgoritmoGenetico`. Las funciones originales ahora son métodos privados de cada objeto
* **Beneficio:** Este diseño es mucho más limpio, organizado y fácil de mantener. Los parámetros del algoritmo se almacenan como atributos de la clase en lugar de tener que pasarlos como argumentos a cada función.

### 2. Optimización de Eficiencia

* **Antes:** El script usaba una clase `Aptitud` temporal. En cada generación, la función `clasificacionRutas` tenía que crear un nuevo objeto `Aptitud` para cada ruta de la población y recalcular su distancia y aptitud desde cero. Esto era ineficiente,
*  especialmente para los individuos "élite".
* **Cambio:** Se eliminó la clase `Aptitud`. En su lugar, se creó la clase `Individuo`. Un Individuo es un objeto que representa una ruta y calcula su propia distancia y aptitud **UNA SOLA VEZ**.
* **Beneficio:** La función `_clasificacionRutas` ya no calcula nada. Simplemente ordena la lista de individuos basándose en el atributo `.aptitud` que ya está guardado. 

### 3. Menos dependencias

* **Antes:** El script requería la biblioteca `pandas` solamente para usar `df.cumsum()`
* **Cambio:** Se eliminó la dependencia de `pandas`. La lógica detrás de `df.cumsum()`  se implementó en Python de manera manual (usando `totalAptitud` y `puntoAleatorio`).
* **Beneficio:** El script es más ligero, tiene menos dependencias externas y es más fácil de ejecutar en cualquier entorno de Python.

### 4. Pruebas locales

* **Cambio:** Se añadió una función `prueba()`. Verifica la lógica de `Individuo.distanciaRuta` con un caso conocido (un cuadrado con distancia 40.0) para asegurar que algoritmo sea correcto.

## Dependencias

* `python 3.x`
* `numpy`
   Instalar `numpy`:
    ```bash
    pip install numpy
    ```

## Ejecución

  Ejecutar el script desde terminal:
  
    ```bash
    python TareaValidacionIII.py
    ```
 O en su defecto, abrir con VSCode y ejecutar localmente.
