package dev.xhyrom.jim.ui.terminal

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.data.ApiService
import kotlinx.coroutines.launch

class TerminalViewModel : ViewModel() {

    private val apiService = ApiService.create()

    private val _commandOutput = MutableLiveData<String>()
    val commandOutput: LiveData<String> = _commandOutput

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage

    fun executeCommand(command: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = apiService.executeCommand(mapOf("command" to command))
                _commandOutput.value = result["output"] ?: "No output"
                _errorMessage.value = null
            } catch (e: Exception) {
                _errorMessage.value = "Failed to execute command: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }
}