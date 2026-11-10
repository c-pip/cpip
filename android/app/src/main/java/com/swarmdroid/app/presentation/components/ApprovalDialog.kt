package com.swarmdroid.app.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.domain.models.SwarmTaskItem

@Composable
fun ApprovalDialog(
    task: SwarmTaskItem,
    onApprove: (String) -> Unit,
    onReject: (String) -> Unit,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(20.dp),
            color = SurfaceCard,
            tonalElevation = 8.dp,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.Start
            ) {
                // Header with Warning Shield Badge
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🛡️", fontSize = 24.sp)
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = "Human Approval Required",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = SoftWhite
                        )
                        Text(
                            text = "Agent: ${task.assignedAgent}",
                            style = MaterialTheme.typography.labelSmall,
                            color = LavenderAccent
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Prompt description
                Text(
                    text = task.approvalPrompt ?: "This action modifies device state or publishes external data.",
                    style = MaterialTheme.typography.bodyLarge,
                    color = SoftWhite
                )

                if (!task.draftJson.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = SurfaceVariantDark,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = task.draftJson,
                            style = MaterialTheme.typography.bodyMedium,
                            color = ElectricCyan,
                            modifier = Modifier.padding(12.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Action Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    OutlinedButton(
                        onClick = { onReject(task.taskId) },
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = StatusError),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text("Reject")
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Button(
                        onClick = { onApprove(task.taskId) },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = ElectricCyan,
                            contentColor = BackgroundDark
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text("Approve Action", fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }
    }
}
