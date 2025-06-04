package dev.xhyrom.jim

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.NavController
import androidx.navigation.NavDestination
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import androidx.preference.PreferenceManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import dev.xhyrom.jim.databinding.ActivityMainBinding
import dev.xhyrom.jim.ui.onboarding.OnboardingActivity

class MainActivity : AppCompatActivity() {
    private lateinit var preferences: SharedPreferences
    private lateinit var binding: ActivityMainBinding
    private lateinit var navController: NavController
    private lateinit var appBarConfiguration: AppBarConfiguration

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        preferences = PreferenceManager.getDefaultSharedPreferences(this)

        if (!preferences.getBoolean("setup_completed", false)) {
            // Launch onboarding to add the first satellite
            startActivity(Intent(this, OnboardingActivity::class.java))
            finish()
            return
        }

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupNavigation()
    }
    
    override fun onResume() {
        super.onResume()
        
        // Double-check if onboarding is completed (in case user pressed back from onboarding)
        if (!preferences.getBoolean("setup_completed", false)) {
            startActivity(Intent(this, OnboardingActivity::class.java))
            finish()
        }
    }

    private fun setupNavigation() {
        val navView: BottomNavigationView = binding.navView
        
        // Get the NavController from the NavHostFragment
        val navHostFragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController
        
        // Define top level destinations (no back button)
        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.homeFragment, R.id.logsFragment, R.id.settingsFragment
            )
        )
        
        // Set the title for the HomeFragment to "Satellites"
        navController.addOnDestinationChangedListener { _, destination, _ ->
            if (destination.id == R.id.homeFragment) {
                supportActionBar?.title = getString(R.string.title_home)
            }
        }
        
        // Connect ActionBar with NavController
        setupActionBarWithNavController(navController, appBarConfiguration)
        
        // Connect BottomNavigationView with NavController
        navView.setupWithNavController(navController)
        
        // Listen for navigation changes to update UI if needed
        navController.addOnDestinationChangedListener { _, destination, _ ->
            updateUIForDestination(destination)
        }
    }
    
    private fun updateUIForDestination(destination: NavDestination) {
        // This method can be used to update UI elements based on the current destination
        // For example, showing/hiding certain buttons or updating the title
        when (destination.id) {
            R.id.homeFragment -> {
                // Set title to Satellites
                supportActionBar?.title = getString(R.string.title_home)
            }
            R.id.logsFragment -> {
                // Logs destination specific UI changes if needed
            }
            R.id.settingsFragment -> {
                // Settings destination specific UI changes if needed
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        // Handle the up button with the AppBarConfiguration
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }
    
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks
        return when (item.itemId) {
            android.R.id.home -> {
                // Handle the back button
                if (!navController.navigateUp()) {
                    onBackPressed()
                }
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
}