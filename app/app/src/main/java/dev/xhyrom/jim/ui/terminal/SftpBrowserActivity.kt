package dev.xhyrom.jim.ui.terminal

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import dev.xhyrom.jim.R
import dev.xhyrom.jim.databinding.ActivitySftpBrowserBinding
import dev.xhyrom.jim.databinding.DialogCreateDirectoryBinding
import dev.xhyrom.jim.databinding.DialogFileNameBinding
import dev.xhyrom.jim.databinding.DialogSshLoginBinding
import dev.xhyrom.jim.ssh.FileInfo
import java.io.File

class SftpBrowserActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySftpBrowserBinding
    private lateinit var viewModel: SftpBrowserViewModel
    private lateinit var adapter: FileListAdapter

    private var currentPath = "/home/pi"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySftpBrowserBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Set up toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        viewModel = ViewModelProvider(this).get(SftpBrowserViewModel::class.java)

        setupRecyclerView()
        setupObservers()
        setupClickListeners()

        // Get satellite info from intent
        val satelliteName = intent.getStringExtra("satellite_name")
        supportActionBar?.title = if (satelliteName != null) "SFTP - $satelliteName" else "SFTP Browser"

        // Show login dialog
        showSshLoginDialog()
    }

    private fun setupRecyclerView() {
        adapter = FileListAdapter(
            onItemClick = { fileInfo ->
                if (fileInfo.isDirectory) {
                    navigateTo(fileInfo.path)
                } else {
                    showFileOptions(fileInfo)
                }
            }
        )
        binding.recyclerFiles.layoutManager = LinearLayoutManager(this)
        binding.recyclerFiles.adapter = adapter
    }

    private fun setupObservers() {
        viewModel.fileList.observe(this) { files ->
            adapter.submitList(files)
            binding.emptyView.visibility = if (files.isEmpty()) View.VISIBLE else View.GONE
        }

        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            binding.swipeRefresh.isRefreshing = false
        }

        viewModel.errorMessage.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_LONG).show()
            }
        }

        viewModel.currentPath.observe(this) { path ->
            currentPath = path
            binding.textCurrentPath.text = path

            // Update back button state
            binding.buttonBack.isEnabled = path != "/"
        }

        viewModel.connectionStatus.observe(this) { connected ->
            if (connected) {
                binding.fabAddFolder.isEnabled = true
                loadFiles()
            } else {
                binding.fabAddFolder.isEnabled = false
                // If disconnected unexpectedly, show login dialog
                if (adapter.itemCount > 0) {
                    Toast.makeText(this, "Connection lost. Please reconnect.", Toast.LENGTH_SHORT).show()
                    showSshLoginDialog()
                }
            }
        }
    }

    private fun setupClickListeners() {
        binding.buttonBack.setOnClickListener {
            navigateUp()
        }

        binding.swipeRefresh.setOnRefreshListener {
            loadFiles()
        }

        binding.fabAddFolder.setOnClickListener {
            showCreateDirectoryDialog()
        }
    }

    private fun showSshLoginDialog() {
        val dialogBinding = DialogSshLoginBinding.inflate(layoutInflater)
        
        // Pre-fill with intent data if available
        val hostname = intent.getStringExtra("satellite_ip")
        val username = intent.getStringExtra("satellite_username") ?: "pi"
        val password = intent.getStringExtra("satellite_password") ?: ""
        
        dialogBinding.editHostname.setText(hostname)
        dialogBinding.editUsername.setText(username)
        dialogBinding.editPassword.setText(password)

        val dialog = MaterialAlertDialogBuilder(this)
            .setTitle("SFTP Login")
            .setView(dialogBinding.root)
            .setCancelable(false)
            .setPositiveButton("Connect", null)
            .create()

        dialog.show()

        dialog.getButton(android.content.DialogInterface.BUTTON_POSITIVE).setOnClickListener {
            val inputHostname = dialogBinding.editHostname.text.toString()
            val inputUsername = dialogBinding.editUsername.text.toString()
            val inputPassword = dialogBinding.editPassword.text.toString()

            if (inputHostname.isEmpty()) {
                dialogBinding.editHostname.error = "Hostname required"
                return@setOnClickListener
            }

            if (inputUsername.isEmpty()) {
                dialogBinding.editUsername.error = "Username required"
                return@setOnClickListener
            }

            if (inputPassword.isEmpty()) {
                dialogBinding.editPassword.error = "Password required"
                return@setOnClickListener
            }

            try {
                viewModel.connect(inputHostname, inputUsername, inputPassword)
                dialog.dismiss()
            } catch (e: Exception) {
                Toast.makeText(this, "Connection error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun showCreateDirectoryDialog() {
        val dialogBinding = DialogCreateDirectoryBinding.inflate(layoutInflater)

        MaterialAlertDialogBuilder(this)
            .setTitle("Create Directory")
            .setView(dialogBinding.root)
            .setPositiveButton("Create") { _, _ ->
                val dirName = dialogBinding.editDirName.text.toString()
                if (dirName.isNotEmpty()) {
                    viewModel.createDirectory("$currentPath/$dirName")
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showFileOptions(fileInfo: FileInfo) {
        val options = arrayOf("Download", "Delete")

        MaterialAlertDialogBuilder(this)
            .setTitle(fileInfo.name)
            .setItems(options) { _, which ->
                when (which) {
                    0 -> downloadFile(fileInfo)
                    1 -> confirmDeleteFile(fileInfo)
                }
            }
            .show()
    }

    private fun downloadFile(fileInfo: FileInfo) {
        // Get download directory
        val downloadDir = getExternalFilesDir(null)
        if (downloadDir == null) {
            Toast.makeText(this, "Download directory not available", Toast.LENGTH_SHORT).show()
            return
        }

        val localPath = File(downloadDir, fileInfo.name).absolutePath
        viewModel.downloadFile(fileInfo.path, localPath)
        Toast.makeText(this, "Downloading ${fileInfo.name}...", Toast.LENGTH_SHORT).show()
    }

    private fun confirmDeleteFile(fileInfo: FileInfo) {
        MaterialAlertDialogBuilder(this)
            .setTitle("Delete ${fileInfo.name}")
            .setMessage("Are you sure you want to delete this ${if (fileInfo.isDirectory) "directory" else "file"}?")
            .setPositiveButton("Delete") { _, _ ->
                if (fileInfo.isDirectory) {
                    viewModel.deleteDirectory(fileInfo.path)
                } else {
                    viewModel.deleteFile(fileInfo.path)
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun navigateTo(path: String) {
        viewModel.navigateTo(path)
    }

    private fun navigateUp() {
        if (currentPath == "/") return

        val parentPath = currentPath.substringBeforeLast('/', "/")
        navigateTo(parentPath)
    }

    private fun loadFiles() {
        viewModel.loadFiles()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_sftp, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                onBackPressed()
                true
            }
            R.id.action_upload -> {
                startFileChooser()
                true
            }
            R.id.action_refresh -> {
                loadFiles()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun startFileChooser() {
        val intent = Intent(Intent.ACTION_GET_CONTENT)
        intent.type = "*/*"
        intent.addCategory(Intent.CATEGORY_OPENABLE)

        try {
            startActivityForResult(
                Intent.createChooser(intent, "Select a file to upload"),
                REQUEST_FILE_CHOOSER
            )
        } catch (e: Exception) {
            Toast.makeText(this, "File browser not available", Toast.LENGTH_SHORT).show()
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == REQUEST_FILE_CHOOSER && resultCode == RESULT_OK) {
            data?.data?.let { uri ->
                val contentResolver = applicationContext.contentResolver
                val cursor = contentResolver.query(uri, null, null, null, null)

                cursor?.use {
                    if (it.moveToFirst()) {
                        val nameIndex = it.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                        val name = if (nameIndex >= 0) it.getString(nameIndex) else "uploaded_file"

                        showUploadNameDialog(uri, name)
                    }
                }
            }
        }
    }

    private fun showUploadNameDialog(uri: android.net.Uri, defaultName: String) {
        val dialogBinding = DialogFileNameBinding.inflate(layoutInflater)
        dialogBinding.editFileName.setText(defaultName)

        MaterialAlertDialogBuilder(this)
            .setTitle("Upload File")
            .setView(dialogBinding.root)
            .setPositiveButton("Upload") { _, _ ->
                val fileName = dialogBinding.editFileName.text.toString()
                if (fileName.isNotEmpty()) {
                    uploadFile(uri, fileName)
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun uploadFile(uri: android.net.Uri, fileName: String) {
        if (!viewModel.connectionStatus.value!!) {
            Toast.makeText(this, "Not connected to SFTP server", Toast.LENGTH_SHORT).show()
            return
        }
        
        // First copy the file from Uri to a temp file we can access
        val tempDir = cacheDir
        val tempFile = File(tempDir, "temp_upload")

        try {
            contentResolver.openInputStream(uri)?.use { input ->
                tempFile.outputStream().use { output ->
                    input.copyTo(output)
                }
            }

            val remotePath = "$currentPath/$fileName"
            viewModel.uploadFile(tempFile.absolutePath, remotePath)
            Toast.makeText(this, "Uploading $fileName...", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Upload failed: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    companion object {
        private const val REQUEST_FILE_CHOOSER = 1001
    }
}