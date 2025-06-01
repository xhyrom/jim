package dev.xhyrom.jim.ui.settings

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.data.ApiService
import dev.xhyrom.jim.data.ConfigModel
import kotlinx.coroutines.launch

class SettingsViewModel : ViewModel() {

    private val apiService = ApiService.create()

    private val _config = MutableLiveData<ConfigModel>()
    val config: LiveData<ConfigModel> = _config

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage

    fun loadConfig() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                _config.value = apiService.getConfig()
                _errorMessage.value = null
            } catch (e: Exception) {
                _errorMessage.value = "Failed to load config: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun updateConfig(config: ConfigModel) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                _config.value = apiService.updateConfig(config)
                _errorMessage.value = null
            } catch (e: Exception) {
                _errorMessage.value = "Failed to update config: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun factoryReset() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                apiService.factoryReset()
                _errorMessage.value = null
            } catch (e: Exception) {
                _errorMessage.value = "Failed to factory reset: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }
}