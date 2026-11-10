package com.swarmdroid.app.presentation.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.swarmdroid.app.core.theme.ElectricCyan
import com.swarmdroid.app.core.theme.LavenderAccent

@Composable
fun VoiceVisualizerBar(
    amplitude: Float,
    isListening: Boolean,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .height(32.dp)
            .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        val barCount = 12
        for (i in 0 until barCount) {
            val factor = 1.0f - (Math.abs(i - barCount / 2f) / (barCount / 2f))
            val targetHeight = if (isListening) {
                (8.dp + 24.dp * amplitude * factor).coerceIn(4.dp, 30.dp)
            } else {
                4.dp
            }

            Box(
                modifier = Modifier
                    .width(4.dp)
                    .height(targetHeight)
                    .background(
                        if (i % 2 == 0) ElectricCyan else LavenderAccent,
                        shape = RoundedCornerShape(2.dp)
                    )
            )
        }
    }
}
