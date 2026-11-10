# SwarmDroid v1.0.0 Release 🤖✨

> *"One companion. An entire swarm of intelligence."*

We are thrilled to present the initial official release of **SwarmDroid** — an autonomous multi-agent AI ecosystem for Android with Directed Acyclic Graph (DAG) task orchestration, hardware-backed encryption, and real Android device integrations.

---

## 🪙 Contract Address (CA) Notice
- **Status:** `CA Soon Available`
- **Notice:** The official token smart contract address will be announced **exclusively** on this GitHub repository and the [official website](https://alaika-cyber.github.io/swarmdroid-/). Beware of fake tokens, copycats, or impersonators.

---

## 📦 Release Assets
- **Deliverable:** `app-debug.apk` (SwarmDroid Android Native Client)
- **Version:** `1.0.0`
- **File Size:** `18.5 MB` (19,074,393 bytes)
- **Target OS:** Android 8.0+ (API Level 26–34)
- **SHA-256 Checksum:** `038c27495ab00b69f4b0aabfa21bbf03fdccea97e2ee080bc495ab892a4fd5c3`

---

## 🌟 Key Features in v1.0.0

### 1. Autonomous Multi-Agent Swarm Engine
- **Master Agent (Aegis Prime):** Deconstructs unstructured natural-language requests into topological DAG task dependency graphs, resolving subtasks with bounded concurrency.
- **8 Specialized Agents:**
  - `BrowserAgent` (Aura Browser): Web search and page extraction.
  - `CommunicationAgent` (Echo Communicator): Email and message drafting with strict human-in-the-loop approvals.
  - `CodingAgent` (ByteForge): Kotlin/Python generation, AST syntax inspection, and safe sandbox execution.
  - `SocialMediaAgent` (Nexus): Social content creation and calendars with approval gates.
  - `DeviceAgent` (DroidLink): Approved Android actions (app launcher, text-to-speech, system settings).
  - `ResearchAgent` (Chronos): Multi-source cross-verification and structured notes.
  - `MemoryAgent` (Mnemosyne): Semantic retrieval via cosine-similarity vector embeddings.
  - `SecurityAgent` (Aegis Guardian): Prompt injection scanning and secret redaction.
- **Dynamic Agent Studio:** Spawns new sandboxed agents on-the-fly when custom capabilities are needed.

### 2. Defense-in-Depth Mobile Security
- **Android Keystore AES-256-GCM:** All AI provider credentials (Gemini, OpenAI, Anthropic Claude, OpenRouter, Ollama) are hardware-encrypted on-device.
- **Human Approval Modal:** High-consequence actions (emails, posts, system configurations) require explicit user confirmation before execution.
- **Local SQLite Room DB:** Private user memories are stored locally on-device with full user-controlled deletion.

### 3. Native Android Architecture
- **Tech Stack:** Kotlin 2.1.0, Jetpack Compose Material 3, Kotlin Coroutines, StateFlow, Room Database, WorkManager.
- **Backend:** FastAPI, WebSockets, Python 3.10+ async task engine.

---

## 📱 Installation Instructions
1. Download `app-debug.apk` from the Assets below.
2. Transfer to your Android device (or download directly on your phone).
3. If prompted, allow "Install from Unknown Sources" in Android Settings.
4. Open **SwarmDroid** and enter your preferred AI model API keys securely into the Keystore.

---

## 🌐 Official Links
- **Website:** [https://alaika-cyber.github.io/swarmdroid-/](https://alaika-cyber.github.io/swarmdroid-/)
- **Repository:** [alaika-cyber/swarmdroid-](https://github.com/alaika-cyber/swarmdroid-)
