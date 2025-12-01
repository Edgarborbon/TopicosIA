package com.example.zuriel_u4
// Pull test?
import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Book
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.zuriel_u4.ui.theme.ZurielU4Theme
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
//import retrofit2.Call
//import retrofit2.Callback
//import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import android.annotation.SuppressLint
import com.google.android.gms.location.LocationServices
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import androidx.activity.compose.BackHandler
import androidx.compose.material.icons.Icons
//import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.ui.res.painterResource
import kotlinx.coroutines.delay
import androidx.compose.material3.CircularProgressIndicator


// Definimos las pantallas que tendrá la aplicación
// Lo hacemos como clases enum para evitar errores
enum class Pantalla {
    Intro,
    Menu,
    Detector,
    Registro,
    Reporte,
    Manual
}

// Definimos la estructura o plantilla de cada botón en el menu
// Esto da consistencia, queremos que cada botón apunte a una pantalla, tenga un String(que representa el texto del botón) y un icono (importado arriba, para darle más estilo
data class opcionMenu(
    val pantalla: Pantalla,
    val etiqueta: String,
    val icono: ImageVector
)


// La lista de botones en el menu
// Siguiendo la estructura definida anteriormente, cada elemento tiene una pantalla, una etiqueta y el icono
val opcionesMenu = listOf(
    opcionMenu(Pantalla.Detector, "Detector de Placas", Icons.Default.DirectionsCar),
    opcionMenu(Pantalla.Registro, "Nuevo Registro", Icons.Default.AccountCircle),
    opcionMenu(Pantalla.Reporte, "Generar Reporte", Icons.Default.Warning),
    opcionMenu(Pantalla.Manual, "Manual de Usuario", Icons.Default.Book)
)



// El punto de inicio de la app
// Al abrir la app en el teléfono, esto es lo primero que se ejecuta para arrancar
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ZurielU4Theme {
                Inicio()
            }
        }
    }
}

// NAVEGADOR
// Esta aplicación está hecha usando Jetpack Compose, librería de diseño de interfaces que nos da Google y la que se enseña en la materia de Desarrollo de Dispositivos Móviles
// Tenemos aquí la lógica de navegación entre pantallas
@OptIn(ExperimentalAnimationApi::class) // AnimatedContent es una función experimental, debemos especificar esta linea para poder usarlo. Sirve para el efecto de transición entre pantallas. Esto aparecerá en todas las pantallas
@Composable
fun Inicio() {
    // pantallaActual recuerda la pantalla actual donde nos encontremos
    // rememberSaveable indica que queremos que nada cambie al girar el teléfono
    var pantallaActual by rememberSaveable { mutableStateOf(Pantalla.Intro) } // Definimos la pantalla inicial, un intro simple que insertamos


    // Asegurarnos que el botón de retorno del teléfono no cierre la app, pero que vuelva al menu
    BackHandler(enabled = (pantallaActual != Pantalla.Menu)) {
        pantallaActual = Pantalla.Menu
    }

    // [Jetpack Compose] trabaja con lo que llama [Scaffold], esta es una estructura básica de diseño que implementa lo básico como:
    // Barra superior, inferior, soporte de botones, cuerpo, etc
    // La estructura y diseño es lo típico de una aplicación Android, casi todas las apps sencillas siguen este patrón
    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->

        // Con [AnimatedContent] definimos el comportamiento de cambio de pantalla
        // Para mejorar la apariencia de la app, implementamos un efecto de difuminado(fade in/out) al cambiar de pantalla
        AnimatedContent(
            targetState = pantallaActual, // La animación ocurrirá cada que cambie [pantallaACtual]
            label = "Efecto de cambio de pantalla",
            transitionSpec = {
                // Declaramos el comportamiento de la animación.
                // un efecto donde la pantalla actual lentamente desaparece y aparece la nueva
                fadeIn(animationSpec = tween(600)) togetherWith // [togetherWith] especifica que ambas animaciones deben iniciar al mismo tiempo
                        fadeOut(animationSpec = tween(600))
            }
        ) { siguientePantalla -> // Definimos la proxima pantalla a la que nos dirige la animación

            // Usamos un when para controlar que objeto Composable(pantalla)
            // Como es posible que la pantalla cambie constantemente, hacerlo con un when es algo fácil
            when (siguientePantalla) {
                Pantalla.Intro -> pantallaIntro(
                    modifier = Modifier.padding(innerPadding),
                    onTimeout = { pantallaActual = Pantalla.Menu } // El intro no necesita/tiene comportamiento de darle al usuario opción de "regresar", así que le definimos un [onTimeout] para que solamente cambie de pantalla al pasar un tiempo
                )
                Pantalla.Menu -> pantallaMenu(
                    modifier = Modifier.padding(innerPadding),
                    onNavigate = { screen -> pantallaActual = screen } // Para el resto, sí es necesario usar [onNavigate]
                )
                Pantalla.Detector -> pantallaDetector(
                    modifier = Modifier.padding(innerPadding),
                    onNavigateBack = { pantallaActual = Pantalla.Menu }
                )
                Pantalla.Registro -> pantallaRegistro(
                    modifier = Modifier.padding(innerPadding),
                    onNavigateBack = { pantallaActual = Pantalla.Menu }
                )
                Pantalla.Reporte -> pantallaReporte(
                    modifier = Modifier.padding(innerPadding),
                    onNavigateBack = { pantallaActual = Pantalla.Menu }
                )
                Pantalla.Manual -> pantallaManual(
                    modifier = Modifier.padding(innerPadding),
                    onNavigateBack = { pantallaActual = Pantalla.Menu }
                )
            }
        }
    }
}

// #################### INTRO ####################
// Especificamos que esta pantalla funciona con [onTimeout] para navegación
@Composable
fun pantallaIntro(modifier: Modifier = Modifier, onTimeout: () -> Unit) {

    // Activamos el BackHandler ahora para que solo "atrape" el uso del botón, pero que no haga nada
    // De esta forma, durante la intro, el botón del teléfono no hará nada, evitando así comportamientos raros
    BackHandler(enabled = true) {} // Vacío para que no tenga función

    // Nos aseguramos de que esto solo pase una vez
    LaunchedEffect(key1 = true) {
        delay(2000L) // Hacemos que la intro dure 2 segundos
        onTimeout()  // Llamamos [onTimeout] para movernos al menu principal
    }

    // La intro es el logo de la escuela, la ponemos dentro de un [Box] para centrarla
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Image(
            painter = painterResource(id = R.drawable.tec), // [tec] es el nombre de la imagen
            contentDescription = "Logo de la App",
            modifier = Modifier.size(200.dp)
        )
    }
}
// #################### MENU ####################
// Esta pantalla, y las que faltan, ya tienen [onNavigate] para navegación
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun pantallaMenu(modifier: Modifier = Modifier, onNavigate: (Pantalla) -> Unit) {
    // Column funciona como un contenedor vertical, nos deja organizar los elementos verticalmente, cosa perfecta para el diseño que pensamos, de tener arriba el titulo y mas abajo los botones
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally, // Lo queremos centrado para mejor estética
    ) { //Aquí inicia la columna
        //Primero el titulo, que queremos dejar arriba
        Text(
            text = "Sistema de Control de Placas",
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(vertical = 24.dp)
        )
        Spacer(modifier = Modifier.weight(1f)) // Spacer funciona como un espacio en blanco que usamos como separador entre objetos. El weight indica cuanto espacio queremos que separe
        // Un LazyGrid(vertical en este caso) sirve para crear una cuadrícula sencilla.
        // Lazy se refiere a que no se va a complicar y solo pondrá en pantalla los objetos que quepan. Se usa mucho para cosas tipo galería de fotos, catalogos, etc
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            //modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) { //Aqui van los objetos que estarán en el grid
            items(opcionesMenu) { item -> // Recorremos la lista [opcionesMenu], y cada objeto de la lista se transforma en un botón [Card]
                // Cada botón del menú es un objeto [Card], nos gustó este por el tamaño y personalización que nos dieron, mas que un simple botón pequeño con texto
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(150.dp)
                        .clickable { onNavigate(item.pantalla) }, // El comportamiento del botón. Al oprimir, nos debe mandar a la pantalla deseada con [onNavigate]
                    elevation = CardDefaults.cardElevation(4.dp)
                ) { //El contenido de cada Card/botón, ordenados en una Column para tener el ícono arriba y el texto abajo
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Icon(item.icono, contentDescription = item.etiqueta, modifier = Modifier.size(48.dp))
                        Spacer(Modifier.height(8.dp)) // Separados por otro [Spacer]. Este usa [height] para que sea vertical solamente, mientras que [weight] es horizontal
                        Text(item.etiqueta, textAlign = TextAlign.Center)
                    }
                }
            }
        }
        Spacer(modifier = Modifier.weight(2f))
    }
}

// #################### DETECTOR DE PLACAS ####################
// Este pantalla funciona solamente para la detección de placas. Solamente nos dejará tomar una foto y al comunicarse con el script de python, nos devolverá la placa detectada, o un error en su defecto
@Composable
fun pantallaDetector(modifier: Modifier = Modifier, onNavigateBack: () -> Unit) {
    var bitmap by remember { mutableStateOf<Bitmap?>(null) } // Usamos bitmap para guardar y usar la foto. Útil porque el script de Python necesita la imagen en ese mismo formato para manipularla
    var resultadoPlaca by remember { mutableStateOf("") } // Variable que guardará el resultado que recibamos de la API, ya sea la placa o el error
    var cargando by remember { mutableStateOf(false) } // Variable para la animación de cargando del botón mientras esperamos respuesta de la API
    val context = LocalContext.current // Necesaria para pedir permisos
    val scope = rememberCoroutineScope() // Usamos scope para ejecutar la comunicación en segundo plano

    // Comportamiento de la cámara. Es necesario pedir permiso al usuario para usarla
    val cameraLauncher = rememberLauncherForActivityResult( // [rememberLauncherForActivityResult] especifica que los permisos deben recordarse una vez dados
        contract = ActivityResultContracts.TakePicturePreview(), // Contrato predefinido que abre la cámara, nos permite tomar la foto y al volver, se guarda en un bitmap
        onResult = { b: Bitmap? -> bitmap = b }
    )
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(), // Contrato que pide permiso para usar la cámara
        onResult = { isGranted: Boolean ->
            if (isGranted) cameraLauncher.launch(null) // Si se da permiso, se abre la cámara
        }
    )

    // El contenido de la interfaz estará dentro de una [Box] para mejor organización
    Box(modifier = modifier.fillMaxSize()) {
        Column(
            modifier = modifier.fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top // Alinea el texto al inicio
        ) {
//            Button(onClick = onNavigateBack) { Text("Volver al Menú") }

            Text(
                text = "Detector de Placas",
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            Spacer(modifier = Modifier.weight(1f))

            // Botón estilo Card para abrir la cámara
            Card(
                modifier = Modifier
                    .size(150.dp)
                    .clickable { launchCamera(context, permissionLauncher, cameraLauncher) },
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Icon(Icons.Default.CameraAlt, contentDescription = "Abrir cámara", modifier = Modifier.size(48.dp))
                    Spacer(Modifier.height(8.dp))
                    Text("Abrir Cámara", textAlign = TextAlign.Center)
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            // Objeto que mostrará la foto capturada
            // Si no hay foto, no se muestra la caja gracias a [bitmap != null]
            if (bitmap != null) {
                FotoPreviewBox(bitmap = bitmap)
            }
            // Texto para mostrar el resultado
            if (resultadoPlaca.isNotEmpty()) {
                Text(
                    text = resultadoPlaca,
                    style = MaterialTheme.typography.titleMedium,
                    color = if (resultadoPlaca.startsWith("Error")) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                )
            }

            // Solo muestra el espaciador y el botón de envío si hay una foto, de lo contrario se oculta, igual que el cuadro de arriba
            if (bitmap != null) {
                Spacer(Modifier.weight(1f))

                // Botón que envía la foto a la API
                Button(
                    onClick = {
                        if (bitmap != null) {
                            cargando = true // Indicamos que se está cargando, para la animación
                            // Hacemos el llamado a la API en 2do plano gracias a [scope]
                             scope.launch {
                                try {
                                    // Preparamos lo que vamos a enviar, en este caso la foto(como bitmap)
                                    // context es necesario para los permisos
                                    val body = bitmapToMultipartBody(bitmap!!, context)
                                    // Con los datos listos, llamamos la API
                                    // Usamos RetrofitClient para hacer la llamada, y guardamos la respuesta en la variable
                                    val apiResponse = RetrofitClient.instance.subirParaDetectar(body)

                                    // En caso de error, se muestra en pantalla
                                    if (apiResponse.error != null) {
                                        resultadoPlaca = "Error: ${apiResponse.error}"
                                    } else {
                                        resultadoPlaca = "Placa Detectada: ${apiResponse.placa}" // Caso contrario, mostramos la placa detectada en el script de Python
                                    }
                                } catch (e: Exception) {
                                    // Por si acaso, definimos comportamiento para errores de red, en lugar de que la app explote
                                    resultadoPlaca = "Error de conexión: ${e.message}"
                                }
                                cargando = false // Paramos la animación una vez termine la comunicación con la APÏ
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !cargando // El botón no debe ser funcional mientras está en proceso la comunicación para evitar errores (y para evitar spam de comunicaciones con el servidor, es una prueba gratuita de 1 mes con datos limitados)
                ) {
                    // Se define el comportamiento de la animación del botón de carga, el típico circulo de cargando
                    if (cargando) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary, // Color del texto del botón
                            strokeWidth = 3.dp
                        )
                    } else {
                        Text("Iniciar script de Detección de Placa") // Texto normal del botón
                    }
                }
            }
        }
        // Flecha hacia atrás en la esquina superior izquierda para volver al menú.
        IconButton(
            onClick = onNavigateBack,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(8.dp)
        ) {
            Icon(
                Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = "Volver al menu"
            )
        }
    }
}

// #################### REGISTRO ####################
@Composable
fun pantallaRegistro(modifier: Modifier = Modifier, onNavigateBack: () -> Unit) {
    // Variables del formulario de registro a la base de datos
    var nombre by rememberSaveable { mutableStateOf("") }
    var apellidoPaterno by rememberSaveable { mutableStateOf("") }
    var apellidoMaterno by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }
    var resultadoFinal by remember { mutableStateOf("") }
    var bitmap by remember { mutableStateOf<Bitmap?>(null) }
    var cargando by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    // Usamos esta variable para la lógica que manegamos de UI "dinamico", si no hay placa detectada, no hay necesidad de mostrar el formulario
    var detectedPlaca by rememberSaveable { mutableStateOf<String?>(null) }

    // Comportamiento de la cámara
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicturePreview(),
        onResult = { b: Bitmap? ->
            if (b != null) {
                bitmap = b
                cargando = true
                resultadoFinal = "Analizando imagen..."

                scope.launch {
                    try {
                        val body = bitmapToMultipartBody(b, context)
                        val apiResponse = RetrofitClient.instance.subirParaDetectar(body) // Misma llamada que la pantalla de detectar, no hay necesidad de crear otra

                        if (apiResponse.error != null) {
                            // Error, seguimos sin mostrar el formulario
                            resultadoFinal = "Error: ${apiResponse.error}. Intenta de nuevo."
                            bitmap = null
                            detectedPlaca = null // No formulario
                        } else {
                            // Caso opuesto, no hay error, entonces se detectó algo, ahora sí mostramos el formulario
                            detectedPlaca = apiResponse.placa
                            resultadoFinal = ""
                        }
                    } catch (e: Exception) {
                        resultadoFinal = "Error de conexión: ${e.message}"
                        bitmap = null
                        detectedPlaca = null
                    } finally {
                        cargando = false
                    }
                }
            }
        }
    )
    // Misma lógica de pedir permisos a usuario para usar la camara
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted: Boolean ->
            if (isGranted) cameraLauncher.launch(null)
        }
    )

    Box(modifier = modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {

            if (detectedPlaca == null) {
                // null = no hay placa detectada, el formulario estará oculto y mostramos solamente el título de la pantalla y el botón para tomar la foto
                Text(
                    "Detectar Placa",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(vertical = 8.dp),
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.weight(1f))

                Card(
                    modifier = Modifier
                        .size(150.dp) // Tamaño cuadrado
                        .clickable(enabled = !cargando) {
                            launchCamera(context, permissionLauncher, cameraLauncher)
                        },
                    elevation = CardDefaults.cardElevation(4.dp)
                ) {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Icon(Icons.Default.CameraAlt, contentDescription = "Abrir cámara", modifier = Modifier.size(48.dp))
                        Spacer(Modifier.height(8.dp))
                        Text("Abrir Cámara", textAlign = TextAlign.Center)
                    }
                }

                Spacer(modifier = Modifier.weight(1f))

                if (bitmap != null && !cargando) {
                    FotoPreviewBox(bitmap = bitmap)
                }

                if (cargando) {
                    CircularProgressIndicator(modifier = Modifier.padding(16.dp))
                }

                if (resultadoFinal.isNotEmpty()) {
                    Text(
                        text = resultadoFinal,
                        style = MaterialTheme.typography.titleMedium,
                        color = if (resultadoFinal.startsWith("Error")) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                    )
                }

            } else {
                // Si no es null, entonces tenemos una placa, así que ahora hay que mostrar el formulario para capturar el resto de datos del propietario

                Text(
                    "Datos del Propietario",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(vertical = 8.dp),
                    textAlign = TextAlign.Center
                )

                // Mostramos en texto la placa que detectamos, para saber si es una detección correcta antes de insertar a la base de datos
                Text(
                    "Placa: $detectedPlaca",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(bottom = 8.dp)
                )

                FotoPreviewBox(bitmap = bitmap) // Como existen placas, existe foto de ellas, así que mostramos dicha foto en el preview

                if (resultadoFinal.isNotEmpty() && !cargando) {
                    Text(
                        text = resultadoFinal,
                        style = MaterialTheme.typography.titleMedium,
                        color = if (resultadoFinal.startsWith("Error")) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary // Diferentes colores si es un mensaje de error o la placa detectada
                    )
                }

                // Formulario con la información a capturar en la base de datos
                TextField(value = nombre, onValueChange = { nombre = it }, label = { Text("Nombre") }, modifier = Modifier.fillMaxWidth())
                TextField(value = apellidoPaterno, onValueChange = { apellidoPaterno = it }, label = { Text("Apellido Paterno") }, modifier = Modifier.fillMaxWidth())
                TextField(value = apellidoMaterno, onValueChange = { apellidoMaterno = it }, label = { Text("Apellido Materno") }, modifier = Modifier.fillMaxWidth())
                TextField(value = email, onValueChange = { email = it }, label = { Text("Email") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email), modifier = Modifier.fillMaxWidth())


                Spacer(Modifier.weight(1f))

                // Botón para enviar
                Button(
                    onClick = {
                        if (bitmap != null) {
                            cargando = true
                            resultadoFinal = "Capturando..."

                            scope.launch {
                                try {
                                    // Preparamos los datos a enviar
                                    val body = bitmapToMultipartBody(bitmap!!, context)
                                    // Nos aseguramos que los datos sean texto plano para evitar errores
                                    val partNombre = RequestBody.create("text/plain".toMediaTypeOrNull(), nombre)
                                    val partApPaterno = RequestBody.create("text/plain".toMediaTypeOrNull(), apellidoPaterno)
                                    val partApMaterno = RequestBody.create("text/plain".toMediaTypeOrNull(), apellidoMaterno)
                                    val partEmail = RequestBody.create("text/plain".toMediaTypeOrNull(), email)
                                    // Enviamos a la API los datos
                                    val apiResponse = RetrofitClient.instance.subirParaRegistrar(
                                        body, partNombre, partApPaterno, partApMaterno, partEmail
                                    )

                                    // Posibles respuestas, un error al capturar (falta de datos, datos erroneos, etc)
                                    if (apiResponse.error != null) {
                                        resultadoFinal = "Error: ${apiResponse.error}"
                                    } else {
                                        resultadoFinal = "Éxito: ${apiResponse.mensaje}" // O mensaje de que la operación salió bien
                                    }

                                } catch (e: Exception) {
                                    resultadoFinal = "Error de conexión: ${e.message}"
                                } finally {
                                    cargando = false
                                }
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !cargando

                ) {
                    if (cargando) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary,
                            strokeWidth = 3.dp
                        )
                    } else {
                        Text("Guardar en la base de datos")
                    }
                }
            }
        }
        IconButton(
            onClick = onNavigateBack,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(8.dp),
            enabled = !cargando
        ) {
            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver al menu")
        }
    }
}

// #################### REPORTE ####################
@SuppressLint("MissingPermission", "SuspiciousIndentation") // Ignoramos el warning de permiso
@Composable
fun pantallaReporte(modifier: Modifier = Modifier, onNavigateBack: () -> Unit) {
    var bitmap by remember { mutableStateOf<Bitmap?>(null) }
    var descripcion by rememberSaveable { mutableStateOf("") }
    var detectedPlaca by rememberSaveable { mutableStateOf<String?>(null) }
    var resultadoFinal by remember { mutableStateOf("") }
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    // Iniciamos una variable que usará los servicios de ubicación que nos da Google
    val fusedLocationClient = remember { LocationServices.getFusedLocationProviderClient(context) }
    var cargando by remember { mutableStateOf(false) }
    // Launcher que pide permisos de ubicación al usuario
    // Igual que con la cámara, el permiso solo se pide una vez
    val locationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted: Boolean ->
            if (isGranted) {
                resultadoFinal = "Permiso concedido. Presiona 'Reportar' de nuevo."
            } else {
                resultadoFinal = "Error: Permiso de ubicación denegado."
            }
        }
    )
    // Nos aseguramos de pedir los permisos en cuanto entremos a la pantalla
    LaunchedEffect(key1 = true) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            // Si no tenemos permiso, lo pedimos
            locationPermissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        }
    }
    // Launcher de la cámara
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicturePreview(),
        onResult = { b: Bitmap? ->
            if (b != null) {
                bitmap = b
                cargando = true
                resultadoFinal = "Detectando placa..."

                scope.launch {
                    try {
                        val body = bitmapToMultipartBody(b, context)
                        val apiResponse = RetrofitClient.instance.subirParaDetectar(body)

                        if (apiResponse.error != null) {
                            resultadoFinal = "Error: ${apiResponse.error}. Intenta de nuevo."
                            bitmap = null
                            detectedPlaca = null
                        } else {
                            detectedPlaca = apiResponse.placa
                            resultadoFinal = ""
                        }
                    } catch (e: Exception) {
                        resultadoFinal = "Error de conexión: ${e.message}"
                        bitmap = null; detectedPlaca = null
                    } finally {
                        cargando = false
                    }
                }
            }
        }
    )
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted: Boolean ->
            if (isGranted) cameraLauncher.launch(null)
        }
    )

    Box(modifier = modifier.fillMaxSize()){
        Column(
            modifier = modifier.fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            if (detectedPlaca == null) {
                Text("Detectar Placa", style = MaterialTheme.typography.headlineSmall, modifier = Modifier.padding(vertical = 8.dp), textAlign = TextAlign.Center)
                Spacer(Modifier.weight(1f))

                Card(
                    modifier = Modifier.size(150.dp).clickable(enabled = !cargando) { launchCamera(context, permissionLauncher, cameraLauncher) },
                    elevation = CardDefaults.cardElevation(4.dp)
                ) {
                    Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                        Icon(Icons.Default.CameraAlt, contentDescription = "Abrir cámara", modifier = Modifier.size(48.dp))
                        Spacer(Modifier.height(8.dp))
                        Text("Abrir Cámara", textAlign = TextAlign.Center)
                    }
                }

                Spacer(Modifier.weight(1f))

                if (cargando) {
                    CircularProgressIndicator(modifier = Modifier.padding(16.dp))
                }

                if (resultadoFinal.isNotEmpty()) {
                    Text(
                        text = resultadoFinal,
                        style = MaterialTheme.typography.titleMedium,
                        color = if (resultadoFinal.startsWith("Error")) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                    )
                }

            } else {
                // Si no es null, entonces tenemos una placa, así que ahora hay que mostrar el cuadro de texto que usaremos para escribir el reporte
                Text("Detalles del reporte", style = MaterialTheme.typography.headlineSmall, modifier = Modifier.padding(vertical = 8.dp), textAlign = TextAlign.Center)
                Text("Placa: $detectedPlaca", style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.primary, modifier = Modifier.padding(bottom = 8.dp))

                // Si la placa que estamos por reportar es erronea, mostramos un botón para escanear de nuevo
                // En una situación ideal, con un modelo perfecto, no debería haber necesidad
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                    Button(onClick = {
                        bitmap = null
                        detectedPlaca = null
                        resultadoFinal = ""
                        descripcion = ""
                    }) { Text("Escanear otra vez") }
                }

                FotoPreviewBox(bitmap = bitmap)

                if (resultadoFinal.isNotEmpty() && !cargando) {
                    Text(
                        text = resultadoFinal,
                        style = MaterialTheme.typography.titleMedium,
                        color = if (resultadoFinal.startsWith("Error")) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                    )
                }
                // El campo de texto que usaremos para escribir el reporte
                TextField(value = descripcion, onValueChange = { descripcion = it }, label = { Text("Descripción del reporte") }, modifier = Modifier.fillMaxWidth())

                Spacer(Modifier.weight(1f))
                // Ya con las placas a reportar, y el reporte escrito, tenemos este nuevo botón para enviar el reporte
                Button(
                    onClick = {
                        if (bitmap != null && descripcion.isNotBlank()) {
                            resultadoFinal = "Revisando permisos..." // Por si acaso, verificamos si existe permiso de ubicación
                            if (ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                                resultadoFinal = "Error: No hay permisos de ubicación."
                            } else {
                                cargando = true
                                resultadoFinal = "Obteniendo ubicación..."
                                scope.launch {
                                    fusedLocationClient.lastLocation.addOnSuccessListener { location -> // Enviamos la última mejor ubicación con lastLocation. Se maneja por latitud y longitud, perfecto para generar el link de Google Maps
                                        if (location != null) {
                                            val lat = location.latitude
                                            val lng = location.longitude
                                            resultadoFinal = "Enviando ubicación..."

                                                                        // Ya con la ubicación, podemos enviar el reporte a la base de datos con otro scope
                                                                        scope.launch {
                                                                            try {
                                                                                val body = bitmapToMultipartBody(bitmap!!, context)
                                                                                val partDescripcion = RequestBody.create("text/plain".toMediaTypeOrNull(), descripcion)
                                                                                val partLat = RequestBody.create("text/plain".toMediaTypeOrNull(), lat.toString())
                                                                                val partLng = RequestBody.create("text/plain".toMediaTypeOrNull(), lng.toString())

                                                                                val apiResponse = RetrofitClient.instance.reportarIncidencia(body, partDescripcion, partLat, partLng)
                                                                                if (apiResponse.error != null) {
                                                                                    resultadoFinal = "Error: ${apiResponse.error}"
                                                                                } else {
                                                                                    resultadoFinal = "Éxito: ${apiResponse.mensaje}"
                                                                                }
                                                                            } catch (e: Exception) {
                                                                                resultadoFinal = "Error de red: ${e.message}"
                                                                            } finally {
                                                                                cargando = false
                                                                            }
                                                                        }
                                        } else {
                                            resultadoFinal = "Error: No se pudo obtener la ubicación"
                                            cargando = false
                                        }
                                    }.addOnFailureListener { e ->
                                        resultadoFinal = "Error: ${e.message}"
                                        cargando = false
                                    }
                                }
                            }
                        } else {
                            resultadoFinal = "Error: Faltan datos"
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = bitmap != null && descripcion.isNotBlank() && !cargando
                ) {
                    if (cargando) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary,
                            strokeWidth = 3.dp
                        )
                    } else {
                        Text("Reportar")
                    }
                }
            }
        }
        IconButton(
            onClick = onNavigateBack,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(8.dp),
            enabled = !cargando
        ) {
            Icon(
                Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = "Volver al Menú"
            )
        }
    }
}

// // #################### MANUAL ####################
@Composable
fun pantallaManual(modifier: Modifier = Modifier, onNavigateBack: () -> Unit) {
    Box(modifier = modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top
        ) {
            Text(
                text = "Manual de Usuario",
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }
        IconButton(
            onClick = onNavigateBack,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(8.dp)
        ) {
            Icon(Icons.Default.ArrowBack, contentDescription = "Volver al Menú")
        }
    }
}


// #################### OBJETOS QUE SE REPITEN ####################

// La caja que muestra la foto capturada que se usa en todas las pantallas menos el manual
@Composable
fun FotoPreviewBox(bitmap: Bitmap?) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
            .border(1.dp, Color.Gray),
        contentAlignment = Alignment.Center
    ) {
        if (bitmap != null) {
            Image(
                bitmap = bitmap.asImageBitmap(),
                contentDescription = "Foto de la placa",
                modifier = Modifier.fillMaxSize()
            )
        } else {
            Text("Foto")
        }
    }
}

// Función que abre la cámara. Igual, se usa en todas las pantallas menos el manual
fun launchCamera(
    context: Context,
    permissionLauncher: androidx.activity.result.ActivityResultLauncher<String>,
    cameraLauncher: androidx.activity.result.ActivityResultLauncher<Void?>
) {
    val permissionStatus = ContextCompat.checkSelfPermission(
        context,
        Manifest.permission.CAMERA
    )
    if (permissionStatus == PackageManager.PERMISSION_GRANTED) {
        cameraLauncher.launch(null)
    } else {
        permissionLauncher.launch(Manifest.permission.CAMERA)
    }
}


// #################### COMUNICACIÓN CON LA API ####################
// Se usa un solo objeto REtrofitClient para todas las llamadas
object RetrofitClient {
      private const val BASE_URL = "https://untreacherous-darleen-silverlike.ngrok-free.dev" // URL de la API que obtuvimos al usar la versión gratuita de ngrok. Más detalles en el README
    val instance: ApiService by lazy {
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        retrofit.create(ApiService::class.java)
    }
}


// Esta función comprime la imagen y transforma el bitmap que representa dicha imagen a una cadena de bytes(los cuales sí entiende el script)
private fun bitmapToMultipartBody(bitmap: Bitmap, context: Context): MultipartBody.Part {
    val file = File(context.cacheDir, "placa.jpg") // Se guarda la imagen en caché
    file.createNewFile()
    // Convertimos el bitmap a bytes
    val bos = ByteArrayOutputStream()
    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, bos)
    val bitmapdata = bos.toByteArray()

    // Se guardan los bytes en un archivo temporal
    val fos = FileOutputStream(file)
    fos.write(bitmapdata)
    // Una vez guardado, se limpia el cache para no acumular eventualmente las imagenes
    fos.flush()
    fos.close()

    // Guardamos el archivo como una parte del body de la llamada
    val reqFile = RequestBody.create("image/jpeg".toMediaTypeOrNull(), file)
    // Y finalmente, crea el objeto MultipartBody.Part para enviar la imagen, con el nombre "image" y el archivo temporal, el resto ya es trabajo del script de Python
    return MultipartBody.Part.createFormData("image", file.name, reqFile)
}


//@Preview(showBackground = true)
//@Composable
//fun DefaultPreview() {
//    ZurielU4Theme {
//        ZurielU4App()
//    }
//}


// #################### PREVIEWS PARA DISEÑO EN ANDROID STUDIO SIN NECESIDAD DE EMULAR LA APP CADA QUE SE QUIERA VER EL CAMBIO ####################
@Preview(showBackground = true, name = "Pantalla del Menú")
@Composable
fun pantallaMenuPreview() {
    ZurielU4Theme {
        pantallaMenu(onNavigate = {})
    }
}

@Preview(showBackground = true, name = "Pantalla del scanner")
@Composable
fun pantallaDetectorPreview() {
    ZurielU4Theme {
        pantallaDetector(onNavigateBack = {})
    }
}

@Preview(showBackground = true, name = "Pantalla de Registro")
@Composable
fun pantallaRegistroPreview() {
    ZurielU4Theme {
        pantallaRegistro(onNavigateBack = {})
    }
}

@Preview(showBackground = true, name = "Pantalla de Incidencia")
@Composable
fun pantallaReportePreview() {
    ZurielU4Theme {
        pantallaReporte(onNavigateBack = {})
    }
}

@Preview(showBackground = true, name = "Pantalla Manual de Usuario")
@Composable
fun pantallaManualPreview() {
    ZurielU4Theme {
        pantallaManual(onNavigateBack = {})
    }
}