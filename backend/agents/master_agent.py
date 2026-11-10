"""
Master Agent for SwarmDroid
The Central Brain of the Swarm.
Decomposes user prompts into a structured DAG plan, detects missing agent capabilities,
creates dynamic agents when needed, and synthesizes final results with 3D companion emotion cues.
"""

from typing import Dict, Any, List, Optional
import json
import re
from .base_agent import BaseAgent
from .dynamic_agent_manager import DynamicAgentManager, DynamicAgentTemplate
from ..orchestration.task_graph import TaskDAG, SwarmTask, TaskState
from ..memory.memory_store import memory_store
from ..security.security_core import PromptDefense, audit_logger


class MasterAgent(BaseAgent):
    def __init__(self, dynamic_agent_mgr: DynamicAgentManager, provider_name: str = "gemini"):
        super().__init__(
            name="Aegis Prime",
            role="MasterAgent",
            description="The central intelligence orchestrator of SwarmDroid. Plans, delegates, and coordinates the swarm.",
            system_prompt=(
                "You are the Master Agent and brain of SwarmDroid. You analyze user instructions, "
                "decompose complex workflows into subtasks, assign them to specialized agents, "
                "synthesize multi-agent outputs, and visually communicate state via your 3D companion mascot."
            ),
            provider_name=provider_name
        )
        self.dynamic_agent_mgr = dynamic_agent_mgr

    async def plan_and_decompose(self, user_prompt: str, available_roles: List[str]) -> TaskDAG:
        """Analyzes user request and decomposes it into a Directed Acyclic Graph (DAG) of subtasks."""
        dag = TaskDAG()
        
        # 1. Security scan
        sec_eval = PromptDefense.evaluate(user_prompt)
        if not sec_eval.is_safe:
            # Create a security alert task
            sec_task = SwarmTask(
                assigned_agent="SecurityAgent",
                description=f"Block prompt injection attempt: {', '.join(sec_eval.flagged_reasons)}",
                priority=5
            )
            dag.add_task(sec_task)
            return dag
            
        # 2. Decomposition using LLM or structured heuristic planner
        clean_prompt = sec_eval.sanitized_input
        planner_instructions = (
            f"You are the SwarmDroid Task Planner.\n"
            f"Available Swarm Agent Roles: {json.dumps(available_roles)}\n"
            f"User Prompt: \"{clean_prompt}\"\n\n"
            "Break this request into a minimal list of actionable subtasks in JSON format.\n"
            "Each subtask must contain:\n"
            "- \"id\": string (e.g. \"t1\", \"t2\")\n"
            "- \"role\": string (choose from available roles, or suggest a new role name if missing capability)\n"
            "- \"description\": string (what this agent must achieve)\n"
            "- \"dependencies\": list of ids that must complete before this subtask runs\n\n"
            "Output ONLY a valid JSON array of objects, with no markdown code fences or conversational text."
        )
        
        plan_items = []
        try:
            llm_reply = await self.call_llm(planner_instructions)
            # Clean possible markdown fences
            json_text = re.sub(r"^```json\s*", "", llm_reply.strip())
            json_text = re.sub(r"^```\s*", "", json_text)
            json_text = re.sub(r"\s*```$", "", json_text)
            parsed = json.loads(json_text)
            if isinstance(parsed, list):
                plan_items = parsed
        except Exception:
            # Fallback heuristic decomposition if LLM is offline or not configured
            plan_items = self._heuristic_decompose(clean_prompt)
            
        # 3. Build DAG and ensure required agents exist
        task_id_map = {}
        for item in plan_items:
            role = item.get("role", "BrowserAgent")
            # If the role is missing from known roles, dynamically instantiate it!
            if role not in available_roles and not self.dynamic_agent_mgr.get_agent(role):
                try:
                    tmpl = DynamicAgentTemplate(
                        name=f"Auto-{role}",
                        role=role,
                        description=f"Dynamically generated agent to handle {item.get('description', '')}",
                        system_instructions=f"You are a specialized {role}. Complete assigned tasks accurately.",
                        requested_tools=["web_search", "fetch_url"]
                    )
                    self.dynamic_agent_mgr.create_agent(tmpl)
                except Exception as e:
                    # Fallback to BrowserAgent or ResearchAgent
                    role = "ResearchAgent"
                    
            task = SwarmTask(
                assigned_agent=role,
                description=item.get("description", clean_prompt),
                dependencies=[]
            )
            task_id_map[item.get("id", task.task_id)] = task.task_id
            dag.add_task(task)
            
        # Link mapped dependencies
        for item in plan_items:
            orig_id = item.get("id")
            if orig_id and orig_id in task_id_map:
                real_id = task_id_map[orig_id]
                real_task = dag.get_task(real_id)
                if real_task:
                    for dep in item.get("dependencies", []):
                        if dep in task_id_map:
                            real_task.dependencies.append(task_id_map[dep])
                            
        return dag

    def _heuristic_decompose(self, prompt: str) -> List[Dict[str, Any]]:
        """Reliable rule-based decomposition for common mobile workflows."""
        p_lower = prompt.lower()
        plan = []
        
        # Social media + research workflow
        if any(w in p_lower for w in ["tweet", "x post", "post on", "social media", "linkedin"]):
            plan.append({
                "id": "t1",
                "role": "BrowserAgent",
                "description": f"Research trending facts and insights for: {prompt}",
                "dependencies": []
            })
            plan.append({
                "id": "t2",
                "role": "SocialMediaAgent",
                "description": f"Draft social post based on findings: {prompt}",
                "dependencies": ["t1"]
            })
            return plan
            
        # Code generation / analysis workflow
        if any(w in p_lower for w in ["code", "script", "python", "kotlin", "debug", "function", "program"]):
            plan.append({
                "id": "t1",
                "role": "CodingAgent",
                "description": prompt,
                "dependencies": []
            })
            return plan
            
        # Email / message workflow
        if any(w in p_lower for w in ["email", "send mail", "draft message", "letter"]):
            plan.append({
                "id": "t1",
                "role": "CommunicationAgent",
                "description": prompt,
                "dependencies": []
            })
            return plan
            
        # Device action
        if any(w in p_lower for w in ["open app", "launch", "settings", "device", "speak", "read aloud"]):
            plan.append({
                "id": "t1",
                "role": "DeviceAgent",
                "description": prompt,
                "dependencies": []
            })
            return plan
            
        # Default: Browser + Research synthesis
        plan.append({
            "id": "t1",
            "role": "BrowserAgent",
            "description": f"Gather relevant information on: {prompt}",
            "dependencies": []
        })
        plan.append({
            "id": "t2",
            "role": "ResearchAgent",
            "description": f"Synthesize structured findings and answer: {prompt}",
            "dependencies": ["t1"]
        })
        return plan

    async def synthesize_final_response(self, user_prompt: str, dag: TaskDAG) -> Dict[str, Any]:
        """Reviews all subtask results, validates success, and generates companion presentation."""
        completed_results = []
        has_failures = False
        waiting_for_approval = False
        approval_details = []
        
        for task in dag.tasks.values():
            if task.state == TaskState.COMPLETED and task.result:
                completed_results.append({
                    "agent": task.assigned_agent,
                    "task": task.description,
                    "result": task.result
                })
            elif task.state == TaskState.WAITING_FOR_APPROVAL:
                waiting_for_approval = True
                approval_details.append({
                    "task_id": task.task_id,
                    "agent": task.assigned_agent,
                    "prompt": task.approval_prompt,
                    "draft": task.result.get("draft") if task.result else None
                })
            elif task.state == TaskState.FAILED:
                has_failures = True
                
        # Determine 3D Mascot emotion state
        if waiting_for_approval:
            companion_emotion = "LISTENING"
            speech_text = "I've prepared the work, but need your approval before proceeding with sensitive actions."
        elif has_failures:
            companion_emotion = "ERROR"
            speech_text = "One of our swarm agents encountered an issue completing a subtask."
        elif completed_results:
            companion_emotion = "CELEBRATING"
            # Synthesize final presentation
            try:
                synth_prompt = (
                    f"User Request: {user_prompt}\n"
                    f"Swarm Results:\n{json.dumps(completed_results, indent=2)}\n\n"
                    "Provide a warm, friendly, comprehensive response as SwarmDroid companion mascot. "
                    "Clearly present the results achieved by the swarm agents."
                )
                speech_text = await self.call_llm(synth_prompt)
            except Exception:
                # Fallback clean synthesis
                lines = [f"Here is what the swarm accomplished for: **{user_prompt}**\n"]
                for r in completed_results:
                    agent = r["agent"]
                    res = r["result"]
                    if "summary" in res:
                        lines.append(f"### {agent}\n{res['summary']}")
                    elif "solution" in res:
                        lines.append(f"### {agent}\n{res['solution']}")
                    elif "report" in res:
                        lines.append(f"### {agent}\n{res['report']}")
                    elif "draft" in res:
                        lines.append(f"### {agent}\n{json.dumps(res['draft'], indent=2)}")
                    else:
                        lines.append(f"### {agent}\n{json.dumps(res)}")
                speech_text = "\n\n".join(lines)
        else:
            companion_emotion = "THINKING"
            speech_text = "The swarm is currently working on your request."
            
        # Store in conversation memory
        memory_store.append_conversation(
            role="assistant",
            content=speech_text,
            agent_id=self.agent_id,
            metadata={"emotion": companion_emotion, "tasks_count": len(dag.tasks)}
        )
        
        return {
            "status": "WAITING_FOR_APPROVAL" if waiting_for_approval else ("FAILED" if has_failures else "COMPLETED"),
            "companion_emotion": companion_emotion,
            "response_text": speech_text,
            "subtask_results": completed_results,
            "approvals_pending": approval_details,
            "graph": dag.to_graph_data()
        }

    async def process_task(self, task_id: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"agent": self.role, "status": "COMPLETED"}
