package com.swarmdroid.app.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.domain.models.AgentInfo
import com.swarmdroid.app.presentation.components.SwarmVisualizerView
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

@Composable
fun AgentDashboardScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier,
    onNavigateToStudio: () -> Unit = {}
) {
    val agents by viewModel.agents.collectAsState()
    val graphData by viewModel.graphData.collectAsState()
    var selectedAgent by remember { mutableStateOf<AgentInfo?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
    ) {
        // Top Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Swarm Intelligence",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = SoftWhite
                )
                Text(
                    text = "${agents.size} Specialized Agents Collaborating",
                    style = MaterialTheme.typography.bodyMedium,
                    color = DimGray
                )
            }

            Button(
                onClick = onNavigateToStudio,
                colors = ButtonDefaults.buttonColors(
                    containerColor = LavenderAccent,
                    contentColor = BackgroundDark
                ),
                shape = RoundedCornerShape(14.dp)
            ) {
                Icon(Icons.Default.Add, contentDescription = "Create Agent", modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(6.dp))
                Text("New Agent", fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Interactive Animated Swarm Node Graph
        Surface(
            shape = RoundedCornerShape(20.dp),
            color = SurfaceCard,
            modifier = Modifier
                .fillMaxWidth()
                .height(220.dp)
        ) {
            SwarmVisualizerView(
                agents = agents,
                graphData = graphData,
                onAgentSelected = { selectedAgent = it }
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Active Agents",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = SoftWhite
        )

        Spacer(modifier = Modifier.height(8.dp))

        // List of all Agents
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            items(agents) { agent ->
                AgentCard(agent = agent)
            }
        }
    }
}

@Composable
fun AgentCard(agent: AgentInfo) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = SurfaceCard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Agent Avatar with status ring
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .background(SurfaceVariantDark, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = when (agent.role) {
                        "MasterAgent" -> "👑"
                        "BrowserAgent" -> "🌐"
                        "CodingAgent" -> "💻"
                        "CommunicationAgent" -> "✉️"
                        "SocialMediaAgent" -> "📱"
                        "DeviceAgent" -> "🤖"
                        "ResearchAgent" -> "🔬"
                        "MemoryAgent" -> "🧠"
                        "SecurityAgent" -> "🛡️"
                        else -> "⚡"
                    },
                    fontSize = 20.sp
                )
            }

            Spacer(modifier = Modifier.width(14.dp))

            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = agent.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = SoftWhite
                    )
                    if (agent.isDynamic) {
                        Spacer(modifier = Modifier.width(6.dp))
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = Color(0x33B892FF)
                        ) {
                            Text(
                                text = "DYNAMIC",
                                style = MaterialTheme.typography.labelSmall,
                                color = LavenderAccent,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
                Text(
                    text = agent.description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = DimGray
                )
            }

            Spacer(modifier = Modifier.width(8.dp))

            // Status Badge
            val statusColor = when (agent.currentStatus) {
                "WORKING" -> ElectricCyan
                "WAITING_APPROVAL" -> StatusWarning
                "ERROR" -> StatusError
                else -> DimGray
            }
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = SurfaceVariantDark
            ) {
                Text(
                    text = agent.currentStatus,
                    style = MaterialTheme.typography.labelSmall,
                    color = statusColor,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                )
            }
        }
    }
}
