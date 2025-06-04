package dev.xhyrom.jim.ui.logs

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class LogsViewModel : ViewModel() {

    private val _logs = MutableLiveData<String>()
    val logs: LiveData<String> = _logs

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    init {
        _logs.value = "No logs available. Tap 'Refresh Logs' to load logs."
    }

    fun refreshLogs() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _errorMessage.value = null
                
                // Simulate network delay
                delay(1000)
                
                // In a real implementation, this would fetch logs from satellites
                // For now, just generate some sample logs
                val sampleLogs = generateSampleLogs()
                _logs.value = sampleLogs
            } catch (e: Exception) {
                _errorMessage.value = "Failed to load logs: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    private fun generateSampleLogs(): String {
        val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        val now = System.currentTimeMillis()
        
        return buildString {
            append("[${dateFormat.format(Date(now))}] INFO: Application started\n")
            append("[${dateFormat.format(Date(now - 30000))}] INFO: Satellite connection established\n")
            append("[${dateFormat.format(Date(now - 60000))}] INFO: Satellite 'Living Room' connected\n")
            append("[${dateFormat.format(Date(now - 90000))}] INFO: Voice recognition service started\n")
            append("[${dateFormat.format(Date(now - 120000))}] INFO: User query processed: 'What's the weather?'\n")
            append("[${dateFormat.format(Date(now - 150000))}] INFO: API request sent to weather service\n")
            append("[${dateFormat.format(Date(now - 180000))}] INFO: Response received from weather service\n")
            append("[${dateFormat.format(Date(now - 210000))}] INFO: TTS engine initialized\n")
            append("[${dateFormat.format(Date(now - 240000))}] INFO: System configuration loaded\n")
            append("[${dateFormat.format(Date(now - 270000))}] WARN: Network latency detected\n")
            append("[${dateFormat.format(Date(now - 300000))}] INFO: Network connection recovered\n")
            append("[${dateFormat.format(Date(now - 330000))}] INFO: System ready\n")
        }
    }
    
    fun clearErrorMessage() {
        _errorMessage.value = null
    }
}