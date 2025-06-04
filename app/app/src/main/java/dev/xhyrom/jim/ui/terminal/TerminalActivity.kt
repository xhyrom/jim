package dev.xhyrom.jim.ui.terminal

import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.preference.PreferenceManager
import dev.xhyrom.jim.databinding.ActivityTerminalBinding
import java.lang.Exception

class TerminalActivity : AppCompatActivity() {

    private lateinit var binding: ActivityTerminalBinding
    private lateinit var viewModel: TerminalViewModel

    private val commandHistory = mutableListOf<String>()
    private var historyPosition = -1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTerminalBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Get satellite information from intent
        val satelliteId = intent.getLongExtra("satellite_id", -1)
        val satelliteName = intent.getStringExtra("satellite_name") ?: "Unknown"
        val satelliteIp = intent.getStringExtra("satellite_ip") ?: ""
        val username = intent.getStringExtra("satellite_username") ?: "pi"
        val password = intent.getStringExtra("satellite_password")
        val port = intent.getIntExtra("satellite_port", 22)

        // Set up toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.title = "SSH: $satelliteName"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        
        // Check if keep screen on is enabled
        val preferences = PreferenceManager.getDefaultSharedPreferences(this)
        if (preferences.getBoolean("keep_screen_on", false)) {
            window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        }

        // Initialize ViewModel
        viewModel = ViewModelProvider(this)[TerminalViewModel::class.java]

        setupObservers()
        setupClickListeners()

        binding.terminalOutput.text = "# Connecting to $username@$satelliteIp:$port...\n\n"

        try {
            // Connect to SSH server
            viewModel.connectToSSH(satelliteIp, username, password ?: "", port)
        } catch (e: Exception) {
            Toast.makeText(this, "Failed to connect: ${e.message}", Toast.LENGTH_LONG).show()
            binding.terminalOutput.append("# Connection error: ${e.message}\n")
        }
    }

    private fun setupObservers() {
        viewModel.commandOutput.observe(this) { output ->
            appendToTerminalOutput(output)
        }

        viewModel.connectionStatus.observe(this) { connected ->
            if (connected) {
                appendToTerminalOutput("# Connection established. Type commands below.")
            } else {
                appendToTerminalOutput("# Connection failed or closed.")
                Toast.makeText(this, "SSH connection failed or closed", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            binding.buttonExecute.isEnabled = !isLoading && viewModel.connectionStatus.value == true
            binding.editCommand.isEnabled = !isLoading && viewModel.connectionStatus.value == true
        }

        viewModel.errorMessage.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_LONG).show()
                appendToTerminalOutput("Error: $it")
            }
        }
    }

    private fun setupClickListeners() {
        binding.buttonExecute.setOnClickListener {
            val command = binding.editCommand.text.toString()
            if (command.isNotEmpty()) {
                executeCommand(command)
            }
        }

        binding.buttonUp.setOnClickListener {
            navigateHistory(-1)
        }

        binding.buttonDown.setOnClickListener {
            navigateHistory(1)
        }

        binding.buttonClear.setOnClickListener {
            binding.terminalOutput.text = "# Terminal cleared\n\n"
        }

        // Handle Enter key press
        binding.editCommand.setOnEditorActionListener { _, _, _ ->
            val command = binding.editCommand.text.toString()
            if (command.isNotEmpty()) {
                executeCommand(command)
                return@setOnEditorActionListener true
            }
            false
        }
    }

    private fun executeCommand(command: String) {
        appendToTerminalOutput("> $command")
        commandHistory.add(command)
        historyPosition = commandHistory.size

        binding.editCommand.setText("")
        try {
            viewModel.executeCommand(command)
        } catch (e: Exception) {
            Toast.makeText(this, "Command execution failed: ${e.message}", Toast.LENGTH_SHORT).show()
            appendToTerminalOutput("# Error: ${e.message}")
        }
    }

    private fun appendToTerminalOutput(text: String) {
        binding.terminalOutput.append("$text\n")
        binding.terminalScrollView.post {
            binding.terminalScrollView.fullScroll(View.FOCUS_DOWN)
        }
    }

    private fun navigateHistory(direction: Int) {
        if (commandHistory.isEmpty()) return

        historyPosition = (historyPosition + direction).coerceIn(0, commandHistory.size - 1)
        binding.editCommand.setText(commandHistory[historyPosition])
        binding.editCommand.setSelection(binding.editCommand.text.length)
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }

    override fun onDestroy() {
        super.onDestroy()
        viewModel.disconnectFromSSH()
    }
}