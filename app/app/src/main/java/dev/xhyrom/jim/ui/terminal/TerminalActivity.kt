package dev.xhyrom.jim.ui.terminal

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import dev.xhyrom.jim.databinding.ActivityTerminalBinding

class TerminalActivity : AppCompatActivity() {

    private lateinit var binding: ActivityTerminalBinding
    private lateinit var viewModel: TerminalViewModel

    private val commandHistory = mutableListOf<String>()
    private var historyPosition = -1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTerminalBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this).get(TerminalViewModel::class.java)

        setupObservers()
        setupClickListeners()

        binding.terminalOutput.text = "# Jim Terminal\n# Type 'help' for available commands\n\n"
    }

    private fun setupObservers() {
        viewModel.commandOutput.observe(this) { output ->
            appendToTerminalOutput(output)
        }

        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            binding.buttonExecute.isEnabled = !isLoading
            binding.editCommand.isEnabled = !isLoading
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
    }

    private fun executeCommand(command: String) {
        appendToTerminalOutput("> $command")
        commandHistory.add(command)
        historyPosition = commandHistory.size

        binding.editCommand.setText("")
        viewModel.executeCommand(command)
    }

    private fun appendToTerminalOutput(text: String) {
        binding.terminalOutput.append("$text\n\n")
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
}