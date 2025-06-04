package dev.xhyrom.jim.ui.satellite

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController

import dev.xhyrom.jim.data.database.AppDatabase
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.data.repository.SatelliteRepository
import dev.xhyrom.jim.databinding.FragmentAddEditSatelliteBinding

class AddSatelliteFragment : Fragment() {
    private var _binding: FragmentAddEditSatelliteBinding? = null
    private val binding get() = _binding!!

    private lateinit var viewModel: SatelliteViewModel

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

        binding.textTitle.text = "Add Satellite"
        binding.editSshUsername.setText("pi")  // Default username
        binding.editSshPort.setText("22")      // Default SSH port

        binding.buttonSave.setOnClickListener {
            saveSatellite()
        }

        binding.buttonCancel.setOnClickListener {
            findNavController().navigateUp()
        }
    }

    private fun saveSatellite() {
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

        val newSatellite = Satellite(
            name = name,
            ipAddress = ip,
            sshUsername = username,
            sshPassword = password.takeIf { it.isNotEmpty() },
            sshPort = port
        )

        viewModel.insertSatellite(newSatellite)
        findNavController().navigateUp()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}