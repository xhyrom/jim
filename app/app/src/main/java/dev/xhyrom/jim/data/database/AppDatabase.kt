package dev.xhyrom.jim.data.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import dev.xhyrom.jim.data.models.Satellite
import dev.xhyrom.jim.data.dao.SatelliteDao

@Database(entities = [Satellite::class], version = 2, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun satelliteDao(): SatelliteDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null
        private const val DATABASE_NAME = "jim_database"

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "satellites_database"
                )
                .fallbackToDestructiveMigration() // Allows database to be reset instead of crashing
                .allowMainThreadQueries() // For simplicity in this app - not recommended for production
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}