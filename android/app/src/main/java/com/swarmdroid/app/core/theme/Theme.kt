package com.swarmdroid.app.core.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = ElectricCyan,
    onPrimary = BackgroundDark,
    primaryContainer = SurfaceVariantDark,
    onPrimaryContainer = ElectricCyan,
    secondary = LavenderAccent,
    onSecondary = BackgroundDark,
    secondaryContainer = SurfaceVariantDark,
    onSecondaryContainer = LavenderAccent,
    tertiary = StatusPlanning,
    background = BackgroundDark,
    onBackground = SoftWhite,
    surface = SurfaceDark,
    onSurface = SoftWhite,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = DimGray,
    error = StatusError,
    onError = SoftWhite
)

@Composable
fun SwarmDroidTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography,
        content = content
    )
}
