package com.swarmdroid.app.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

@Composable
fun MemoryManagementScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier
) {
    var searchQuery by remember { mutableStateOf("") }

    val mockMemories = remember {
        mutableStateListOf(
            "User prefers concise code implementations in Kotlin",
            "Active project: Open-source multi-agent Android framework",
            "Research notes: GLTF binary specifications and animation state machines",
            "Favorite visual theme: Cyber dark matte with lavender accents"
        )
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
    ) {
        Text(
            text = "Memory & Knowledge System",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = SoftWhite
        )
        Text(
            text = "Inspect and delete short-term, long-term, and shared knowledge records.",
            style = MaterialTheme.typography.bodyMedium,
            color = DimGray
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder = { Text("Search semantic memories...", color = DimGray) },
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = ElectricCyan,
                unfocusedBorderColor = DimGray,
                focusedTextColor = SoftWhite,
                unfocusedTextColor = SoftWhite
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        val filtered = if (searchQuery.isBlank()) mockMemories else mockMemories.filter { it.contains(searchQuery, ignoreCase = true) }

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            items(filtered) { mem ->
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = SurfaceCard,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = mem,
                            style = MaterialTheme.typography.bodyMedium,
                            color = SoftWhite,
                            modifier = Modifier.weight(1f)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        TextButton(
                            onClick = { mockMemories.remove(mem) },
                            colors = ButtonDefaults.textButtonColors(contentColor = StatusError)
                        ) {
                            Text("Delete")
                        }
                    }
                }
            }
        }
    }
}
