package dev.xhyrom.jim.ui.satellite

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.api.ApiResponse
import dev.xhyrom.jim.api.Command
import dev.xhyrom.jim.api.CommandResponse
import dev.xhyrom.jim.api.SatelliteApiClient
import dev.xhyrom.jim.api.SatelliteApiService
import dev.xhyrom.jim.api.SatelliteStatus
import dev.xhyrom.jim.api.SystemInfo
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.data.repository.SatelliteRepository
import kotlinx.coroutines.launch
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class SatelliteViewModel(private val repository: SatelliteRepository) : ViewModel() {

    private val _selectedSatellite = MutableLiveData<Satellite>()
    val selectedSatellite: LiveData<Satellite> = _selectedSatellite

    private val _isConnected = MutableLiveData<Boolean>()
    val isConnected: LiveData<Boolean> = _isConnected

    private val _operationResult = MutableLiveData<String>()
    val operationResult: LiveData<String> = _operationResult
    
    // API related properties
    private val apiService = SatelliteApiService.getInstance()
    private var apiClient: SatelliteApiClient? = null
    
    private val _apiStatus = MutableLiveData<Boolean>()
    val apiStatus: LiveData<Boolean> = _apiStatus
    
    private val _systemInfo = MutableLiveData<SystemInfo>()
    val systemInfo: LiveData<SystemInfo> = _systemInfo
    
    private val _satelliteStatus = MutableLiveData<SatelliteStatus>()
    val satelliteStatus: LiveData<SatelliteStatus> = _satelliteStatus

    fun getSatelliteById(id: Long) = repository.getSatelliteById(id)

    fun loadSatellite(id: Long) {
        viewModelScope.launch {
            repository.getSatelliteById(id).observeForever { satellite ->
                _selectedSatellite.value = satellite
            }
        }
    }

    fun deleteSatellite(satellite: Satellite) {
        viewModelScope.launch {
            try {
                repository.delete(satellite)
                _operationResult.value = "Satellite removed successfully"
            } catch (e: Exception) {
                _operationResult.value = "Error removing satellite: ${e.message}"
            }
        }
    }

    fun updateSatellite(satellite: Satellite) {
        viewModelScope.launch {
            try {
                repository.update(satellite)
                _operationResult.value = "Satellite updated successfully"
            } catch (e: Exception) {
                _operationResult.value = "Error updating satellite: ${e.message}"
            }
        }
    }

    fun insertSatellite(satellite: Satellite) {
        viewModelScope.launch {
            try {
                repository.insert(satellite)
                _operationResult.value = "Satellite added successfully"
            } catch (e: Exception) {
                _operationResult.value = "Error adding satellite: ${e.message}"
            }
        }
    }

    fun updateConnection(isConnected: Boolean) {
        _isConnected.value = isConnected
    }
    
    /**
     * Connect to satellite API
     */
    private fun connectToApi(satellite: Satellite) {
        val baseUrl = "http://${satellite.ipAddress}:5000/"
        apiClient = apiService.getApiClient(baseUrl)
    }
    
    /**
     * Check the satellite API status
     */
    fun checkApiStatus() {
        viewModelScope.launch {
            try {
                val satellite = _selectedSatellite.value ?: return@launch
                connectToApi(satellite)
                
                apiClient?.getStatus()?.enqueue(object : Callback<SatelliteStatus> {
                    override fun onResponse(call: Call<SatelliteStatus>, response: Response<SatelliteStatus>) {
                        if (response.isSuccessful && response.body() != null) {
                            _satelliteStatus.postValue(response.body())
                            _apiStatus.postValue(true)
                            _isConnected.postValue(true)
                            _operationResult.postValue("Connected to satellite API")
                        } else {
                            _apiStatus.postValue(false)
                            _isConnected.postValue(false)
                            _operationResult.postValue("Failed to connect to satellite API: ${response.code()}")
                        }
                    }
                    
                    override fun onFailure(call: Call<SatelliteStatus>, t: Throwable) {
                        _apiStatus.postValue(false)
                        _isConnected.postValue(false)
                        _operationResult.postValue("Failed to connect to satellite API: ${t.message}")
                    }
                })
            } catch (e: Exception) {
                _apiStatus.postValue(false)
                _isConnected.postValue(false)
                _operationResult.postValue("Error connecting to API: ${e.message}")
            }
        }
    }
    
    /**
     * Get system information from the satellite
     */
    fun getSystemInfo() {
        viewModelScope.launch {
            try {
                val satellite = _selectedSatellite.value ?: return@launch
                connectToApi(satellite)
                
                apiClient?.getSystemInfo()?.enqueue(object : Callback<SystemInfo> {
                    override fun onResponse(call: Call<SystemInfo>, response: Response<SystemInfo>) {
                        if (response.isSuccessful && response.body() != null) {
                            _systemInfo.postValue(response.body())
                            _operationResult.postValue("System information retrieved successfully")
                        } else {
                            _operationResult.postValue("Failed to get system information: ${response.code()}")
                        }
                    }
                    
                    override fun onFailure(call: Call<SystemInfo>, t: Throwable) {
                        _operationResult.postValue("Failed to get system information: ${t.message}")
                    }
                })
            } catch (e: Exception) {
                _operationResult.postValue("Error getting system information: ${e.message}")
            }
        }
    }
    
    /**
     * Send a command to the satellite
     */
    fun sendCommand(text: String) {
        viewModelScope.launch {
            try {
                val satellite = _selectedSatellite.value ?: return@launch
                connectToApi(satellite)
                
                val command = Command(text)
                apiClient?.sendCommand(command)?.enqueue(object : Callback<CommandResponse> {
                    override fun onResponse(call: Call<CommandResponse>, response: Response<CommandResponse>) {
                        if (response.isSuccessful) {
                            _operationResult.postValue("Command sent successfully")
                        } else {
                            _operationResult.postValue("Failed to send command: ${response.code()}")
                        }
                    }
                    
                    override fun onFailure(call: Call<CommandResponse>, t: Throwable) {
                        _operationResult.postValue("Failed to send command: ${t.message}")
                    }
                })
            } catch (e: Exception) {
                _operationResult.postValue("Error sending command: ${e.message}")
            }
        }
    }

    fun restartSatellite() {
        viewModelScope.launch {
            try {
                val satellite = _selectedSatellite.value ?: return@launch
                connectToApi(satellite)
                
                apiClient?.restartSatellite()?.enqueue(object : Callback<ApiResponse> {
                    override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                        if (response.isSuccessful) {
                            _operationResult.postValue("Restart command sent successfully")
                        } else {
                            _operationResult.postValue("Error sending restart command: ${response.code()}")
                        }
                    }
                    
                    override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                        _operationResult.postValue("Error sending restart command: ${t.message}")
                    }
                })
            } catch (e: Exception) {
                _operationResult.postValue("Error sending restart command: ${e.message}")
            }
        }
    }

    class Factory(private val repository: SatelliteRepository) : ViewModelProvider.Factory {
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            if (modelClass.isAssignableFrom(SatelliteViewModel::class.java)) {
                @Suppress("UNCHECKED_CAST")
                return SatelliteViewModel(repository) as T
            }
            throw IllegalArgumentException("Unknown ViewModel class")
        }
    }
}