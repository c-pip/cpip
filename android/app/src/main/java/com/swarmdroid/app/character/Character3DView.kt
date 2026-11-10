package com.swarmdroid.app.character

import android.annotation.SuppressLint
import android.content.Context
import android.opengl.GLSurfaceView
import android.view.MotionEvent
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView

@SuppressLint("ClickableViewAccessibility")
@Composable
fun Character3DView(
    emotion: CharacterEmotion = CharacterEmotion.IDLE,
    speechAmplitude: Float = 0f,
    modifier: Modifier = Modifier,
    onTap: () -> Unit = {}
) {
    var rendererRef by remember { mutableStateOf<CharacterRenderer?>(null) }

    LaunchedEffect(emotion) {
        rendererRef?.stateMachine?.setEmotion(emotion)
    }

    LaunchedEffect(speechAmplitude) {
        rendererRef?.stateMachine?.speechAmplitude = speechAmplitude
    }

    Box(modifier = modifier) {
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                TouchGLSurfaceView(ctx).apply {
                    val renderer = CharacterRenderer(ctx)
                    setRenderer(renderer)
                    rendererRef = renderer
                    this.onTapCallback = onTap
                }
            },
            update = { view ->
                // updates handled via stateMachine directly
            }
        )
    }
}

class TouchGLSurfaceView(context: Context) : GLSurfaceView(context) {
    private var renderer: CharacterRenderer? = null
    var onTapCallback: (() -> Unit)? = null
    
    private var previousX: Float = 0f
    private var previousY: Float = 0f
    private var isDragging: Boolean = false
    private var touchDownTime: Long = 0

    init {
        setEGLContextClientVersion(2)
        // Enable translucent surface to blend with Compose dark matte background
        setZOrderOnTop(true)
        holder.setFormat(android.graphics.PixelFormat.TRANSLUCENT)
    }

    override fun setRenderer(renderer: Renderer) {
        super.setRenderer(renderer)
        if (renderer is CharacterRenderer) {
            this.renderer = renderer
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val x = event.x
        val y = event.y

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                previousX = x
                previousY = y
                isDragging = false
                touchDownTime = System.currentTimeMillis()
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                val dx = x - previousX
                val dy = y - previousY
                if (dx * dx + dy * dy > 25) {
                    isDragging = true
                }
                renderer?.let { r ->
                    r.rotationY += dx * 0.4f
                    r.rotationX = (r.rotationX + dy * 0.4f).coerceIn(-40f, 40f)
                }
                previousX = x
                previousY = y
                return true
            }
            MotionEvent.ACTION_UP -> {
                val duration = System.currentTimeMillis() - touchDownTime
                if (!isDragging && duration < 300) {
                    // Tap event!
                    renderer?.stateMachine?.setEmotion(CharacterEmotion.HAPPY)
                    onTapCallback?.invoke()
                }
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
