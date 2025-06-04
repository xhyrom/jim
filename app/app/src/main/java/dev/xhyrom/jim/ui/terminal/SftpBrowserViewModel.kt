package dev.xhyrom.jim.ui.terminal

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.xhyrom.jim.ssh.FileInfo
import dev.xhyrom.jim.ssh.SFTPManager
import kotlinx.coroutines.launch

class SftpBrowserViewModel : ViewModel() {

    private val sftpManager = SFTPManager()

    private val _fileList = MutableLiveData<List<FileInfo>>()
    val fileList: LiveData<List<FileInfo>> = _fileList

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage

    private val _currentPath = MutableLiveData<String>("/home/pi")
    val currentPath: LiveData<String> = _currentPath

    private val _connectionStatus = MutableLiveData<Boolean>(false)
    val connectionStatus: LiveData<Boolean> = _connectionStatus

    fun connect(hostname: String, username: String, password: String) {
        viewModelScope.launch {
            _isLoading.value = true
            sftpManager.connect(hostname, username, password).fold(
                onSuccess = {
                    _connectionStatus.value = true
                    _currentPath.value = "/home/pi"  // Default to home directory
                    loadFiles()
                },
                onFailure = { e ->
                    _errorMessage.value = "SFTP connection failed: ${e.localizedMessage}"
                    _connectionStatus.value = false
                }
            )
            _isLoading.value = false
        }
    }

    fun loadFiles() {
        val path = _currentPath.value ?: "/home/pi"

        viewModelScope.launch {
            _isLoading.value = true
            sftpManager.listFiles(path).fold(
                onSuccess = { files ->
                    _fileList.value = files
                },
                onFailure = { e ->
                    _errorMessage.value = "Failed to list files: ${e.localizedMessage}"
                    _connectionStatus.value = false
                }
            )
            _isLoading.value = false
        }
    }

    fun navigateTo(path: String) {
        _currentPath.value = path
        loadFiles()
    }

    fun createDirectory(path: String) {
        viewModelScope.launch {
            _isLoading.value = true
            sftpManager.mkdir(path).fold(
                onSuccess = {
                    loadFiles()  // Refresh after creating dir
                },
                onFailure = { e ->
                    _errorMessage.value = "Failed to create directory: ${e.localizedMessage}"
                }
            )
            _isLoading.value = false
        }
    }

    fun downloadFile(remotePath: String, localPath: String) {
        viewModelScope.launch {
            sftpManager.downloadFile(remotePath, localPath).fold(
                onSuccess = {
                    _errorMessage.value = "File downloaded successfully"
                },
                onFailure = { e ->
                    _errorMessage.value = "Download failed: ${e.localizedMessage}"
                }
            )
        }
    }

    fun uploadFile(localPath: String, remotePath: String) {
        viewModelScope.launch {
            sftpManager.uploadFile(localPath, remotePath).fold(
                onSuccess = {
                    loadFiles()  // Refresh file list
                },
                onFailure = { e ->
                    _errorMessage.value = "Upload failed: ${e.localizedMessage}"
                }
            )
        }
    }

    fun deleteFile(path: String) {
        viewModelScope.launch {
            _isLoading.value = true
            sftpManager.removeFile(path).fold(
                onSuccess = {
                    loadFiles()  // Refresh after deletion
                },
                onFailure = { e ->
                    _errorMessage.value = "Failed to delete file: ${e.localizedMessage}"
                }
            )
            _isLoading.value = false
        }
    }

    fun deleteDirectory(path: String) {
        viewModelScope.launch {
            _isLoading.value = true
            sftpManager.removeDirectory(path).fold(
                onSuccess = {
                    loadFiles()  // Refresh after deletion
                },
                onFailure = { e ->
                    _errorMessage.value = "Failed to delete directory: ${e.localizedMessage}"
                }
            )
            _isLoading.value = false
        }
    }

    override fun onCleared() {
        super.onCleared()
        sftpManager.disconnect()
    }
}