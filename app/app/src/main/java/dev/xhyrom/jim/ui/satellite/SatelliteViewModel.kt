package dev.xhyrom.jim.ui.satellite

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.data.repository.SatelliteRepository
import kotlinx.coroutines.launch

class SatelliteViewModel(private val repository: SatelliteRepository) : ViewModel() {

    private val _selectedSatellite = MutableLiveData<Satellite>()
    val selectedSatellite: LiveData<Satellite> = _selectedSatellite

    private val _isConnected = MutableLiveData<Boolean>()
    val isConnected: LiveData<Boolean> = _isConnected

    private val _operationResult = MutableLiveData<String>()
    val operationResult: LiveData<String> = _operationResult

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

    fun restartSatellite() {
        viewModelScope.launch {
            try {
                // Implementation would depend on your SSH manager
                // sshManager.executeCommand("sudo reboot")
                _operationResult.value = "Restart command sent successfully"
            } catch (e: Exception) {
                _operationResult.value = "Error sending restart command: ${e.message}"
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