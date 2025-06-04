package dev.xhyrom.jim.api

import android.util.Log
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Service class for Satellite API communication
 */
class SatelliteApiService {
    private var retrofit: Retrofit? = null
    private var apiClient: SatelliteApiClient? = null
    
    companion object {
        private const val TAG = "SatelliteApiService"
        private const val CONNECT_TIMEOUT = 30L
        private const val READ_TIMEOUT = 30L
        private const val WRITE_TIMEOUT = 30L
        
        @Volatile
        private var INSTANCE: SatelliteApiService? = null
        
        fun getInstance(): SatelliteApiService {
            return INSTANCE ?: synchronized(this) {
                val instance = SatelliteApiService()
                INSTANCE = instance
                instance
            }
        }
    }
    
    /**
     * Creates or returns the API client
     * @param baseUrl Base URL of the satellite API
     * @return SatelliteApiClient interface implementation
     */
    fun getApiClient(baseUrl: String): SatelliteApiClient {
        if (apiClient == null || retrofit == null) {
            Log.d(TAG, "Creating new API client for $baseUrl")
            
            // Create logging interceptor
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            
            // Create OkHttp client
            val okHttpClient = OkHttpClient.Builder()
                .connectTimeout(CONNECT_TIMEOUT, TimeUnit.SECONDS)
                .readTimeout(READ_TIMEOUT, TimeUnit.SECONDS)
                .writeTimeout(WRITE_TIMEOUT, TimeUnit.SECONDS)
                .addInterceptor(loggingInterceptor)
                .build()
            
            // Create Gson instance
            val gson: Gson = GsonBuilder()
                .setLenient()
                .create()
            
            // Create Retrofit instance
            retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build()
            
            apiClient = retrofit?.create(SatelliteApiClient::class.java)
        }
        
        return apiClient ?: throw IllegalStateException("API Client could not be created")
    }
    
    /**
     * Checks if the API client is already initialized
     */
    fun hasClient(): Boolean {
        return apiClient != null && retrofit != null
    }
    
    /**
     * Resets the API client, forcing a new one to be created on the next call
     */
    fun resetClient() {
        apiClient = null
        retrofit = null
    }
}