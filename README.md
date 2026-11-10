# SwarmDroid 🤖✨

> *"One companion. An entire swarm of intelligence."*

**SwarmDroid** is an advanced multi-agent AI ecosystem for Android featuring an adorable, fully animated 3D AI companion mascot. 

Rather than presenting users with a generic chatbot or a static loading spinner, SwarmDroid provides an interactive 3D robot companion that **blinks, breathes, walks, waves, talks, and reacts emotionally**, visually communicating what a collaborative swarm of specialized AI agents is doing in real-time.

---

## 🌟 Key Features

- **Cute 3D Companion Mascot:**
  - Real-time 3D rendering using **OpenGL ES 3.0 / GLSurfaceView** seamlessly embedded in **Jetpack Compose**.
  - PBR metallic-roughness lighting, specular highlights, and emissive electric cyan/lavender glow.
  - **14 Full Animation States:** `IDLE`, `HAPPY`, `THINKING`, `LISTENING`, `SPEAKING`, `WORKING`, `WALKING`, `RUNNING`, `WAVING`, `CELEBRATING`, `SLEEPING`, `ERROR`, `SURPRISED`, `SAD`.
  - Natural secondary procedural animation: breathing sine wave, periodic eye blinks, ear twitches, hover bobbing, and speech-synchronized lip-sync waveform modulation.
  - Interactive touch: Tap triggers emotional celebration; drag rotates companion in 3D.
  - **Floating Companion Mode:** Android Foreground Service with system overlay (`TYPE_APPLICATION_OVERLAY`) allowing the companion to float over any app!

- **Multi-Agent Intelligence Engine:**
  - **Master Agent (Aegis Prime):** Analyzes natural-language requests, decomposes goals into a Directed Acyclic Graph (DAG) with explicit dependencies, delegates to agents, and presents final results through the 3D companion.
  - **Specialized Agents:**
    - `BrowserAgent` (Aura Browser): Web research, search, and page content extraction.
    - `CommunicationAgent` (Echo Communicator): Email and message drafting with strict human approval gates.
    - `CodingAgent` (ByteForge Coder): Code analysis, generation, and safe restricted sandbox execution.
    - `SocialMediaAgent` (Nexus Social): Social post composition and calendars with human approval.
    - `DeviceAgent` (DroidLink Controller): Approved Android system actions (apps, settings, TTS, sharing).
    - `ResearchAgent` (Chronos Researcher): Deep multi-source fact-checking and structured report synthesis.
    - `MemoryAgent` (Mnemosyne Memory): Semantic context retrieval and memory management.
    - `SecurityAgent` (Aegis Guardian): Prompt injection defense, tool allowlists, and secret redaction.
  - **Dynamic Agent Creation:** When a novel capability is needed (e.g. `DocumentationAgent`), the Master Agent instantiates a new agent from an approved template with sandboxed tool scopes.
  - **Interactive Swarm Visualizer:** Real-time animated Compose Canvas node graph displaying the Master Agent at the center, orbiting specialized agents, glowing pulse lines, and moving data packets.

- **Security & Privacy by Design:**
  - Hardware-backed local credential encryption via **Android Keystore** (`EncryptedSharedPreferences`).
  - Strict **Human-in-the-Loop** confirmation for sensitive operations (sending emails, posting to social media, modifying system settings).
  - Multi-provider AI support: **Google Gemini, OpenAI, Anthropic Claude, Ollama (Local), OpenRouter, and Custom OpenAI-compatible endpoints**.
  - Zero silent data collection; inspectable and deletable Room SQLite memory store.

---

## 🏗️ Repository Architecture

```
SwarmDroid/
├── android/                        # Android Native Application
│   ├── app/
│   │   ├── src/main/java/com/swarmdroid/app/
│   │   │   ├── core/               # DI (AppContainer), Room DB, Theme, OkHttp
│   │   │   ├── character/          # 3D GLSurfaceView, 14-State Animation SM, Floating Service
│   │   │   ├── voice/              # SpeechRecognizer (STT) & TextToSpeech (TTS)
│   │   │   ├── device/             # Android Intent Bridge & System Capabilities
│   │   │   ├── security/           # Android Keystore EncryptedSharedPreferences
│   │   │   ├── domain/             # Domain Models (AgentInfo, SwarmTaskItem, SwarmGraph)
│   │   │   └── presentation/       # Compose Screens, SwarmVisualizerView, Navigation
│   │   ├── src/main/assets/        # 3D GLB Mascot Asset (swarmdroid_mascot.glb)
│   │   └── src/test/               # Android JUnit Unit Tests
│   ├── build.gradle.kts
│   └── settings.gradle.kts
│
├── backend/                        # Multi-Agent Python Backend
│   ├── api/                        # FastAPI REST endpoints (/chat, /agents, /tasks, /models)
│   ├── websocket/                  # Real-time WebSocket connection manager & event streaming
│   ├── orchestration/              # TaskDAG, ExecutionEngine, SwarmOrchestrator
│   ├── agents/                     # MasterAgent, 8 Core Agents, DynamicAgentManager
│   ├── models/                     # LLM Provider Abstraction (Gemini, OpenAI, Anthropic, Ollama)
│   ├── memory/                     # MemoryStore (SQLite) & VectorIndex (Cosine Similarity)
│   ├── tools/                      # WebSearch, FetchUrl, SandboxCode, DraftEmail, DeviceIntent
│   ├── security/                   # PromptDefense, SecretRedactor, PermissionScope, AuditLogger
│   └── main.py                     # FastAPI entrypoint
│
├── assets/                         # 3D Mascot Assets
│   ├── characters/swarmdroid_mascot.glb  # Valid glTF 2.0 Binary Model
│   └── generate_mascot_glb.py      # Binary GLB Procedural Generator
│
├── docs/                           # Architecture & Engineering Documentation
│   ├── ARCHITECTURE.md             # Complete Architecture Deep Dive
│   ├── PRD.md                      # Product Requirements Document
│   ├── SECURITY.md                 # Threat Model, Sandboxing & Keystore Encryption
│   ├── PRIVACY.md                  # Privacy, Minimum Privilege & Data Governance
│   └── API.md                      # REST & WebSocket API Specification
│
└── tests/                          # Test Suites
    ├── backend/                    # Python Backend & Orchestrator Pytest Suite
    └── android/                    # Android Unit Test Suite
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python:** 3.10+
- **Android SDK:** API 34+
- **JDK:** 21 LTS

### 2. Running the Multi-Agent Backend
```bash
# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Run the backend server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
The FastAPI documentation will be available at `http://localhost:8000/docs`.

### 3. Running Backend Tests
```bash
PYTHONPATH=. .venv/bin/pytest tests/backend/ -v
```

### 4. Building & Testing the Android Application
```bash
cd android
./gradlew testDebugUnitTest
```

---

## 🛡️ Security Verification
- **Prompt Injection Defense:** Scanned via `PromptDefense.evaluate()`.
- **Credential Protection:** Secrets redacted before logging using `SecretRedactor`.
- **Tool Allowlist:** Strict validation against `PermissionScope`.
- **Human Approval:** Sensitive tasks trigger `ApprovalDialog` on Android before execution.

---

## 📜 License
Apache License 2.0. Built with pride for Android and the autonomous multi-agent future.
