package dev.xhyrom.jim.ui.settings

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import dev.xhyrom.jim.R
import dev.xhyrom.jim.data.AsrConfig
import dev.xhyrom.jim.data.ConfigModel
import dev.xhyrom.jim.data.CoreConfig
import dev.xhyrom.jim.data.LedConfig
import dev.xhyrom.jim.data.Schedule
import dev.xhyrom.jim.data.TtsConfig
import dev.xhyrom.jim.data.WakeConfig
import dev.xhyrom.jim.databinding.FragmentSettingsBinding
import dev.xhyrom.jim.ui.bluetooth.BluetoothScanActivity
import dev.xhyrom.jim.ui.terminal.TerminalActivity

class SettingsFragment : Fragment() {

    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!

    private lateinit var settingsViewModel: SettingsViewModel
    private var currentConfig: ConfigModel? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        settingsViewModel = ViewModelProvider(this).get(SettingsViewModel::class.java)

        _binding = FragmentSettingsBinding.inflate(inflater, container, false)
        val root: View = binding.root

        setupObservers()
        setupClickListeners()

        // Load configuration when fragment is created
        settingsViewModel.loadConfig()

        return root
    }

    private fun setupObservers() {
        settingsViewModel.config.observe(viewLifecycleOwner) { config ->
            currentConfig = config

            // ASR settings
            binding.asrTypeSpinner.setSelection(
                resources.getStringArray(R.array.asr_types).indexOf(config.asr.type)
            )
            binding.editAsrModelPath.setText(config.asr.model_path ?: "")
            binding.editAsrApiKey.setText(config.asr.api_key ?: "")

            // TTS settings
            binding.ttsTypeSpinner.setSelection(
                resources.getStringArray(R.array.tts_types).indexOf(config.tts.type)
            )
            binding.editTtsModelPath.setText(config.tts.model_path)

            // Wake word settings
            binding.editWakewordThreshold.setText(config.wake.threshold.toString())
            binding.editWakewordModels.setText(config.wake.model_paths.joinToString("\n"))

            // Core settings
            binding.editCoreUrl.setText(config.core.url)
            binding.editCoreApiKey.setText(config.core.api_key ?: "")

            // LED settings
            binding.ledDriverTypeSpinner.setSelection(
                resources.getStringArray(R.array.led_driver_types).indexOf(config.led.driver_type)
            )
            binding.editNumLeds.setText(config.led.num_leds.toString())
            binding.editLedBrightness.setText(config.led.brightness.toString())
            binding.editLedColor.setText(config.led.base_color)

            binding.switchScheduleEnabled.isChecked = config.led.schedule.enabled
            binding.editScheduleStart.setText(config.led.schedule.start_hour.toString())
            binding.editScheduleEnd.setText(config.led.schedule.end_hour.toString())
        }

        settingsViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        settingsViewModel.errorMessage.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun setupClickListeners() {
        binding.buttonSaveConfig.setOnClickListener {
            saveConfig()
        }

        binding.buttonFactoryReset.setOnClickListener {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle("Factory Reset")
                .setMessage("Are you sure you want to reset to factory defaults? This will erase all settings.")
                .setPositiveButton("Reset") { _, _ ->
                    settingsViewModel.factoryReset()
                }
                .setNegativeButton("Cancel", null)
                .show()
        }

        binding.buttonTerminal.setOnClickListener {
            startActivity(Intent(requireContext(), TerminalActivity::class.java))
        }

        binding.buttonBluetooth.setOnClickListener {
            startActivity(Intent(requireContext(), BluetoothScanActivity::class.java))
        }
    }

    private fun saveConfig() {
        try {
            val asrType = binding.asrTypeSpinner.selectedItem.toString()
            val asrModelPath = binding.editAsrModelPath.text.toString().takeIf { it.isNotEmpty() }
            val asrApiKey = binding.editAsrApiKey.text.toString().takeIf { it.isNotEmpty() }

            val ttsType = binding.ttsTypeSpinner.selectedItem.toString()
            val ttsModelPath = binding.editTtsModelPath.text.toString()

            val wakeThreshold = binding.editWakewordThreshold.text.toString().toFloatOrNull() ?: 0.5f
            val wakeModelPaths = binding.editWakewordModels.text.toString()
                .split("\n")
                .filter { it.isNotEmpty() }

            val coreUrl = binding.editCoreUrl.text.toString()
            val coreApiKey = binding.editCoreApiKey.text.toString().takeIf { it.isNotEmpty() }

            val ledDriverType = binding.ledDriverTypeSpinner.selectedItem.toString()
            val numLeds = binding.editNumLeds.text.toString().toIntOrNull() ?: 3
            val brightness = binding.editLedBrightness.text.toString().toIntOrNull() ?: 10
            val baseColor = binding.editLedColor.text.toString()

            val scheduleEnabled = binding.switchScheduleEnabled.isChecked
            val scheduleStart = binding.editScheduleStart.text.toString().toIntOrNull() ?: 7
            val scheduleEnd = binding.editScheduleEnd.text.toString().toIntOrNull() ?: 22

            val newConfig = ConfigModel(
                asr = AsrConfig(
                    type = asrType,
                    model_path = asrModelPath,
                    api_key = asrApiKey
                ),
                tts = TtsConfig(
                    type = ttsType,
                    model_path = ttsModelPath
                ),
                wake = WakeConfig(
                    model_paths = wakeModelPaths,
                    threshold = wakeThreshold
                ),
                core = CoreConfig(
                    url = coreUrl,
                    api_key = coreApiKey
                ),
                led = LedConfig(
                    driver_type = ledDriverType,
                    num_leds = numLeds,
                    brightness = brightness,
                    base_color = baseColor,
                    schedule = Schedule(
                        enabled = scheduleEnabled,
                        start_hour = scheduleStart,
                        end_hour = scheduleEnd
                    )
                )
            )

            settingsViewModel.updateConfig(newConfig)
            Toast.makeText(requireContext(), "Config saved", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(requireContext(), "Error saving config: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}