/**
 * SwarmDroid Interactive 3D Companion Mascot Viewer (Three.js WebGL)
 * Real-time PBR shaders, procedural breathing, blinking, and 14 animation state interpolations.
 */

class Companion3DViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.currentEmotion = 'IDLE';
    this.speechAmplitude = 0.0;
    this.time = 0;

    // Mouse / Touch Drag Rotation
    this.isDragging = false;
    this.previousMousePosition = { x: 0, y: 0 };
    this.targetRotation = { x: 0.1, y: 0.0 };
    this.currentRotation = { x: 0.1, y: 0.0 };

    this.initScene();
    this.buildMascotGeometry();
    this.initEvents();
    this.animate();
  }

  initScene() {
    const width = this.container.clientWidth || 400;
    const height = this.container.clientHeight || 360;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    this.camera.position.set(0, 0.2, 3.2);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.container.appendChild(this.renderer.domElement);

    // 3-Point Lighting + Cyber Ambient
    const ambientLight = new THREE.AmbientLight(0x222634, 1.8);
    this.scene.add(ambientLight);

    // Key Light (Warm Key)
    const keyLight = new THREE.DirectionalLight(0xF4F6FF, 1.6);
    keyLight.position.set(2, 4, 3);
    this.scene.add(keyLight);

    // Rim Light (Electric Cyan)
    const rimLight = new THREE.DirectionalLight(0x00F5D4, 2.2);
    rimLight.position.set(-3, -1, -2);
    this.scene.add(rimLight);

    // Fill Light (Lavender)
    const fillLight = new THREE.DirectionalLight(0xB892FF, 1.4);
    fillLight.position.set(0, -3, 2);
    this.scene.add(fillLight);

    // Root Group
    this.mascotGroup = new THREE.Group();
    this.scene.add(this.mascotGroup);
  }

  buildMascotGeometry() {
    // --- Materials ---
    // 1. Ceramic Pearl White
    const matCeramic = new THREE.MeshStandardMaterial({
      color: 0xF4F6F9,
      roughness: 0.18,
      metalness: 0.08
    });

    // 2. Obsidian Visor Glass
    const matVisor = new THREE.MeshStandardMaterial({
      color: 0x080A10,
      roughness: 0.10,
      metalness: 0.90
    });

    // 3. Metallic Lavender
    const matLavender = new THREE.MeshStandardMaterial({
      color: 0xB892FF,
      roughness: 0.28,
      metalness: 0.45
    });

    // 4. Electric Cyan Emissive
    this.matCyanEmissive = new THREE.MeshStandardMaterial({
      color: 0x00F5D4,
      emissive: 0x00F5D4,
      emissiveIntensity: 1.8,
      roughness: 0.15,
      metalness: 0.1
    });

    // 5. Dark Carbon Joints
    const matCarbon = new THREE.MeshStandardMaterial({
      color: 0x141822,
      roughness: 0.5,
      metalness: 0.3
    });

    // --- Sub-Groups for Hierarchical Animation ---
    this.torsoGroup = new THREE.Group();
    this.headGroup = new THREE.Group();
    this.armsGroup = new THREE.Group();
    this.thrusterGroup = new THREE.Group();

    this.mascotGroup.add(this.torsoGroup);
    this.mascotGroup.add(this.headGroup);
    this.mascotGroup.add(this.armsGroup);
    this.mascotGroup.add(this.thrusterGroup);

    // --- 1. Head Assembly ---
    this.headGroup.position.set(0, 0.54, 0);

    const headGeo = new THREE.SphereGeometry(0.45, 32, 24);
    headGeo.scale(1.02, 0.98, 1.0);
    this.headMesh = new THREE.Mesh(headGeo, matCeramic);
    this.headGroup.add(this.headMesh);

    // Visor Outer Glass
    const visorGeo = new THREE.SphereGeometry(0.31, 32, 24);
    visorGeo.scale(1.05, 0.65, 0.55);
    const visorMesh = new THREE.Mesh(visorGeo, matVisor);
    visorMesh.position.set(0, 0.02, 0.27);
    this.headGroup.add(visorMesh);

    // Left & Right Holographic Cyan Eyes
    const eyeGeo = new THREE.SphereGeometry(0.065, 16, 16);
    eyeGeo.scale(0.9, 1.1, 0.35);

    this.eyeLeft = new THREE.Mesh(eyeGeo, this.matCyanEmissive);
    this.eyeLeft.position.set(-0.13, 0.04, 0.41);
    this.headGroup.add(this.eyeLeft);

    this.eyeRight = new THREE.Mesh(eyeGeo, this.matCyanEmissive);
    this.eyeRight.position.set(0.13, 0.04, 0.41);
    this.headGroup.add(this.eyeRight);

    // Visor Mouth Lip-Sync Waveform
    const mouthGeo = new THREE.CylinderGeometry(0.012, 0.012, 0.12, 16);
    mouthGeo.rotateZ(Math.PI / 2);
    this.mouthMesh = new THREE.Mesh(mouthGeo, this.matCyanEmissive);
    this.mouthMesh.position.set(0, -0.09, 0.42);
    this.headGroup.add(this.mouthMesh);

    // Levitating Winged Antenna Pods
    const antGeo = new THREE.SphereGeometry(0.11, 16, 16);
    antGeo.scale(0.4, 1.2, 0.8);

    this.antennaLeft = new THREE.Mesh(antGeo, matLavender);
    this.antennaLeft.position.set(-0.50, 0.06, 0);
    this.headGroup.add(this.antennaLeft);

    this.antennaRight = new THREE.Mesh(antGeo, matLavender);
    this.antennaRight.position.set(0.50, 0.06, 0);
    this.headGroup.add(this.antennaRight);

    // --- 2. Torso Assembly ---
    this.torsoGroup.position.set(0, -0.05, 0);

    const torsoGeo = new THREE.SphereGeometry(0.33, 24, 20);
    torsoGeo.scale(1.05, 0.95, 0.9);
    const torsoMesh = new THREE.Mesh(torsoGeo, matLavender);
    this.torsoGroup.add(torsoMesh);

    // Swarm Arc Reactor Core (Pulsing Cyan)
    const reactorGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.03, 24);
    reactorGeo.rotateX(Math.PI / 2);
    this.reactorMesh = new THREE.Mesh(reactorGeo, this.matCyanEmissive);
    this.reactorMesh.position.set(0, 0.04, 0.30);
    this.torsoGroup.add(this.reactorMesh);

    // Neck Collar (Dark Carbon)
    const collarGeo = new THREE.TorusGeometry(0.16, 0.03, 16, 24);
    collarGeo.rotateX(Math.PI / 2);
    const collarMesh = new THREE.Mesh(collarGeo, matCarbon);
    collarMesh.position.set(0, 0.22, 0);
    this.torsoGroup.add(collarMesh);

    // --- 3. Articulated Arms ---
    // Left Arm (Shoulder + Forearm + Hand)
    this.armLeftGroup = new THREE.Group();
    this.armLeftGroup.position.set(-0.42, 0.0, 0);

    const shoulderGeo = new THREE.SphereGeometry(0.085, 16, 16);
    const shoulderL = new THREE.Mesh(shoulderGeo, matCeramic);
    this.armLeftGroup.add(shoulderL);

    const forearmGeo = new THREE.CylinderGeometry(0.04, 0.045, 0.20, 16);
    const forearmL = new THREE.Mesh(forearmGeo, matLavender);
    forearmL.position.set(-0.02, -0.12, 0.04);
    this.armLeftGroup.add(forearmL);

    const handGeo = new THREE.SphereGeometry(0.06, 16, 16);
    const handL = new THREE.Mesh(handGeo, matCeramic);
    handL.position.set(-0.03, -0.24, 0.08);
    this.armLeftGroup.add(handL);
    this.armsGroup.add(this.armLeftGroup);

    // Right Arm (Interactive Waving / Celebrating)
    this.armRightGroup = new THREE.Group();
    this.armRightGroup.position.set(0.42, 0.0, 0);

    const shoulderR = new THREE.Mesh(shoulderGeo, matCeramic);
    this.armRightGroup.add(shoulderR);

    const forearmR = new THREE.Mesh(forearmGeo, matLavender);
    forearmR.position.set(0.02, -0.12, 0.04);
    this.armRightGroup.add(forearmR);

    const handR = new THREE.Mesh(handGeo, matCeramic);
    handR.position.set(0.03, -0.24, 0.08);
    this.armRightGroup.add(handR);
    this.armsGroup.add(this.armRightGroup);

    // --- 4. Anti-Gravity Thruster Assembly ---
    this.thrusterGroup.position.set(0, -0.44, 0);

    const ringPrimaryGeo = new THREE.TorusGeometry(0.30, 0.042, 16, 32);
    ringPrimaryGeo.rotateX(Math.PI / 2);
    this.thrusterPrimary = new THREE.Mesh(ringPrimaryGeo, this.matCyanEmissive);
    this.thrusterGroup.add(this.thrusterPrimary);

    const ringSecondaryGeo = new THREE.TorusGeometry(0.20, 0.032, 16, 24);
    ringSecondaryGeo.rotateX(Math.PI / 2);
    this.thrusterSecondary = new THREE.Mesh(ringSecondaryGeo, matLavender);
    this.thrusterSecondary.position.set(0, -0.07, 0);
    this.thrusterGroup.add(this.thrusterSecondary);

    const plasmaGeo = new THREE.SphereGeometry(0.09, 16, 16);
    plasmaGeo.scale(1.0, 0.6, 1.0);
    this.plasmaMesh = new THREE.Mesh(plasmaGeo, this.matCyanEmissive);
    this.thrusterGroup.add(this.plasmaMesh);
  }

  setEmotion(emotion) {
    this.currentEmotion = emotion;
    const bubble = document.getElementById('mascot-speech-bubble');
    if (!bubble) return;

    const dialogues = {
      IDLE: '"Standing by with the intelligence swarm. What should we solve?"',
      HAPPY: '"Glad to help! The agents and I are energized and ready!"',
      THINKING: '"Hmm... Analyzing instruction dependencies and planning task graph..."',
      LISTENING: '"I am listening attentively. Voice soundwaves calibrated."',
      SPEAKING: '"Dispatched subtask results across the swarm network."',
      WORKING: '"Swarm agents actively collaborating on your task right now..."',
      CELEBRATING: '"Mission accomplished! All swarm tasks completed successfully! 🎉"',
      SLEEPING: '"Power-saving low orbit mode... (Zzz... zzz...)"',
      WAVING: '"Greetings, mobile explorer! SwarmDroid at your service!"'
    };

    bubble.textContent = dialogues[emotion] || `"Swarm status: ${emotion}"`;
  }

  initEvents() {
    // Window Resize
    window.addEventListener('resize', () => {
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });

    // Mouse / Touch Drag to Rotate
    const onDown = (e) => {
      this.isDragging = true;
      const clientX = e.clientX || (e.touches && e.touches[0].clientX);
      const clientY = e.clientY || (e.touches && e.touches[0].clientY);
      this.previousMousePosition = { x: clientX, y: clientY };
    };

    const onMove = (e) => {
      if (!this.isDragging) return;
      const clientX = e.clientX || (e.touches && e.touches[0].clientX);
      const clientY = e.clientY || (e.touches && e.touches[0].clientY);
      const deltaX = clientX - this.previousMousePosition.x;
      const deltaY = clientY - this.previousMousePosition.y;

      this.targetRotation.y += deltaX * 0.008;
      this.targetRotation.x = Math.max(-0.4, Math.min(0.4, this.targetRotation.x + deltaY * 0.008));

      this.previousMousePosition = { x: clientX, y: clientY };
    };

    const onUp = () => {
      this.isDragging = false;
    };

    this.container.addEventListener('mousedown', onDown);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);

    this.container.addEventListener('touchstart', onDown, { passive: true });
    window.addEventListener('touchmove', onMove, { passive: true });
    window.addEventListener('touchend', onUp);

    // Click to Celebrate Tap
    this.container.addEventListener('click', (e) => {
      if (this.currentEmotion !== 'CELEBRATING') {
        this.setEmotion('CELEBRATING');
        setTimeout(() => this.setEmotion('HAPPY'), 3500);
      }
    });

    // Emotion Pills Interaction
    document.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        const emotion = e.target.getAttribute('data-emotion');
        this.setEmotion(emotion);
      });
    });

    // State Cards Click-to-Test
    document.querySelectorAll('.state-card').forEach(card => {
      card.addEventListener('click', () => {
        const state = card.getAttribute('data-state');
        if (state) {
          this.setEmotion(state);
          // Highlight active pill if exists
          document.querySelectorAll('.pill-btn').forEach(b => {
            b.classList.toggle('active', b.getAttribute('data-emotion') === state);
          });
          // Scroll smoothly to mascot
          document.getElementById('mascot')?.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    this.time += 0.016;
    const t = this.time;

    // Smooth inertia interpolation on drag
    this.currentRotation.x += (this.targetRotation.x - this.currentRotation.x) * 0.08;
    this.currentRotation.y += (this.targetRotation.y - this.currentRotation.y) * 0.08;

    this.mascotGroup.rotation.x = this.currentRotation.x;
    this.mascotGroup.rotation.y = this.currentRotation.y;

    // Natural Eye Blink Cycle (Every ~3.5s)
    const blinkCycle = t % 3.5;
    const isBlink = blinkCycle < 0.16;
    const eyeScaleY = isBlink ? 0.05 : (this.currentEmotion === 'HAPPY' ? 0.6 : (this.currentEmotion === 'SLEEPING' ? 0.05 : 1.0));
    this.eyeLeft.scale.y = eyeScaleY;
    this.eyeRight.scale.y = eyeScaleY;

    // Spinning Anti-Gravity Thruster Rings
    this.thrusterPrimary.rotation.z = t * 1.5;
    this.thrusterSecondary.rotation.z = -t * 2.2;

    // Procedural Poses by Emotion State
    switch (this.currentEmotion) {
      case 'IDLE':
        this.mascotGroup.position.y = Math.sin(t * 2.0) * 0.04;
        this.headGroup.rotation.x = Math.sin(t * 0.8) * 0.03;
        this.headGroup.rotation.z = 0;
        this.armRightGroup.rotation.z = 0;
        this.armLeftGroup.rotation.z = 0;
        this.matCyanEmissive.emissiveIntensity = 1.6 + Math.sin(t * 2.5) * 0.3;
        break;

      case 'HAPPY':
        this.mascotGroup.position.y = Math.sin(t * 6.0) * 0.08;
        this.headGroup.rotation.z = Math.sin(t * 4.0) * 0.06;
        this.antennaLeft.rotation.z = Math.sin(t * 8.0) * 0.12;
        this.antennaRight.rotation.z = -Math.sin(t * 8.0) * 0.12;
        this.matCyanEmissive.emissiveIntensity = 2.2;
        break;

      case 'THINKING':
        this.mascotGroup.position.y = Math.sin(t * 1.2) * 0.02;
        this.headGroup.rotation.z = 0.18; // Inquisitive tilt
        this.headGroup.rotation.x = -0.08;
        const scan = Math.sin(t * 3.0) * 0.04;
        this.eyeLeft.position.x = -0.13 + scan;
        this.eyeRight.position.x = 0.13 + scan;
        this.matCyanEmissive.emissiveIntensity = 1.8 + Math.sin(t * 6.0) * 0.5;
        break;

      case 'LISTENING':
        this.mascotGroup.position.y = Math.sin(t * 2.5) * 0.03;
        this.headGroup.rotation.x = 0.12; // Forward attentive lean
        this.antennaLeft.rotation.z = 0.15;
        this.antennaRight.rotation.z = -0.15;
        this.matCyanEmissive.emissiveIntensity = 2.4;
        break;

      case 'SPEAKING':
        this.mascotGroup.position.y = Math.sin(t * 3.0) * 0.03;
        this.headGroup.rotation.x = Math.sin(t * 4.0) * 0.05;
        // Mouth waveform modulation
        const mouthWave = Math.sin(t * 14.0) * 0.5 + 0.5;
        this.mouthMesh.scale.y = 1.0 + mouthWave * 2.5;
        this.matCyanEmissive.emissiveIntensity = 1.8 + mouthWave * 0.6;
        break;

      case 'WORKING':
        this.mascotGroup.position.y = Math.sin(t * 5.0) * 0.04;
        this.headGroup.rotation.x = 0.14;
        this.thrusterPrimary.rotation.z = t * 4.0;
        this.matCyanEmissive.emissiveIntensity = 2.6;
        break;

      case 'CELEBRATING':
        this.mascotGroup.position.y = Math.abs(Math.sin(t * 7.0)) * 0.18;
        this.mascotGroup.rotation.y = this.currentRotation.y + Math.sin(t * 3.5) * 0.4;
        // Raise arms high!
        this.armRightGroup.rotation.z = 2.4 + Math.sin(t * 8.0) * 0.2;
        this.armLeftGroup.rotation.z = -2.4 - Math.sin(t * 8.0) * 0.2;
        this.matCyanEmissive.emissiveIntensity = 3.2;
        break;

      case 'SLEEPING':
        this.mascotGroup.position.y = -0.12 + Math.sin(t * 1.0) * 0.02;
        this.headGroup.rotation.x = -0.12;
        this.matCyanEmissive.emissiveIntensity = 0.6;
        break;

      case 'WAVING':
        this.mascotGroup.position.y = Math.sin(t * 2.0) * 0.03;
        this.headGroup.rotation.z = -0.08;
        this.armRightGroup.rotation.z = 1.8 + Math.sin(t * 9.0) * 0.35;
        this.matCyanEmissive.emissiveIntensity = 1.8;
        break;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

// Instantiate once DOM loads
window.addEventListener('DOMContentLoaded', () => {
  window.mascot3D = new Companion3DViewer('companion-3d-stage');
});
