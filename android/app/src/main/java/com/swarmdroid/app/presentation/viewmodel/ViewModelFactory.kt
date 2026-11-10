package com.swarmdroid.app.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.swarmdroid.app.core.di.AppContainer

class SwarmViewModelFactory(private val container: AppContainer) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(SwarmViewModel::class.java)) {
            return SwarmViewModel(
                database = container.database,
                apiClient = container.apiClient,
                webSocketClient = container.webSocketClient,
                voiceManager = container.voiceManager,
                deviceManager = container.deviceManager,
                securityManager = container.securityManager
            ) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class ${modelClass.name}")
    }
}
