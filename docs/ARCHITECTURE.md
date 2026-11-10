# SwarmDroid — System Architecture

> **"One companion. An entire swarm of intelligence."**

SwarmDroid is an advanced multi-agent AI ecosystem for Android centered around an adorable, fully animated 3D companion robot that visually and emotionally communicates the active intelligence of a collaborative swarm of specialized AI agents.

---

## 1. Architectural Philosophy

Traditional AI assistants present either a static chat box or a simple text-in, text-out interface that hides whether anything is happening behind a single spinning loader. 

SwarmDroid changes this paradigm:
1. **Visual Empathy & Transparency:** The user interacts with an adorable 3D mascot that breathes, blinks, talks, reacts emotionally, and directly reflects what the background agents are doing.
2. **True Swarm Collaboration:** Complex goals are solved by specialized agents collaborating in a Directed Acyclic Graph (DAG) task engine.
3. **Dynamic Capability Spawning:** When a capability is absent, the swarm dynamically instantiates a new sandboxed agent template.
4. **Android Native Precision:** Real device capabilities (TTS, STT, app launching, intent sharing, notifications, camera/document picking) operating under strict human-in-the-loop approvals.
5. **Security by Design:** Android Keystore hardware-backed encryption, prompt injection shields, tool allowlisting, and secret redaction.

---

## 2. System Architecture Diagram

```mermaid
flowchart TD
    subgraph Android_App["Android Application (Kotlin + Jetpack Compose)"]
        UI["Modern Dark Matte UI\n(Material 3 + Compose)"]
        
        subgraph Visual_Systems["Visual & Emotional Systems"]
            GLView["Character3DView\n(OpenGL ES 3.0 / GLSurfaceView)"]
            AnimSM["AnimationStateMachine\n(14 States: Breathing, Blinking, Lip-sync)"]
            MascotModel["SwarmDroid Mascot Geometry\n(PBR Shading, Emissive Cyan/Lavender)"]
            SwarmVis["SwarmVisualizerView\n(Animated Canvas Node Graph)"]
        end
        
        subgraph Interaction_Services["Interaction & Integration Services"]
            VoiceEngine["VoiceInteractionManager\n(STT, TTS & Realtime Audio VAD)"]
            DeviceBridge["DeviceIntegrationManager\n(App Launch, Share, System Settings)"]
            FloatingService["FloatingCompanionService\n(Overlay Foreground Service)"]
            SecurityVault["SecurityManager\n(Android Keystore AES-256)"]
        end
        
        subgraph Local_Storage["Local Storage Layer"]
            RoomDB["Room Database\n(Conversations, Tasks, Memories, Audit)"]
        end

        UI --> GLView
        GLView --> AnimSM
        AnimSM --> MascotModel
        UI --> SwarmVis
        UI --> VoiceEngine
        UI --> FloatingService
        UI --> DeviceBridge
        UI --> SecurityVault
        UI --> RoomDB
    end

    subgraph Transport_Layer["Network Transport Layer"]
        WS["WebSocket Streamer\n(OkHttp <-> FastAPI /ws)"]
        REST["REST API Client\n(OkHttp <-> FastAPI /api/*)"]
    end

    Android_App <--> Transport_Layer

    subgraph Backend_Engine["Swarm Backend Engine (Python + FastAPI)"]
        Master["Master Agent (Aegis Prime)\n(Decomposition, DAG Planning & Synthesis)"]
        ExecEngine["ExecutionEngine\n(Bounded Concurrency, DAG, Retries, Timeouts)"]
        
        subgraph Agents_Roster["Specialized Swarm Agents"]
            Browser["Browser Agent (Aura Browser)"]
            Comm["Communication Agent (Echo Communicator)"]
            Coder["Coding Agent (ByteForge Coder)"]
            Social["Social Media Agent (Nexus Social)"]
            Device["Device Agent (DroidLink Controller)"]
            Research["Research Agent (Chronos Researcher)"]
            Memory["Memory Agent (Mnemosyne Memory)"]
            Security["Security Agent (Aegis Guardian)"]
            Dynamic["DynamicAgentManager\n(Template Validation & Sandbox)"]
        end
        
        subgraph Memory_System["Memory & Semantic Index"]
            MemStore["MemoryStore\n(SQLite + Short/Long/Shared)"]
            VecIdx["VectorIndex\n(Cosine Similarity & Semantic Search)"]
        end

        Master --> ExecEngine
        ExecEngine --> Agents_Roster
        Agents_Roster <--> Memory_System
        Agents_Roster --> Security
    end

    subgraph AI_Providers["Configurable AI Providers"]
        Gemini["Google Gemini (2.0 Flash)"]
        OpenAI["OpenAI (GPT-4o)"]
        Anthropic["Anthropic (Claude 3.5 Sonnet)"]
        Ollama["Ollama (Local Models)"]
        OpenRouter["OpenRouter / Custom Endpoints"]
    end

    Backend_Engine --> AI_Providers
```

---

## 3. Character 3D & Animation Engine

### 3.1 Mascot Geometry and Design
The companion mascot is an original cute humanoid robot:
- **Head:** Smooth spherical white ceramic finish (`#F0F4F8`).
- **Visor:** Dark curved glossy glass (`#0D0F14`) with real-time specular highlights.
- **Eyes:** Dual expressive glowing electric cyan LED eyes (`#00F5D4`) capable of blinking, pupil dilation, smiling slits, and scan animations.
- **Torso:** Compact chassis with metallic lavender plating (`#B892FF`) and a central glowing swarm reactor orb.
- **Antennas:** Levitating ear pods with synchronized twitch and audio-reactive tilt.
- **Thruster:** Levitating anti-gravity torus ring with spinning cyan particle trails.

### 3.2 14 Animation States
1. `IDLE`: Gentle breathing sine wave, levitation bobbing, natural periodic eye blinks.
2. `HAPPY`: Bouncing excitement, smiling curved eye slits, ear twitch.
3. `THINKING`: Inquisitive head tilt, eyes scanning left to right, pulsing cyan antenna orb.
4. `LISTENING`: Forward attentive posture, audio-reactive soundwave response.
5. `SPEAKING`: Visor mouth waveform modulation synchronized with speech amplitude.
6. `WORKING`: Focused forward lean, multi-agent status halo, orbiting particle ring.
7. `WALKING`: Procedural walk cycle with rhythmic foot/thruster tilts.
8. `RUNNING`: Dynamic forward lean, speed lines, animated thruster flare.
9. `WAVING`: Right hand raised greeting cycle, friendly nod.
10. `CELEBRATING`: Triumphant jump/spin, double hand raise, celebratory glow flare.
11. `SLEEPING`: Low float altitude, closed eye slits, slow rhythmic breathing.
12. `ERROR`: Puzzled head scratch, amber eye flicker, tilted question posture.
13. `SURPRISED`: Sudden jump-back, dilated wide eyes `(o.o)`, expanding aura.
14. `SAD`: Drooped ears, downward gaze, dim slow-pulsing glow.

---

## 4. Multi-Agent Orchestration & Task DAG

When a user submits a prompt:
1. **Prompt Defense:** `SecurityAgent` scans for prompt injection and jailbreak attempts.
2. **Decomposition:** `MasterAgent` evaluates the intent and generates a `TaskDAG` with subtasks, assigned roles, and dependencies.
3. **Capability Gap Check:** If a required role is absent (e.g. `DocumentationAgent`), `DynamicAgentManager` creates a validated, scoped agent instance.
4. **Asynchronous Execution:** `ExecutionEngine` executes ready tasks in parallel within bounded concurrency limits.
5. **Human Approval:** If an agent attempts a sensitive action (e.g. `send_email`, `post_social_media`), execution halts into `WAITING_FOR_APPROVAL` until the user confirms.
6. **Synthesis:** `MasterAgent` reviews the results, produces the response, and sets the companion's 3D emotion to `CELEBRATING`.
