package dev.xhyrom.jim.ui.home

import androidx.lifecycle.LiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.data.repository.SatelliteRepository
import kotlinx.coroutines.launch

class HomeViewModel(private val repository: SatelliteRepository) : ViewModel() {
    val allSatellites: LiveData<List<Satellite>> = repository.allSatellites

    fun addSatellite(
        name: String, 
        ipAddress: String, 
        sshUsername: String = "pi", 
        sshPassword: String? = null, 
        sshPort: Int = 22,
        description: String? = null
    ) = viewModelScope.launch {
        repository.insert(
            Satellite(
                name = name,
                ipAddress = ipAddress,
                sshUsername = sshUsername,
                sshPassword = sshPassword,
                sshPort = sshPort,
                description = description
            )
        )
    }

    fun deleteSatellite(satellite: Satellite) = viewModelScope.launch {
        repository.delete(satellite)
    }

    fun getSatellitesByStatus(status: String): LiveData<List<Satellite>> {
        return repository.getSatellitesByStatus(status)
    }

    class Factory(private val repository: SatelliteRepository) : ViewModelProvider.Factory {
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            if (modelClass.isAssignableFrom(HomeViewModel::class.java)) {
                @Suppress("UNCHECKED_CAST")
                return HomeViewModel(repository) as T
            }
            throw IllegalArgumentException("Unknown ViewModel class")
        }
    }
}