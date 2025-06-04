package dev.xhyrom.jim.ui.terminal

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.ssh.SSHManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TerminalViewModel : ViewModel() {

    private val sshManager = SSHManager()

    private val _connectionStatus = MutableLiveData<Boolean>()
    val connectionStatus: LiveData<Boolean> = _connectionStatus

    private val _commandOutput = MutableLiveData<String>()
    val commandOutput: LiveData<String> = _commandOutput

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage

    fun connectToSSH(hostname: String, username: String, password: String, port: Int = 22) {
        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            try {
                val result = sshManager.connect(hostname, username, password, port)
                result.fold(
                    onSuccess = {
                        _connectionStatus.value = true
                        _commandOutput.value = "Connected successfully to $username@$hostname:$port"
                    },
                    onFailure = { e ->
                        _connectionStatus.value = false
                        _errorMessage.value = "Failed to connect: ${e.message}"
                        _commandOutput.value = "Connection failed: ${e.message}"
                    }
                )
            } catch (e: Exception) {
                _connectionStatus.value = false
                _errorMessage.value = "Connection error: ${e.message}"
                _commandOutput.value = "Connection error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun executeCommand(command: String) {
        viewModelScope.launch {
            if (_connectionStatus.value != true) {
                _errorMessage.value = "Not connected to SSH server"
                _commandOutput.value = "Error: Not connected to SSH server"
                return@launch
            }
            
            _isLoading.value = true
            _errorMessage.value = null
            try {
                val result = sshManager.executeCommand(command)
                result.fold(
                    onSuccess = { output ->
                        _commandOutput.value = output.ifEmpty { "(Command executed with no output)" }
                    },
                    onFailure = { e ->
                        _errorMessage.value = "Command failed: ${e.message}"
                        _commandOutput.value = "Error: ${e.message}"
                        // Check if connection was lost
                        if (e.message?.contains("Not connected", ignoreCase = true) == true) {
                            _connectionStatus.value = false
                        }
                    }
                )
            } catch (e: Exception) {
                _errorMessage.value = "Error executing command: ${e.message}"
                _commandOutput.value = "Error executing command: ${e.message}"
                // Check if connection was lost
                if (e.message?.contains("Not connected", ignoreCase = true) == true) {
                    _connectionStatus.value = false
                }
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun disconnectFromSSH() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                withContext(Dispatchers.IO) {
                    sshManager.disconnect()
                }
                _connectionStatus.value = false
                _commandOutput.value = "Disconnected from SSH server"
            } catch (e: Exception) {
                _errorMessage.value = "Error during disconnection: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun clearErrorMessage() {
        _errorMessage.value = null
    }
    
    fun isConnected(): Boolean {
        return _connectionStatus.value == true
    }

    override fun onCleared() {
        super.onCleared()
        disconnectFromSSH()
    }
}