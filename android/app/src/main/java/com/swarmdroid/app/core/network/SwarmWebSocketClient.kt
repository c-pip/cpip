package com.swarmdroid.app.core.network

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import okhttp3.*
import org.json.JSONObject
import java.util.concurrent.TimeUnit

data class SwarmWebSocketEvent(
    val type: String,
    val data: JSONObject
)

class SwarmWebSocketClient(private val wsUrl: String = "ws://10.0.2.2:8000/ws") {
    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS)
        .build()
        
    private var webSocket: WebSocket? = null
    private val _events = MutableSharedFlow<SwarmWebSocketEvent>(replay = 1)
    val events: SharedFlow<SwarmWebSocketEvent> = _events.asSharedFlow()

    fun connect() {
        if (webSocket != null) return
        val request = Request.Builder().url(wsUrl).build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json = JSONObject(text)
                    val type = json.optString("type", "UNKNOWN")
                    val data = json.optJSONObject("data") ?: JSONObject()
                    _events.tryEmit(SwarmWebSocketEvent(type, data))
                } catch (e: Exception) {
                    // Ignore parse error
                }
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                this@SwarmWebSocketClient.webSocket = null
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                this@SwarmWebSocketClient.webSocket = null
            }
        })
    }

    fun disconnect() {
        webSocket?.close(1000, "Client disconnect")
        webSocket = null
    }

    fun sendApproval(taskId: String, approved: Boolean) {
        val payload = JSONObject().apply {
            put("type", "APPROVAL")
            put("task_id", taskId)
            put("approved", approved)
        }
        webSocket?.send(payload.toString())
    }
}
