package com.swarmdroid.app.core.network

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

class SwarmApiClient(private val baseUrl: String = "http://10.0.2.2:8000") {
    private val client = OkHttpClient.Builder().build()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    suspend fun sendChatPrompt(prompt: String): JSONObject = withContext(Dispatchers.IO) {
        val payload = JSONObject().apply { put("prompt", prompt) }
        val body = payload.toString().toRequestBody(jsonMediaType)
        val request = Request.Builder()
            .url("$baseUrl/api/chat")
            .post(body)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("HTTP ${response.code}: ${response.body?.string()}")
            JSONObject(response.body?.string() ?: "{}")
        }
    }

    suspend fun getAgents(): JSONArray = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$baseUrl/api/agents").get().build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("HTTP ${response.code}")
            JSONArray(response.body?.string() ?: "[]")
        }
    }

    suspend fun createDynamicAgent(role: String, name: String, description: String, instructions: String, tools: List<String>): JSONObject = withContext(Dispatchers.IO) {
        val payload = JSONObject().apply {
            put("role", role)
            put("name", name)
            put("description", description)
            put("system_instructions", instructions)
            put("requested_tools", JSONArray(tools))
        }
        val body = payload.toString().toRequestBody(jsonMediaType)
        val request = Request.Builder().url("$baseUrl/api/agents/dynamic").post(body).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("HTTP ${response.code}: ${response.body?.string()}")
            JSONObject(response.body?.string() ?: "{}")
        }
    }

    suspend fun submitApproval(taskId: String, approved: Boolean): JSONObject = withContext(Dispatchers.IO) {
        val payload = JSONObject().apply {
            put("task_id", taskId)
            put("approved", approved)
        }
        val body = payload.toString().toRequestBody(jsonMediaType)
        val request = Request.Builder().url("$baseUrl/api/tasks/approval").post(body).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("HTTP ${response.code}")
            JSONObject(response.body?.string() ?: "{}")
        }
    }

    suspend fun getModelStatus(): JSONObject = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$baseUrl/api/models").get().build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("HTTP ${response.code}")
            JSONObject(response.body?.string() ?: "{}")
        }
    }

    suspend fun configureModel(provider: String, apiKey: String, model: String): JSONObject = withContext(Dispatchers.IO) {
        val payload = JSONObject().apply {
            put("provider_name", provider)
            put("api_key", apiKey)
            put("default_model", model)
        }
        val body = payload.toString().toRequestBody(jsonMediaType)
        val request = Request.Builder().url("$baseUrl/api/models/configure").post(body).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("HTTP ${response.code}")
            JSONObject(response.body?.string() ?: "{}")
        }
    }
}
