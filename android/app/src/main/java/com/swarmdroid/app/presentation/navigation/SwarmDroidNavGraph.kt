package com.swarmdroid.app.presentation.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.compose.*
import com.swarmdroid.app.core.theme.*
import com.swarmdroid.app.presentation.screens.*
import com.swarmdroid.app.presentation.viewmodel.SwarmViewModel

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Companion : Screen("companion", "Companion", Icons.Default.Face)
    object Swarm : Screen("swarm", "Swarm", Icons.Default.Hub)
    object History : Screen("history", "History", Icons.Default.ChatBubble)
    object Models : Screen("models", "Models", Icons.Default.Settings)
    object Customize : Screen("customize", "Style", Icons.Default.Palette)
    object Studio : Screen("studio", "Studio", Icons.Default.AddCircle)
}

@Composable
fun SwarmDroidNavGraph(viewModel: SwarmViewModel) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val bottomNavItems = listOf(
        Screen.Companion,
        Screen.Swarm,
        Screen.History,
        Screen.Models,
        Screen.Customize
    )

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = SurfaceDark,
                contentColor = SoftWhite
            ) {
                bottomNavItems.forEach { screen ->
                    val isSelected = currentRoute == screen.route
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = screen.title) },
                        label = { Text(screen.title) },
                        selected = isSelected,
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = ElectricCyan,
                            selectedTextColor = ElectricCyan,
                            unselectedIconColor = DimGray,
                            unselectedTextColor = DimGray,
                            indicatorColor = SurfaceVariantDark
                        ),
                        onClick = {
                            if (currentRoute != screen.route) {
                                navController.navigate(screen.route) {
                                    popUpTo(Screen.Companion.route) { saveState = true }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Companion.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Companion.route) {
                MainCompanionScreen(
                    viewModel = viewModel,
                    onNavigateToSwarm = { navController.navigate(Screen.Swarm.route) }
                )
            }
            composable(Screen.Swarm.route) {
                AgentDashboardScreen(
                    viewModel = viewModel,
                    onNavigateToStudio = { navController.navigate(Screen.Studio.route) }
                )
            }
            composable(Screen.History.route) {
                ConversationHistoryScreen(viewModel = viewModel)
            }
            composable(Screen.Models.route) {
                ModelManagementScreen(viewModel = viewModel)
            }
            composable(Screen.Customize.route) {
                CharacterCustomizationScreen(viewModel = viewModel)
            }
            composable(Screen.Studio.route) {
                DynamicAgentStudioScreen(
                    viewModel = viewModel,
                    onAgentCreated = { navController.popBackStack() }
                )
            }
        }
    }
}
