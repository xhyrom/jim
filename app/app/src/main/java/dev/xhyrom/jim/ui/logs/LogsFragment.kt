package dev.xhyrom.jim.ui.logs

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import dev.xhyrom.jim.databinding.FragmentLogsBinding

class LogsFragment : Fragment() {
    private var _binding: FragmentLogsBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: LogsViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLogsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel = ViewModelProvider(this).get(LogsViewModel::class.java)

        setupObservers()
        setupClickListeners()
        loadLogs()
    }

    private fun setupObservers() {
        viewModel.logs.observe(viewLifecycleOwner) { logs ->
            binding.logContent.text = logs
        }

        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.buttonRefreshLogs.isEnabled = !isLoading
            if (isLoading) {
                binding.buttonRefreshLogs.text = "Loading..."
            } else {
                binding.buttonRefreshLogs.text = "Refresh Logs"
            }
        }

        viewModel.errorMessage.observe(viewLifecycleOwner) { errorMsg ->
            errorMsg?.let {
                Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupClickListeners() {
        binding.buttonRefreshLogs.setOnClickListener {
            loadLogs()
        }
    }

    private fun loadLogs() {
        // For the initial implementation, just show some example logs
        // In a real app, this would fetch logs from the server/device
        viewModel.refreshLogs()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}