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
fun DynamicAgentStudioScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier,
    onAgentCreated: () -> Unit = {}
) {
    var role by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var instructions by remember { mutableStateOf("") }

    val availableTools = listOf("web_search", "fetch_url", "run_sandbox_code", "draft_email", "draft_post", "device_action")
    val selectedTools = remember { mutableStateListOf("web_search") }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Dynamic Agent Studio",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = SoftWhite
        )
        Text(
            text = "Spawn new specialized intelligences into the swarm with strict sandbox boundaries.",
            style = MaterialTheme.typography.bodyMedium,
            color = DimGray
        )

        Spacer(modifier = Modifier.height(20.dp))

        OutlinedTextField(
            value = role,
            onValueChange = { role = it },
            label = { Text("Agent Role (e.g. DocumentationAgent)") },
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = ElectricCyan,
                unfocusedBorderColor = DimGray,
                focusedTextColor = SoftWhite,
                unfocusedTextColor = SoftWhite
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Display Name (e.g. DocuBot Prime)") },
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = ElectricCyan,
                unfocusedBorderColor = DimGray,
                focusedTextColor = SoftWhite,
                unfocusedTextColor = SoftWhite
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        OutlinedTextField(
            value = description,
            onValueChange = { description = it },
            label = { Text("Specialty Description") },
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = ElectricCyan,
                unfocusedBorderColor = DimGray,
                focusedTextColor = SoftWhite,
                unfocusedTextColor = SoftWhite
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        OutlinedTextField(
            value = instructions,
            onValueChange = { instructions = it },
            label = { Text("System Instructions & Persona Prompt") },
            minLines = 3,
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = ElectricCyan,
                unfocusedBorderColor = DimGray,
                focusedTextColor = SoftWhite,
                unfocusedTextColor = SoftWhite
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = "Permitted Tools Allowlist",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = SoftWhite
        )

        Spacer(modifier = Modifier.height(8.dp))

        availableTools.forEach { tool ->
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
            ) {
                Checkbox(
                    checked = selectedTools.contains(tool),
                    onCheckedChange = { checked ->
                        if (checked) selectedTools.add(tool) else selectedTools.remove(tool)
                    },
                    colors = CheckboxDefaults.colors(
                        checkedColor = ElectricCyan,
                        checkmarkColor = BackgroundDark
                    )
                )
                Text(text = tool, style = MaterialTheme.typography.bodyLarge, color = SoftWhite)
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                if (role.isNotBlank() && name.isNotBlank()) {
                    viewModel.createDynamicAgent(
                        role = role.trim(),
                        name = name.trim(),
                        desc = description.trim(),
                        instructions = instructions.trim(),
                        tools = selectedTools.toList()
                    )
                    onAgentCreated()
                }
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
            Text("Instantiate Agent Into Swarm", fontWeight = FontWeight.Bold)
        }
    }
}
