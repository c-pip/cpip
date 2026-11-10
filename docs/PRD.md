# SwarmDroid — Product Requirements Document (PRD)

## 1. Product Vision
SwarmDroid is an intelligent mobile agent ecosystem for Android featuring an adorable, fully animated 3D AI companion mascot. It transforms traditional static chatbots into a living, collaborative AI swarm where specialized agents work together to execute complex user requests on Android.

---

## 2. Core Pillars
1. **One Companion. An Entire Swarm of Intelligence:** The user interacts with a single charming 3D robot character that serves as the visual identity, emotional anchor, and presentation layer of the underlying multi-agent engine.
2. **Transparent Collaboration:** The user watches specialized agents plan, converse, pass signals, and collaborate on an interactive node graph instead of waiting on a blind loading spinner.
3. **Dynamic Agent Evolution:** The swarm dynamically spawns new specialized agents when an unrepresented capability is required, bounded by strict sandbox permissions.
4. **Android Native Power:** Official integration with Android APIs for speech recognition, text-to-speech, app launching, sharing, file picking, and an optional floating overlay companion.
5. **Privacy and User Authority:** Sensitive operations strictly require human approval. Credentials remain encrypted in hardware via Android Keystore.

---

## 3. User Personas & Scenarios
- **The Mobile Builder / Power User:** Directs the swarm to research GitHub repositories, analyze code architecture, and synthesize launch checklists.
- **The Content Creator:** Dictates ideas via voice; the swarm conducts web research, extracts facts, drafts social posts for X/LinkedIn, and waits for user approval before publishing.
- **The Daily Communicator:** Drafts professional emails and context-rich messages, asks the companion to review tone, and approves actions with one tap.

---

## 4. Key Functional Requirements

### 4.1 3D Companion Mascot
- Original futuristic robot mascot (white ceramic shell, dark visor glass, glowing electric cyan eyes, metallic lavender chassis accents, levitating ear antennas, anti-gravity hover thruster).
- Real-time 3D rendering (OpenGL ES 3.0 / GLSurfaceView) with PBR lighting and emissive materials.
- All 14 animation states supported: `IDLE`, `HAPPY`, `THINKING`, `LISTENING`, `SPEAKING`, `WORKING`, `WALKING`, `RUNNING`, `WAVING`, `CELEBRATING`, `SLEEPING`, `ERROR`, `SURPRISED`, `SAD`.
- Interactive touch handling: Tapping triggers emotional reactions; dragging rotates in 3D.
- Floating overlay companion service (`SYSTEM_ALERT_WINDOW`).

### 4.2 Swarm Intelligence Engine
- **Master Agent (Aegis Prime):** Deconstructs natural language into a Directed Acyclic Graph (DAG) of subtasks, identifies dependencies, and presents syntheses.
- **Core Specialized Agents:**
  - `BrowserAgent`: Real-time web retrieval, extraction, and summarization.
  - `CommunicationAgent`: Prepares emails and messages; enforces human approval.
  - `CodingAgent`: Code generation, static analysis, and sandboxed execution.
  - `SocialMediaAgent`: Drafts social posts and content calendars with approval hooks.
  - `DeviceAgent`: Android intent execution (launch apps, open settings, TTS, share).
  - `ResearchAgent`: Multi-source synthesis, fact-checking, and structured reports.
  - `MemoryAgent`: Semantic retrieval, vector indexing, provenance, and deletion.
  - `SecurityAgent`: Prompt injection defense, tool allowlists, and secret redaction.
- **Dynamic Agent Studio:** Runtime instantiation of specialized agents with validated tool allowlists.

### 4.3 Human-in-the-Loop Approvals
- Sensitive actions (`send_email`, `post_social_media`, `modify_device_settings`, `execute_command`) immediately transition to `WAITING_FOR_APPROVAL`.
- Modal approval dialog displays action details and draft payload.
- Companion mascot adopts attentive `LISTENING` posture during approval.

### 4.4 Model & Memory Systems
- Configurable AI providers: Google Gemini, OpenAI, Anthropic Claude, Ollama (Local), OpenRouter, Custom endpoints.
- Android Keystore AES-256 encrypted credential storage.
- Hierarchical memory: Short-term conversation, long-term facts, agent-private, and shared memory with cosine similarity vector search.
