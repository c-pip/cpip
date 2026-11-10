package com.swarmdroid.app

import com.swarmdroid.app.character.AnimationStateMachine
import com.swarmdroid.app.character.CharacterEmotion
import com.swarmdroid.app.domain.models.AgentInfo
import com.swarmdroid.app.domain.models.SwarmTaskItem
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class SwarmDroidUnitTest {

    private lateinit var stateMachine: AnimationStateMachine

    @Before
    fun setUp() {
        stateMachine = AnimationStateMachine()
    }

    @Test
    fun testAll14AnimationStatesAreDefined() {
        val states = CharacterEmotion.entries
        assertEquals("Must support exactly 14 required animation states", 14, states.size)
        
        val requiredNames = listOf(
            "IDLE", "HAPPY", "THINKING", "LISTENING", "SPEAKING",
            "WORKING", "WALKING", "RUNNING", "WAVING", "CELEBRATING",
            "SLEEPING", "ERROR", "SURPRISED", "SAD"
        )
        for (name in requiredNames) {
            assertNotNull("State $name must be present", CharacterEmotion.valueOf(name))
        }
    }

    @Test
    fun testIdlePoseCalculation() {
        stateMachine.setEmotion(CharacterEmotion.IDLE)
        val pose = stateMachine.computePose(1.0f)
        assertNotNull(pose)
        assertTrue("Idle pose should maintain standard scale", pose.bounceScale in 0.99f..1.01f)
        assertTrue("Glow should be active", pose.glowIntensity > 0.5f)
    }

    @Test
    fun testCelebratingPoseCalculation() {
        stateMachine.setEmotion(CharacterEmotion.CELEBRATING)
        val pose = stateMachine.computePose(0.5f)
        assertTrue("Celebrating should raise right hand", pose.rightHandY > 0.2f)
        assertTrue("Celebrating should have elevated glow", pose.glowIntensity >= 1.5f)
        assertTrue("Celebrating should bounce scale up", pose.bounceScale >= 1.05f)
    }

    @Test
    fun testSpeakingLipSyncAmplitude() {
        stateMachine.setEmotion(CharacterEmotion.SPEAKING)
        stateMachine.speechAmplitude = 0.85f
        val pose = stateMachine.computePose(0.2f)
        assertEquals(0.85f, pose.mouthWaveAmp, 0.01f)
    }

    @Test
    fun testSleepingEyesClosed() {
        stateMachine.setEmotion(CharacterEmotion.SLEEPING)
        val pose = stateMachine.computePose(1.5f)
        assertTrue("Sleeping eyes should be near closed slits", pose.eyeScaleY <= 0.1f)
        assertTrue("Sleeping companion floats lower", pose.hoverY < 0f)
    }

    @Test
    fun testThinkingHeadTilt() {
        stateMachine.setEmotion(CharacterEmotion.THINKING)
        val pose = stateMachine.computePose(2.0f)
        assertTrue("Thinking should have non-zero inquisitive head tilt", pose.headTiltZ > 0.1f)
    }

    @Test
    fun testDomainModels() {
        val agent = AgentInfo(
            role = "CodingAgent",
            name = "ByteForge Coder",
            description = "Code analysis and generation",
            currentStatus = "WORKING",
            isDynamic = false,
            allowedTools = listOf("run_sandbox_code")
        )
        assertEquals("CodingAgent", agent.role)
        assertEquals("WORKING", agent.currentStatus)
        assertEquals(1, agent.allowedTools.size)

        val task = SwarmTaskItem(
            taskId = "t_101",
            assignedAgent = "SocialMediaAgent",
            description = "Draft announcement tweet",
            state = "WAITING_FOR_APPROVAL",
            approvalPrompt = "Approve publishing this tweet?"
        )
        assertEquals("WAITING_FOR_APPROVAL", task.state)
        assertNotNull(task.approvalPrompt)
    }
}
