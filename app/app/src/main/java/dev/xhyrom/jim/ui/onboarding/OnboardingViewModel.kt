package dev.xhyrom.jim.ui.onboarding

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.data.database.AppDatabase
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.data.repository.SatelliteRepository
import kotlinx.coroutines.launch

class OnboardingViewModel(application: Application) : AndroidViewModel(application) {
    private val repository: SatelliteRepository

    init {
        val satelliteDao = AppDatabase.getDatabase(application).satelliteDao()
        repository = SatelliteRepository(satelliteDao)
    }

    fun addSatellite(
        name: String,
        ipAddress: String,
        sshUsername: String = "pi",
        sshPassword: String? = null,
        sshPort: Int = 22
    ): LiveData<Boolean> {
        val result = MutableLiveData<Boolean>()

        viewModelScope.launch {
            try {
                // Create a new satellite with the provided details
                val satellite = Satellite(
                    name = name,
                    ipAddress = ipAddress,
                    sshUsername = sshUsername,
                    sshPassword = sshPassword,
                    sshPort = sshPort
                )

                // Insert the satellite into the database
                val satelliteId = repository.insert(satellite)

                // If the satellite was inserted successfully (satelliteId > 0), return true
                result.postValue(satelliteId > 0)
            } catch (e: Exception) {
                result.postValue(false)
            }
        }

        return result
    }

    fun checkForExistingSatellites(): LiveData<Boolean> {
        val result = MutableLiveData<Boolean>()

        repository.allSatellites.observeForever { satellites ->
            result.postValue(satellites.isNotEmpty())
        }

        return result
    }
}