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
import dev.xhyrom.jim.data.database.AppDatabase
import dev.xhyrom.jim.data.repository.SatelliteRepository
import dev.xhyrom.jim.databinding.FragmentSatelliteDetailBinding
import dev.xhyrom.jim.ui.terminal.SftpBrowserActivity
import dev.xhyrom.jim.ui.terminal.TerminalActivity

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
    }

    private fun setupObservers() {
        viewModel.selectedSatellite.observe(viewLifecycleOwner) { satellite ->
            if (satellite != null) {
                binding.textSatelliteName.text = satellite.name
                binding.textSatelliteIp.text = satellite.ipAddress
                binding.textStatus.text = "Status: Online" // Simplified, ideally you'd check connectivity
            }
        }

        viewModel.isConnected.observe(viewLifecycleOwner) { isConnected ->
            binding.textStatus.text = if (isConnected) "Status: Online" else "Status: Offline"
            binding.textStatus.setTextColor(
                resources.getColor(
                    if (isConnected) android.R.color.holo_green_dark else android.R.color.holo_red_dark,
                    null
                )
            )
        }

        viewModel.operationResult.observe(viewLifecycleOwner) { result ->
            Toast.makeText(requireContext(), result, Toast.LENGTH_SHORT).show()
        }
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

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}