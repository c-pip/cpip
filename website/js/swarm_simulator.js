/**
 * SwarmDroid Interactive Multi-Agent Swarm Simulator
 * Canvas DAG node graph demonstrator showing planning, signal streaming, and task execution.
 */

class SwarmSimulator {
  constructor(canvasId, logStreamId) {
    this.canvas = document.getElementById(canvasId);
    this.logStream = document.getElementById(logStreamId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.currentWorkflow = 'research_social';
    this.time = 0;
    this.activePackets = [];

    this.initAgents();
    this.initEvents();
    this.animate();
  }

  initAgents() {
    this.agents = [
      { id: 'master', name: 'Master Agent', role: 'Aegis Prime', x: 0, y: 0, status: 'IDLE', color: '#00F5D4', radius: 36, isMaster: true },
      { id: 'browser', name: 'Browser', role: 'Aura', angle: 0, status: 'IDLE', color: '#38BDF8', radius: 22 },
      { id: 'coder', name: 'Coding', role: 'ByteForge', angle: Math.PI / 4, status: 'IDLE', color: '#A78BFA', radius: 22 },
      { id: 'social', name: 'Social Media', role: 'Nexus', angle: Math.PI / 2, status: 'IDLE', color: '#F472B6', radius: 22 },
      { id: 'device', name: 'Device', role: 'DroidLink', angle: 3 * Math.PI / 4, status: 'IDLE', color: '#34D399', radius: 22 },
      { id: 'research', name: 'Research', role: 'Chronos', angle: Math.PI, status: 'IDLE', color: '#FBBF24', radius: 22 },
      { id: 'memory', name: 'Memory', role: 'Mnemosyne', angle: 5 * Math.PI / 4, status: 'IDLE', color: '#C084FC', radius: 22 },
      { id: 'security', name: 'Security', role: 'Aegis Guardian', angle: 3 * Math.PI / 2, status: 'IDLE', color: '#F87171', radius: 22 },
      { id: 'dynamic', name: 'Dynamic Agent', role: 'Docs Architect', angle: 7 * Math.PI / 4, status: 'OFFLINE', color: '#E879F9', radius: 22, isDynamic: true }
    ];
  }

  initEvents() {
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());

    // Preset buttons
    document.querySelectorAll('.preset-pill, .preset-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.preset-pill, .preset-btn').forEach(b => b.classList.remove('active'));
        const target = e.currentTarget;
        target.classList.add('active');
        this.currentWorkflow = target.getAttribute('data-flow');
        this.log(`Switched workflow to: ${target.textContent.trim()}`, 'info');
      });
    });

    // Run trigger button
    const runBtn = document.getElementById('btn-run-simulation');
    if (runBtn) {
      runBtn.addEventListener('click', () => this.runSimulation());
    }
  }

  resizeCanvas() {
    const parent = this.canvas.parentElement;
    if (!parent) return;
    const rect = parent.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(Math.floor(rect.width), 280);
    const isMobile = w < 640;
    const h = isMobile ? Math.max(300, Math.min(Math.floor(w * 0.8), 360)) : Math.min(Math.floor(w * 0.44), 400);

    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.canvas.style.width = w + 'px';
    this.canvas.style.height = h + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    this._renderWidth = w;
    this._renderHeight = h;
    this._isMobile = isMobile;
  }

  log(msg, type = 'info') {
    if (!this.logStream) return;
    const entry = document.createElement('div');
    entry.className = `log-line ${type}`;
    const now = new Date();
    const timeStr = `[${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}.${String(Math.floor(now.getMilliseconds() / 10)).padStart(2, '0')}]`;
    entry.innerHTML = `<span class="log-time">${timeStr}</span> ${msg}`;
    this.logStream.appendChild(entry);
    this.logStream.scrollTop = this.logStream.scrollHeight;
  }

  runSimulation() {
    this.resetStatuses();
    const master = this.agents[0];
    master.status = 'WORKING';

    if (this.currentWorkflow === 'research_social') {
      this.log('👑 Master Agent deconstructing goal: "Research latest Android AI and draft X post"', 'active');

      setTimeout(() => {
        this.spawnPacket('master', 'browser');
        this.setAgentStatus('browser', 'WORKING');
        this.log('🌐 Browser Agent dispatched: Crawling web documentation...', 'active');
      }, 700);

      setTimeout(() => {
        this.setAgentStatus('browser', 'COMPLETED');
        this.log('✓ Browser Agent: Extracted 4 technical benchmarks.', 'success');
        this.spawnPacket('browser', 'research');
        this.setAgentStatus('research', 'WORKING');
        this.log('🔬 Research Agent: Fact-checking and synthesizing summary...', 'active');
      }, 2200);

      setTimeout(() => {
        this.setAgentStatus('research', 'COMPLETED');
        this.log('✓ Research Agent: Stored knowledge in shared vector index.', 'success');
        this.spawnPacket('research', 'social');
        this.setAgentStatus('social', 'WORKING');
        this.log('📱 Social Media Agent: Drafting publication text and hashtags...', 'active');
      }, 3800);

      setTimeout(() => {
        this.setAgentStatus('social', 'APPROVAL');
        this.log('🛑 Security Agent: Tool "post_social_media" triggered Human Approval Gate.', 'approval');
      }, 5200);

      setTimeout(() => {
        this.setAgentStatus('social', 'COMPLETED');
        master.status = 'COMPLETED';
        this.log('🎉 Human verified action! Task successfully completed by swarm.', 'success');
      }, 6800);

    } else if (this.currentWorkflow === 'code_debug') {
      this.log('👑 Master Agent planning code audit & verification workflow', 'active');

      setTimeout(() => {
        this.spawnPacket('master', 'coder');
        this.setAgentStatus('coder', 'WORKING');
        this.log('💻 Coding Agent: Generating solution in isolated Python sandbox...', 'active');
      }, 700);

      setTimeout(() => {
        this.setAgentStatus('coder', 'COMPLETED');
        this.log('✓ Coding Agent: Code syntax verified clean, zero sandbox errors.', 'success');
        this.spawnPacket('coder', 'security');
        this.setAgentStatus('security', 'WORKING');
        this.log('🛡️ Security Agent: Scanning artifact for prompt injection/exfiltration...', 'active');
      }, 2400);

      setTimeout(() => {
        this.setAgentStatus('security', 'COMPLETED');
        master.status = 'COMPLETED';
        this.log('🎉 All security validations passed! Execution verified.', 'success');
      }, 4000);

    } else if (this.currentWorkflow === 'dynamic_agent') {
      this.log('👑 Master Agent: Required capability "DocumentationAgent" is missing in current roster.', 'active');

      setTimeout(() => {
        this.log('⚡ Dynamic Agent Manager: Instantiating sandboxed DocumentationAgent with tool scope [web_search, fetch_url]...', 'active');
        this.setAgentStatus('dynamic', 'WORKING');
        this.spawnPacket('master', 'dynamic');
      }, 1000);

      setTimeout(() => {
        this.setAgentStatus('dynamic', 'COMPLETED');
        master.status = 'COMPLETED';
        this.log('🎉 Dynamically spawned agent successfully finalized Markdown specification!', 'success');
      }, 3200);
    }
  }

  setAgentStatus(id, status) {
    const ag = this.agents.find(a => a.id === id);
    if (ag) ag.status = status;
  }

  resetStatuses() {
    this.agents.forEach(a => {
      a.status = a.id === 'dynamic' ? 'OFFLINE' : 'IDLE';
    });
    this.activePackets = [];
  }

  spawnPacket(fromId, toId) {
    this.activePackets.push({
      fromId,
      toId,
      progress: 0,
      speed: 0.02
    });
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    this.time += 0.016;
    const t = this.time;
    const ctx = this.ctx;
    const w = this._renderWidth || this.canvas.width;
    const h = this._renderHeight || this.canvas.height;
    const cx = w / 2;
    const cy = h / 2;
    const isMobile = this._isMobile;
    const orbitRadius = Math.min(w, h) * (isMobile ? 0.35 : 0.38);

    ctx.clearRect(0, 0, w, h);

    // Orbit Guide Rings
    ctx.strokeStyle = 'rgba(0, 245, 212, 0.08)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, cy, orbitRadius, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(139, 92, 246, 0.05)';
    ctx.beginPath();
    ctx.arc(cx, cy, orbitRadius * 0.6, 0, Math.PI * 2);
    ctx.stroke();

    // Calculate Coordinates
    this.agents.forEach(ag => {
      if (ag.isMaster) {
        ag.x = cx;
        ag.y = cy;
      } else {
        ag.x = cx + Math.cos(ag.angle) * orbitRadius;
        ag.y = cy + Math.sin(ag.angle) * orbitRadius;
      }
    });

    // Draw Connecting Edges
    const master = this.agents[0];
    this.agents.slice(1).forEach(ag => {
      if (ag.status === 'OFFLINE') return;
      const isWorking = ag.status === 'WORKING';
      ctx.strokeStyle = isWorking ? 'rgba(0, 245, 212, 0.65)' : 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = isWorking ? 2.5 : 1;
      ctx.beginPath();
      ctx.moveTo(master.x, master.y);
      ctx.lineTo(ag.x, ag.y);
      ctx.stroke();
    });

    // Draw Moving Data Packets
    this.activePackets.forEach((pkt, idx) => {
      pkt.progress += pkt.speed;
      const from = this.agents.find(a => a.id === pkt.fromId);
      const to = this.agents.find(a => a.id === pkt.toId);
      if (from && to) {
        const px = from.x + (to.x - from.x) * pkt.progress;
        const py = from.y + (to.y - from.y) * pkt.progress;

        ctx.fillStyle = 'rgba(0, 245, 212, 0.35)';
        ctx.beginPath();
        ctx.arc(px, py, 8, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#00F5D4';
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fill();
      }
      if (pkt.progress >= 1) {
        this.activePackets.splice(idx, 1);
      }
    });

    // Draw Agent Nodes
    const scale = isMobile ? 0.78 : 1.0;
    this.agents.forEach(ag => {
      const radius = ag.isMaster ? (36 * scale) : (22 * scale);

      if (ag.status === 'OFFLINE') {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.beginPath();
        ctx.arc(ag.x, ag.y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#4E5766';
        ctx.font = isMobile ? '8px JetBrains Mono' : '10px JetBrains Mono';
        ctx.textAlign = 'center';
        ctx.fillText('+ Dynamic', ag.x, ag.y + 3);
        return;
      }

      const isWorking = ag.status === 'WORKING';
      const isApproval = ag.status === 'APPROVAL';

      // Outer Pulsing Halo
      if (isWorking) {
        const pulseR = radius + 8 + Math.sin(t * 8) * 4;
        ctx.fillStyle = ag.isMaster ? 'rgba(0, 245, 212, 0.20)' : 'rgba(0, 245, 212, 0.25)';
        ctx.beginPath();
        ctx.arc(ag.x, ag.y, pulseR, 0, Math.PI * 2);
        ctx.fill();
      }

      // Base Node
      ctx.fillStyle = '#0F121B';
      ctx.beginPath();
      ctx.arc(ag.x, ag.y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Border Ring
      ctx.strokeStyle = isApproval ? '#F59E0B' : (isWorking ? '#00F5D4' : ag.color);
      ctx.lineWidth = ag.isMaster ? 3.5 : 2;
      ctx.beginPath();
      ctx.arc(ag.x, ag.y, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Inner Core
      ctx.fillStyle = isApproval ? '#F59E0B' : (isWorking ? '#00F5D4' : ag.color);
      ctx.beginPath();
      ctx.arc(ag.x, ag.y, ag.isMaster ? (10 * scale) : (6 * scale), 0, Math.PI * 2);
      ctx.fill();

      // Label
      ctx.fillStyle = '#F3F4F6';
      ctx.font = ag.isMaster 
        ? (isMobile ? 'bold 11px Plus Jakarta Sans' : 'bold 12px Plus Jakarta Sans')
        : (isMobile ? '10px Plus Jakarta Sans' : '11px Plus Jakarta Sans');
      ctx.textAlign = 'center';
      ctx.fillText(ag.name, ag.x, ag.y + radius + (isMobile ? 12 : 14));

      ctx.fillStyle = '#9CA3AF';
      ctx.font = isMobile ? '8px JetBrains Mono' : '9px JetBrains Mono';
      ctx.fillText(ag.status, ag.x, ag.y + radius + (isMobile ? 22 : 26));
    });
  }
}

// Instantiate simulator once DOM loads
window.addEventListener('DOMContentLoaded', () => {
  window.swarmSim = new SwarmSimulator('swarm-canvas', 'sim-log-stream');
});
