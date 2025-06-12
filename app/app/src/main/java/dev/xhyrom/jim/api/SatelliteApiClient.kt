package dev.xhyrom.jim.api

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.Call

/**
 * Interface for Satellite API communication
 */
interface SatelliteApiClient {
    /**
     * Get the current status of the satellite
     * @return SatelliteStatus object containing status information
     */
    @GET("/api/status")
    fun getStatus(): Call<SatelliteStatus>

    /**
     * Send a command to the satellite
     * @param command Command object containing the text to process
     * @return CommandResponse object with processing status
     */
    @POST("/api/ask")
    fun sendCommand(@Body command: Command): Call<CommandResponse>

    /**
     * Get the current configuration of the satellite
     * @return SatelliteConfig object with configuration settings
     */
    @GET("/api/config")
    fun getConfig(): Call<SatelliteConfig>

    /**
     * Update the satellite configuration
     * @param config SatelliteConfig object with updated settings
     * @return ApiResponse indicating success or failure
     */
    @PUT("/api/config")
    fun updateConfig(@Body config: SatelliteConfig): Call<ApiResponse>

    /**
     * Get system information from the satellite
     * @return SystemInfo object with hardware/software details
     */
    @GET("/api/system")
    fun getSystemInfo(): Call<SystemInfo>

    /**
     * Request a restart of the satellite service
     * @return ApiResponse indicating success or failure
     */
    @POST("/api/restart")
    fun restartSatellite(): Call<ApiResponse>
}

/**
 * Data classes for API responses and requests
 */
data class SatelliteStatus(
    val status: String,
    val state: String,
    val version: String
)

data class Command(
    val text: String
)

data class CommandResponse(
    val status: String,
    val message: String
)

data class ApiResponse(
    val status: String,
    val message: String,
    val error: String? = null
)

data class SystemInfo(
    val platform: String,
    val processor: String,
    val memory: MemoryInfo,
    val disk: DiskInfo
)

data class MemoryInfo(
    val total: Long,
    val available: Long,
    val percent: Double
)

data class DiskInfo(
    val total: Long,
    val free: Long,
    val percent: Double
)

data class SatelliteConfig(
    val asr: Map<String, Any>,
    val tts: Map<String, Any>,
    val wake: Map<String, Any>,
    val core: Map<String, Any>,
    val led: Map<String, Any>
)