package dev.xhyrom.jim.ui.onboarding

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.preference.PreferenceManager
import dev.xhyrom.jim.MainActivity
import dev.xhyrom.jim.databinding.ActivityOnboardingBinding

class OnboardingActivity : AppCompatActivity() {
    private lateinit var binding: ActivityOnboardingBinding
    private lateinit var viewModel: OnboardingViewModel
    private lateinit var preferences: SharedPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOnboardingBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this).get(OnboardingViewModel::class.java)
        preferences = PreferenceManager.getDefaultSharedPreferences(this)

        binding.buttonContinue.setOnClickListener {
            val satelliteName = binding.editSatelliteName.text.toString()
            val satelliteIp = binding.editSatelliteIp.text.toString()
            val sshUsername = binding.editSshUsername.text.toString()
            val sshPassword = binding.editSshPassword.text.toString().takeIf { it.isNotEmpty() }

            if (satelliteName.isBlank() || satelliteIp.isBlank() || sshUsername.isBlank()) {
                Toast.makeText(this, "Please fill in all required fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            viewModel.addSatellite(satelliteName, satelliteIp, sshUsername, sshPassword).observe(this) { success ->
                if (success) {
                    // Mark setup as completed
                    preferences.edit().putBoolean("setup_completed", true).apply()

                    // Continue to main app
                    startActivity(Intent(this, MainActivity::class.java))
                    finish()
                } else {
                    Toast.makeText(this, "Failed to add satellite. Please try again.", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}