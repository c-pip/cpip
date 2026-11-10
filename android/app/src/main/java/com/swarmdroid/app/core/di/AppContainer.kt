package com.swarmdroid.app.core.di

import android.content.Context
import com.swarmdroid.app.core.database.SwarmDatabase
import com.swarmdroid.app.core.network.SwarmApiClient
import com.swarmdroid.app.core.network.SwarmWebSocketClient
import com.swarmdroid.app.device.DeviceIntegrationManager
import com.swarmdroid.app.security.SecurityManager
import com.swarmdroid.app.voice.VoiceInteractionManager

class AppContainer(context: Context) {
    val database: SwarmDatabase by lazy {
        SwarmDatabase.getDatabase(context)
    }

    val apiClient: SwarmApiClient by lazy {
        SwarmApiClient()
    }

    val webSocketClient: SwarmWebSocketClient by lazy {
        SwarmWebSocketClient()
    }

    val voiceManager: VoiceInteractionManager by lazy {
        VoiceInteractionManager(context)
    }

    val deviceManager: DeviceIntegrationManager by lazy {
        DeviceIntegrationManager(context)
    }

    val securityManager: SecurityManager by lazy {
        SecurityManager(context)
    }
}
