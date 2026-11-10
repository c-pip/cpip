# Contributing to SwarmDroid 🤖

Thank you for contributing to SwarmDroid! Whether you are designing new specialized agents, building Android UI features, crafting 3D animations, or enhancing security defenses, your contributions are welcome.

---

## 🛠️ Development Setup

### 1. Multi-Agent Backend (Python)
```bash
# Clone the repository
git clone https://github.com/your-username/swarmdroid.git
cd swarmdroid

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Run pytest suite
PYTHONPATH=. pytest tests/backend/ -v

# Start FastAPI dev server with live reload
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Android Native Application (Kotlin + Jetpack Compose)
- Install **Android Studio Ladybug (or newer)** with **Android SDK 34** and **JDK 21**.
- Open the `android/` directory in Android Studio.
- Run tests via terminal:
  ```bash
  cd android
  ./gradlew testDebugUnitTest
  ```
- Build APK:
  ```bash
  cd android
  ./gradlew assembleDebug
  ```

---

## 🧩 Adding a New Specialized Agent

1. Inherit from `BaseAgent` in `backend/agents/`:
   ```python
   from backend.agents.base_agent import BaseAgent

   class TranslationAgent(BaseAgent):
       def __init__(self, provider_name: str = "gemini"):
           super().__init__(
               name="Polyglot Translator",
               role="TranslationAgent",
               description="Specializes in multi-language context-aware translations.",
               system_prompt="You are SwarmDroid's Translation Agent. Translate text with nuanced cultural context.",
               provider_name=provider_name
           )

       async def process_task(self, task_id: str, description: str, context: dict) -> dict:
           self.current_status = "WORKING"
           translation = await self.call_llm(f"Translate: {description}")
           self.current_status = "IDLE"
           return {"status": "COMPLETED", "result": translation}
   ```
2. Register the agent in `backend/orchestration/swarm_orchestrator.py`.
3. Add unit test coverage in `tests/backend/test_backend.py`.

---

## 🎨 3D Mascot & Animations
- The mascot asset is stored at `assets/characters/swarmdroid_mascot.glb` and copied to `android/app/src/main/assets/characters/`.
- Regenerate or modify 3D primitives using `assets/generate_mascot_glb.py`.
- Animation parameters and states are controlled in `android/app/src/main/java/com/swarmdroid/app/character/AnimationStateMachine.kt`.

---

## 🛡️ Security Guidelines
- **Never hardcode secrets:** All credentials must be passed via environment variables or entered via the encrypted Android Keystore.
- **Sensitive actions require human approval:** Any tool that modifies device state, sends external messages, or deletes memories must be flagged in `PermissionScope.SENSITIVE_ACTIONS`.
- **Sanitize prompts:** Always validate inputs using `PromptDefense.evaluate()`.

---

## 📋 Pull Request Process
1. Create a feature branch: `git checkout -b feature/my-new-agent`.
2. Ensure all tests pass:
   ```bash
   ./scripts/run_tests.sh
   ```
3. Commit with clear, descriptive commit messages.
4. Submit a Pull Request targeting `main`.
