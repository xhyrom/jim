package dev.xhyrom.jim.ui.satellite

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import dev.xhyrom.jim.api.SystemInfo
import dev.xhyrom.jim.data.database.AppDatabase
import dev.xhyrom.jim.data.repository.SatelliteRepository
import dev.xhyrom.jim.databinding.FragmentSatelliteDetailBinding
import dev.xhyrom.jim.ui.terminal.SftpBrowserActivity
import dev.xhyrom.jim.ui.terminal.TerminalActivity
import java.text.DecimalFormat

class SatelliteDetailFragment : Fragment() {
    private var _binding: FragmentSatelliteDetailBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: SatelliteViewModel
    private val args: SatelliteDetailFragmentArgs by navArgs()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSatelliteDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val repository = SatelliteRepository(
            AppDatabase.getDatabase(requireContext()).satelliteDao()
        )
        viewModel = ViewModelProvider(
            this,
            SatelliteViewModel.Factory(repository)
        )[SatelliteViewModel::class.java]

        viewModel.loadSatellite(args.satelliteId)

        setupObservers()
        setupClickListeners()
        
        // Check API status after loading satellite
        viewModel.selectedSatellite.observe(viewLifecycleOwner) { satellite ->
            if (satellite != null) {
                viewModel.checkApiStatus()
            }
        }
    }

    private fun setupObservers() {
        viewModel.selectedSatellite.observe(viewLifecycleOwner) { satellite ->
            if (satellite != null) {
                binding.textSatelliteName.text = satellite.name
                binding.textSatelliteIp.text = satellite.ipAddress
            }
        }

        viewModel.isConnected.observe(viewLifecycleOwner) { isConnected ->
            updateConnectionStatus(isConnected)
        }

        viewModel.apiStatus.observe(viewLifecycleOwner) { apiConnected ->
            if (apiConnected) {
                binding.apiStatusBadge.visibility = View.VISIBLE
                // Get system info when API is connected
                viewModel.getSystemInfo()
            } else {
                binding.apiStatusBadge.visibility = View.GONE
            }
        }
        
        viewModel.satelliteStatus.observe(viewLifecycleOwner) { status ->
            binding.textStatus.text = "Status: ${status.state}"
            updateConnectionStatus(true)
        }
        
        viewModel.systemInfo.observe(viewLifecycleOwner) { systemInfo ->
            updateSystemInfo(systemInfo)
        }

        viewModel.operationResult.observe(viewLifecycleOwner) { result ->
            Toast.makeText(requireContext(), result, Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun updateConnectionStatus(isConnected: Boolean) {
        binding.textStatus.text = if (isConnected) "Status: Online" else "Status: Offline"
        binding.textStatus.setTextColor(
            resources.getColor(
                if (isConnected) android.R.color.holo_green_dark else android.R.color.holo_red_dark,
                null
            )
        )
    }
    
    private fun updateSystemInfo(systemInfo: SystemInfo) {
        val df = DecimalFormat("#.##")
        
        val memoryUsed = systemInfo.memory.total - systemInfo.memory.available
        val memoryUsedMB = memoryUsed / (1024 * 1024)
        val memoryTotalMB = systemInfo.memory.total / (1024 * 1024)
        val memoryPercentage = df.format(systemInfo.memory.percent)
        
        val diskUsedGB = (systemInfo.disk.total - systemInfo.disk.free) / (1024 * 1024 * 1024)
        val diskTotalGB = systemInfo.disk.total / (1024 * 1024 * 1024)
        val diskPercentage = df.format(systemInfo.disk.percent)
        
        val systemInfoText = """
            Platform: ${systemInfo.platform}
            Memory: ${memoryUsedMB}MB / ${memoryTotalMB}MB (${memoryPercentage}%)
            Disk: ${diskUsedGB}GB / ${diskTotalGB}GB (${diskPercentage}%)
        """.trimIndent()
        
        binding.textSystemInfo.text = systemInfoText
        binding.cardSystemInfo.visibility = View.VISIBLE
    }

    private fun setupClickListeners() {
        binding.buttonSsh.setOnClickListener {
            viewModel.selectedSatellite.value?.let { satellite ->
                val intent = Intent(requireContext(), TerminalActivity::class.java).apply {
                    putExtra("satellite_id", satellite.id)
                    putExtra("satellite_name", satellite.name)
                    putExtra("satellite_ip", satellite.ipAddress)
                    putExtra("satellite_username", satellite.sshUsername)
                    putExtra("satellite_password", satellite.sshPassword)
                    putExtra("satellite_port", satellite.sshPort)
                }
                startActivity(intent)
            }
        }

        binding.buttonSftp.setOnClickListener {
            viewModel.selectedSatellite.value?.let { satellite ->
                val intent = Intent(requireContext(), SftpBrowserActivity::class.java).apply {
                    putExtra("satellite_id", satellite.id)
                    putExtra("satellite_name", satellite.name)
                    putExtra("satellite_ip", satellite.ipAddress)
                    putExtra("satellite_username", satellite.sshUsername)
                    putExtra("satellite_password", satellite.sshPassword)
                    putExtra("satellite_port", satellite.sshPort)
                }
                startActivity(intent)
            }
        }

        binding.buttonRestart.setOnClickListener {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle("Restart Satellite")
                .setMessage("Are you sure you want to restart this satellite device?")
                .setPositiveButton("Restart") { _, _ ->
                    viewModel.restartSatellite()
                }
                .setNegativeButton("Cancel", null)
                .show()
        }

        binding.buttonSendCommand.setOnClickListener {
            showSendCommandDialog()
        }

        binding.buttonRefreshStatus.setOnClickListener {
            viewModel.checkApiStatus()
            viewModel.getSystemInfo()
        }

        binding.buttonEditSatellite.setOnClickListener {
            viewModel.selectedSatellite.value?.let { satellite ->
                val action = SatelliteDetailFragmentDirections.actionSatelliteDetailFragmentToEditSatelliteFragment(
                    satelliteId = args.satelliteId
                )
                findNavController().navigate(action)
            }
        }

        binding.buttonRemoveSatellite.setOnClickListener {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle("Remove Satellite")
                .setMessage("Are you sure you want to remove this satellite from your system? This action cannot be undone.")
                .setPositiveButton("Remove") { _, _ ->
                    viewModel.selectedSatellite.value?.let { satellite ->
                        viewModel.deleteSatellite(satellite)
                        findNavController().navigateUp()
                    }
                }
                .setNegativeButton("Cancel", null)
                .show()
        }
    }
    
    private fun showSendCommandDialog() {
        val editText = android.widget.EditText(requireContext()).apply {
            hint = "Enter command text"
            setSingleLine(false)
            minLines = 2
        }
        
        val container = android.widget.FrameLayout(requireContext()).apply {
            val padding = resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 2
            setPadding(padding, padding / 2, padding, padding / 2)
            addView(editText)
        }
        
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Send Command")
            .setView(container)
            .setPositiveButton("Send") { _, _ ->
                val commandText = editText.text.toString()
                if (commandText.isNotEmpty()) {
                    viewModel.sendCommand(commandText)
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}