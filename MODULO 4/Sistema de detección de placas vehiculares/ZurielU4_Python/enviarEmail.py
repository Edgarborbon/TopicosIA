#################### BIBLIOTECAS IMPORTADAS ####################
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import (
    load_dotenv,
)  # Permite cargar variables externas desde un archivo oculto .env, sin que se vean en este código, sirve para datos sensibles como contraseñas

load_dotenv()  # Cargar el archivo con los datos (Contraseña de la BD y del email)

#################### CONFIGURACIÓN DEL EMAIL ####################
emailRemitente = "eborbonsanchez@gmail.com"
emailContraseña = os.getenv("EMAIL_PASSWORD")


def enviarEmail(infoPropietario, descReporte, lat, lng, numReporte):
    try:
        #################### PREPARAR EMAIL ####################
        # Recibimos los datos que mencionaremos en el email
        # Recordemos que [datos_propietario] es un diccionario con los datos de la persona y el carro como definimos en la función: buscar_propietario_db()
        # Gracias a esto, podemos pedir en el codigo lo que necesitamos por nombre y no por índice
        emailDestinatario = infoPropietario["email"]
        placaReportada = infoPropietario["placa"]
        nombrePropietario = infoPropietario["nombre"]

        # Con la ubicación recibida, creamos el link de Google Maps que enviaremos para que el dueño sepa el lugar del reporte
        linkUbicacionReporte = f"https://www.google.com/maps?q={lat},{lng}"

        #################### CONTENIDO DEL EMAIL ####################
        # [MIMEMultipart] es el formato que permite crear emails, se le puede poner texto, imágenes, archivos adjuntos, etc
        # Definimos [alternative] para que el email pueda ser leído por cualquier servicio(Gmail, Outlook, etc)
        # Primero creamos el objeto
        objetoEmail = MIMEMultipart("alternative")
        # Y luego especificamos los campos típicos de un email, el asunto, el remitente y el destinatario
        objetoEmail["Subject"] = (
            f"Alerta de Incidencia - Placa: {placaReportada} (Incidencia #{numReporte})"
        )
        objetoEmail["From"] = emailRemitente
        objetoEmail["To"] = emailDestinatario

        # Ahora sigue el contenido
        # Como se explicó antes en el apartado de SQL, usamos [""""] para que Python respete los saltos de linea y espacios que escribamos aqui
        # De esta forma, si todo sale bien, el correo se verá tal cual y como está escrito, mismos saltos de linea y todo
        cuerpoEmail = f"""
        Saludos, {nombrePropietario},
        
        Hemos recibido un reporte acerca de su vehículo con placas: [{placaReportada}].
        
        Motivo del reporte:
        "{descReporte}"
        
        Este es el reporte número {numReporte} registrado para este vehículo.
        Recuerde que al tercer reporte, se le revocará el acceso al estacionamiento de forma temporal.
        
        Ubicación aproximada del reporte:
        {linkUbicacionReporte}
        
        Le pedimos que por favor genere conciencia sobre el uso adecuado de los espacios de estacionamiento y evitenos la pena de tomar medidas adicionales.
        Atentamente,
        Borbón Sánchez Edgar y Millán López Ana Karen.
        """

        # Adjuntamos el texto al mensaje del email
        # "plain" indica que es texto simple, sin formato especial ni nada
        objetoEmail.attach(MIMEText(cuerpoEmail, "plain"))

        # Ya con el correo construido, toca enviarlo usando [SMTP](Simple Mail Transfer Protocol) de Gmail
        # SSL (Secure Sockets Layer) es un protocolo de seguridad que cifra el contenido, es un requisito de Gmail
        protocoloSSL = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=protocoloSSL) as server:
            # Iniciamos sesión en el servidor SMTP de Gmail
            server.login(emailRemitente, emailContraseña)
            server.sendmail(emailRemitente, emailDestinatario, objetoEmail.as_string())
        # Monitoreo
        print(f"Email enviado con éxito a {emailDestinatario}")
        return (
            True,
            f"Incidencia #{numReporte} reportada con éxito para {placaReportada}",
        )

    except Exception as e:
        print(f"Error al enviar email: {e}")
        return (False, f"Error al enviar email: {e}")
