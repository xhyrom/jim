package dev.xhyrom.jim.data

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

data class DeviceStatus(
    val status: String,
    val version: String,
    val uptime: Long,
    val connected: Boolean
)

data class ConfigModel(
    val asr: AsrConfig,
    val tts: TtsConfig,
    val wake: WakeConfig,
    val core: CoreConfig,
    val led: LedConfig
)

data class AsrConfig(
    val type: String,
    val model_path: String?,
    val api_key: String?
)

data class TtsConfig(
    val type: String,
    val model_path: String
)

data class WakeConfig(
    val model_paths: List<String>,
    val threshold: Float
)

data class CoreConfig(
    val url: String,
    val api_key: String?
)

data class LedConfig(
    val driver_type: String,
    val num_leds: Int,
    val brightness: Int,
    val base_color: String,
    val schedule: Schedule
)

data class Schedule(
    val enabled: Boolean,
    val start_hour: Int,
    val end_hour: Int
)

interface ApiService {
    @GET("status")
    suspend fun getDeviceStatus(): DeviceStatus

    @GET("config")
    suspend fun getConfig(): ConfigModel

    @POST("config")
    suspend fun updateConfig(@Body config: ConfigModel): ConfigModel

    @POST("terminal/execute")
    suspend fun executeCommand(@Body command: Map<String, String>): Map<String, String>

    @POST("reboot")
    suspend fun rebootDevice(): Map<String, String>

    @POST("factory-reset")
    suspend fun factoryReset(): Map<String, String>

    @GET("bluetooth/scan")
    suspend fun scanBluetoothDevices(): List<BluetoothDevice>

    @POST("bluetooth/pair/{deviceId}")
    suspend fun pairWithDevice(@Path("deviceId") deviceId: String): Map<String, Boolean>

    companion object {
        private const val BASE_URL = "http://192.168.1.100:5000/api/"

        fun create(): ApiService {
            val logger = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY }

            val client = OkHttpClient.Builder()
                .addInterceptor(logger)
                .build()

            return Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(ApiService::class.java)
        }
    }
}

data class BluetoothDevice(
    val id: String,
    val name: String,
    val address: String,
    val type: String
)