package com.swarmdroid.app.core.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.swarmdroid.app.core.database.dao.*
import com.swarmdroid.app.core.database.entities.*

@Database(
    entities = [
        ConversationEntity::class,
        AgentEntity::class,
        TaskEntity::class,
        MemoryEntity::class,
        AuditLogEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class SwarmDatabase : RoomDatabase() {
    abstract fun conversationDao(): ConversationDao
    abstract fun agentDao(): AgentDao
    abstract fun taskDao(): TaskDao
    abstract fun memoryDao(): MemoryDao
    abstract fun auditLogDao(): AuditLogDao

    companion object {
        @Volatile
        private var INSTANCE: SwarmDatabase? = null

        fun getDatabase(context: Context): SwarmDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    SwarmDatabase::class.java,
                    "swarmdroid.db"
                ).fallbackToDestructiveMigration().build()
                INSTANCE = instance
                instance
            }
        }
    }
}
