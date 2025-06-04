package dev.xhyrom.jim.ui.settings

import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.appcompat.app.AppCompatDelegate
import androidx.fragment.app.Fragment
import dev.xhyrom.jim.databinding.FragmentSettingsBinding

class SettingsFragment : Fragment() {
    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSettingsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupUI()
        setupClickListeners()
    }

    private fun setupUI() {
        // Set app version using PackageManager
        try {
            val packageInfo = requireContext().packageManager.getPackageInfo(requireContext().packageName, 0)
            val versionName = packageInfo.versionName
            val versionCode = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                packageInfo.longVersionCode.toString()
            } else {
                @Suppress("DEPRECATION")
                packageInfo.versionCode.toString()
            }
            binding.textAppVersion.text = "App Version: $versionName ($versionCode)"
        } catch (e: PackageManager.NameNotFoundException) {
            binding.textAppVersion.text = "App Version: Unknown"
        }
    }

    private fun setupClickListeners() {
        // Dark mode toggle
        binding.switchDarkMode.setOnCheckedChangeListener { _, isChecked ->
            val mode = if (isChecked) {
                AppCompatDelegate.MODE_NIGHT_YES
            } else {
                AppCompatDelegate.MODE_NIGHT_NO
            }
            AppCompatDelegate.setDefaultNightMode(mode)
        }

        // Keep screen on during terminal sessions
        binding.switchKeepScreenOn.setOnCheckedChangeListener { _, isChecked ->
            val preferences = androidx.preference.PreferenceManager.getDefaultSharedPreferences(requireContext())
            preferences.edit().putBoolean("keep_screen_on", isChecked).apply()
        }

        // GitHub repository button
        binding.buttonGithub.setOnClickListener {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/xhyrom/jim"))
            startActivity(intent)
        }
    }

    override fun onResume() {
        super.onResume()
        
        // Update switch states based on current settings
        val preferences = androidx.preference.PreferenceManager.getDefaultSharedPreferences(requireContext())
        binding.switchDarkMode.isChecked = AppCompatDelegate.getDefaultNightMode() == AppCompatDelegate.MODE_NIGHT_YES
        binding.switchKeepScreenOn.isChecked = preferences.getBoolean("keep_screen_on", false)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}