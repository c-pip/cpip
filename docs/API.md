# SwarmDroid — API Specification

The SwarmDroid backend exposes both a RESTful API and a high-performance WebSocket streaming gateway for real-time interaction between Android devices and the multi-agent swarm.

---

## 1. REST Endpoints

### 1.1 Chat & Swarm Execution
- **`POST /api/chat`**
  - **Description:** Submit a user prompt to the Master Agent for decomposition, planning, swarm collaboration, and response synthesis.
  - **Request Body:**
    ```json
    {
      "prompt": "Research the latest Android AI frameworks and draft an X post"
    }
    ```
  - **Response (200 OK):**
    ```json
    {
      "status": "COMPLETED",
      "companion_emotion": "CELEBRATING",
      "response_text": "Here is what the swarm accomplished...",
      "subtask_results": [
        {
          "agent": "BrowserAgent",
          "task": "Gather relevant information...",
          "result": { "summary": "..." }
        }
      ],
      "approvals_pending": [],
      "graph": {
        "nodes": [...],
        "edges": [...]
      },
      "dag_id": "dag_1731248000"
    }
    ```

### 1.2 Agents & Dynamic Studio
- **`GET /api/agents`**
  - **Description:** List all active agents in the swarm (core + dynamic) with their current state, model, and allowed tools.
- **`POST /api/agents/dynamic`**
  - **Description:** Dynamically instantiate a new specialized agent with strict sandboxing and tool allowlisting.
  - **Request Body:**
    ```json
    {
      "name": "Documentation Architect",
      "role": "DocumentationAgent",
      "description": "Generates technical architecture docs",
      "system_instructions": "You write clean, structured Markdown specifications.",
      "requested_tools": ["web_search", "fetch_url"],
      "model_name": "default",
      "provider_name": "gemini"
    }
    ```

### 1.3 Human Approvals
- **`POST /api/tasks/approval`**
  - **Description:** Authorize or reject a pending sensitive task action.
  - **Request Body:**
    ```json
    {
      "task_id": "task_a1b2c3d4",
      "approved": true
    }
    ```

### 1.4 AI Model Management
- **`GET /api/models`**
  - **Description:** View status of configured AI providers (Gemini, OpenAI, Anthropic, OpenRouter, Ollama, Custom).
- **`POST /api/models/configure`**
  - **Description:** Update API keys, base URLs, or active models.
- **`POST /api/models/test`**
  - **Description:** Perform real connectivity health checks against configured providers.

### 1.5 Memory & Knowledge
- **`GET /api/memory`**
  - **Description:** List stored memories with provenance tags.
- **`GET /api/memory/search?q={query}`**
  - **Description:** Semantic vector search using cosine similarity over memory embeddings.
- **`DELETE /api/memory/{id}`**
  - **Description:** Permanently delete a memory record.

### 1.6 Security & Audit
- **`GET /api/security/audit`**
  - **Description:** Retrieve append-only security logs, tool executions, and prompt injection defense alerts.

---

## 2. WebSocket Real-time Protocol

- **Endpoint:** `ws://{host}:{port}/ws`

### Outgoing Server Events (to Android Client)
```json
{
  "type": "TASK_STARTED",
  "data": {
    "task_id": "task_123",
    "agent": "BrowserAgent",
    "description": "Searching DuckDuckGo for Jetpack Compose 3D..."
  }
}
```
```json
{
  "type": "TASK_APPROVAL_REQUIRED",
  "data": {
    "task_id": "task_456",
    "agent": "SocialMediaAgent",
    "prompt": "Approve publishing this X post?",
    "draft": {
      "platform": "X",
      "content": "Excited to share SwarmDroid!"
    }
  }
}
```
```json
{
  "type": "TASK_COMPLETED",
  "data": {
    "task_id": "task_123",
    "agent": "BrowserAgent",
    "result": { "summary": "Found 4 references..." }
  }
}
```
```json
{
  "type": "SWARM_COMPLETED",
  "data": {
    "graph": { "nodes": [...], "edges": [...] }
  }
}
```

### Incoming Client Events (from Android Client)
```json
{
  "type": "APPROVAL",
  "task_id": "task_456",
  "approved": true
}
```
