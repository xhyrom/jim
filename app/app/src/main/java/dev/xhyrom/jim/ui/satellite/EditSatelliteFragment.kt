package dev.xhyrom.jim.ui.satellite

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import dev.xhyrom.jim.data.database.AppDatabase
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.data.repository.SatelliteRepository
import dev.xhyrom.jim.databinding.FragmentAddEditSatelliteBinding

class EditSatelliteFragment : Fragment() {
    private var _binding: FragmentAddEditSatelliteBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: SatelliteViewModel
    private val args: EditSatelliteFragmentArgs by navArgs()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAddEditSatelliteBinding.inflate(inflater, container, false)
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

        val satelliteId = args.satelliteId
        viewModel.getSatelliteById(satelliteId).observe(viewLifecycleOwner) { satellite ->
            if (satellite != null) {
                binding.editSatelliteName.setText(satellite.name)
                binding.editSatelliteIp.setText(satellite.ipAddress)
                binding.editSshUsername.setText(satellite.sshUsername)
                binding.editSshPassword.setText(satellite.sshPassword)
                binding.editSshPort.setText(satellite.sshPort.toString())
            }
        }

        binding.buttonSave.setOnClickListener {
            updateSatellite(satelliteId)
        }

        binding.buttonCancel.setOnClickListener {
            findNavController().navigateUp()
        }
    }

    private fun updateSatellite(satelliteId: Long) {
        val name = binding.editSatelliteName.text.toString()
        val ip = binding.editSatelliteIp.text.toString()
        val username = binding.editSshUsername.text.toString()
        val password = binding.editSshPassword.text.toString()
        val portStr = binding.editSshPort.text.toString()

        if (name.isBlank() || ip.isBlank() || username.isBlank()) {
            Toast.makeText(context, "Please fill in all required fields", Toast.LENGTH_SHORT).show()
            return
        }

        val port = portStr.toIntOrNull() ?: 22

        viewModel.selectedSatellite.value?.let { currentSatellite ->
            val updatedSatellite = Satellite(
                id = satelliteId,
                name = name,
                ipAddress = ip,
                sshUsername = username,
                sshPassword = password.takeIf { it.isNotEmpty() },
                sshPort = port
            )

            viewModel.updateSatellite(updatedSatellite)
            findNavController().navigateUp()
        } ?: run {
            Toast.makeText(context, "Satellite not found", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}