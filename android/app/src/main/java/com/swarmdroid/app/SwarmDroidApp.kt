package com.swarmdroid.app

import android.app.Application
import com.swarmdroid.app.core.di.AppContainer

class SwarmDroidApp : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
