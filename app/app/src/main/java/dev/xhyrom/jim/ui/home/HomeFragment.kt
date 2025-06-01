package dev.xhyrom.jim.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import dev.xhyrom.jim.R
import dev.xhyrom.jim.databinding.FragmentHomeBinding

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private lateinit var homeViewModel: HomeViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        homeViewModel = ViewModelProvider(this).get(HomeViewModel::class.java)

        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        val root: View = binding.root

        setupObservers()
        setupClickListeners()

        homeViewModel.loadDeviceStatus()

        return root
    }

    private fun setupObservers() {
        homeViewModel.deviceStatus.observe(viewLifecycleOwner) { status ->
            binding.textDeviceName.text = getString(R.string.device_name, "Jim Satellite")
            binding.textDeviceStatus.text = getString(R.string.device_status, status.status)
            binding.textDeviceVersion.text = getString(R.string.device_version, status.version)

            val uptimeHours = status.uptime / 3600
            val uptimeMinutes = (status.uptime % 3600) / 60
            binding.textDeviceUptime.text = getString(R.string.device_uptime,
                "$uptimeHours hrs $uptimeMinutes min")

            binding.connectionStatus.setImageResource(
                if (status.connected) R.drawable.ic_connected
                else R.drawable.ic_disconnected
            )

            binding.deviceImage.setImageResource(R.drawable.device_satellite)
        }

        homeViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        homeViewModel.errorMessage.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun setupClickListeners() {
        binding.buttonRefresh.setOnClickListener {
            homeViewModel.loadDeviceStatus()
        }

        binding.buttonReboot.setOnClickListener {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle("Reboot Device")
                .setMessage("Are you sure you want to reboot the device?")
                .setPositiveButton("Reboot") { _, _ ->
                    homeViewModel.rebootDevice()
                    Toast.makeText(requireContext(), "Rebooting device...", Toast.LENGTH_SHORT).show()
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