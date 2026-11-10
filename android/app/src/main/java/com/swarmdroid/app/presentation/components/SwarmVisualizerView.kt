package com.swarmdroid.app.presentation.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.domain.models.AgentInfo
import com.swarmdroid.app.domain.models.SwarmGraphData
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun SwarmVisualizerView(
    agents: List<AgentInfo>,
    graphData: SwarmGraphData = SwarmGraphData(),
    modifier: Modifier = Modifier,
    onAgentSelected: (AgentInfo) -> Unit = {}
) {
    val infiniteTransition = rememberInfiniteTransition(label = "SwarmSignals")
    val pulseAnim by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2400, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "PulseProgress"
    )

    Canvas(
        modifier = modifier
            .fillMaxSize()
            .pointerInput(agents) {
                detectTapGestures { offset ->
                    val centerX = size.width / 2f
                    val centerY = size.height / 2f
                    val outerAgents = agents.filter { it.role != "MasterAgent" }
                    val orbitRadius = size.width.coerceAtMost(size.height) * 0.38f

                    // Check center tap (Master Agent)
                    val distCenter = (offset - Offset(centerX, centerY)).getDistance()
                    if (distCenter < 50f) {
                        agents.firstOrNull { it.role == "MasterAgent" }?.let(onAgentSelected)
                        return@detectTapGestures
                    }

                    // Check orbital taps
                    outerAgents.forEachIndexed { index, agent ->
                        val angle = (2 * Math.PI * index / outerAgents.size) - (Math.PI / 2)
                        val nodeX = centerX + orbitRadius * cos(angle).toFloat()
                        val nodeY = centerY + orbitRadius * sin(angle).toFloat()
                        val dist = (offset - Offset(nodeX, nodeY)).getDistance()
                        if (dist < 40f) {
                            onAgentSelected(agent)
                            return@detectTapGestures
                        }
                    }
                }
            }
    ) {
        val centerX = size.width / 2f
        val centerY = size.height / 2f
        val orbitRadius = size.width.coerceAtMost(size.height) * 0.38f
        val outerAgents = agents.filter { it.role != "MasterAgent" }

        // Draw Orbit Guide Ring
        drawCircle(
            color = Color(0x1A00F5D4),
            radius = orbitRadius,
            center = Offset(centerX, centerY),
            style = Stroke(width = 1.5f)
        )

        // Draw Edges & Animated Moving Signals from Center to Orbiting Agents
        outerAgents.forEachIndexed { index, agent ->
            val angle = (2 * Math.PI * index / outerAgents.size) - (Math.PI / 2)
            val nodeX = centerX + orbitRadius * cos(angle).toFloat()
            val nodeY = centerY + orbitRadius * sin(angle).toFloat()

            val isWorking = agent.currentStatus == "WORKING" || agent.currentStatus == "THINKING"
            val edgeColor = if (isWorking) ElectricCyan else Color(0x338E99A8)
            val strokeWidth = if (isWorking) 2.5f else 1.2f

            // Connecting Edge Line
            drawLine(
                color = edgeColor,
                start = Offset(centerX, centerY),
                end = Offset(nodeX, nodeY),
                strokeWidth = strokeWidth
            )

            // Animated Moving Data Packet Signal along the Edge
            if (isWorking) {
                val signalX = centerX + (nodeX - centerX) * pulseAnim
                val signalY = centerY + (nodeY - centerY) * pulseAnim
                drawCircle(
                    color = ElectricCyan,
                    radius = 4.5f,
                    center = Offset(signalX, signalY)
                )
                // Signal glow
                drawCircle(
                    color = Color(0x6600F5D4),
                    radius = 9f,
                    center = Offset(signalX, signalY)
                )
            }

            // Outer Agent Satellite Node
            val statusColor = when (agent.currentStatus) {
                "WORKING" -> ElectricCyan
                "WAITING_APPROVAL" -> StatusWarning
                "ERROR" -> StatusError
                else -> LavenderAccent
            }

            // Glow ring for active agents
            if (isWorking) {
                drawCircle(
                    color = Color(0x3300F5D4),
                    radius = 28f + (pulseAnim * 6f),
                    center = Offset(nodeX, nodeY)
                )
            }

            // Node core
            drawCircle(
                color = SurfaceDark,
                radius = 20f,
                center = Offset(nodeX, nodeY)
            )
            drawCircle(
                color = statusColor,
                radius = 20f,
                center = Offset(nodeX, nodeY),
                style = Stroke(width = 2.5f)
            )
            drawCircle(
                color = statusColor,
                radius = 8f,
                center = Offset(nodeX, nodeY)
            )
        }

        // Draw Center Node (Master Agent - Aegis Prime)
        val masterWorking = agents.any { it.currentStatus == "WORKING" }
        // Pulsing halo
        drawCircle(
            color = if (masterWorking) Color(0x4400F5D4) else Color(0x22B892FF),
            radius = 36f + (pulseAnim * 8f),
            center = Offset(centerX, centerY)
        )
        drawCircle(
            color = SurfaceCard,
            radius = 30f,
            center = Offset(centerX, centerY)
        )
        drawCircle(
            color = ElectricCyan,
            radius = 30f,
            center = Offset(centerX, centerY),
            style = Stroke(width = 3.5f)
        )
        drawCircle(
            color = LavenderAccent,
            radius = 12f,
            center = Offset(centerX, centerY)
        )
    }
}
