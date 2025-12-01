package com.example.zuriel_u4

import okhttp3.MultipartBody
import okhttp3.RequestBody
//import retrofit2.Call
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import com.google.gson.annotations.SerializedName



// Una clase genérica para todas las respuestas.d
// Algunos campos serán 'null' dependiendo de la llamada.
data class ApiResponse(
    @SerializedName("placa") val placa: String?,
    @SerializedName("mensaje") val mensaje: String?,
    @SerializedName("error") val error: String?,
    @SerializedName("nombre") val nombre: String?,
    @SerializedName("apPaterno") val apPaterno: String?,
    @SerializedName("email") val email: String?
)

interface ApiService {

    // Llamada a la API para el detector
    @Multipart
    @POST("enviarImagen")
    suspend fun subirParaDetectar(
        @Part imagen: MultipartBody.Part
    ): ApiResponse

    // Llamada a la API para registrar
    @Multipart
    @POST("registrarPlaca")
    suspend fun subirParaRegistrar(
        @Part imagen: MultipartBody.Part,
        @Part("nombre") nombre: RequestBody,
        @Part("apPaterno") apPaterno: RequestBody,
        @Part("apMaterno") apMaterno: RequestBody,
        @Part("email") email: RequestBody
    ): ApiResponse

    // Llamada a la API para reportar
    @Multipart
    @POST("crearReporte")
    suspend fun reportarIncidencia( //
        @Part imagen: MultipartBody.Part,
        @Part("descripcion") descripcion: RequestBody,
        @Part("lat") lat: RequestBody,
        @Part("lng") lng: RequestBody
    ): ApiResponse
}
