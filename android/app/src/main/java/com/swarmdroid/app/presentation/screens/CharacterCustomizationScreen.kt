package com.swarmdroid.app.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.swarmdroid.app.character.CharacterEmotion
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

@Composable
fun CharacterCustomizationScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier
) {
    var selectedOutfit by remember { mutableStateOf("Cyber Core") }
    var selectedAntenna by remember { mutableStateOf("Floating Orbs") }
    var selectedGlow by remember { mutableStateOf("Electric Cyan") }

    val outfits = listOf("Cyber Core", "Neon Explorer", "Quantum Tux", "Lavender Blossom")
    val antennas = listOf("Floating Orbs", "Halo Ring", "Dual Wings")
    val glowColors = listOf("Electric Cyan", "Lavender Violet", "Emerald Spark", "Solar Gold")

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Companion Customization",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = SoftWhite
        )
        Text(
            text = "Customize the aesthetic appearance and test emotional animation states.",
            style = MaterialTheme.typography.bodyMedium,
            color = DimGray
        )

        Spacer(modifier = Modifier.height(20.dp))

        // Outfit Selection
        Text(text = "Chassis Outfit", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = SoftWhite)
        Spacer(modifier = Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            outfits.forEach { outfit ->
                val isSelected = outfit == selectedOutfit
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = if (isSelected) LavenderAccent else SurfaceCard,
                    modifier = Modifier.clickable { selectedOutfit = outfit }
                ) {
                    Text(
                        text = outfit,
                        color = if (isSelected) BackgroundDark else SoftWhite,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(18.dp))

        // Antenna Orbs
        Text(text = "Levitating Antennas", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = SoftWhite)
        Spacer(modifier = Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            antennas.forEach { ant ->
                val isSelected = ant == selectedAntenna
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = if (isSelected) ElectricCyan else SurfaceCard,
                    modifier = Modifier.clickable { selectedAntenna = ant }
                ) {
                    Text(
                        text = ant,
                        color = if (isSelected) BackgroundDark else SoftWhite,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(18.dp))

        // Emissive Glow Palette
        Text(text = "Emissive Visor Glow", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = SoftWhite)
        Spacer(modifier = Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            glowColors.forEach { glow ->
                val isSelected = glow == selectedGlow
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = if (isSelected) ElectricCyan else SurfaceCard,
                    modifier = Modifier.clickable { selectedGlow = glow }
                ) {
                    Text(
                        text = glow,
                        color = if (isSelected) BackgroundDark else SoftWhite,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Test Animation States (All 14 States Trigger)
        Text(text = "Test 14 Animation States", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = SoftWhite)
        Spacer(modifier = Modifier.height(8.dp))

        val emotions = CharacterEmotion.entries
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            for (rowEmotions in emotions.chunked(3)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                    for (emo in rowEmotions) {
                        Surface(
                            shape = RoundedCornerShape(10.dp),
                            color = SurfaceVariantDark,
                            modifier = Modifier
                                .weight(1f)
                                .clickable { viewModel.setEmotion(emo) }
                        ) {
                            Text(
                                text = emo.name,
                                style = MaterialTheme.typography.labelSmall,
                                color = SoftWhite,
                                modifier = Modifier.padding(vertical = 8.dp, horizontal = 4.dp),
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center
                            )
                        }
                    }
                }
            }
        }
    }
}
