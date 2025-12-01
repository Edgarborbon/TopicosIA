#################### BIBLIOTECAS IMPORTADAS ####################
import io
import logging
import re

import cv2 # [cv2] es la biblioteca [OpenCV], su función es procesar y manipular imágenes
import numpy as np # [NumPy] es la  clásica biblioteca encargada de manipular datos númericos, principalmente listas. Se necesita porque recibimos una lista de bytes que representan la imagen
from ultralytics import YOLO # [YOLO] es la librería encargada del modelo de IA. Es la usada para entrenar el modelo de reconocimiento de placas y utilizarlo. 
import easyocr # Mientras [YOLO] aprende a identificar qué es una placa (forma, textura, caracteristicas, etc) [easyocr] es el que se encarga de extraer el texto de dicha placa
from paddleocr import PaddleOCR # Al igual que [EasyOCR], [PaddleOCR] esa herramienta de reconocimiento y lectura de texto. Lo usamos en conjunto con [EasyOCR] por si este tiene problemas de lectura
from PIL import Image, ImageOps # [Pillow] es otra biblioteca de preprocesamiento y manejo de imagenes

#################### CARGA DE MODELOS ####################
print("CARGANDO YOLO")
# Cargamos nuestro modelo YOLO. Realizamos 3 modelos:
# 1.- 025 Epochs, 1 hora de entrenamiento. Muy ineficiente 
# 2.- 100 Epochs, 2 horas de entrenamiento. Mucho mejor que el primero pero seguía teniendo problemas. Fue entrenado igual de manera básica
# 3.- 150 Epochs, 6 horas de entrenamiento. Este fue el que decidimos usar al final. Es bastante inteligente pero todavía comete errores de vez, aunque muy pocos 
# Varias veces nos vimos tentados a buscar un modelo pre-entrenado de entre los miles que existen tento en Kaggle como en GitHub, foros, etc. Pero nos interesaba ver si podía realizarse esta tarea entrenando uno nosotros, y afortunadamente se logró
modeloYOLO = YOLO("bestV2.pt")

# Paddle genera mucha basura en la terminal, que si bien es util para el debugging, no nos sirve mucho así que los filtramos con esta linea de codigo
logging.getLogger("ppocr").setLevel(logging.WARNING)

#################### INICIALIZAR OCRS (Optical Character Recognition) ####################
# Para [Paddle], declarar [use_angole_cls] como False para evitar que interactue con la rotación de la imagen
ocrPaddle = PaddleOCR(use_angle_cls=False, lang="en")
ocrEasy = easyocr.Reader(["en"], gpu=False)
print("Modelos cargados.")

#################### FUNCIONES ####################


def limpiarTexto(textoRaw):
    """
        Función que recibe el texto de alguno de nuestros OCRs y se encarga de eliminar todo aquello que no sea una letra o un numero
        utilizando [isalnum]
        También aseguramos que sea una mayúsucla
    """
    # Recorremos caracter [c] por caracter el texto recibido y si es numero y/o letra, se concatena a la cadena de texto que regresamos a donde se llamó la función
    return "".join([c for c in textoRaw if c.isalnum()]).upper()


def validarFormato(textoCandidato):
    """
    Esta función garantiza que el texto extraído sea realmente el de la placa
    Durante el proceso de testeo, usamos fotos de placas aleatorias que encontramos en internet, esta función nos dice 
    si el texto que nos dio el OCR sea del formato de una de las placas que usamos para testeo.
    Esto es posible gracias a la biblioteca [re]. Usamos Regex para validar

    En otras palabras, las placas suelen seguir cierto formato (por ejemplo una placa de carro de sinaloa, el formato es LLL-NNN-L siendo L=Letra y N=Numero)
    Esta funcion comprueba que el texto sea de este formato
    """
    # Caso 1: LLL-NNN-A(Alfanumerico)
    if re.match(r"^[A-Z]{3}[0-9]{3}[A-Z0-9]$", textoCandidato):
        return True
    # Caso 2: LLL-NNNNN
    if re.match(r"^[A-Z]{3}[0-9]{4}$", textoCandidato):
        return True
    # Caso 3: LLL-NNN
    if re.match(r"^[A-Z]{3}[0-9]{3}$", textoCandidato):
        return True
    # Caso 4: N-LLL-N
    if re.match(r"^[0-9]{1}[A-Z]{3}[0-9]{3}$", textoCandidato):
        return True

    return False


def tecnicaSlidingWindow(textoRaw):
    """
    Esta función toma todo el texto capturado por el OCR y se asegura de que el texto que usaremos al final sea el de los valores de la placa.
    Por ejemplo, una placa puede tener un marco que diga la marca del carro (Nissan, por ejemplo), nos interesa que el texto que vamos a usar de aquí en adelante sea el texto de
    la placa, y no algún texto externo que se encuentre dentro del cuadro que nos dio [YOLO]
    """
    # Usamos la función ya explicada para tener solo los caracteres que nos importan
    textoLimpio = limpiarTexto(textoRaw)
    n = len(textoLimpio)
    if n < 6: # Si por alguna razón tenemos una cadena corta, paramos, algo anda mal
        return textoLimpio

    #################### TÉCNICA [SLIDING WINDOW] ####################
    # Una forma muy útil que encontramos para analizar cadenas de texto fue la conocida como [Sliding Window], o [Ventana Deslizante] en español
    # El concepto de esta técnica es de, en lugar de recorrer un texto caracter por caracter, generamos un fragmento de texto que vamos extrayendo y analizando y moviendo la posición
    # de dicho fragmento poco a poco de un lado a otro. 
    # De ahí viene el nombre, funciona igual que el concepto de una ventana o puerta corrediza
    # Supongamos que el OCR lee una cadena enorme de texto por alguna extraña razón, y en medio de esa cadena está lo que necesitamos, las placas
    # Con esta tecnica vamos analizando poco a pooco la cadena hasta que el fragmento que estamos analizando cumpla con el formato que uno espera de una placa (LLL-NNN por ejemplo)
    # Hacemos esto 2 veces, primero para 7 caracteres y luego para 6
    # Esto porque algunas placas modernas tienen 7 caracteres en lugar de 6
    # Si realizamos este procedimiento primero para placas viejas de 6, es posible que, en caso de que el texto contenga una placa nueva, y en este caso ignoraría el último caracter 

    # Sliding Window para placas de 7
    for i in range(n - 6): 
        fragmentoSlidingWindow = textoLimpio[i : i + 7] #Cortamos un fragmento de 7 caracteres
        if validarFormato(fragmentoSlidingWindow): # Se manda a la función que nos dice si tiene formato de placa o no
            return fragmentoSlidingWindow

    # Sliding Window para placas de 6
    for i in range(n - 5):
        fragmentoSlidingWindow = textoLimpio[i : i + 6]
        if validarFormato(fragmentoSlidingWindow):
            return fragmentoSlidingWindow

    # Si alguno de los ciclos anteriores nos dio una placa, se retorna dicho texto, de lo contrario retornamos el texto tal cual como llegó, de igual manera será rechazado por el algoritmo más adelante si este filtro no encontró nada
    return textoLimpio


def calificacionManual(texto, confianza, alturaRelativa):
    """
    Esta función calcula de otra forma la "calificación" del texto que hasta ahora creemos que es una placa.
    Es como una capa externa a la calificación que nos de alguno de los OCRs, más "personalizada" a las necesidades de este proyecto.
    Esto fue necesario porque si bien los OCRs son herramientas maravillosas, nada es perfecto y pueden cometer errores(principalmente porque son herramientas pre definidas para problemas más generales)
    
    Ejemplo, nuestros OCRs pueden estar 100% seguros de que "NISSAN" o "SINALOA" sean nuestra placa (confundiendo letras con numeros, viendo que ambas palabras tienen 7 letras así que podrían ser placas de 7 caracteres)
    Con esta función nos enfrentamos a esos errores
    """
    calificacion = confianza # Iniciamos con la misma calificación que nos dio el OCR

    # Primer evaluación: Tamaño
    # alturaRelativa representa el tamaño de la caja de texto extraida en comparación con la imagen (que debería ser SOLAMENTE la placa, extraída por [YOLO])
    # Si dicha caja de texto es muy pequeña en comparación, probablemente estamos usando algo que NO es nuestra placa (SINALOA, por ejemplo, suele venir abajo mucho más pequeño que nuestra placa)
    # En este caso, disminuímos por mucho la confianza que le tenemos al texto que creemos es una placa
    if alturaRelativa < 0.20:
        calificacion -= 0.5
    else:
        calificacion += 0.3

    # Segunda evaluación: Formato
    if validarFormato(texto):
        calificacion += 0.6

    # Tercera evaluación: Contenido
    # Las placas nunca tienen solamente letras o solamente numeros, siempre es una combinación estructurada de las dos cosas
    # Aquí evaluamos caracter por caracter y se suma o resta calificación dependiendo de si es una mezcla de ambos o no
    tieneLetras = any(c.isalpha() for c in texto)
    tieneNumeros = any(c.isdigit() for c in texto)

    if tieneLetras and tieneNumeros:
        calificacion += 0.2

    # Como ultimo pase, si la cadena de texto es más larga que una placa, restamos puntaje
    if len(texto) < 6 or len(texto) > 8:
        calificacion -= 0.3

    return calificacion #Devolvemos el puntaje final manual, separado de la confianza que tiene el OCR en el texto que se piensa es una placa


def generarCandidatosConFiltro(recorteYOLO):
    """
    Esta función genera varias versiones de la imagen recibida por [YOLO], cada una bajo un preprocesado diferente.
    De esta forma, si hay dificultad al leer la iamgen original, tenemos todavía otras opciones con distintas alteraciones y así alguna versión de la imagen
    debe ser fácil de leer por nuesstros OCRs
    """
    placaHDR = [] #Arreglo que contendrá las imagenes alteradas junto con la original

    # La imagen original siempre vale la pena revisar, pueden darse casos donde no haya ningun problema con ella y el OCR pueda extraer la placa sin dificultad
    placaHDR.append(recorteYOLO)

    # Tomamos la imagen y la convvertimos a blanco y negro, para mejorar el resultado de los siguientes filtros
    placaBlancoyNegro = cv2.cvtColor(recorteYOLO, cv2.COLOR_BGR2GRAY)

    # [Erosión Morfológica]
    # Esta versión de las placas es super util en casos donde las letras de las placas sean muy gruesas, causndo así que algunas se mezclen o que una letra extraña se deforme, como por ejemplo la M con la H
    # El proceso de [Erosión] elimina un poco de los bordes de las letras, quitando así parte del grosor excesivo. Así, obtenemos letras más delgadas, que deberían ser más fáciles de leer por el OCR en algunos casos

    # Primero generamos una matriz de [1s], de 2x2. Dicha matriz será la que pasaremos por encima de cada pixel de la imagen aplicando el filtro de erosión
    matrizPincel = np.ones((2, 2), np.uint8)
    # Ahora toca aplicar dicho filtro. Usamos [erode] de [OpenCV] para tomar el objeto matriz que acabamos de crear, y lo aplica cada pixel de la imagen hasta recorrer todos los pixeles al menos 1 vez
    placaErosion = cv2.erode(placaBlancoyNegro, matrizPincel, iterations=1)
    # Finalmente, devolvemos los canales RGB a la imagen por que tienen que por lo menos existir para que funcionen correctamente los OCR y se añaden al arreglo 
    placaHDR.append(cv2.cvtColor(placaErosion, cv2.COLOR_GRAY2BGR))

    # [HDR]
    # [High Dynamic Range] es un filtro muy común que altera mucho el contraste y los colores de una imagen
    # Pueden darse casos donde la iluminación de la imagen haga imposible para el OCR leer su contenido, o puede darse un caso donde las letras de las placas estén ya muy viejas y sin color, haciendo que
    # se pierdan con el fondo
    # Aplicando estos filtros nivelamos los brillos con los oscuros, facilitando así la lectura en estos casos que si bien son raros, existen

    # Primero eliminamos el efecto [Moire], este es el nombre del efecto visual como la famosa rueda de hipnosis
    # En terminos más tecnicos, es el efecto que se da cuando dos patrones repetitivos se superponen
    # Muy común al tomar fotos a pantallas o al hacer zoom excesivo en algunos casos
    
    antiMoire = cv2.bilateralFilter(placaBlancoyNegro, 9, 75, 75) 
    # 9 = diametro de pixeles que va explorando 
    # 75 = Valor que define qué tan diferentes deben ser dos colores para no mezclarse. El 75 es un valor alto así que solo mezclará colores parecidos
    # 2do 75 = La distancia definida para que un pixel afecte a otro. En otras palabras, que tanta distancia va a evaluar este filtro para decir "estos dos puntos están cerca/lejos"

    # [CLAHE] o [Contrast Limited Adaptive Histogram Equalization]
    # El algoritmo [CLAHE] se encarga de mejorar el contraste local de una imagen
    # Divide la imagen en pequeños fragmengtos(grids se les llama aquí), altera el contraste de cada grid y finalmente los une todos de nuevo
    # Creamos el objeto CLAHE con [OpenCV], definiendo sus dimensiones
    objetoCLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    claheConHDR = objetoCLAHE.apply(antiMoire) # Finalmente, al objeto le aplicamos el efecto anti Moire creado anteriormente
    placaHDR.append(cv2.cvtColor(claheConHDR, cv2.COLOR_GRAY2BGR)) #De nuevo, restaurar canales RGB antes de añadir a array de imagenes candidatas y retornar al llamado de la funcion

    return placaHDR


#################### FUNCIÓN PRINCIPAL DE LECTURA ####################


def leerPlaca(imagenBytes):
    """
    Función que recibe los bytes que representan la iamgen, la reconstruye y aplica todo el procedimiento.
    Extraer placa con [YOLO]
    """

    try:
        fotoPillow = Image.open(io.BytesIO(imagenBytes.read())) #Abrimos la imagen desde la RAM para no tener que almancenarla localmente, agilizando el proceso
        fotoPillow = ImageOps.exif_transpose(fotoPillow) # Normalmente, los telefonos guardan la rotación de la imagen en sus metadatos. Con esta linea garantizamos que la iamgen tenga la orientación que [YOLO] puede leer
        # Convertimos la imagen del formato de [Pillow] a un formato numerico[NumPy]
        frame = np.array(fotoPillow)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convertimos de RGB a BGR, el formato que manipula [OpenCV]
    except Exception as e:
        return (False, f"Error imagen: {e}")

    # Si la imagen viene de una altísima calidad, hacemos downscaling para agilizar
    alto, ancho = frame.shape[:2]
    if ancho > 1280:
        factor = 1280 / ancho
        frame = cv2.resize(frame, (1280, int(alto * factor)))

    #################### EJECUCIÓN DE MODELO [YOLO] #################### 
    # Pasamos la imagen al modelo [YOLO] para que este nos devuelva el recorte con la pura placa
    # El valor de la confianza está un poco bajo para evitar casos donde no pueda detectar placas un poco deformes/sucias
    resultadosYOLO = modeloYOLO(frame, conf=0.15, verbose=False)

    # Iniciamos las variables en un caso negativo para devolverlas así tal cual en caso de que no haya ninguna placa detectada
    mejorPlaca = "No detectado"
    mejorCalificacionTotal = -1.0
    cajasDetectadas = 0

    # Por cada elemento en [resultadosYOLO]...
    for r in resultadosYOLO:
        # Evaluamos cada caja de texto detectada
        for box in r.boxes:
            cajasDetectadas += 1
            # Tomamos la coordenadas crudas que tenemos de la caja y las convertimos del formato de PyTorch a valores enteros normales
            # Definimos que los datos deben ser evaluados por el CPU, ya que configurar una GPU no Nvidia para todo este proedimiento es una tortura
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int) 

            # [YOLO] suele hacer recortes muy perfectos, lo que puede lastimar la lectura del OCR. 
            # Expandimos el recorte 30px para facilitarle el trabajo a los OCR
            # Usamos -30 y +30 para los valores mínimos y máximos respectivamente porque si x está en la pura esquina, restarle 30 daría -30, rompiendo el script, así que tenemos que aclarar que ese límite es aceptable
            # Lo mismo al revés, si estamos en el tope, sumar 30 al valor maximo sería como querer interactuar con un indice inexistente en un ciclo for, rompiendo todo
            h, w = frame.shape[:2] #Definimos la altura(height/[h]) y anchura(width/[w]) a que sean iguales a la foto original
            x1 = max(0, x1 - 30)
            y1 = max(0, y1 - 30)
            x2 = min(w, x2 + 30)
            y2 = min(h, y2 + 30)
            # Con estos datos, hacemos el recorte
            recorteAmplio = frame[y1:y2, x1:x2]

            # Creamos una copia invertida de la imagen en el EXTRAÑO pero no imposible caso que el teléfono mande la imagen al revés
            # De esta forma debemos tener al menos 1 foto con la rotación deseada 
            recorteInvertido = cv2.rotate(recorteAmplio, cv2.ROTATE_180)
            placasAmbasOrientaciones = [recorteAmplio, recorteInvertido]

            print(f"--- PROCESANDO CAJA {cajasDetectadas} ---") #Monitoreo

            for imagen in placasAmbasOrientaciones: # Este ciclo es el que usará dichas imagenes, donde una sí o sí tendrá la orientación deseada
                # Mandamos la imagen y generamos las copias con los filtros definidos anteriormente: [Erosión] y [HDR/CLAHE]
                candidatosConFiltro = generarCandidatosConFiltro(imagen)

                #################### PRIMER ANALISIS: [EASYOCR] ####################
                try:
                    # Pasamos por cada imagen generada y le pedimos a [EasyOCR] que intente leer las placas
                    for i, imagenConFiltro in enumerate(candidatosConFiltro):
                        resultadoEasyOCR = ocrEasy.readtext(
                            imagenConFiltro,
                            detail=1,
                            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-", #Definimos los únicos caracteres que nos importan, para mayor seguridad
                        )

                        # Ahora tomamos lo que leyó, y le aplicamos los distintos filtros y verificacion de formato antes definidos
                        for bbox, textoSucio, conf in resultadoEasyOCR:
                            # Calculamos qué tan alto es el texto en relación a la imagen recortada
                            ys = [pt[1] for pt in bbox]
                            alturaRel = (max(ys) - min(ys)) / imagen.shape[0]

                            textoLimpio = tecnicaSlidingWindow(textoSucio) #Limpiamos el texto de caracteres innecesarios
                            # Y calculamos el puntaje manual nuestro
                            calificacion = calificacionManual(
                                textoLimpio, float(conf), alturaRel
                            )

                            print(
                                f"   EasyOCR (Filtro {i}): {textoLimpio} (S:{calificacion:.2f}) Original: {textoSucio}" #Monitoreo
                            )

                            # Vamos modificando el puntaje total sobre la marcha
                            if calificacion > mejorCalificacionTotal:
                                mejorCalificacionTotal = calificacion
                                mejorPlaca = textoLimpio
                except:
                    pass

                #################### SEGUNDO ANALISIS: [PADDLEOCR] ####################
                # En el caso de que [EasyOCR] no haya podido leer nada con una confianza aceptable, probamos con [PaddleOCR]
                # Tomamos la mejor calificación que tenemos hasta ahora y si está por debajo de 1.2, pasamos ahora a PaddleOCR
                if mejorCalificacionTotal < 1.2:
                    for i, imagenConFiltro in enumerate(candidatosConFiltro): # Repetimos el mismo procedimiento que con [EasyOCR]
                        try:
                            # [PaddleOCR] funciona de manera diferente, es más delicado con los bordes así que añadimos un borde blanco extra a la imagen para que [PaddleOCR] no tenga problemas
                            imagenPaddle = cv2.copyMakeBorder(
                                imagenConFiltro,
                                20,
                                20,
                                20,
                                20,
                                cv2.BORDER_CONSTANT,
                                value=(255, 255, 255), # Color blanco
                            )
                            # Ejecutamos [PaddleOCR]
                            # Ejecutamos el modelo sobre la imagen con borde añadido y guardamos el resultado en una lista
                            # 
                            resultadoPaddleOCR = ocrPaddle.ocr(imagenPaddle, cls=False) # IMPORTANTE: cls=False para evitar errores, ya manipulamos la orientación nosotros

                            # Verificamos que haya leído algo
                            if resultadoPaddleOCR and resultadoPaddleOCR[0]:
                                # Se dieron situaciones donde [PaddleOCR] nos devolvía diferentes formatos de lista, con este if cubrimos ambos casos (uno siendo [Texto, Confianza], y otro siendo [Coordenadas, Texto, Confianza])
                                for linea in resultadoPaddleOCR[0]:
                                    if isinstance(linea[1], list):
                                        textoSucio, conf = linea[1][0], linea[1][1] 
                                    else:
                                        textoSucio, conf = (
                                            linea[1],
                                            linea[2] if len(linea) > 2 else 0.5,
                                        )

                                    # Calculamos qué tan alto es el texto en relación a la imagen de [YOLO], tomando en cuenta el borde añadido
                                    ys = [pt[1] for pt in linea[0]] #Guardamos los 4 puntos Y de la caja y se guardan en una lista, estos puntos representan las esquinas de la caja que [PaddleOCR] detectó
                                    alturaRel = (max(ys) - min(ys)) / imagenPaddle.shape[0] # [.shape[0]] porque la imagen creció al añadir el borde

                                    # Limpiamos el texto y calculamos la calificacion manual igual que antes
                                    textoLimpio = tecnicaSlidingWindow(textoSucio)
                                    calificacion = calificacionManual(
                                        textoLimpio, float(conf), alturaRel
                                    )

                                    print(
                                        f"   Paddle (Filtro {i}): {textoLimpio} (S:{calificacion:.2f})" #Monitoreo
                                    )

                                    # Si la calificación es mejor que la mejor hasta ahora, la guardamos, en este caso [PaddleOCR] encontró un mejor resultado que [EasyOCR]
                                    if calificacion > mejorCalificacionTotal:
                                        mejorCalificacionTotal = calificacion
                                        mejorPlaca = textoLimpio
                        except:
                            continue

    if cajasDetectadas == 0:
        return (False, "No se detectó ninguna placa en la imagen")

    if mejorPlaca != "No detectado" and mejorCalificacionTotal > 0.5:
        return (True, mejorPlaca)
    else:
        return (False, "Lectura de baja confianza, intente de nuevo")
