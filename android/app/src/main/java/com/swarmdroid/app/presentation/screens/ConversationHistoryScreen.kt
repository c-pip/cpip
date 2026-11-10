package com.swarmdroid.app.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.swarmdroid.app.core.database.entities.ConversationEntity
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

@Composable
fun ConversationHistoryScreen(
    viewModel: SwarmViewModel,
    modifier: Modifier = Modifier
) {
    val messages by viewModel.conversations.collectAsState(initial = emptyList())

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
    ) {
        Text(
            text = "Conversation & Swarm History",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = SoftWhite
        )
        Text(
            text = "Full trace of user prompts, task orchestrations, and companion syntheses.",
            style = MaterialTheme.typography.bodyMedium,
            color = DimGray
        )

        Spacer(modifier = Modifier.height(16.dp))

        if (messages.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "No conversations yet. Tap the 3D companion or ask a question!",
                    style = MaterialTheme.typography.bodyMedium,
                    color = DimGray
                )
            }
        } else {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                items(messages) { msg ->
                    ConversationBubble(msg)
                }
            }
        }
    }
}

@Composable
fun ConversationBubble(msg: ConversationEntity) {
    val isUser = msg.role == "user"

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        Surface(
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (isUser) 16.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 16.dp
            ),
            color = if (isUser) SurfaceVariantDark else SurfaceCard,
            modifier = Modifier.widthIn(max = 320.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                if (!isUser) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(text = "🤖 SwarmDroid", style = MaterialTheme.typography.labelSmall, color = ElectricCyan)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "(${msg.companionEmotion})",
                            style = MaterialTheme.typography.labelSmall,
                            color = LavenderAccent,
                            fontSize = 10.sp
                        )
                    }
                    Spacer(modifier = Modifier.height(6.dp))
                }
                Text(
                    text = msg.content,
                    style = MaterialTheme.typography.bodyLarge,
                    color = SoftWhite
                )
            }
        }
    }
}
