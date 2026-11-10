package com.swarmdroid.app.character

/**
 * The 14 Required Animation States for the SwarmDroid 3D Companion Mascot.
 */
enum class CharacterEmotion(val description: String) {
    IDLE("Gentle breathing, soft floating bob, natural eye blinks"),
    HAPPY("Smiling curved eyes, joyful bouncing motion"),
    THINKING("Inquisitive head tilt, eyes scanning left to right"),
    LISTENING("Attentive forward lean, ears angled, soundwave reactivity"),
    SPEAKING("Mouth visor wave modulation synchronized with speech"),
    WORKING("Focused forward posture, multi-agent status halo"),
    WALKING("Rhythmic stepping / thruster forward cycle"),
    RUNNING("Excited forward thrust and dynamic particles"),
    WAVING("Friendly raised hand greeting cycle"),
    CELEBRATING("Triumphant jumping and spin celebration"),
    SLEEPING("Low float altitude, closed eye slits, deep relaxed breathing"),
    ERROR("Puzzled head scratch, amber eye flicker, concerned tilt"),
    SURPRISED("Sudden jump back, widened eyes, expanding aura"),
    SAD("Drooped ears, downward gaze, dim slow-pulsing glow")
}
