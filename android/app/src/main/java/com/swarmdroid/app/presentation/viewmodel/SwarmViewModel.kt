package com.swarmdroid.app.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.swarmdroid.app.character.CharacterEmotion
import com.swarmdroid.app.core.database.SwarmDatabase
import com.swarmdroid.app.core.database.entities.ConversationEntity
import com.swarmdroid.app.core.network.SwarmApiClient
import com.swarmdroid.app.core.network.SwarmWebSocketClient
import com.swarmdroid.app.device.DeviceIntegrationManager
import com.swarmdroid.app.domain.models.*
import com.swarmdroid.app.security.SecurityManager
import com.swarmdroid.app.voice.VoiceInteractionManager
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import org.json.JSONObject

class SwarmViewModel(
    private val database: SwarmDatabase,
    private val apiClient: SwarmApiClient,
    private val webSocketClient: SwarmWebSocketClient,
    val voiceManager: VoiceInteractionManager,
    val deviceManager: DeviceIntegrationManager,
    val securityManager: SecurityManager
) : ViewModel() {

    private val _currentEmotion = MutableStateFlow(CharacterEmotion.IDLE)
    val currentEmotion: StateFlow<CharacterEmotion> = _currentEmotion.asStateFlow()

    private val _agents = MutableStateFlow<List<AgentInfo>>(emptyList())
    val agents: StateFlow<List<AgentInfo>> = _agents.asStateFlow()

    private val _tasks = MutableStateFlow<List<SwarmTaskItem>>(emptyList())
    val tasks: StateFlow<List<SwarmTaskItem>> = _tasks.asStateFlow()

    private val _graphData = MutableStateFlow(SwarmGraphData())
    val graphData: StateFlow<SwarmGraphData> = _graphData.asStateFlow()

    val conversations: Flow<List<ConversationEntity>> = database.conversationDao().getAllConversations()

    private val _pendingApproval = MutableStateFlow<SwarmTaskItem?>(null)
    val pendingApproval: StateFlow<SwarmTaskItem?> = _pendingApproval.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    init {
        initDefaultAgents()
        connectWebSocket()
        observeVoiceInput()
    }

    private fun initDefaultAgents() {
        val defaultList = listOf(
            AgentInfo("MasterAgent", "Aegis Prime", "Swarm Coordinator & Task Planner", "IDLE"),
            AgentInfo("BrowserAgent", "Aura Browser", "Web extraction & live search", "IDLE"),
            AgentInfo("CommunicationAgent", "Echo Communicator", "Emails & drafted responses", "IDLE"),
            AgentInfo("CodingAgent", "ByteForge Coder", "Code generation & verification", "IDLE"),
            AgentInfo("SocialMediaAgent", "Nexus Social", "Social posts & calendars", "IDLE"),
            AgentInfo("DeviceAgent", "DroidLink Controller", "Android system intents & apps", "IDLE"),
            AgentInfo("ResearchAgent", "Chronos Researcher", "Deep multi-source research", "IDLE"),
            AgentInfo("MemoryAgent", "Mnemosyne Memory", "Semantic search & memory storage", "IDLE"),
            AgentInfo("SecurityAgent", "Aegis Guardian", "Prompt defense & privacy shield", "IDLE")
        )
        _agents.value = defaultList
    }

    private fun connectWebSocket() {
        webSocketClient.connect()
        viewModelScope.launch {
            webSocketClient.events.collect { event ->
                handleWebSocketEvent(event.type, event.data)
            }
        }
    }

    private fun observeVoiceInput() {
        viewModelScope.launch {
            voiceManager.recognizedText.collect { text ->
                if (text.isNotBlank()) {
                    sendUserPrompt(text)
                }
            }
        }
    }

    private fun handleWebSocketEvent(type: String, data: JSONObject) {
        when (type) {
            "SWARM_STARTED" -> {
                _currentEmotion.value = CharacterEmotion.WORKING
            }
            "TASK_STARTED" -> {
                val taskId = data.optString("task_id")
                val agent = data.optString("agent")
                val desc = data.optString("description")
                updateAgentStatus(agent, "WORKING")
                addTask(SwarmTaskItem(taskId, agent, desc, "RUNNING"))
            }
            "TASK_COMPLETED" -> {
                val taskId = data.optString("task_id")
                val agent = data.optString("agent")
                updateAgentStatus(agent, "IDLE")
                updateTaskState(taskId, "COMPLETED")
            }
            "TASK_APPROVAL_REQUIRED" -> {
                val taskId = data.optString("task_id")
                val agent = data.optString("agent")
                val prompt = data.optString("prompt")
                val draft = data.optJSONObject("draft")?.toString(2)
                val item = SwarmTaskItem(taskId, agent, "Approval Required", "WAITING_FOR_APPROVAL", prompt, draft)
                _pendingApproval.value = item
                _currentEmotion.value = CharacterEmotion.LISTENING
                updateAgentStatus(agent, "WAITING_APPROVAL")
            }
            "SWARM_COMPLETED" -> {
                _currentEmotion.value = CharacterEmotion.CELEBRATING
            }
        }
    }

    fun sendUserPrompt(prompt: String) {
        if (prompt.isBlank()) return
        viewModelScope.launch {
            _isLoading.value = true
            _currentEmotion.value = CharacterEmotion.THINKING

            // Record user message in DB
            database.conversationDao().insert(
                ConversationEntity(role = "user", content = prompt)
            )

            try {
                // Call backend API
                val response = apiClient.sendChatPrompt(prompt)
                val emotionStr = response.optString("companion_emotion", "HAPPY")
                val responseText = response.optString("response_text", "Tasks processed successfully.")

                val emotion = try {
                    CharacterEmotion.valueOf(emotionStr)
                } catch (e: Exception) {
                    CharacterEmotion.HAPPY
                }

                _currentEmotion.value = emotion

                // Record assistant reply in DB
                database.conversationDao().insert(
                    ConversationEntity(
                        role = "assistant",
                        content = responseText,
                        agentRole = "MasterAgent",
                        companionEmotion = emotionStr
                    )
                )

                // Speak via TTS
                voiceManager.speak(responseText)

            } catch (e: Exception) {
                // Handle offline or error gracefully
                _currentEmotion.value = CharacterEmotion.ERROR
                val errMsg = "Swarm completed locally: ${e.localizedMessage ?: "Network connection error"}"
                database.conversationDao().insert(
                    ConversationEntity(
                        role = "assistant",
                        content = errMsg,
                        companionEmotion = "ERROR"
                    )
                )
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun triggerVoiceQuery() {
        _currentEmotion.value = CharacterEmotion.LISTENING
        voiceManager.startListening()
    }

    fun setEmotion(emotion: CharacterEmotion) {
        _currentEmotion.value = emotion
    }

    fun approvePendingTask(approved: Boolean) {
        val task = _pendingApproval.value ?: return
        viewModelScope.launch {
            try {
                apiClient.submitApproval(task.taskId, approved)
                webSocketClient.sendApproval(task.taskId, approved)
            } catch (e: Exception) {
                // Fallback
            }
            _pendingApproval.value = null
            _currentEmotion.value = if (approved) CharacterEmotion.HAPPY else CharacterEmotion.IDLE
        }
    }

    fun createDynamicAgent(role: String, name: String, desc: String, instructions: String, tools: List<String>) {
        viewModelScope.launch {
            try {
                apiClient.createDynamicAgent(role, name, desc, instructions, tools)
            } catch (e: Exception) {
                // Local fallback
            }
            val newAgent = AgentInfo(role, name, desc, "IDLE", isDynamic = true, allowedTools = tools)
            _agents.value = _agents.value + newAgent
        }
    }

    private fun updateAgentStatus(role: String, status: String) {
        _agents.value = _agents.value.map {
            if (it.role == role) it.copy(currentStatus = status) else it
        }
    }

    private fun addTask(task: SwarmTaskItem) {
        _tasks.value = listOf(task) + _tasks.value.filter { it.taskId != task.taskId }
    }

    private fun updateTaskState(taskId: String, state: String) {
        _tasks.value = _tasks.value.map {
            if (it.taskId == taskId) it.copy(state = state) else it
        }
    }

    override fun onCleared() {
        super.onCleared()
        webSocketClient.disconnect()
        voiceManager.release()
    }
}
