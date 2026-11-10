package com.swarmdroid.app.character

import android.content.Context
import android.opengl.GLES20
import android.opengl.GLSurfaceView
import android.opengl.Matrix
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.FloatBuffer
import java.nio.ShortBuffer
import javax.microedition.khronos.egl.EGLConfig
import javax.microedition.khronos.opengles.GL10
import kotlin.math.cos
import kotlin.math.sin

class CharacterRenderer(private val context: Context) : GLSurfaceView.Renderer {

    val stateMachine = AnimationStateMachine()
    
    // Touch rotation
    var rotationY: Float = 0f
    var rotationX: Float = 0f
    
    private val vPMatrix = FloatArray(16)
    private val projectionMatrix = FloatArray(16)
    private val viewMatrix = FloatArray(16)
    private val modelMatrix = FloatArray(16)
    private val tempMatrix = FloatArray(16)
    
    private var programId: Int = 0
    private var uMVPMatrixHandle: Int = -1
    private var uModelMatrixHandle: Int = -1
    private var uColorHandle: Int = -1
    private var uEmissiveHandle: Int = -1
    private var aPositionHandle: Int = -1
    private var aNormalHandle: Int = -1

    private var sphereVertexBuffer: FloatBuffer? = null
    private var sphereNormalBuffer: FloatBuffer? = null
    private var sphereIndexBuffer: ShortBuffer? = null
    private var sphereIndexCount: Int = 0

    private var torusVertexBuffer: FloatBuffer? = null
    private var torusNormalBuffer: FloatBuffer? = null
    private var torusIndexBuffer: ShortBuffer? = null
    private var torusIndexCount: Int = 0

    private var startTimeMs: Long = System.currentTimeMillis()

    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        GLES20.glClearColor(0.04f, 0.05f, 0.07f, 1.0f) // Deep matte background
        GLES20.glEnable(GLES20.GL_DEPTH_TEST)
        GLES20.glDepthFunc(GLES20.GL_LEQUAL)
        GLES20.glEnable(GLES20.GL_BLEND)
        GLES20.glBlendFunc(GLES20.GL_SRC_ALPHA, GLES20.GL_ONE_MINUS_SRC_ALPHA)

        initShaders()
        generateGeometry()
    }

    override fun onSurfaceChanged(gl: GL10?, width: Int, height: Int) {
        GLES20.glViewport(0, 0, width, height)
        val ratio = width.toFloat() / height.toFloat()
        Matrix.perspectiveM(projectionMatrix, 0, 42.0f, ratio, 0.1f, 100.0f)
    }

    override fun onDrawFrame(gl: GL10?) {
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT or GLES20.GL_DEPTH_BUFFER_BIT)
        GLES20.glUseProgram(programId)

        val timeSec = (System.currentTimeMillis() - startTimeMs) / 1000.0f
        val pose = stateMachine.computePose(timeSec)

        // Camera setup
        Matrix.setLookAtM(viewMatrix, 0, 0f, 0.2f, 3.2f, 0f, 0.1f, 0f, 0f, 1f, 0f)

        // Draw Parts of Mascot
        // 1. Torso (Lavender Chassis)
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, -0.05f, 0f)
        Matrix.scaleM(modelMatrix, 0, 0.33f, 0.36f, 0.30f)
        drawSphere(color = floatArrayOf(0.72f, 0.57f, 1.0f, 1.0f), emissive = 0.15f)

        // 2. Chest Swarm Arc Reactor & Bezel (Electric Cyan Glow)
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, -0.02f, 0.29f)
        Matrix.scaleM(modelMatrix, 0, 0.085f, 0.085f, 0.04f)
        drawSphere(color = floatArrayOf(0.0f, 0.96f, 0.83f, 1.0f), emissive = pose.glowIntensity * 1.8f)

        // 3. Magnetic Floating Neck Collar (Dark Carbon Fiber)
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, 0.18f, 0f)
        Matrix.scaleM(modelMatrix, 0, 0.55f, 0.4f, 0.55f)
        drawTorus(color = floatArrayOf(0.12f, 0.14f, 0.18f, 1.0f), emissive = 0.1f)

        // 4. Head (White Ceramic Sphere)
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, 0.54f, 0f)
        Matrix.rotateM(modelMatrix, 0, pose.headTiltX * 57.3f, 1f, 0f, 0f)
        Matrix.rotateM(modelMatrix, 0, pose.headTiltZ * 57.3f, 0f, 0f, 1f)
        Matrix.scaleM(modelMatrix, 0, 0.45f, 0.43f, 0.43f)
        drawSphere(color = floatArrayOf(0.96f, 0.97f, 0.99f, 1.0f), emissive = 0.08f)

        // 5. Visor (Obsidian Glossy Glass)
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, 0.54f, 0f)
        Matrix.rotateM(modelMatrix, 0, pose.headTiltX * 57.3f, 1f, 0f, 0f)
        Matrix.rotateM(modelMatrix, 0, pose.headTiltZ * 57.3f, 0f, 0f, 1f)
        Matrix.translateM(modelMatrix, 0, 0f, 0.02f, 0.27f)
        Matrix.scaleM(modelMatrix, 0, 0.31f, 0.19f, 0.18f)
        drawSphere(color = floatArrayOf(0.04f, 0.05f, 0.08f, 0.96f), emissive = 0.25f)

        // 6. Holographic Cyan Eyes (Left & Right)
        val eyeY = 0.56f
        val eyeZ = 0.44f
        val eyeScaleY = 0.06f * pose.eyeScaleY
        val eyePupil = pose.eyePupilX * 0.035f

        // Left Eye
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, -0.13f + eyePupil, eyeY, eyeZ)
        Matrix.scaleM(modelMatrix, 0, 0.048f, eyeScaleY, 0.02f)
        drawSphere(color = floatArrayOf(0.0f, 0.96f, 0.83f, 1.0f), emissive = pose.glowIntensity * 2.0f)

        // Right Eye
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0.13f + eyePupil, eyeY, eyeZ)
        Matrix.scaleM(modelMatrix, 0, 0.048f, eyeScaleY, 0.02f)
        drawSphere(color = floatArrayOf(0.0f, 0.96f, 0.83f, 1.0f), emissive = pose.glowIntensity * 2.0f)

        // Mouth Waveform (Cyan lip-sync waveform)
        val mouthScale = 0.02f + (pose.mouthWaveAmp * 0.025f)
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, 0.46f, 0.42f)
        Matrix.scaleM(modelMatrix, 0, 0.08f, mouthScale, 0.015f)
        drawSphere(color = floatArrayOf(0.0f, 0.96f, 0.83f, 1.0f), emissive = pose.glowIntensity * 1.5f)

        // 7. Side Winged Antennas & Glowing Cores
        val earTilt = pose.earAngleZ * 57.3f
        // Left Antenna
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, -0.50f, 0.60f, 0f)
        Matrix.rotateM(modelMatrix, 0, -earTilt, 0f, 0f, 1f)
        Matrix.scaleM(modelMatrix, 0, 0.09f, 0.12f, 0.08f)
        drawSphere(color = floatArrayOf(0.72f, 0.57f, 1.0f, 1.0f), emissive = 0.35f)

        // Right Antenna
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0.50f, 0.60f, 0f)
        Matrix.rotateM(modelMatrix, 0, earTilt, 0f, 0f, 1f)
        Matrix.scaleM(modelMatrix, 0, 0.09f, 0.12f, 0.08f)
        drawSphere(color = floatArrayOf(0.72f, 0.57f, 1.0f, 1.0f), emissive = 0.35f)

        // 8. Articulated Arms & Hands
        // Left Arm (Resting or Celebratory)
        val armLeftY = if (pose.rightHandY > 0.3f && stateMachine.currentEmotion == CharacterEmotion.CELEBRATING) 0.3f else 0f
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, -0.42f, 0.02f + armLeftY, 0f)
        Matrix.scaleM(modelMatrix, 0, 0.085f, 0.085f, 0.085f)
        drawSphere(color = floatArrayOf(0.95f, 0.96f, 0.98f, 1.0f), emissive = 0.1f)

        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, -0.45f, -0.16f + armLeftY, 0.04f)
        Matrix.scaleM(modelMatrix, 0, 0.065f, 0.065f, 0.075f)
        drawSphere(color = floatArrayOf(0.72f, 0.57f, 1.0f, 1.0f), emissive = 0.2f)

        // Right Arm (Interactive: Waving / Celebrating raised posture)
        val armRightY = pose.rightHandY * 0.7f
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0.42f, 0.02f + armRightY, 0.04f)
        Matrix.scaleM(modelMatrix, 0, 0.085f, 0.085f, 0.085f)
        drawSphere(color = floatArrayOf(0.95f, 0.96f, 0.98f, 1.0f), emissive = 0.1f)

        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0.45f, -0.16f + armRightY, 0.08f)
        Matrix.scaleM(modelMatrix, 0, 0.065f, 0.065f, 0.075f)
        drawSphere(color = floatArrayOf(0.72f, 0.57f, 1.0f, 1.0f), emissive = 0.2f)

        // 9. Concentric Anti-Gravity Thruster Rings (Spinning Cyan Plasma)
        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, -0.44f, 0f)
        Matrix.rotateM(modelMatrix, 0, (timeSec * 50f) % 360f, 0f, 1f, 0f)
        drawTorus(color = floatArrayOf(0.0f, 0.96f, 0.83f, 0.9f), emissive = pose.glowIntensity * 1.5f)

        Matrix.setIdentityM(modelMatrix, 0)
        applyGlobalTransform(modelMatrix, pose)
        Matrix.translateM(modelMatrix, 0, 0f, -0.52f, 0f)
        Matrix.rotateM(modelMatrix, 0, -(timeSec * 70f) % 360f, 0f, 1f, 0f)
        Matrix.scaleM(modelMatrix, 0, 0.72f, 0.72f, 0.72f)
        drawTorus(color = floatArrayOf(0.72f, 0.57f, 1.0f, 0.8f), emissive = 0.8f)
    }

    private fun applyGlobalTransform(matrix: FloatArray, pose: MascotPose) {
        Matrix.translateM(matrix, 0, 0f, pose.hoverY, 0f)
        Matrix.rotateM(matrix, 0, rotationX, 1f, 0f, 0f)
        Matrix.rotateM(matrix, 0, rotationY, 0f, 1f, 0f)
        Matrix.scaleM(matrix, 0, pose.bounceScale, pose.bounceScale, pose.bounceScale)
    }

    private fun drawSphere(color: FloatArray, emissive: Float) {
        Matrix.multiplyMM(tempMatrix, 0, viewMatrix, 0, modelMatrix, 0)
        Matrix.multiplyMM(vPMatrix, 0, projectionMatrix, 0, tempMatrix, 0)

        GLES20.glUniformMatrix4fv(uMVPMatrixHandle, 1, false, vPMatrix, 0)
        GLES20.glUniformMatrix4fv(uModelMatrixHandle, 1, false, modelMatrix, 0)
        GLES20.glUniform4fv(uColorHandle, 1, color, 0)
        GLES20.glUniform1f(uEmissiveHandle, emissive)

        sphereVertexBuffer?.position(0)
        GLES20.glVertexAttribPointer(aPositionHandle, 3, GLES20.GL_FLOAT, false, 0, sphereVertexBuffer)
        GLES20.glEnableVertexAttribArray(aPositionHandle)

        sphereNormalBuffer?.position(0)
        GLES20.glVertexAttribPointer(aNormalHandle, 3, GLES20.GL_FLOAT, false, 0, sphereNormalBuffer)
        GLES20.glEnableVertexAttribArray(aNormalHandle)

        sphereIndexBuffer?.position(0)
        GLES20.glDrawElements(GLES20.GL_TRIANGLES, sphereIndexCount, GLES20.GL_UNSIGNED_SHORT, sphereIndexBuffer)
    }

    private fun drawTorus(color: FloatArray, emissive: Float) {
        Matrix.multiplyMM(tempMatrix, 0, viewMatrix, 0, modelMatrix, 0)
        Matrix.multiplyMM(vPMatrix, 0, projectionMatrix, 0, tempMatrix, 0)

        GLES20.glUniformMatrix4fv(uMVPMatrixHandle, 1, false, vPMatrix, 0)
        GLES20.glUniformMatrix4fv(uModelMatrixHandle, 1, false, modelMatrix, 0)
        GLES20.glUniform4fv(uColorHandle, 1, color, 0)
        GLES20.glUniform1f(uEmissiveHandle, emissive)

        torusVertexBuffer?.position(0)
        GLES20.glVertexAttribPointer(aPositionHandle, 3, GLES20.GL_FLOAT, false, 0, torusVertexBuffer)
        GLES20.glEnableVertexAttribArray(aPositionHandle)

        torusNormalBuffer?.position(0)
        GLES20.glVertexAttribPointer(aNormalHandle, 3, GLES20.GL_FLOAT, false, 0, torusNormalBuffer)
        GLES20.glEnableVertexAttribArray(aNormalHandle)

        torusIndexBuffer?.position(0)
        GLES20.glDrawElements(GLES20.GL_TRIANGLES, torusIndexCount, GLES20.GL_UNSIGNED_SHORT, torusIndexBuffer)
    }

    private fun initShaders() {
        val vertexShaderCode = """
            uniform mat4 uMVPMatrix;
            uniform mat4 uModelMatrix;
            attribute vec4 aPosition;
            attribute vec3 aNormal;
            varying vec3 vNormal;
            varying vec3 vWorldPos;
            void main() {
                gl_Position = uMVPMatrix * aPosition;
                vNormal = normalize(mat3(uModelMatrix) * aNormal);
                vWorldPos = vec3(uModelMatrix * aPosition);
            }
        """.trimIndent()

        val fragmentShaderCode = """
            precision mediump float;
            uniform vec4 uColor;
            uniform float uEmissive;
            varying vec3 vNormal;
            varying vec3 vWorldPos;
            void main() {
                vec3 lightDir = normalize(vec3(0.5, 1.0, 1.2));
                vec3 viewDir = normalize(vec3(0.0, 0.2, 3.2) - vWorldPos);
                
                // Diffuse
                float diff = max(dot(vNormal, lightDir), 0.0);
                
                // Blinn-Phong Specular
                vec3 halfDir = normalize(lightDir + viewDir);
                float spec = pow(max(dot(vNormal, halfDir), 0.0), 32.0);
                
                // Fresnel Rim Glow for futuristic cyber aesthetics
                float fresnel = pow(1.0 - max(dot(vNormal, viewDir), 0.0), 2.8);
                vec3 rimGlow = vec3(0.0, 0.96, 0.83) * fresnel * 0.45;
                
                vec3 ambient = vec3(0.22, 0.25, 0.32);
                vec3 lighting = ambient + diff * vec3(0.85) + spec * vec3(0.55);
                
                vec3 finalColor = uColor.rgb * lighting + (uColor.rgb * uEmissive * 1.2) + rimGlow;
                gl_FragColor = vec4(finalColor, uColor.a);
            }
        """.trimIndent()

        val vs = loadShader(GLES20.GL_VERTEX_SHADER, vertexShaderCode)
        val fs = loadShader(GLES20.GL_FRAGMENT_SHADER, fragmentShaderCode)

        programId = GLES20.glCreateProgram().also {
            GLES20.glAttachShader(it, vs)
            GLES20.glAttachShader(it, fs)
            GLES20.glLinkProgram(it)
        }

        uMVPMatrixHandle = GLES20.glGetUniformLocation(programId, "uMVPMatrix")
        uModelMatrixHandle = GLES20.glGetUniformLocation(programId, "uModelMatrix")
        uColorHandle = GLES20.glGetUniformLocation(programId, "uColor")
        uEmissiveHandle = GLES20.glGetUniformLocation(programId, "uEmissive")
        aPositionHandle = GLES20.glGetAttribLocation(programId, "aPosition")
        aNormalHandle = GLES20.glGetAttribLocation(programId, "aNormal")
    }

    private fun loadShader(type: Int, shaderCode: String): Int {
        return GLES20.glCreateShader(type).also { shader ->
            GLES20.glShaderSource(shader, shaderCode)
            GLES20.glCompileShader(shader)
        }
    }

    private fun generateGeometry() {
        // 1. Sphere Geometry
        val latBands = 14
        val lonBands = 18
        val radius = 1.0f
        val posList = mutableListOf<Float>()
        val normList = mutableListOf<Float>()
        val idxList = mutableListOf<Short>()

        for (lat in 0..latBands) {
            val theta = lat * Math.PI / latBands
            val sinTheta = sin(theta).toFloat()
            val cosTheta = cos(theta).toFloat()

            for (lon in 0..lonBands) {
                val phi = lon * 2 * Math.PI / lonBands
                val sinPhi = sin(phi).toFloat()
                val cosPhi = cos(phi).toFloat()

                val x = cosPhi * sinTheta
                val y = cosTheta
                val z = sinPhi * sinTheta

                normList.add(x); normList.add(y); normList.add(z)
                posList.add(x * radius); posList.add(y * radius); posList.add(z * radius)
            }
        }

        for (lat in 0 until latBands) {
            for (lon in 0 until lonBands) {
                val first = (lat * (lonBands + 1) + lon).toShort()
                val second = (first + lonBands + 1).toShort()

                idxList.add(first); idxList.add(second); idxList.add((first + 1).toShort())
                idxList.add(second); idxList.add((second + 1).toShort()); idxList.add((first + 1).toShort())
            }
        }

        sphereVertexBuffer = ByteBuffer.allocateDirect(posList.size * 4).order(ByteOrder.nativeOrder()).asFloatBuffer().apply {
            put(posList.toFloatArray()); position(0)
        }
        sphereNormalBuffer = ByteBuffer.allocateDirect(normList.size * 4).order(ByteOrder.nativeOrder()).asFloatBuffer().apply {
            put(normList.toFloatArray()); position(0)
        }
        sphereIndexBuffer = ByteBuffer.allocateDirect(idxList.size * 2).order(ByteOrder.nativeOrder()).asShortBuffer().apply {
            put(idxList.toShortArray()); position(0)
        }
        sphereIndexCount = idxList.size

        // 2. Torus Geometry (Ring)
        val radialSegments = 18
        val tubularSegments = 12
        val ringR = 0.28f
        val tubeR = 0.045f
        val tPosList = mutableListOf<Float>()
        val tNormList = mutableListOf<Float>()
        val tIdxList = mutableListOf<Short>()

        for (j in 0..radialSegments) {
            val u = j * 2 * Math.PI / radialSegments
            val cosU = cos(u).toFloat()
            val sinU = sin(u).toFloat()

            for (i in 0..tubularSegments) {
                val v = i * 2 * Math.PI / tubularSegments
                val cosV = cos(v).toFloat()
                val sinV = sin(v).toFloat()

                val x = (ringR + tubeR * cosV) * cosU
                val y = tubeR * sinV
                val z = (ringR + tubeR * cosV) * sinU

                tNormList.add(cosV * cosU); tNormList.add(sinV); tNormList.add(cosV * sinU)
                tPosList.add(x); tPosList.add(y); tPosList.add(z)
            }
        }

        for (j in 0 until radialSegments) {
            for (i in 0 until tubularSegments) {
                val first = (j * (tubularSegments + 1) + i).toShort()
                val second = ((j + 1) * (tubularSegments + 1) + i).toShort()

                tIdxList.add(first); tIdxList.add(second); tIdxList.add((first + 1).toShort())
                tIdxList.add(second); tIdxList.add((second + 1).toShort()); tIdxList.add((first + 1).toShort())
            }
        }

        torusVertexBuffer = ByteBuffer.allocateDirect(tPosList.size * 4).order(ByteOrder.nativeOrder()).asFloatBuffer().apply {
            put(tPosList.toFloatArray()); position(0)
        }
        torusNormalBuffer = ByteBuffer.allocateDirect(tNormList.size * 4).order(ByteOrder.nativeOrder()).asFloatBuffer().apply {
            put(tNormList.toFloatArray()); position(0)
        }
        torusIndexBuffer = ByteBuffer.allocateDirect(tIdxList.size * 2).order(ByteOrder.nativeOrder()).asShortBuffer().apply {
            put(tIdxList.toShortArray()); position(0)
        }
        torusIndexCount = tIdxList.size
    }
}
