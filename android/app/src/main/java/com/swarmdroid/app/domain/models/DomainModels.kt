package com.swarmdroid.app.domain.models

data class AgentInfo(
    val role: String,
    val name: String,
    val description: String,
    val currentStatus: String = "IDLE", // "IDLE", "THINKING", "WORKING", "WAITING_APPROVAL", "COMPLETED", "ERROR"
    val modelName: String = "default",
    val providerName: String = "gemini",
    val isDynamic: Boolean = false,
    val allowedTools: List<String> = emptyList()
)

data class SwarmTaskItem(
    val taskId: String,
    val assignedAgent: String,
    val description: String,
    val state: String, // "PENDING", "RUNNING", "WAITING_FOR_APPROVAL", "COMPLETED", "FAILED"
    val approvalPrompt: String? = null,
    val draftJson: String? = null
)

data class SwarmGraphNode(
    val id: String,
    val agent: String,
    val description: String,
    val state: String
)

data class SwarmGraphEdge(
    val from: String,
    val to: String
)

data class SwarmGraphData(
    val nodes: List<SwarmGraphNode> = emptyList(),
    val edges: List<SwarmGraphEdge> = emptyList()
)
