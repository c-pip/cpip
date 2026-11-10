package com.swarmdroid.app.character

import kotlin.math.cos
import kotlin.math.sin

data class MascotPose(
    val hoverY: Float = 0f,
    val headTiltX: Float = 0f,
    val headTiltZ: Float = 0f,
    val eyeScaleY: Float = 1f,        // 1f = open, 0f = closed blink
    val eyePupilX: Float = 0f,        // Looking left/right
    val earAngleZ: Float = 0f,        // Antenna/ear twitch
    val rightHandY: Float = 0f,       // Waving/celebrating
    val mouthWaveAmp: Float = 0f,     // Lip-sync speech amplitude
    val glowIntensity: Float = 1f,    // 0.5f to 2.0f
    val bounceScale: Float = 1f
)

class AnimationStateMachine {
    var currentEmotion: CharacterEmotion = CharacterEmotion.IDLE
    private var targetEmotion: CharacterEmotion = CharacterEmotion.IDLE
    private var transitionProgress: Float = 1.0f

    // Speech amplitude for lip-sync (0.0 to 1.0)
    var speechAmplitude: Float = 0f

    fun setEmotion(emotion: CharacterEmotion) {
        if (targetEmotion != emotion) {
            targetEmotion = emotion
            transitionProgress = 0.0f
        }
    }

    fun computePose(timeSec: Float): MascotPose {
        // Natural blink calculation (every ~3.5 seconds)
        val blinkCycle = (timeSec % 3.5f)
        val isBlinking = blinkCycle < 0.15f
        val blinkFactor = if (isBlinking) (1.0f - (sin(blinkCycle / 0.15f * Math.PI).toFloat())) else 1.0f

        return when (targetEmotion) {
            CharacterEmotion.IDLE -> {
                val hover = sin(timeSec * 2.0f) * 0.04f
                MascotPose(
                    hoverY = hover,
                    headTiltX = sin(timeSec * 0.8f) * 0.03f,
                    eyeScaleY = blinkFactor,
                    glowIntensity = 1.0f + sin(timeSec * 1.5f) * 0.15f
                )
            }
            CharacterEmotion.HAPPY -> {
                val bounce = sin(timeSec * 6.0f) * 0.08f
                MascotPose(
                    hoverY = bounce,
                    headTiltZ = sin(timeSec * 4.0f) * 0.06f,
                    eyeScaleY = 0.7f, // Smiling curved slit
                    earAngleZ = sin(timeSec * 8.0f) * 0.12f,
                    glowIntensity = 1.4f,
                    bounceScale = 1.05f
                )
            }
            CharacterEmotion.THINKING -> {
                val scanX = sin(timeSec * 3.0f) * 0.25f
                MascotPose(
                    hoverY = sin(timeSec * 1.2f) * 0.02f,
                    headTiltZ = 0.18f, // Inquisitive tilt
                    headTiltX = -0.08f,
                    eyePupilX = scanX,
                    eyeScaleY = blinkFactor * 0.9f,
                    glowIntensity = 1.2f + sin(timeSec * 5.0f) * 0.3f
                )
            }
            CharacterEmotion.LISTENING -> {
                val audioReact = speechAmplitude * 0.1f
                MascotPose(
                    hoverY = sin(timeSec * 2.5f) * 0.03f + audioReact,
                    headTiltX = 0.12f, // Forward lean
                    earAngleZ = 0.15f + sin(timeSec * 5.0f) * 0.08f,
                    eyeScaleY = blinkFactor,
                    glowIntensity = 1.3f + audioReact * 2.0f
                )
            }
            CharacterEmotion.SPEAKING -> {
                val mouthWave = if (speechAmplitude > 0.05f) speechAmplitude else (sin(timeSec * 12.0f) * 0.5f + 0.5f)
                MascotPose(
                    hoverY = sin(timeSec * 2.5f) * 0.03f,
                    headTiltX = sin(timeSec * 4.0f) * 0.05f,
                    mouthWaveAmp = mouthWave,
                    eyeScaleY = blinkFactor,
                    glowIntensity = 1.2f + mouthWave * 0.4f
                )
            }
            CharacterEmotion.WORKING -> {
                val rapidBob = sin(timeSec * 4.0f) * 0.04f
                MascotPose(
                    hoverY = rapidBob,
                    headTiltX = 0.14f,
                    earAngleZ = sin(timeSec * 6.0f) * 0.05f,
                    glowIntensity = 1.6f + sin(timeSec * 8.0f) * 0.3f
                )
            }
            CharacterEmotion.WALKING -> {
                val stepBob = sin(timeSec * 5.0f) * 0.06f
                MascotPose(
                    hoverY = stepBob,
                    headTiltX = 0.05f,
                    headTiltZ = sin(timeSec * 5.0f) * 0.08f,
                    eyeScaleY = blinkFactor
                )
            }
            CharacterEmotion.RUNNING -> {
                val sprintBob = sin(timeSec * 9.0f) * 0.09f
                MascotPose(
                    hoverY = sprintBob,
                    headTiltX = 0.22f, // Strong forward lean
                    headTiltZ = sin(timeSec * 9.0f) * 0.12f,
                    glowIntensity = 1.8f
                )
            }
            CharacterEmotion.WAVING -> {
                val waveY = sin(timeSec * 8.0f) * 0.2f
                MascotPose(
                    hoverY = sin(timeSec * 2.0f) * 0.03f,
                    headTiltZ = -0.08f,
                    rightHandY = 0.3f + waveY,
                    eyeScaleY = blinkFactor,
                    glowIntensity = 1.2f
                )
            }
            CharacterEmotion.CELEBRATING -> {
                val jump = sin(timeSec * 7.0f) * 0.14f
                MascotPose(
                    hoverY = jump,
                    headTiltZ = sin(timeSec * 7.0f) * 0.15f,
                    rightHandY = 0.4f,
                    earAngleZ = sin(timeSec * 10.0f) * 0.2f,
                    glowIntensity = 2.0f,
                    bounceScale = 1.1f
                )
            }
            CharacterEmotion.SLEEPING -> {
                val deepBreath = sin(timeSec * 1.0f) * 0.02f
                MascotPose(
                    hoverY = -0.1f + deepBreath,
                    headTiltX = -0.1f,
                    eyeScaleY = 0.05f, // Closed slits
                    glowIntensity = 0.5f + sin(timeSec * 1.0f) * 0.1f
                )
            }
            CharacterEmotion.ERROR -> {
                val twitch = sin(timeSec * 12.0f) * 0.04f
                MascotPose(
                    hoverY = twitch,
                    headTiltZ = -0.2f,
                    eyePupilX = sin(timeSec * 10.0f) * 0.2f,
                    eyeScaleY = 0.6f,
                    glowIntensity = 1.5f
                )
            }
            CharacterEmotion.SURPRISED -> {
                MascotPose(
                    hoverY = 0.12f,
                    headTiltX = -0.18f,
                    eyeScaleY = 1.35f, // Wide eyes
                    earAngleZ = 0.25f,
                    glowIntensity = 1.8f,
                    bounceScale = 1.08f
                )
            }
            CharacterEmotion.SAD -> {
                val slowSigh = sin(timeSec * 0.8f) * 0.02f
                MascotPose(
                    hoverY = -0.06f + slowSigh,
                    headTiltX = 0.15f, // Looking down
                    earAngleZ = -0.12f, // Drooped ears
                    eyeScaleY = 0.7f,
                    glowIntensity = 0.6f
                )
            }
        }
    }
}
