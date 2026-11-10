package com.swarmdroid.app.core.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "conversations")
data class ConversationEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val role: String, // "user" or "assistant"
    val content: String,
    val agentRole: String? = null,
    val companionEmotion: String = "IDLE",
    val timestamp: Long = System.currentTimeMillis()
)

@Entity(tableName = "agents")
data class AgentEntity(
    @PrimaryKey val role: String,
    val name: String,
    val description: String,
    val currentStatus: String = "IDLE",
    val modelName: String = "default",
    val providerName: String = "gemini",
    val isDynamic: Boolean = false,
    val allowedToolsJson: String = "[]"
)

@Entity(tableName = "tasks")
data class TaskEntity(
    @PrimaryKey val taskId: String,
    val parentId: String? = null,
    val assignedAgent: String,
    val description: String,
    val state: String, // "PENDING", "RUNNING", "WAITING_FOR_APPROVAL", "COMPLETED", "FAILED"
    val resultJson: String? = null,
    val error: String? = null,
    val approvalPrompt: String? = null,
    val createdAt: Long = System.currentTimeMillis(),
    val completedAt: Long? = null
)

@Entity(tableName = "memories")
data class MemoryEntity(
    @PrimaryKey val id: String,
    val category: String, // "SHORT_TERM", "LONG_TERM", "AGENT_PRIVATE", "SHARED"
    val key: String,
    val content: String,
    val tagsJson: String = "[]",
    val provenance: String = "system",
    val timestamp: Long = System.currentTimeMillis()
)

@Entity(tableName = "audit_logs")
data class AuditLogEntity(
    @PrimaryKey val entryId: String,
    val agentId: String,
    val actionType: String,
    val detailsJson: String,
    val status: String,
    val timestamp: Long = System.currentTimeMillis()
)
