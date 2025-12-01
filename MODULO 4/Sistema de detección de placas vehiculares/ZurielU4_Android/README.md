# Sistema de Detección de Placas (Full-Stack)

> Este es un proyecto académico full-stack diseñado para la detección y gestión de placas vehiculares. Combina una aplicación móvil nativa de Android (Kotlin/Compose) con un potente backend de Inteligencia Artificial (Python/Flask) para identificar, registrar y reportar vehículos.

El sistema es capaz de:
* Detectar el texto de una placa vehicular usando la cámara.
* Registrar nuevos propietarios y asociarlos a un vehículo.
* Generar reportes de incidentes (con ubicación GPS), buscar al propietario en la base de datos e incrementar un contador de incidencias.
* Notificar al propietario de un vehículo reportado vía email.

---

##  Tecnologías Utilizadas

* **Frontend (App Móvil):**
    * Kotlin
    * Jetpack Compose
    * Retrofit2 (para comunicación de red)
* **Backend (API):**
    * Python
    * Flask (como framework de API)
    * Gunicorn (como servidor de producción WSGI)
* **Inteligencia Artificial:**
    * Ultralytics YOLO (para detección de objetos/placas)
    * EasyOCR (para extracción de texto de la placa)
* **Base de Datos:**
    * MySQL
* **Servicios y Herramientas:**
    * `ngrok` (para crear un túnel público a localhost)
    * `smtplib` (para el envío de emails de notificación)

---

##  Flujo de Operaciones

La arquitectura del proyecto se divide en 3 componentes principales que se comunican de la siguiente manera:

1.  **Cliente (App Android):** El usuario interactúa con la app en Jetpack Compose. Al tomar una foto y llenar un formulario (ej. un reporte de incidencia), la app también obtiene la **ubicación GPS** del dispositivo.
2.  **Túnel (`ngrok`):** La app Android no apunta a una IP local, sino a una **URL pública estática** provista por `ngrok` (ej. `https://mi-app.ngrok-free.app/`).
3.  **Servidor Local (PC/Laptop):**
    * `ngrok` recibe la petición y la redirige de forma segura a `localhost:5000` en la máquina que corre el servidor.
    * **Gunicorn** recibe la solicitud y la pasa a un *worker* de Flask.
    * **Flask** (`apiSQLFULL.py`) recibe los datos (imagen, texto, lat, lng).
4.  **Procesamiento de IA:**
    * El backend usa **YOLO** para encontrar la *ubicación* de la placa en la imagen.
    * Luego, recorta esa área y usa **EasyOCR** para *leer* el texto de la placa.
5.  **Base de Datos (MySQL):**
    * La API (Flask) usa la placa detectada para consultar la base de datos MySQL.
    * Dependiendo del *endpoint*, puede:
        * `/registrar`: Guardar una nueva persona, carro y su relación.
        * `/reportar_incidencia`: Buscar al dueño de la placa, obtener sus IDs y actualizar la tabla `incidencias` (incrementando el contador `numIncidencia`).
6.  **Notificación (Email):**
    * Si un reporte es generado, el servidor usa `smtplib` y una cuenta de Gmail para enviar una alerta por correo al propietario, incluyendo la descripción de la incidencia y un enlace de Google Maps con la ubicación GPS del reporte.



---

##  Configuración y Dependencias

Para ejecutar este proyecto, necesitas configurar los 3 componentes.

### 1. Base de Datos (MySQL)

1.  Asegúrate de tener un servidor MySQL en ejecución (ej. XAMPP, MariaDB, MySQL Workbench).
2.  Crea una nueva base de datos llamada `appPlacas`.
3.  Crea las cuatro tablas según el esquema: `Personas`, `Carros`, `Propietarios`, e `Incidencias`.
4.  **(Recomendado)** Añade índices para optimizar las búsquedas de la API:
    ```sql
    CREATE UNIQUE INDEX idx_placa ON Carros (placa);
    CREATE INDEX idx_incidencias_carroID ON incidencias (carroID);
    ```

### 2. Backend (Python)

1.  Clona este repositorio y navega a la carpeta del backend.
2.  **¡IMPORTANTE!** Descarga tu modelo entrenado de YOLO y colócalo en la raíz con el nombre `best.pt`.
3.  Crea un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # (En Linux/macOS)
    .\venv\Scripts\activate   # (En Windows)
    ```
4.  Instala todas las dependencias:
    ```bash
    pip install flask gunicorn ultralytics easyocr opencv-python-headless mysql-connector-python python-dotenv
    ```
5.  **¡No guardes contraseñas en el código!** (ver sección de Precauciones).

### 3. Frontend (Android)

1.  Abre el proyecto de la app en Android Studio.
2.  Navega a `MainActivity.kt`.
3.  Busca el objeto `RetrofitClient` y **actualiza la `BASE_URL`** con tu URL estática de `ngrok`:
    ```kotlin
    object RetrofitClient {
        // CAMBIA ESTA URL POR TU DOMINIO ESTÁTICO DE NGROK
        private const val BASE_URL = "[https://tu-dominio-estatico.ngrok-free.app/](https://tu-dominio-estatico.ngrok-free.app/)"
    
        // ...
    }
    ```
   
4.  Compila la app y ejecútala en un dispositivo físico.

---

##  Precauciones de Seguridad: El archivo `.env`

Este proyecto es público gracias a `ngrok`, por lo que **NUNCA** debes escribir contraseñas directamente en `apiSQLFULL.py`.

1.  En la carpeta del backend, crea un archivo llamado `.env`.
2.  Añade tus credenciales en este archivo:
    ```.env
    # Contraseña de tu usuario 'root' de MySQL
    DB_PASSWORD="tu_password_de_mysql"
    
    # Contraseña de App de Google (NO tu contraseña normal de Gmail)
    EMAIL_PASSWORD="xxxx xxxx xxxx xxxx"
    ```
3.  Asegúrate de que tu `apiSQLFULL.py` esté configurado para leer estas variables (usando `os.getenv()`).
4.  Crea un archivo `.gitignore` para evitar subir tus credenciales o el modelo de IA (si es muy grande) a GitHub.
    ```.gitignore
    # Entorno virtual
    venv/
    
    # Archivos de caché de Python
    __pycache__/
    
    # ¡NUNCA SUBIR ESTO!
    .env
    
    # Modelo de IA (opcional si es muy grande)
    best.pt
    ```

---

##  Modo de Uso (Ejecución)

Para que el sistema funcione, debes tener 3 procesos corriendo:

1.  **Terminal 1: Base de Datos**
    * Asegúrate de que tu servicio MySQL (ej. XAMPP) esté en ejecución.

2.  **Terminal 2: Servidor Backend (Gunicorn)**
    * Activa tu entorno virtual y ejecuta Gunicorn enlazado a `localhost:5000`:
    ```bash
    source venv/bin/activate
    gunicorn -w 4 -b 127.0.0.1:5000 apiSQLFULL:app
    ```

3.  **Terminal 3: Túnel (`ngrok`)**
    * Inicia `ngrok` para exponer tu puerto 5000 usando tu dominio estático:
    ```bash
    ngrok http 5000 --domain=tu-dominio-estatico.ngrok-free.app
    ```

4.  **Dispositivo Móvil:**
    * Abre la app en tu teléfono (conectado a WiFi o datos móviles).
    * El sistema ahora está 100% operativo.

