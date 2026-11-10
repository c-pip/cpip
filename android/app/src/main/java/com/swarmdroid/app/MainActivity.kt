package com.swarmdroid.app

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.swarmdroid.app.core.theme.SwarmDroidTheme
import com.swarmdroid.app.presentation.navigation.SwarmDroidNavGraph
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModelFactory

class MainActivity : ComponentActivity() {

    private lateinit var viewModel: SwarmViewModel

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        // Handle audio recording and notification results if needed
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val appContainer = (application as SwarmDroidApp).container
        val factory = SwarmViewModelFactory(appContainer)
        viewModel = ViewModelProvider(this, factory)[SwarmViewModel::class.java]

        checkAndRequestPermissions()

        setContent {
            SwarmDroidTheme {
                SwarmDroidNavGraph(viewModel = viewModel)
            }
        }
    }

    private fun checkAndRequestPermissions() {
        val permissionsToRequest = mutableListOf<String>()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            permissionsToRequest.add(Manifest.permission.RECORD_AUDIO)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissionsToRequest.isNotEmpty()) {
            requestPermissionLauncher.launch(permissionsToRequest.toTypedArray())
        }
    }
}
