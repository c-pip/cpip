package com.swarmdroid.app.presentation.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.swarmdroid.app.R
import com.swarmdroid.app.character.Character3DView
import com.swarmdroid.app.character.CharacterEmotion
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.presentation.components.ApprovalDialog
import com.swarmdroid.app.presentation.components.VoiceVisualizerBar
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

@Composable
fun MainCompanionScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier,
    onNavigateToSwarm: () -> Unit = {}
) {
    val emotion by viewModel.currentEmotion.collectAsState()
    val isListening by viewModel.voiceManager.isListening.collectAsState()
    val speechAmplitude by viewModel.voiceManager.audioAmplitude.collectAsState()
    val pendingApproval by viewModel.pendingApproval.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    var textInput by remember { mutableStateOf("") }

    val suggestions = listOf(
        "Research latest Android AI technologies",
        "Launch open-source project workflow",
        "Draft an X post on multi-agent swarms",
        "Check device battery and network"
    )

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Top Bar: Mascot Status Chip & Swarm Graph Shortcut
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = SurfaceCard,
                    modifier = Modifier.clickable { onNavigateToSwarm() }
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Image(
                            painter = painterResource(id = R.drawable.logo),
                            contentDescription = "SwarmDroid Logo",
                            modifier = Modifier
                                .size(26.dp)
                                .clip(CircleShape)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(
                                    if (isLoading) ElectricCyan else StatusSuccess,
                                    shape = CircleShape
                                )
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = if (isLoading) "Swarm Active" else "Swarm Ready",
                            style = MaterialTheme.typography.labelSmall,
                            color = SoftWhite
                        )
                    }
                }

                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = SurfaceVariantDark,
                    modifier = Modifier.clickable { onNavigateToSwarm() }
                ) {
                    Text(
                        text = "Visualizer 🌐",
                        style = MaterialTheme.typography.labelSmall,
                        color = ElectricCyan,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Centerpiece: Adorable 3D Companion Mascot (interactive!)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1.0f),
                contentAlignment = Alignment.Center
            ) {
                Character3DView(
                    emotion = emotion,
                    speechAmplitude = speechAmplitude,
                    modifier = Modifier.fillMaxSize(),
                    onTap = {
                        // Tapping companion triggers a joyful celebration or greeting
                        viewModel.setEmotion(CharacterEmotion.CELEBRATING)
                        viewModel.voiceManager.speak("Hello! I am your SwarmDroid companion. What shall we achieve today?")
                    }
                )

                // Emotional State Floating Tag
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = Color(0xCC141721),
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(bottom = 12.dp)
                ) {
                    Text(
                        text = "Mood: ${emotion.name.lowercase().replaceFirstChar { it.uppercase() }}",
                        style = MaterialTheme.typography.labelSmall,
                        color = LavenderAccent,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }

            // Voice Activity Waveform Bar
            VoiceVisualizerBar(
                amplitude = speechAmplitude,
                isListening = isListening,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Quick Task Suggestions Row
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                items(suggestions) { sugg ->
                    Surface(
                        shape = RoundedCornerShape(14.dp),
                        color = SurfaceCard,
                        modifier = Modifier.clickable {
                            viewModel.sendUserPrompt(sugg)
                        }
                    ) {
                        Text(
                            text = sugg,
                            style = MaterialTheme.typography.bodyMedium,
                            color = DimGray,
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Bottom Input Bar
            Surface(
                shape = RoundedCornerShape(24.dp),
                color = SurfaceCard,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 12.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextField(
                        value = textInput,
                        onValueChange = { textInput = it },
                        placeholder = { Text("Ask your swarm anything...", color = DimGray) },
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent,
                            focusedTextColor = SoftWhite,
                            unfocusedTextColor = SoftWhite
                        ),
                        modifier = Modifier.weight(1f)
                    )

                    // Mic button for STT
                    IconButton(
                        onClick = { viewModel.triggerVoiceQuery() },
                        modifier = Modifier
                            .background(if (isListening) ElectricCyan else SurfaceVariantDark, CircleShape)
                            .size(42.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Mic,
                            contentDescription = "Voice Input",
                            tint = if (isListening) BackgroundDark else ElectricCyan
                        )
                    }

                    Spacer(modifier = Modifier.width(8.dp))

                    // Send prompt button
                    IconButton(
                        onClick = {
                            if (textInput.isNotBlank()) {
                                viewModel.sendUserPrompt(textInput)
                                textInput = ""
                            }
                        },
                        modifier = Modifier
                            .background(ElectricCyan, CircleShape)
                            .size(42.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Send,
                            contentDescription = "Send",
                            tint = BackgroundDark
                        )
                    }
                }
            }
        }

        // Sensitive Action Human-in-the-Loop Approval Modal
        pendingApproval?.let { task ->
            ApprovalDialog(
                task = task,
                onApprove = { viewModel.approvePendingTask(true) },
                onReject = { viewModel.approvePendingTask(false) },
                onDismiss = { /* must choose */ }
            )
        }
    }
}
