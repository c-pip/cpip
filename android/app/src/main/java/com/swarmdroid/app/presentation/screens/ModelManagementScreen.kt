package com.swarmdroid.app.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

@Composable
fun ModelManagementScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier
) {
    val security = viewModel.securityManager

    var geminiKey by remember { mutableStateOf(security.getApiKey("gemini")) }
    var openaiKey by remember { mutableStateOf(security.getApiKey("openai")) }
    var anthropicKey by remember { mutableStateOf(security.getApiKey("anthropic")) }
    var openrouterKey by remember { mutableStateOf(security.getApiKey("openrouter")) }
    var ollamaUrl by remember { mutableStateOf("http://10.0.2.2:11434") }

    var saveMessage by remember { mutableStateOf("") }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "AI Model Management",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = SoftWhite
        )
        Text(
            text = "Configure API keys securely. Credentials are encrypted in hardware via Android Keystore.",
            style = MaterialTheme.typography.bodyMedium,
            color = DimGray
        )

        Spacer(modifier = Modifier.height(20.dp))

        // Google Gemini
        ModelProviderCard(
            title = "Google Gemini",
            subtitle = "gemini-2.0-flash / gemini-1.5-pro",
            apiKey = geminiKey,
            onKeyChanged = { geminiKey = it }
        )

        Spacer(modifier = Modifier.height(14.dp))

        // OpenAI
        ModelProviderCard(
            title = "OpenAI",
            subtitle = "gpt-4o / gpt-4o-mini",
            apiKey = openaiKey,
            onKeyChanged = { openaiKey = it }
        )

        Spacer(modifier = Modifier.height(14.dp))

        // Anthropic
        ModelProviderCard(
            title = "Anthropic Claude",
            subtitle = "claude-3-5-sonnet-20241022",
            apiKey = anthropicKey,
            onKeyChanged = { anthropicKey = it }
        )

        Spacer(modifier = Modifier.height(14.dp))

        // OpenRouter
        ModelProviderCard(
            title = "OpenRouter",
            subtitle = "Multi-provider unified gateway",
            apiKey = openrouterKey,
            onKeyChanged = { openrouterKey = it }
        )

        Spacer(modifier = Modifier.height(14.dp))

        // Ollama Local
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = SurfaceCard,
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = "Ollama (Local / Embedded)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = SoftWhite)
                Text(text = "Connects to local on-device or LAN LLM instances without cloud keys.", style = MaterialTheme.typography.bodyMedium, color = DimGray)
                Spacer(modifier = Modifier.height(10.dp))
                OutlinedTextField(
                    value = ollamaUrl,
                    onValueChange = { ollamaUrl = it },
                    label = { Text("Base URL") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = ElectricCyan,
                        unfocusedBorderColor = DimGray,
                        focusedTextColor = SoftWhite,
                        unfocusedTextColor = SoftWhite
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        if (saveMessage.isNotBlank()) {
            Text(text = saveMessage, color = StatusSuccess, style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(8.dp))
        }

        Button(
            onClick = {
                security.saveApiKey("gemini", geminiKey.trim())
                security.saveApiKey("openai", openaiKey.trim())
                security.saveApiKey("anthropic", anthropicKey.trim())
                security.saveApiKey("openrouter", openrouterKey.trim())
                saveMessage = "✓ Credentials securely encrypted in Android Keystore."
            },
            colors = ButtonDefaults.buttonColors(
                containerColor = ElectricCyan,
                contentColor = BackgroundDark
            ),
            shape = RoundedCornerShape(14.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp)
        ) {
            Text("Save Encrypted Credentials", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun ModelProviderCard(
    title: String,
    subtitle: String,
    apiKey: String,
    onKeyChanged: (String) -> Unit
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = SurfaceCard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = SoftWhite)
            Text(text = subtitle, style = MaterialTheme.typography.bodyMedium, color = DimGray)
            Spacer(modifier = Modifier.height(10.dp))
            OutlinedTextField(
                value = apiKey,
                onValueChange = onKeyChanged,
                label = { Text("API Key") },
                placeholder = { Text("sk-••••••••") },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = ElectricCyan,
                    unfocusedBorderColor = DimGray,
                    focusedTextColor = SoftWhite,
                    unfocusedTextColor = SoftWhite
                ),
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}
