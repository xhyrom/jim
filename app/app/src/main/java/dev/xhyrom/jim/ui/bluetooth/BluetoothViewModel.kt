package dev.xhyrom.jim.ui.bluetooth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.data.ApiService
import dev.xhyrom.jim.data.BluetoothDevice
import kotlinx.coroutines.launch

class BluetoothViewModel : ViewModel() {

    private val apiService = ApiService.create()

    private val _devices = MutableLiveData<List<BluetoothDevice>>()
    val devices: LiveData<List<BluetoothDevice>> = _devices

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage

    private val _pairingStatus = MutableLiveData<Boolean>()
    val pairingStatus: LiveData<Boolean> = _pairingStatus

    fun scanForDevices() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                _devices.value = apiService.scanBluetoothDevices()
                _errorMessage.value = null
            } catch (e: Exception) {
                _errorMessage.value = "Failed to scan for devices: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun pairWithDevice(device: BluetoothDevice) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = apiService.pairWithDevice(device.id)
                _pairingStatus.value = result["success"] == true
                _errorMessage.value = null
            } catch (e: Exception) {
                _errorMessage.value = "Failed to pair with device: ${e.localizedMessage}"
                _pairingStatus.value = false
            } finally {
                _isLoading.value = false
            }
        }
    }
}