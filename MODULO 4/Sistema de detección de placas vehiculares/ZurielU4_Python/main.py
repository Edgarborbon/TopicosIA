#################### BIBLIOTECAS IMPORTADAS ####################
# [Flask] es la librería principal para utlizar la computadora ejecutando el script como "servidor"
# [request] es la clase utilizada para envíar y recibir información desde el teléfono. Es la encargada de los típicos [POST] y [GET]
# [jsonify] convertirá la información que enviará este script de Python a formato [JSON], el cual es el que entiende la API en el celular
from flask import Flask, jsonify, request

# Funciones necesarias para el algoritmo, en sus propios archivos para mejor organización
import detectorDePlacas
import enviarEmail
import operacionesSQL

app = Flask(__name__)

#################### COMUNICACIÓN CON LA APP  ####################

# Aquí definimos los llamados "endpoints" o "puertas" que la app usará para comunicarse con este script
# Cada endpoint debe coincidir con los definidos en Android Studio


#################### REGISTRAR ####################
# POST y GET son los métodos más comunes para enviar y recibir datos
@app.route("/registrarPlaca", methods=["POST"])
def registrarPlaca():
    # Tomamos los datos que capturamos en el formulario de la app
    # try-except para validar que no falten datos, evitando errores
    try:
        nombre = request.form["nombre"]
        apPaterno = request.form["apPaterno"]
        apMaterno = request.form["apMaterno"]
        email = request.form["email"]
    except Exception as e:
        return jsonify({"error": f"Faltan datos en el formulario: {e}"}), 400
    # De igual manera, comprobamos que se haya enviado una imagen
    if "image" not in request.files:
        return jsonify({"error": "No se envió imagen"}), 400
    imagenBytes = request.files["image"]

    # Una vez validados los datos, mandamos los bytes que representan la imagen a la función que la procesará
    # El formato de respuesta es una tupla (bool, string)
    # boolResultadoLEerPlaca = True, el string contiene la placa detectada
    # boolResultadoLeerPlaca = False, el string contiene el mensaje de error
    # De esta forma se nos facilita mucho devolverle a la app la respuesta adecuada
    (boolResultadoLeerPlaca, resultadoLeerPlaca) = detectorDePlacas.leerPlaca(imagenBytes)

    if not boolResultadoLeerPlaca:
        return jsonify({"error": resultadoLeerPlaca}), 400

    # Guardamos en la base de datos a la persona y su carro, relacionandolos con una tabla intermedia
    # Igual que arriba, tupla(bool, string)
    # True para avisar que se guardó23
    # False para mostrar error
    (boolResultadoQuery, resultadoQuery) = operacionesSQL.insertPersonaCarro(
        nombre, apPaterno, apMaterno, email, resultadoLeerPlaca
    )

    if boolResultadoQuery:
        return jsonify({"mensaje": resultadoQuery, "placa": resultadoLeerPlaca})
    else:
        return jsonify({"error": str(resultadoQuery)}), 500


#################### DETECTAR ####################
@app.route("/enviarImagen", methods=["POST"])
def detectarPlacaSolo():
    # Validar que recibimos una imagen
    if "image" not in request.files:
        return jsonify({"error": "No se envió imagen"}), 400
    imagenBytes = request.files["image"]

    # Enviamos la imagen a la función que la procesará
    (boolResultadoLeerPlaca, resultadoLeerPlaca) = detectorDePlacas.leerPlaca(imagenBytes)

    if boolResultadoLeerPlaca:
        return jsonify({"placa": resultadoLeerPlaca})
    else:
        return jsonify({"error": resultadoLeerPlaca}), 400


#################### REPORTAR  ####################
@app.route("/crearReporte", methods=["POST"])
def reportarIncidencia():
    # Tomamos los datos que capturamos en el formulario de la app
    # try-except para validar que no falten datos, evitando errores
    try:
        descripcion = request.form["descripcion"]
        lat = request.form["lat"]
        lng = request.form["lng"]
    except Exception as e:
        return jsonify({"error": f"Faltan datos (descripcion, lat, lng): {e}"}), 400

    # De igual manera, comprobamos que se haya enviado una imagen
    if "image" not in request.files:
        return jsonify({"error": "No se envió imagen"}), 400
    imagenBytes = request.files["image"]

    # Enviamos la imagen a la función que la procesará
    (boolResultadoLeerPlaca, resultadoLeerPlaca) = detectorDePlacas.leerPlaca(imagenBytes)
    if not boolResultadoLeerPlaca:
        return jsonify({"error": resultadoLeerPlaca}), 400

    # Buscamos al dueño de la placa que estamos reportando
    (boolResultadoSelect, resultadoSelect) = operacionesSQL.selectPropietario(
        resultadoLeerPlaca
    )
    if not boolResultadoSelect:
        return jsonify({"error": str(resultadoSelect)}), 404

    # Una vez tenemos los datos de la persona a reportar, los enviamos a la función
    personaID = resultadoSelect["personaID"]
    carroID = resultadoSelect["carroID"]
    (boolResultadoInsert, resultadoInsert) = operacionesSQL.insertIncidencia(
        personaID, carroID
    )

    # En caso de error, se notifica TODO poner otro error
    if not boolResultadoInsert:
        return jsonify({"error": str(resultadoInsert)}), 500

    #################### ENVIAR EMAIL DE REPORTE ####################
    # Ya se registró el reporte en la base de datos, lo siguiente es, en caso de ser la 3era vez que se reporta, enviar el email al dueño para notificarle
    if resultadoInsert >= 1:
        print(f"Lógica de email activada. {resultadoInsert} es >= 3.")
        (boolResultadoEmail, resultadoEmail) = enviarEmail.enviarEmail(
            resultadoSelect, descripcion, lat, lng, resultadoInsert
        )

        if boolResultadoEmail:
            return jsonify({"mensaje": resultadoEmail})
        else:
            return jsonify({"error": str(resultadoEmail)}), 500
    else:
        # Si es la incidencia 1 o 2 (en producción), solo guardamos pero no enviamos email
        print(f"Incidencia registrada. {resultadoInsert} es < 3. No se envía email.")
        return jsonify(
            {
                "mensaje": f"Incidencia #{resultadoInsert} registrada para {resultadoLeerPlaca}. Se notificará al propietario a las 3 incidencias."
            }
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
