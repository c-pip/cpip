package com.swarmdroid.app.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

@Composable
fun PermissionsCenterScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier
) {
    val device = viewModel.deviceManager

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
    ) {
        Text(
            text = "Permissions & Security Center",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = SoftWhite
        )
        Text(
            text = "Strict sandboxing, tool allowlists, and device integrity verification.",
            style = MaterialTheme.typography.bodyMedium,
            color = DimGray
        )

        Spacer(modifier = Modifier.height(20.dp))

        // Device Diagnostics Card
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = SurfaceCard,
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = "Android System Health", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = SoftWhite)
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "Battery Level:", style = MaterialTheme.typography.bodyMedium, color = DimGray)
                    Text(text = "${device.getBatteryLevel()}%", style = MaterialTheme.typography.bodyMedium, color = ElectricCyan)
                }
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "Network Active:", style = MaterialTheme.typography.bodyMedium, color = DimGray)
                    Text(text = if (device.isNetworkConnected()) "Connected ✓" else "Offline ✗", style = MaterialTheme.typography.bodyMedium, color = if (device.isNetworkConnected()) StatusSuccess else StatusError)
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Sensitive Action Policies
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = SurfaceCard,
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = "Human-in-the-Loop Policies", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = SoftWhite)
                Spacer(modifier = Modifier.height(8.dp))
                Text(text = "• Email Sending: Explicit confirmation required", style = MaterialTheme.typography.bodyMedium, color = SoftWhite)
                Text(text = "• Social Media Publishing: Explicit confirmation required", style = MaterialTheme.typography.bodyMedium, color = SoftWhite)
                Text(text = "• Device Settings Modification: Explicit confirmation required", style = MaterialTheme.typography.bodyMedium, color = SoftWhite)
                Text(text = "• Prompt Injection Defense: Aegis Guardian Active", style = MaterialTheme.typography.bodyMedium, color = ElectricCyan)
            }
        }
    }
}
