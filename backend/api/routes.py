"""
FastAPI REST and WebSocket Routes for SwarmDroid
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
import json
from pydantic import BaseModel
from ..orchestration.swarm_orchestrator import swarm_orchestrator
from ..models.provider_factory import provider_manager
from ..memory.memory_store import memory_store
from ..agents.dynamic_agent_manager import DynamicAgentTemplate
from ..websocket.connection_manager import ws_manager
from ..security.security_core import audit_logger

router = APIRouter()


# --- Chat & Swarm Execution ---
class ChatRequest(BaseModel):
    prompt: str


@router.post("/api/chat")
async def handle_chat(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    result = await swarm_orchestrator.handle_user_request(req.prompt)
    return result


# --- Agents Management & Dynamic Studio ---
@router.get("/api/agents")
async def list_agents():
    return [a.model_dump() for a in swarm_orchestrator.list_agent_states()]


@router.post("/api/agents/dynamic")
async def create_dynamic_agent(template: DynamicAgentTemplate):
    try:
        agent = swarm_orchestrator.dynamic_agent_mgr.create_agent(template)
        return {"status": "created", "agent": agent.get_state().model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Approvals for Sensitive Actions ---
class ApprovalRequest(BaseModel):
    task_id: str
    approved: bool


@router.post("/api/tasks/approval")
async def handle_task_approval(req: ApprovalRequest):
    success = await swarm_orchestrator.handle_approval(req.task_id, req.approved)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task {req.task_id} not found or not awaiting approval")
    return {"status": "success", "task_id": req.task_id, "approved": req.approved}


# --- Models & API Key Management ---
class ProviderConfigRequest(BaseModel):
    provider_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    enabled: Optional[bool] = None


@router.get("/api/models")
async def get_models_status():
    return provider_manager.list_status()


@router.post("/api/models/configure")
async def configure_model_provider(req: ProviderConfigRequest):
    cfg_dict = {}
    if req.api_key is not None:
        cfg_dict["api_key"] = req.api_key
    if req.base_url is not None:
        cfg_dict["base_url"] = req.base_url
    if req.default_model is not None:
        cfg_dict["default_model"] = req.default_model
    if req.enabled is not None:
        cfg_dict["enabled"] = req.enabled
    provider_manager.configure_provider(req.provider_name, cfg_dict)
    return {"status": "configured", "provider": req.provider_name}


@router.post("/api/models/test")
async def test_models():
    return await provider_manager.test_all()


# --- Memory Management ---
@router.get("/api/memory")
async def get_memories(limit: int = 50):
    return [m.model_dump() for m in memory_store.list_all(limit=limit)]


@router.get("/api/memory/search")
async def search_memory(q: str):
    return memory_store.search_semantic(q)


@router.delete("/api/memory/{memory_id}")
async def delete_memory(memory_id: str):
    success = memory_store.delete(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory item not found")
    return {"status": "deleted", "memory_id": memory_id}


# --- Security Audit Log ---
@router.get("/api/security/audit")
async def get_audit_logs(limit: int = 50):
    return [l.model_dump() for l in audit_logger.get_recent(limit=limit)]


# --- Real-time WebSocket ---
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Client can send pings or approval decisions via WS
            try:
                msg = json.loads(data)
                if msg.get("type") == "APPROVAL":
                    t_id = msg.get("task_id")
                    appr = msg.get("approved", False)
                    await swarm_orchestrator.handle_approval(t_id, appr)
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
