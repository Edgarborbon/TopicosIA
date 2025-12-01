#################### BIBLIOTECAS IMPORTADAS ####################
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

#################### CONFIGURAR BASE DE DATOS ####################
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),
    "database": "appPlacas",
}

#################### FUNCIONES DE BASE DE DATOS ####################


def insertPersonaCarro(nombre, apPaterno, apMaterno, email, placaDetectada):
    # Declaramos las variables a utilizar para la conexión a la base de datos y el cursor que ejecuta consultas
    dbConexion = None
    dbCursor = None
    try:
        # Iniciamos la conexión a la base de datos
        dbConexion = mysql.connector.connect(**DB_CONFIG)
        dbCursor = dbConexion.cursor()

        # Declaramos el insert. [ON DUPLICATE KEY UPDATE] sirve para actualizar el nombre en caso de que el email ya exista, así no separamos
        # en dos consultas el proceso de verificación e inserción
        # %s es una forma en Python de declarar los llamados "placeholders", que se reemplazarán por los valores que recibamos en la función
        queryInsertPersona = "INSERT INTO Personas (nombre, apPaterno, apMaterno, email) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombre=VALUES(nombre)"
        dbCursor.execute(queryInsertPersona, (nombre, apPaterno, apMaterno, email))

        # Tomamos a la persona recién capturada/actualizada
        querySelectPersona = "SELECT personaID FROM Personas WHERE email = %s"
        dbCursor.execute(querySelectPersona, (email,))
        personaID = dbCursor.fetchone()[
            0
        ]  # [fetchone()] nos regresa una tupla con la fila en el cursor, de ahí agarramos el dato en el índice 0 que es el [personaID]

        # Insertamos el carro con las placas detectadas
        queryInsertCarro = "INSERT IGNORE INTO Carros (placa) VALUES (%s)"
        dbCursor.execute(queryInsertCarro, (placaDetectada,))

        # Tomamos al carro recién insertado
        querySelectCarro = "SELECT carroID FROM Carros WHERE placa = %s"
        dbCursor.execute(querySelectCarro, (placaDetectada,))
        carroID = dbCursor.fetchone()[0]

        # Y finalmente, creamos la relación en la tabla [Propietarios]
        queryInsertPropietario = "INSERT IGNORE INTO Propietarios (personaID, carroID, placeholder) VALUES (%s, %s, %s)"
        dbCursor.execute(
            queryInsertPropietario, (personaID, carroID, "Propietario Principal")
        )

        dbConexion.commit()  # Confirmamos los cambios en la base de datos, necesario para que los insert se guarden, algo similar a git commit

        # Devolvemos un mensaje para monitoreo
        resultadoQuery = (
            f"Registro guardado: {nombre} es propietario de {placaDetectada}"
        )
        print(resultadoQuery)
        return (True, resultadoQuery)

    # Configuramos la reacción a los errores.
    # En caso de error, hacemos un [rollback] para revertir las operaciones anteriores
    except mysql.connector.Error as err:
        if dbConexion:
            dbConexion.rollback()
        print(f"Error de BD: {err}")
        return (False, f"Error de base de datos: {err}")
    finally:  # [finally] es parte de la estructura try-catch en Python. Este bloque siempre se ejecuta, independientemente de si existieron errores o no
        # Nos aseguramos de cerrar conexión y cursor
        if dbCursor:
            dbCursor.close()
        if dbConexion:
            dbConexion.close()


def selectPropietario(placaDetectada):
    dbConexion = None
    dbCursor = None
    try:
        dbConexion = mysql.connector.connect(**DB_CONFIG)
        #################### DIFERENCIA CLAVE: DICCIONARIO ####################
        # Le indicamos al cursor que nos devuelva los resultado en forma de diccionario en lugar de tuplas como hace por defecto
        # Esto nos permite interactuar con los datos con los nombres de las columnas en lugar de sus índices
        # Ejemplo: Personas['nombre'] en lugar de Personas[1]
        # Hace más fácil leer el código y así no tenemos que memorizar los índices de cada columna
        dbCursor = dbConexion.cursor(dictionary=True)

        # Buscamos al dueño de la placa detectada, jalando datos de las 3 tablas con JOIN
        # Strings con [""""] en Python respetan los saltos de linea tal cual como se ponen.
        # Suele usarse mucho al integrar SQL en código para hacerlo más fácil de leer y de escribir
        querySelectPropietario = """
            SELECT 
                Personas.personaID, 
                Carros.carroID, 
                Personas.nombre, 
                Personas.apPaterno, 
                Personas.email, 
                Carros.placa
            FROM Personas
            JOIN Propietarios ON Personas.personaID = Propietarios.personaID
            JOIN Carros ON Propietarios.carroID = Carros.carroID
            WHERE Carros.placa = %s
        """
        dbCursor.execute(querySelectPropietario, (placaDetectada,))

        propietario = dbCursor.fetchone()

        # Revisamos si se encontró un propietario
        # Si sí, devolvemos los datos como diccionario
        if propietario:
            print(f"Propietario encontrado: {propietario}")
            return (True, propietario)
        else:  # Si no, devolvemos mensaje de error
            print(f"Placa {placaDetectada} no encontrada en la BD.")
            return (False, "Placa no encontrada en la base de datos")

    except mysql.connector.Error as err:
        print(f"Error de BD: {err}")
        return (False, f"Error de base de datos: {err}")
    finally:
        if dbCursor:
            dbCursor.close()
        if dbConexion:
            dbConexion.close()


def insertIncidencia(personaID, carroID):
    dbConexion = None
    dbCursor = None
    try:
        dbConexion = mysql.connector.connect(**DB_CONFIG)
        dbCursor = dbConexion.cursor()

        # Aquí hacemos uso de la técnica UPSERT para insertar o actualizar la fila en una sola consulta
        # Si la fila no existe, se inserta con numIncidencia = 1
        # Si ya existe, se actualiza incrementando numIncidencia en 1
        # El objetivo al final es saber cuantos reportes tiene un carro, ya que a los 3 se envía el email
        queryInsertIncidencia = """
            INSERT INTO incidencias (personaID, carroID, numIncidencia)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE
            numIncidencia = numIncidencia + 1
        """
        # Ejecutamos el upsert
        dbCursor.execute(queryInsertIncidencia, (personaID, carroID))

        # Una vez hecho el upsert, revisamos cuantos reportes tiene un carro y eso es lo que devuelve la función
        querySelectNumIncidencia = (
            "SELECT numIncidencia FROM incidencias WHERE carroID = %s"
        )
        dbCursor.execute(querySelectNumIncidencia, (carroID,))
        numIncidencias = dbCursor.fetchone()[0]

        dbConexion.commit()

        print(
            f"Reporte realizado. Carro {carroID} tiene ahora {numIncidencias} incidencias."
        )
        return (True, numIncidencias)  # Devolvemos el total de reportes

    except mysql.connector.Error as err:
        if dbConexion:
            dbConexion.rollback()
        print(f"Error de BD al registrar incidencia: {err}")
        return (False, f"Error de BD: {err}")
    finally:
        if dbCursor:
            dbCursor.close()
        if dbConexion:
            dbConexion.close()
